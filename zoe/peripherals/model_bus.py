"""
ZOE V1.3 — Universal Model Bus (Fase 7B)

Un bus que gestiona múltiples backends LLM simultáneamente y selecciona
el óptimo según contexto, recursos disponibles y nivel ACD.

ZOE habla con el ModelBus, no con un runtime específico. El bus decide
qué backend usar para cada petición.

Características:
- Gestiona múltiples LLMPeripheral activos (Ollama, OpenAI, Anthropic, etc.)
- Selecciona automáticamente el mejor backend según:
  * Nivel ACD (L0-L3): L0/L1 prefiere local rápido, L3 prefiere calidad
  * Dominio sensible: prefiere local por privacidad
  * Disponibilidad: si un backend cae, usa otro
  * Coste: L0-L1 prefiere gratis, L3 puede pagar
  * Latencia: L0 necesita <1s
- Fallback automático: si el backend seleccionado falla, intenta el siguiente
- Compatible con ResourceGraph: usa recursos descubiertos por Fase 7A
- Compatible con ModelOptimizer: usa recomendaciones de Fase 7F
- Streaming: delega al backend seleccionado
- Sin desconstruir: es un LLMPeripheral más (compuesto)

Uso:
    bus = ModelBus()
    bus.add_backend(OllamaPeripheral(model="qwen2.5:3b"), priority=10, cost=0.0)
    bus.add_backend(OpenAICompatiblePeripheral(model="gpt-4o", api_key="..."), priority=8, cost=0.03)
    bus.add_backend(AnthropicPeripheral(model="claude-sonnet-4-20250514", api_key="..."), priority=9, cost=0.02)

    # El bus selecciona automáticamente
    response = await bus.generate("hola", acd_level="L0")
    # → usa Ollama (gratis, rápido, local)

    response = await bus.generate("analiza las causas profundas", acd_level="L3")
    # → usa Anthropic (mejor calidad para análisis profundo)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, AsyncIterator
from enum import Enum

from .llm import LLMPeripheral, MockPeripheral

logger = logging.getLogger(__name__)


class SelectionStrategy(str, Enum):
    """Estrategia de selección de backend."""
    PRIORITY = "priority"           # Mayor prioridad disponible
    ACD_AWARE = "acd_aware"         # Según nivel ACD
    CHEAPEST = "cheapest"           # Menor coste
    FASTEST = "fastest"             # Menor latencia
    LOCAL_FIRST = "local_first"     # Local primero, cloud como fallback
    ROUND_ROBIN = "round_robin"     # Rotación entre disponibles


@dataclass
class BackendEntry:
    """Un backend registrado en el bus."""
    peripheral: LLMPeripheral
    name: str
    priority: int = 5               # 1-10, mayor = más prioritario
    cost_per_1k: float = 0.0        # EUR por 1000 tokens
    latency_ms: float = 500.0       # latencia estimada
    privacy: str = "local"          # local | network | cloud
    streaming: bool = True
    available: bool = True
    max_tokens: int = 4096
    health_check_ts: float = 0.0
    fail_count: int = 0
    max_fails: int = 3              # tras N fallos, marcar como no disponible
    models: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)  # ["local", "fast", "quality", "cheap", "cloud"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "priority": self.priority,
            "cost_per_1k": self.cost_per_1k,
            "latency_ms": self.latency_ms,
            "privacy": self.privacy,
            "streaming": self.streaming,
            "available": self.available,
            "fail_count": self.fail_count,
            "models": self.models,
            "tags": self.tags,
        }


class ModelBus(LLMPeripheral):
    """
    Universal Model Bus — gestiona múltiples backends LLM.

    Es un LLMPeripheral compuesto: ZOE no sabe si habla con un LLM
    directo o con un bus. El bus decide internamente qué backend usar.

    Selección ACD-aware:
    - L0/L1: prefiere local, rápido, gratis (Ollama 3B)
    - L2: prefiere local medio (Ollama 7B) o cloud barato
    - L3: prefiere máxima calidad (GPT-4o, Claude, 72B local)
    - Dominio sensible: prefiere local por privacidad (no cloud)
    """

    def __init__(self, strategy: SelectionStrategy = SelectionStrategy.ACD_AWARE):
        self._backends: Dict[str, BackendEntry] = {}
        self._strategy = strategy
        self._round_robin_idx = 0

        # Stats
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._fallback_count = 0
        self._selection_log: List[Dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "model_bus"

    @property
    def supports_streaming(self) -> bool:
        # Si cualquier backend soporta streaming, el bus también
        return any(b.streaming for b in self._backends.values() if b.available)

    def add_backend(
        self,
        peripheral: LLMPeripheral,
        name: str = None,
        priority: int = 5,
        cost_per_1k: float = 0.0,
        latency_ms: float = 500.0,
        privacy: str = "local",
        streaming: bool = True,
        models: List[str] = None,
        tags: List[str] = None,
        max_tokens: int = 4096,
        max_fails: int = 3,
    ) -> None:
        """Añade un backend al bus."""
        name = name or peripheral.name
        entry = BackendEntry(
            peripheral=peripheral,
            name=name,
            priority=priority,
            cost_per_1k=cost_per_1k,
            latency_ms=latency_ms,
            privacy=privacy,
            streaming=streaming,
            models=models or [],
            tags=tags or [],
            max_tokens=max_tokens,
            max_fails=max_fails,
        )
        self._backends[name] = entry
        logger.info(f"ModelBus: added backend '{name}' (priority={priority}, cost={cost_per_1k}, privacy={privacy})")

    def remove_backend(self, name: str) -> bool:
        return self._backends.pop(name, None) is not None

    def list_backends(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self._backends.values()]

    def get_available_backends(self) -> List[BackendEntry]:
        return [b for b in self._backends.values() if b.available]

    def mark_unavailable(self, name: str) -> None:
        if name in self._backends:
            self._backends[name].available = False
            logger.warning(f"ModelBus: backend '{name}' marked unavailable")

    def mark_available(self, name: str) -> None:
        if name in self._backends:
            self._backends[name].available = True
            self._backends[name].fail_count = 0
            logger.info(f"ModelBus: backend '{name}' marked available")

    def select_backend(
        self,
        acd_level: str = None,
        sensitive_domain: bool = False,
        prefer_local: bool = False,
    ) -> Optional[BackendEntry]:
        """
        Selecciona el mejor backend según estrategia y contexto.

        Args:
            acd_level: "L0_REFLEX" | "L1_FAST" | "L2_STANDARD" | "L3_DEEP"
            sensitive_domain: si True, excluye cloud (privacidad)
            prefer_local: si True, prefiere backends locales

        Returns:
            BackendEntry seleccionado o None si no hay disponibles
        """
        available = self.get_available_backends()
        if not available:
            return None

        # Filtrar por dominio sensible (excluir cloud)
        if sensitive_domain:
            available = [b for b in available if b.privacy == "local"]

        if not available:
            return None

        if self._strategy == SelectionStrategy.ACD_AWARE:
            return self._select_acd_aware(available, acd_level, prefer_local)
        elif self._strategy == SelectionStrategy.PRIORITY:
            return max(available, key=lambda b: b.priority)
        elif self._strategy == SelectionStrategy.CHEAPEST:
            return min(available, key=lambda b: b.cost_per_1k)
        elif self._strategy == SelectionStrategy.FASTEST:
            return min(available, key=lambda b: b.latency_ms)
        elif self._strategy == SelectionStrategy.LOCAL_FIRST:
            local = [b for b in available if b.privacy == "local"]
            if local:
                return max(local, key=lambda b: b.priority)
            return max(available, key=lambda b: b.priority)
        elif self._strategy == SelectionStrategy.ROUND_ROBIN:
            if not available:
                return None
            selected = available[self._round_robin_idx % len(available)]
            self._round_robin_idx += 1
            return selected
        else:
            return max(available, key=lambda b: b.priority)

    def _select_acd_aware(
        self,
        available: List[BackendEntry],
        acd_level: str,
        prefer_local: bool,
    ) -> BackendEntry:
        """Selección inteligente según nivel ACD."""

        # Score cada backend
        def score(b: BackendEntry) -> float:
            s = b.priority * 10

            # ACD-aware adjustments
            if acd_level:
                if acd_level in ("L0_REFLEX", "L1_FAST"):
                    # Priorizar velocidad y gratis
                    if "fast" in b.tags or b.latency_ms < 200:
                        s += 30
                    if b.cost_per_1k == 0:
                        s += 20
                    if b.privacy == "local":
                        s += 15
                elif acd_level == "L2_STANDARD":
                    # Balance
                    if b.privacy == "local":
                        s += 10
                    if b.cost_per_1k < 0.02:
                        s += 10
                elif acd_level == "L3_DEEP":
                    # Priorizar calidad
                    if "quality" in b.tags:
                        s += 30
                    if b.max_tokens >= 4096:
                        s += 10
                    # Local grande también es válido
                    if b.privacy == "local" and "quality" in b.tags:
                        s += 20

            # Prefer local
            if prefer_local and b.privacy == "local":
                s += 15

            # Penalizar fallos
            s -= b.fail_count * 5

            return s

        return max(available, key=score)

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
        acd_level: str = None,
        sensitive_domain: bool = False,
        prefer_local: bool = False,
    ) -> str:
        """
        Genera texto usando el backend óptimo.

        Si el backend seleccionado falla, intenta el siguiente (fallback).
        """
        self._total_requests += 1

        # Seleccionar backend
        selected = self.select_backend(
            acd_level=acd_level,
            sensitive_domain=sensitive_domain,
            prefer_local=prefer_local,
        )

        if not selected:
            self._failed_requests += 1
            logger.error("ModelBus: no backends available")
            return "[ModelBus: no backends available]"

        # Log selección
        self._selection_log.append({
            "timestamp": time.time(),
            "backend": selected.name,
            "acd_level": acd_level,
            "sensitive": sensitive_domain,
        })
        if len(self._selection_log) > 100:
            self._selection_log = self._selection_log[-50:]

        # Intentar con el backend seleccionado
        try:
            effective_max = min(max_tokens, selected.max_tokens)
            response = await selected.peripheral.generate(
                prompt=prompt,
                system=system,
                max_tokens=effective_max,
                temperature=temperature,
            )
            self._successful_requests += 1
            selected.health_check_ts = time.time()
            return response

        except Exception as e:
            logger.warning(f"ModelBus: backend '{selected.name}' failed: {e}")
            selected.fail_count += 1
            if selected.fail_count >= selected.max_fails:
                self.mark_unavailable(selected.name)

            # Fallback: intentar con el siguiente disponible
            self._fallback_count += 1
            return await self._fallback_generate(
                prompt, system, max_tokens, temperature,
                acd_level, sensitive_domain, prefer_local,
                exclude=[selected.name],
            )

    async def _fallback_generate(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        acd_level: str,
        sensitive_domain: bool,
        prefer_local: bool,
        exclude: List[str],
    ) -> str:
        """Intenta generar con backends alternativos."""
        available = [
            b for b in self.get_available_backends()
            if b.name not in exclude
        ]

        if sensitive_domain:
            available = [b for b in available if b.privacy == "local"]

        if not available:
            self._failed_requests += 1
            return f"[ModelBus: all backends failed]"

        # Ordenar por prioridad
        available.sort(key=lambda b: b.priority, reverse=True)

        for backend in available:
            try:
                effective_max = min(max_tokens, backend.max_tokens)
                response = await backend.peripheral.generate(
                    prompt=prompt,
                    system=system,
                    max_tokens=effective_max,
                    temperature=temperature,
                )
                self._successful_requests += 1
                backend.health_check_ts = time.time()
                logger.info(f"ModelBus: fallback to '{backend.name}' succeeded")
                return response
            except Exception as e:
                logger.warning(f"ModelBus: fallback '{backend.name}' also failed: {e}")
                backend.fail_count += 1
                if backend.fail_count >= backend.max_fails:
                    self.mark_unavailable(backend.name)
                continue

        self._failed_requests += 1
        return "[ModelBus: all backends failed]"

    async def generate_streaming(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
        acd_level: str = None,
        sensitive_domain: bool = False,
        prefer_local: bool = False,
    ) -> AsyncIterator[str]:
        """Streaming usando el backend óptimo que soporte streaming."""
        selected = self.select_backend(
            acd_level=acd_level,
            sensitive_domain=sensitive_domain,
            prefer_local=prefer_local,
        )

        if not selected:
            yield "[ModelBus: no backends available]"
            return

        if not selected.streaming:
            # Fallback: generate sin streaming
            response = await self.generate(
                prompt, system, max_tokens, temperature,
                acd_level, sensitive_domain, prefer_local,
            )
            yield response
            return

        try:
            effective_max = min(max_tokens, selected.max_tokens)
            async for chunk in selected.peripheral.generate_streaming(
                prompt=prompt,
                system=system,
                max_tokens=effective_max,
                temperature=temperature,
            ):
                yield chunk
        except Exception as e:
            logger.warning(f"ModelBus: streaming from '{selected.name}' failed: {e}")
            selected.fail_count += 1
            if selected.fail_count >= selected.max_fails:
                self.mark_unavailable(selected.name)
            # Fallback: generate sin streaming
            response = await self._fallback_generate(
                prompt, system, max_tokens, temperature,
                acd_level, sensitive_domain, prefer_local,
                exclude=[selected.name],
            )
            yield response

    async def health_check(self) -> bool:
        """Verifica que al menos un backend esté disponible."""
        available = self.get_available_backends()
        return len(available) > 0

    def get_stats(self) -> Dict[str, Any]:
        return {
            "strategy": self._strategy.value,
            "total_backends": len(self._backends),
            "available_backends": len(self.get_available_backends()),
            "total_requests": self._total_requests,
            "successful_requests": self._successful_requests,
            "failed_requests": self._failed_requests,
            "fallback_count": self._fallback_count,
            "success_rate": round(
                self._successful_requests / max(1, self._total_requests), 3
            ),
            "backends": self.list_backends(),
            "recent_selections": self._selection_log[-10:],
        }

    @classmethod
    def from_resource_graph(cls, resource_graph: Any) -> "ModelBus":
        """
        Crea un ModelBus desde un ResourceGraph (Fase 7A).

        Convierte cada nodo de tipo OLLAMA o CLOUD_API en un backend del bus.
        """
        from ..peripherals.resource_discovery import ResourceType, ResourceGraph
        from ..peripherals.llm import (
            OllamaPeripheral, OpenAICompatiblePeripheral, AnthropicPeripheral,
        )

        bus = cls(strategy=SelectionStrategy.ACD_AWARE)

        if not isinstance(resource_graph, ResourceGraph):
            return bus

        # Ollama nodes
        for node in resource_graph.get_ollama_nodes():
            base_url = node.address or "http://localhost:11434"
            for model_name in node.models:
                try:
                    peripheral = OllamaPeripheral(
                        model=model_name,
                        base_url=base_url,
                    )
                    # Estimar tamaño del modelo para prioridad
                    import re
                    match = re.search(r'(\d+(?:\.\d+)?)b', model_name.lower())
                    params_b = float(match.group(1)) if match else 3.0

                    if params_b <= 3:
                        priority = 10
                        tags = ["local", "fast", "cheap"]
                    elif params_b <= 8:
                        priority = 8
                        tags = ["local", "balanced"]
                    else:
                        priority = 7
                        tags = ["local", "quality"]

                    bus.add_backend(
                        peripheral=peripheral,
                        name=f"ollama_{model_name}",
                        priority=priority,
                        cost_per_1k=0.0,
                        latency_ms=node.latency_ms or 100.0,
                        privacy="local",
                        streaming=True,
                        models=[model_name],
                        tags=tags,
                    )
                except Exception as e:
                    logger.warning(f"ModelBus: failed to add Ollama backend {model_name}: {e}")

        # Cloud API nodes
        for node in resource_graph.get_cloud_apis():
            try:
                api_key = None
                model = node.models[0] if node.models else "gpt-4o"

                if "openai" in node.id:
                    import os
                    api_key = os.environ.get("OPENAI_API_KEY")
                    peripheral = OpenAICompatiblePeripheral(
                        model=model, api_key=api_key, base_url=node.address,
                    )
                    tags = ["cloud", "quality"]
                    priority = 9
                elif "anthropic" in node.id:
                    import os
                    api_key = os.environ.get("ANTHROPIC_API_KEY")
                    peripheral = AnthropicPeripheral(
                        model=model, api_key=api_key, base_url=node.address,
                    )
                    tags = ["cloud", "quality", "ethical"]
                    priority = 9
                elif "deepseek" in node.id:
                    import os
                    api_key = os.environ.get("DEEPSEEK_API_KEY")
                    peripheral = OpenAICompatiblePeripheral(
                        model=model, api_key=api_key, base_url=node.address,
                    )
                    tags = ["cloud", "reasoning"]
                    priority = 8
                else:
                    # Cloud API genérico
                    peripheral = OpenAICompatiblePeripheral(
                        model=model, api_key="placeholder", base_url=node.address,
                    )
                    tags = ["cloud"]
                    priority = 6

                bus.add_backend(
                    peripheral=peripheral,
                    name=node.id,
                    priority=priority,
                    cost_per_1k=node.cost_per_1k_tokens or 0.02,
                    latency_ms=node.latency_ms or 500.0,
                    privacy="cloud",
                    streaming=True,
                    models=node.models,
                    tags=tags,
                )
            except Exception as e:
                logger.warning(f"ModelBus: failed to add cloud backend {node.id}: {e}")

        return bus
