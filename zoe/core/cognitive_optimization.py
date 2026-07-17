"""
ZOE V1.8 — Cognitive Optimization Layer (Sprint 5)

3 capas aditivas que usan la información cognitiva de ZOE para optimizar
la inferencia del LLM SIN deconstruir nada.

1. ZMAP — Tensor Optimization Map
   Archivo metadata que acompaña al GGUF con estrategias de carga optimizadas.

2. CognitivePrefetchLayer (CPL)
   Usa ACD + memory + capsules para pre-cargar modelo y contexto ANTES
   de que el Speaker llame al LLM.

3. TensorPredictionEngine (TPE)
   Predice qué capas del modelo necesitará según ACD + intención + dominio.

Sin deconstruir: son capas NUEVAS. No modifican ModelOptimizer, ni Speaker,
ni el bucle cognitivo. Se integran como capas de optimización transparentes.

Utilizable en TODAS las formas de uso de ZOE:
- .zoe (PatternSpeaker usa CPL para decidir si necesita LLM)
- Pendrive (ModelOptimizer usa .zmap para optimizar mmap)
- Dashboard (CPL pre-carga modelo antes de generar)
- Voice-first (CPL pre-calienta Ollama antes de hablar)
- Portátil (TPE decide qué capas cargar)
- VPS (CPL + TPE + .zmap combinados)
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


# ============================================================
# 1. ZMAP — Tensor Optimization Map
# ============================================================

class ZMAPStrategy(str, Enum):
    """Estrategias de carga definidas en .zmap."""
    FULL_LOAD = "full_load"
    PARTIAL_LOAD = "partial_load"
    MMAP_SEQUENTIAL = "mmap_sequential"
    MMAP_RANDOM = "mmap_random"
    PATTERN_ONLY = "pattern_only"


@dataclass
class LayerInfo:
    """Información de una capa del modelo."""
    name: str
    size_gb: float
    priority: str  # critical | high | medium | low
    access_pattern: str  # once | sequential | random


@dataclass
class RAMStrategy:
    """Estrategia para una cantidad de RAM."""
    ram_gb: float
    keep_in_ram: List[str]
    mmap: List[str]
    prefetch_layers: int
    strategy: str


@dataclass
class ZMAP:
    """
    Tensor Optimization Map — metadata de optimización para un modelo GGUF.

    Acompaña al .gguf (no lo reemplaza). Contiene:
    - Información de capas (tamaño, prioridad, patrón de acceso)
    - Estrategias por RAM disponible
    - Perfil de acceso (capas calientes/frías)
    - Optimizaciones ZOE-específicas (ACD, dominio sensible)
    """
    model: str
    format: str = "gguf"
    version: str = "1.0"
    layers: Dict[str, LayerInfo] = field(default_factory=dict)
    strategies: List[RAMStrategy] = field(default_factory=list)
    access_profile: Dict[str, Any] = field(default_factory=dict)
    zoe_optimizations: Dict[str, Any] = field(default_factory=dict)

    def get_strategy_for_ram(self, ram_gb: float) -> Optional[RAMStrategy]:
        """Devuelve la mejor estrategia para la RAM disponible."""
        best = None
        for s in self.strategies:
            if s.ram_gb <= ram_gb:
                if best is None or s.ram_gb > best.ram_gb:
                    best = s
        return best

    def get_zoe_optimization(self, acd_level: str, 
                              sensitive_domain: bool = False) -> Dict[str, Any]:
        """Devuelve optimización ZOE-específica para el contexto."""
        key = f"acd_{acd_level.lower().replace('_', '')}"
        opt = self.zoe_optimizations.get(key, {})

        if sensitive_domain:
            sensitive_opt = self.zoe_optimizations.get("sensitive_domain", {})
            opt = {**opt, **sensitive_opt}

        return opt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "format": self.format,
            "version": self.version,
            "layers": {k: asdict(v) for k, v in self.layers.items()},
            "strategies": [asdict(s) for s in self.strategies],
            "access_profile": self.access_profile,
            "zoe_optimizations": self.zoe_optimizations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZMAP":
        layers = {}
        for name, info in data.get("layers", {}).items():
            layers[name] = LayerInfo(**info)

        strategies = []
        for s in data.get("strategies", []):
            strategies.append(RAMStrategy(**s))

        return cls(
            model=data["model"],
            format=data.get("format", "gguf"),
            version=data.get("version", "1.0"),
            layers=layers,
            strategies=strategies,
            access_profile=data.get("access_profile", {}),
            zoe_optimizations=data.get("zoe_optimizations", {}),
        )


class ZMAPLoader:
    """
    Carga archivos .zmap desde disco.

    Busca .zmap junto al modelo GGUF o en un directorio centralizado.
    """

    def __init__(self, zmap_dir: str = None):
        self.zmap_dir = Path(zmap_dir) if zmap_dir else None
        self._cache: Dict[str, ZMAP] = {}

    def load(self, model_name: str) -> Optional[ZMAP]:
        """Carga el .zmap para un modelo."""
        if model_name in self._cache:
            return self._cache[model_name]

        # Normalizar nombre del modelo
        clean_name = model_name.replace(":", "_").replace("/", "_")

        # Buscar .zmap
        zmap_path = self._find_zmap(clean_name)
        if not zmap_path:
            logger.debug(f"ZMAPLoader: no .zmap found for {model_name}")
            return None

        try:
            with open(zmap_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            zmap = ZMAP.from_dict(data)
            self._cache[model_name] = zmap
            logger.info(f"ZMAPLoader: loaded .zmap for {model_name} from {zmap_path}")
            return zmap
        except Exception as e:
            logger.warning(f"ZMAPLoader: error loading .zmap: {e}")
            return None

    def _find_zmap(self, clean_name: str) -> Optional[Path]:
        """Busca archivo .zmap para el modelo."""
        candidates = []

        # Directorio centralizado
        if self.zmap_dir:
            candidates.append(self.zmap_dir / f"{clean_name}.zmap")

        # Directorio de modelos de Ollama
        ollama_models = os.environ.get("OLLAMA_MODELS", os.path.expanduser("~/.ollama/models"))
        candidates.append(Path(ollama_models) / f"{clean_name}.zmap")

        # Directorio actual
        candidates.append(Path(f"{clean_name}.zmap"))

        for path in candidates:
            if path.exists():
                return path

        return None

    def generate_default_zmap(self, model_name: str, params_b: float,
                               num_layers: int = 32) -> ZMAP:
        """
        Genera un .zmap por defecto basado en heurísticas del modelo.

        Esto se puede usar cuando no existe un .zmap optimizado para un modelo.
        """
        total_size_gb = params_b * 0.6  # Q4 estimate
        layer_size_gb = total_size_gb / num_layers

        # Capas por defecto
        layers = {
            "embedding": LayerInfo(
                name="embedding",
                size_gb=total_size_gb * 0.03,
                priority="critical",
                access_pattern="once",
            ),
            "attention": LayerInfo(
                name="attention",
                size_gb=layer_size_gb * 0.4 * num_layers,
                priority="high",
                access_pattern="sequential",
            ),
            "mlp": LayerInfo(
                name="mlp",
                size_gb=layer_size_gb * 0.6 * num_layers,
                priority="medium",
                access_pattern="sequential",
            ),
            "output": LayerInfo(
                name="output",
                size_gb=total_size_gb * 0.02,
                priority="low",
                access_pattern="once",
            ),
        }

        # Estrategias por RAM
        strategies = [
            RAMStrategy(
                ram_gb=4.0,
                keep_in_ram=["embedding"],
                mmap=["attention", "mlp", "output"],
                prefetch_layers=2,
                strategy=ZMAPStrategy.MMAP_SEQUENTIAL.value,
            ),
            RAMStrategy(
                ram_gb=8.0,
                keep_in_ram=["embedding", "attention"],
                mmap=["mlp", "output"],
                prefetch_layers=4,
                strategy=ZMAPStrategy.MMAP_SEQUENTIAL.value,
            ),
            RAMStrategy(
                ram_gb=16.0,
                keep_in_ram=["embedding", "attention", "mlp"],
                mmap=["output"],
                prefetch_layers=8,
                strategy=ZMAPStrategy.FULL_LOAD.value,
            ),
        ]

        # Perfil de acceso
        access_profile = {
            "total_layers": num_layers,
            "hot_layers": list(range(min(8, num_layers))) + list(range(max(0, num_layers - 4), num_layers)),
            "cold_layers": list(range(8, max(8, num_layers - 4))) if num_layers > 12 else [],
            "typical_sequence": "embedding → attention_1 → mlp_1 → attention_2 → mlp_2 → ...",
        }

        # Optimizaciones ZOE
        zoe_opt = {
            "acd_l0reflex": {
                "use_layers": list(range(min(4, num_layers))) + list(range(max(0, num_layers - 2), num_layers)),
                "skip_layers": list(range(4, max(4, num_layers - 2))) if num_layers > 6 else [],
                "pattern_first": True,
            },
            "acd_l1fast": {
                "use_layers": list(range(min(8, num_layers))) + list(range(max(0, num_layers - 4), num_layers)),
                "skip_layers": list(range(8, max(8, num_layers - 4))) if num_layers > 12 else [],
                "pattern_first": True,
            },
            "acd_l2standard": {
                "use_layers": "all",
                "skip_layers": [],
                "pattern_first": False,
            },
            "acd_l3deep": {
                "use_layers": "all",
                "skip_layers": [],
                "pattern_first": False,
                "max_tokens": 1024,
            },
            "sensitive_domain": {
                "prioritize_layers": list(range(max(0, num_layers - 6), num_layers)),
                "require_validation": True,
            },
        }

        return ZMAP(
            model=model_name,
            layers=layers,
            strategies=strategies,
            access_profile=access_profile,
            zoe_optimizations=zoe_opt,
        )

    def save_zmap(self, zmap: ZMAP, output_path: str):
        """Guarda un .zmap a disco."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(zmap.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"ZMAPLoader: saved .zmap to {output_path}")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "cached_zmaps": len(self._cache),
            "zmap_dir": str(self.zmap_dir) if self.zmap_dir else None,
            "cached_models": list(self._cache.keys()),
        }


# ============================================================
# 2. Tensor Prediction Engine (TPE)
# ============================================================

class TensorPredictionEngine:
    """
    Predice qué capas del modelo necesitará ZOE basándose en contexto cognitivo.

    Usa:
    - Nivel ACD (L0=solo capas rápidas, L3=todas)
    - Intención detectada (greeting, question, emotion, etc.)
    - Dominio (médico, psicológico, técnico)
    - Estado metabólico (energía, fatiga)
    - .zmap si disponible

    Devuelve una predicción de qué capas cargar/saltar.
    """

    def __init__(self, zmap_loader: ZMAPLoader = None):
        self.zmap_loader = zmap_loader or ZMAPLoader()
        self._predictions = 0

    def predict(self, model_name: str, acd_level: str,
                intent: str = None, domain: str = None,
                sensitive_domain: bool = False,
                metabolic_energy: float = 1.0) -> Dict[str, Any]:
        """
        Predice qué capas del modelo necesitará.

        Returns:
            {
                "use_layers": "all" | [layer_indices],
                "skip_layers": [layer_indices],
                "pattern_first": bool,  # usar PatternSpeaker primero
                "predicted_model": str,  # modelo recomendado
                "reason": str,
                "zmap_used": bool,
            }
        """
        self._predictions += 1

        # Cargar .zmap si existe
        zmap = self.zmap_loader.load(model_name)

        if zmap:
            # Usar optimización del .zmap
            opt = zmap.get_zoe_optimization(acd_level, sensitive_domain)
            result = {
                "use_layers": opt.get("use_layers", "all"),
                "skip_layers": opt.get("skip_layers", []),
                "pattern_first": opt.get("pattern_first", False),
                "predicted_model": model_name,
                "reason": f"zmap_optimized_{acd_level.lower()}",
                "zmap_used": True,
            }
        else:
            # Fallback: heurísticas por defecto
            result = self._heuristic_predict(acd_level, intent, domain, sensitive_domain, metabolic_energy)
            result["zmap_used"] = False

        # Ajustar por energía metabólica
        if metabolic_energy < 0.3:
            # ZOE cansada → usar PatternSpeaker, no LLM
            result["pattern_first"] = True
            result["reason"] += "_low_energy"

        return result

    def _heuristic_predict(self, acd_level: str, intent: str,
                            domain: str, sensitive_domain: bool,
                            energy: float) -> Dict[str, Any]:
        """Predicción por heurísticas cuando no hay .zmap."""
        acd_lower = acd_level.lower().replace("_", "")

        if acd_lower == "l0reflex":
            return {
                "use_layers": [0, 1, 2, -2, -1],
                "skip_layers": list(range(3, 30)),
                "pattern_first": True,
                "predicted_model": "pattern",
                "reason": "reflex_pattern_first",
            }
        elif acd_lower == "l1fast":
            return {
                "use_layers": list(range(8)) + [-4, -3, -2, -1],
                "skip_layers": list(range(8, 28)),
                "pattern_first": True,
                "predicted_model": "pattern_or_small_llm",
                "reason": "fast_partial_layers",
            }
        elif acd_lower == "l2standard":
            return {
                "use_layers": "all",
                "skip_layers": [],
                "pattern_first": False,
                "predicted_model": "standard_llm",
                "reason": "standard_full_load",
            }
        elif acd_lower == "l3deep":
            return {
                "use_layers": "all",
                "skip_layers": [],
                "pattern_first": False,
                "predicted_model": "quality_llm",
                "reason": "deep_full_load",
                "max_tokens": 1024,
            }
        else:
            return {
                "use_layers": "all",
                "skip_layers": [],
                "pattern_first": False,
                "predicted_model": "standard_llm",
                "reason": "default",
            }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "predictions_made": self._predictions,
            "zmap_loader": self.zmap_loader.get_stats(),
        }


# ============================================================
# 3. Cognitive Prefetch Layer (CPL)
# ============================================================

@dataclass
class PrefetchResult:
    """Resultado del prefetch cognitivo."""
    context_built: bool
    model_preloaded: bool
    pattern_response: Optional[str] = None
    predicted_layers: Optional[Dict[str, Any]] = None
    model_name: str = ""
    time_saved_ms: float = 0.0
    reason: str = ""


class CognitivePrefetchLayer:
    """
    Capa entre el bucle cognitivo y el Speaker que usa la información
    de ZOE para preparar la inferencia ANTES de que el Speaker llame al LLM.

    ZOE sabe, antes de llamar al LLM:
    1. Nivel ACD (L0=reflejo, L3=profundo)
    2. Estado emocional del usuario
    3. Memoria relevante recuperada
    4. Cápsulas cargadas
    5. Estado metabólico (energía, fatiga)

    El CPL usa esta información para:
    - Pre-cargar el modelo óptimo (si no está en RAM)
    - Pre-construir el contexto (system prompt + memoria + cápsula)
    - Pre-calentar Ollama (si está idle)
    - Decidir si usar PatternSpeaker en vez de LLM

    Sin deconstruir: el CPL es una capa OPCIONAL. Si no está, el Speaker
    funciona como siempre. Si está, el Speaker recibe contexto pre-construido
    y modelo pre-cargado, reduciendo latencia.

    Utilizable en TODAS las formas de uso de ZOE:
    - .zoe: CPL decide si PatternSpeaker es suficiente
    - Pendrive: CPL usa .zmap para optimizar mmap
    - Dashboard: CPL pre-carga modelo antes de generar
    - Voice-first: CPL pre-calienta Ollama antes de hablar
    - VPS: CPL + TPE + .zmap combinados
    """

    def __init__(
        self,
        zmap_loader: ZMAPLoader = None,
        tpe: TensorPredictionEngine = None,
        model_bus: Any = None,
        pattern_speaker: Any = None,
    ):
        self.zmap_loader = zmap_loader or ZMAPLoader()
        self.tpe = tpe or TensorPredictionEngine(self.zmap_loader)
        self.model_bus = model_bus
        self.pattern_speaker = pattern_speaker

        self._prefetches = 0
        self._pattern_shortcuts = 0
        self._models_preloaded = 0
        self._total_time_saved_ms = 0.0

    async def prefetch(
        self,
        acd_level: str,
        user_input: str,
        memory: Any = None,
        capsules: List[str] = None,
        metabolic_state: Any = None,
        sensitive_domain: bool = False,
        model_name: str = None,
    ) -> PrefetchResult:
        """
        Ejecuta el prefetch cognitivo.

        ANTES de que el Speaker llame al LLM, este método:
        1. Predice qué modelo necesitará (TPE)
        2. Si L0/L1, prueba PatternSpeaker primero
        3. Si necesita LLM, pre-carga el modelo
        4. Pre-construye contexto enriquecido
        5. Devuelve todo listo para el Speaker

        Returns:
            PrefetchResult con contexto, modelo y predicción
        """
        start_time = time.time()
        self._prefetches += 1

        # 1. Obtener energía metabólica
        energy = 1.0
        if metabolic_state and hasattr(metabolic_state, 'energy'):
            energy = metabolic_state.energy

        # 2. Predecir qué capas/modelo necesitará (TPE)
        predicted_model = model_name or "qwen2.5:7b"
        prediction = self.tpe.predict(
            model_name=predicted_model,
            acd_level=acd_level,
            sensitive_domain=sensitive_domain,
            metabolic_energy=energy,
        )

        # 3. Si pattern_first, intentar PatternSpeaker antes de LLM
        pattern_response = None
        if prediction.get("pattern_first") and self.pattern_speaker:
            try:
                pattern_response = await self.pattern_speaker.generate(
                    user_input, max_tokens=200, temperature=0.7
                )
                # Si PatternSpeaker da respuesta de calidad, usarla
                if pattern_response and len(pattern_response) > 20:
                    self._pattern_shortcuts += 1
                    elapsed = (time.time() - start_time) * 1000
                    self._total_time_saved_ms += elapsed
                    return PrefetchResult(
                        context_built=False,
                        model_preloaded=False,
                        pattern_response=pattern_response,
                        predicted_layers=prediction,
                        model_name="pattern",
                        time_saved_ms=elapsed,
                        reason=f"pattern_shortcut_{acd_level}",
                    )
            except Exception as e:
                logger.debug(f"CPL: pattern speaker failed: {e}")
                pattern_response = None

        # 4. Pre-cargar modelo en Ollama si es necesario
        model_preloaded = False
        if self.model_bus and prediction.get("predicted_model") != "pattern":
            model_preloaded = await self._preload_model(prediction["predicted_model"])

        # 5. Pre-construir contexto enriquecido
        context = self._build_context(
            acd_level=acd_level,
            user_input=user_input,
            memory=memory,
            capsules=capsules,
            prediction=prediction,
        )

        elapsed = (time.time() - start_time) * 1000
        self._total_time_saved_ms += elapsed

        return PrefetchResult(
            context_built=True,
            model_preloaded=model_preloaded,
            pattern_response=None,
            predicted_layers=prediction,
            model_name=prediction.get("predicted_model", ""),
            time_saved_ms=elapsed,
            reason=f"prefetched_{acd_level}",
        )

    async def _preload_model(self, model_name: str) -> bool:
        """Pre-carga modelo en Ollama si no está cargado."""
        if not self.model_bus:
            return False

        try:
            # Verificar si Ollama está disponible
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            result = sock.connect_ex(("localhost", 11434))
            sock.close()

            if result != 0:
                return False  # Ollama no disponible

            # Hacer petición warmup a Ollama
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # /api/generate con prompt vacío = warmup
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model_name, "prompt": "", "stream": False},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        self._models_preloaded += 1
                        logger.info(f"CPL: preloaded model {model_name}")
                        return True
            return False
        except Exception as e:
            logger.debug(f"CPL: preload failed: {e}")
            return False

    def _build_context(
        self,
        acd_level: str,
        user_input: str,
        memory: Any,
        capsules: List[str],
        prediction: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Pre-construye contexto enriquecido para el Speaker."""
        context = {
            "acd_level": acd_level,
            "user_input": user_input,
            "prediction": prediction,
            "capsules_loaded": capsules or [],
            "timestamp": time.time(),
        }

        # Recuperar memoria relevante si disponible
        if memory and hasattr(memory, "search"):
            try:
                relevant = memory.search(user_input, n=3)
                context["relevant_memories"] = [
                    {"content": m.content, "type": getattr(m, "memory_type", "unknown")}
                    for m in relevant
                ]
            except Exception as e:
                logger.warning(f"Memory search failed: {e}")
                context["relevant_memories"] = []

        # Añadir info del .zmap si disponible
        zmap = self.zmap_loader.load(prediction.get("predicted_model", ""))
        if zmap:
            context["zmap_strategy"] = zmap.get_strategy_for_ram(8.0)
            context["zmap_access_profile"] = zmap.access_profile

        return context

    def get_stats(self) -> Dict[str, Any]:
        return {
            "prefetches": self._prefetches,
            "pattern_shortcuts": self._pattern_shortcuts,
            "models_preloaded": self._models_preloaded,
            "total_time_saved_ms": round(self._total_time_saved_ms, 1),
            "avg_time_saved_ms": round(
                self._total_time_saved_ms / max(1, self._prefetches), 1
            ),
            "tpe_stats": self.tpe.get_stats(),
            "zmap_stats": self.zmap_loader.get_stats(),
        }
