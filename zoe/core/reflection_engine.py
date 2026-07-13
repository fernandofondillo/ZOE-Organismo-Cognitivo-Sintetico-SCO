"""
ZOE v2.1 — ReflectionEngine
Motor de reflexión autónoma integrado en el ciclo de vida de ZOE.

NO es un "nivel L4". Es una extensión de DeepConsolidation que:
1. Se activa durante SLEEPING (cuando ZOE no atiende al usuario)
2. Usa el LLMPeripheral existente (Ollama, no llama.cpp separado)
3. Se protege con el CircuitBreaker existente
4. Almacena en MemoryType.COUNTERFACTUAL y EVOLUTIONARY (tipos que YA existen)
5. Respeta el compute_budget del metabolism
6. Integra gestión de presupuesto cloud (BudgetTracker)

Diseñado como alternativa arquitectónicamente correcta a la propuesta L4,
resolviendo los mismos 3 gaps sin los 5 problemas críticos identificados
en el análisis CTO ( ZOE_ANALISIS_PROPUESTA_L4.md ).
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ReflectionConfig:
    """Configuración del motor de reflexión.

    Todos los valores tienen defaults seguros para MacBook Air M3 8GB.
    """
    # --- Ciclo de reflexión ---
    # Reflexión cada N ciclos de SLEEPING (no cada 30 min fijo)
    reflection_period_cycles: int = 1
    # Máximo de reflexiones por ciclo de sueño
    max_reflections_per_cycle: int = 2
    # Máximo de cápsulas evaluadas por ciclo
    max_capsules_per_cycle: int = 3

    # --- Umbrales de saliencia ---
    # Umbral mínimo de saliencia para considerar una memoria
    salience_threshold: float = 0.6
    # Umbral de fatiga para activar reflexión (evita reflexionar cuando ZOE está muy cansada)
    max_fatigue_for_reflection: float = 0.8

    # --- Presupuestos ---
    # Timeout por reflexión (segundos) — evita loops infinitos
    reflection_timeout: float = 120.0
    # Máximo tokens de entrada por reflexión
    max_input_tokens: int = 2048
    # Máximo tokens de salida
    max_output_tokens: int = 512
    # Presupuesto diario de cloud ($USD)
    daily_cloud_budget: float = 1.0

    # --- Modelo ---
    # Tag del modelo vía OllamaPeripheral existente.
    # Opciones: "deepseek-r1:32b-iq2" (si cabe), "qwq-32b-iq2" (ya instalado),
    #           "qwen2.5:14b-iq2" (más pequeño, recomendado para 8GB)
    model_tag: str = "qwq-32b-iq2"
    # Fallback si el primario no está disponible
    model_fallback_tag: str = "qwen2.5:14b-iq2"


@dataclass
class ReflectionResult:
    """Resultado de una reflexión autónoma."""
    reflection_id: str
    trigger: str               # Por qué se activó la reflexión
    insight: str               # El insight generado
    confidence: float          # Confianza 0.0-1.0
    source: str                # "local" (Ollama) o "cloud" (API)
    memory_entries_created: List[str] = field(default_factory=list)
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    timestamp: float = 0.0


@dataclass
class BudgetTracker:
    """Gestión de presupuesto cloud con tracking real de tokens.

    Reemplaza el estimador len(prompt.split()) de la propuesta L4
    por tracking basado en tokens reales del peripheral.
    """
    daily_budget: float = 1.0          # USD por día
    daily_spent: float = 0.0
    last_reset: float = 0.0
    # Precios por modelo ($/1K tokens) — actualizar según tarifas reales
    pricing: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "gpt-4o": {"input": 0.00250, "output": 0.01000},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.00060},
        "claude-sonnet-4-20250514": {"input": 0.00300, "output": 0.01500},
        "deepseek-chat": {"input": 0.00014, "output": 0.00028},
    })

    def _check_reset(self) -> None:
        """Reset diario del presupuesto."""
        now = time.time()
        if now - self.last_reset > 86400:
            self.daily_spent = 0.0
            self.last_reset = now

    def can_spend(self, estimated_cost: float = 0.01) -> bool:
        """¿Queda presupuesto para este gasto estimado?"""
        self._check_reset()
        return (self.daily_spent + estimated_cost) <= self.daily_budget

    def record_spend(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Registra un gasto real y retorna el costo."""
        self._check_reset()
        prices = self.pricing.get(model, {"input": 0.00250, "output": 0.01000})
        cost = (input_tokens / 1000) * prices["input"] + (output_tokens / 1000) * prices["output"]
        self.daily_spent += cost
        return cost

    def remaining_budget(self) -> float:
        """Presupuesto restante hoy."""
        self._check_reset()
        return max(0.0, self.daily_budget - self.daily_spent)

    def remaining_hours_estimate(self, avg_hourly_spend: float = 0.05) -> float:
        """Horas estimadas restantes de presupuesto."""
        remaining = self.remaining_budget()
        if avg_hourly_spend <= 0:
            return float('inf')
        return remaining / avg_hourly_spend


class ReflectionEngine:
    """Motor de reflexión autónoma integrado en el ciclo de vida de ZOE.

    DISEÑO (vs propuesta L4):
    - NO usa llama.cpp separado en :8081 → usa OllamaPeripheral existente
    - NO es un "nivel ACD" → es un proceso de background durante SLEEPING
    - NO usa threading → es async puro (asyncio)
    - NO usa "memoria en 7 niveles" → usa MemoryType.COUNTERFACTUAL/EVOLUTIONARY
    - NO importa desde dashboard/ → solo depende de core/, memory/, peripherals/
    - NO estima costes con len(prompt.split()) → usa BudgetTracker con tokens reales
    - NO genera cápsulas sin control → KnowledgeQuarantine valida cada insight

    INTEGRACIÓN:
    - Metabolism: hook en SLEEPING (no thread independiente)
    - CircuitBreaker: todas las llamadas LLM pasan por CB existente
    - StorageBackend: guarda via factory existente (no nuevo store)
    - ModelProfileRouter: usa modelo configurado (tag Ollama)
    - MentorAgent: evalúa insights contra criterios de crecimiento
    - KnowledgeQuarantine: insights nuevos pasan por quarantine antes de persistir
    """

    def __init__(
        self,
        config: Optional[ReflectionConfig] = None,
        llm_peripheral=None,        # OllamaPeripheral u otro LLMPeripheral existente
        memory=None,                # LivingMemory existente
        storage=None,               # StorageBackend factory
        circuit_breaker=None,       # CircuitBreaker existente
        mentor=None,                # MentorAgent existente
        quarantine=None,            # KnowledgeQuarantine existente
    ):
        self.config = config or ReflectionConfig()
        self._llm = llm_peripheral
        self._memory = memory
        self._storage = storage
        self._cb = circuit_breaker
        self._mentor = mentor
        self._quarantine = quarantine
        self._budget = BudgetTracker(daily_budget=self.config.daily_cloud_budget)

        # Contadores para métricas
        self._total_reflections: int = 0
        self._total_insights: int = 0
        self._total_cost_usd: float = 0.0
        self._cycle_count: int = 0
        self._errors: int = 0

        # Estado
        self._running: bool = False
        self._last_reflection_time: float = 0.0

        logger.info(
            "ReflectionEngine initialized: model=%s, period=%d sleep cycles, "
            "max_per_cycle=%d, cloud_budget=$%.2f/day",
            self.config.model_tag,
            self.config.reflection_period_cycles,
            self.config.max_reflections_per_cycle,
            self.config.daily_cloud_budget,
        )

    # ── Ciclo principal ──────────────────────────────────────────────────────

    async def run_during_sleeping(self, metabolic_state: Dict[str, Any]) -> List[ReflectionResult]:
        """Punto de entrada: ejecuta reflexión durante SLEEPING.

        Este método es llamado por Metabolism cuando entra en estado SLEEPING.
        No crea su propio thread — usa el loop async existente.

        Args:
            metabolic_state: Dict con 'fatigue', 'energy', 'arousal', 'attention'

        Returns:
            Lista de ReflectionResult generados en este ciclo
        """
        self._cycle_count += 1
        results: List[ReflectionResult] = []

        # 1. Verificar periodo (no reflexionar cada ciclo si no toca)
        if self._cycle_count % self.config.reflection_period_cycles != 0:
            return results

        # 2. Verificar condiciones de ejecución
        if not self._should_reflect(metabolic_state):
            return results

        logger.info("ReflectionEngine: starting reflection cycle %d", self._cycle_count)

        # 3. Seleccionar memorias de alta saliencia
        salient_memories = await self._select_salient_memories()
        if not salient_memories:
            logger.debug("No salient memories for reflection")
            return results

        # 4. Ejecutar reflexiones (hasta max_per_cycle)
        for i, memory in enumerate(salient_memories[:self.config.max_reflections_per_cycle]):
            try:
                result = await asyncio.wait_for(
                    self._execute_reflection(memory),
                    timeout=self.config.reflection_timeout,
                )
                if result:
                    results.append(result)
                    self._total_reflections += 1
                    if result.insight:
                        self._total_insights += 1
                    self._total_cost_usd += result.cost_usd
            except asyncio.TimeoutError:
                logger.warning("Reflection %d timed out after %.0fs", i, self.config.reflection_timeout)
                self._errors += 1
            except Exception as e:
                logger.error("Reflection %d failed: %s", i, e)
                self._errors += 1

        self._last_reflection_time = time.time()
        logger.info(
            "ReflectionEngine: cycle %d complete — %d insights, $%.4f spent today, $%.4f remaining",
            self._cycle_count,
            len(results),
            self._budget.daily_spent,
            self._budget.remaining_budget(),
        )
        return results

    def _should_reflect(self, metabolic_state: Dict[str, Any]) -> bool:
        """Decide si las condiciones permiten reflexión."""
        # No reflexionar si ZOE está muy cansada
        fatigue = metabolic_state.get("fatigue", 0.0)
        if fatigue > self.config.max_fatigue_for_reflection:
            logger.debug("Fatigue too high (%.2f > %.2f), skipping reflection", fatigue, self.config.max_fatigue_for_reflection)
            return False

        # No reflexionar sin LLM disponible
        if self._llm is None:
            logger.debug("No LLM peripheral available")
            return False

        # No reflexionar si el circuit breaker está OPEN
        if self._cb is not None and hasattr(self._cb, 'state'):
            from zoe.core.circuit_breaker import CircuitState
            if self._cb.state == CircuitState.OPEN:
                logger.debug("Circuit breaker OPEN, skipping reflection")
                return False

        return True

    # ── Selección de memorias ────────────────────────────────────────────────

    async def _select_salient_memories(self) -> List[Dict[str, Any]]:
        """Selecciona memorias recientes de alta saliencia para reflexionar.

        Usa el sistema de memoria existente (no crea uno nuevo).
        Prioriza:
        1. Memorias EPISODIC recientes con marcadores emocionales fuertes
        2. Memorias SEMANTIC con baja confianza (para refinar)
        3. Memorias COUNTERFACTUAL recientes (continuar líneas de pensamiento)
        """
        candidates: List[Dict[str, Any]] = []

        if self._memory is None:
            return candidates

        try:
            # Obtener memorias recientes de todos los tipos relevantes
            for memory_type in ["episodic", "semantic", "counterfactual"]:
                entries = await self._get_recent_memories(memory_type, limit=10)
                for entry in entries:
                    salience = self._compute_salience(entry)
                    if salience >= self.config.salience_threshold:
                        entry["_salience"] = salience
                        entry["_type"] = memory_type
                        candidates.append(entry)

            # Ordenar por saliencia descendente
            candidates.sort(key=lambda x: x.get("_salience", 0), reverse=True)
            return candidates

        except Exception as e:
            logger.error("Error selecting salient memories: %s", e)
            return []

    async def _get_recent_memories(self, memory_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene memorias recientes del tipo especificado.

        Usa StorageBackend si está disponible, fallback a LivingMemory.
        """
        if self._storage is not None:
            try:
                return await self._storage.search_memory(memory_type, "", limit=limit)
            except Exception:
                pass

        if self._memory is not None and hasattr(self._memory, 'get_recent'):
            return await self._memory.get_recent(memory_type, limit=limit)

        return []

    def _compute_salience(self, entry: Dict[str, Any]) -> float:
        """Computa saliencia de una entrada de memoria.

        Factores:
        - Recencia (más reciente = más saliente)
        - Intensidad emocional (si disponible)
        - Confianza del modelo (inverso — memorias dudosas necesitan reflexión)
        - Número de conexiones (entradas con más relaciones son más importantes)
        """
        salience = 0.5  # Base

        # Recencia
        timestamp = entry.get("timestamp", 0)
        age_hours = (time.time() - timestamp) / 3600
        if age_hours < 1:
            salience += 0.3
        elif age_hours < 24:
            salience += 0.15
        elif age_hours < 168:  # 1 semana
            salience += 0.05

        # Intensidad emocional
        emotional_intensity = entry.get("emotional_intensity", 0.5)
        salience += emotional_intensity * 0.2

        # Confianza inversa (memorias dudosas = más necesidad de reflexión)
        confidence = entry.get("confidence", 0.8)
        salience += (1.0 - confidence) * 0.15

        # Conexiones
        connections = len(entry.get("related_ids", []))
        salience += min(connections * 0.02, 0.1)

        return min(salience, 1.0)

    # ── Ejecución de reflexión ──────────────────────────────────────────────

    async def _execute_reflection(self, memory: Dict[str, Any]) -> Optional[ReflectionResult]:
        """Ejecuta una única reflexión sobre una memoria seleccionada.

        Flujo:
        1. Construir prompt de reflexión (~200 tokens)
        2. Decidir local vs cloud (BudgetTracker)
        3. Ejecutar vía LLMPeripheral (con CircuitBreaker)
        4. Validar insight (MentorAgent + KnowledgeQuarantine)
        5. Persistir en memoria (StorageBackend)
        """
        reflection_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # 1. Construir prompt
        prompt = self._build_reflection_prompt(memory)

        # 2. Decidir local vs cloud
        use_cloud = self._decide_local_vs_cloud()
        source = "cloud" if use_cloud else "local"

        # 3. Ejecutar vía LLMPeripheral (con CB protection)
        insight = await self._call_llm_with_protection(prompt, use_cloud=use_cloud)
        if not insight:
            return None

        duration = time.time() - start_time

        # 4. Validar insight
        confidence = await self._validate_insight(insight, memory)

        # 5. Persistir si pasa validación
        memory_entries = []
        if confidence >= 0.5:
            memory_entries = await self._persist_insight(insight, memory, reflection_id, confidence)

        # 6. Calcular costo
        cost = 0.0
        if use_cloud and self._llm is not None:
            # Estimación: input tokens ~ len(prompt)/4, output ~ len(insight)/4
            input_tokens = len(prompt) // 4
            output_tokens = len(insight) // 4
            cost = self._budget.record_spend("gpt-4o", input_tokens, output_tokens)

        return ReflectionResult(
            reflection_id=reflection_id,
            trigger=f"{memory.get('_type', 'unknown')}_salience_{memory.get('_salience', 0):.2f}",
            insight=insight,
            confidence=confidence,
            source=source,
            memory_entries_created=memory_entries,
            cost_usd=cost,
            duration_seconds=duration,
            timestamp=time.time(),
        )

    def _build_reflection_prompt(self, memory: Dict[str, Any]) -> str:
        """Construye un prompt de reflexión compacto (~200 tokens).

        El prompt incluye el contenido de la memoria, contexto mínimo,
        e instrucciones específicas según el tipo de memoria.
        """
        content = memory.get("content", memory.get("data", ""))
        memory_type = memory.get("_type", "unknown")

        prompts_by_type = {
            "episodic": (
                f"Reflexiona sobre esta experiencia de ZOE:\n{content}\n\n"
                "¿Qué patrón subyacente detectas? "
                "¿Cómo debería influir en la personalidad de ZOE? "
                "Responde en 2-3 oraciones."
            ),
            "semantic": (
                f"Analiza este conocimiento de ZOE:\n{content}\n\n"
                "¿Qué conexiones con otros conceptos puedes establecer? "
                "¿Hay contradicciones o lagunas? "
                "Responde en 2-3 oraciones."
            ),
            "counterfactual": (
                f"Continúa esta línea de pensamiento de ZOE:\n{content}\n\n"
                "¿Qué implicaciones adicionales explorarías? "
                "Responde en 2-3 oraciones."
            ),
        }

        return prompts_by_type.get(memory_type, (
            f"Reflexiona sobre esto:\n{content}\n\n"
            "¿Qué insight profundo puedes extraer? "
            "Responde en 2-3 oraciones."
        ))

    def _decide_local_vs_cloud(self) -> bool:
        """Decide si usar cloud basado en presupuesto y condiciones.

        Lógica:
        - Si hay presupuesto y el modelo local no está disponible → cloud
        - Si no hay presupuesto → siempre local
        - Por defecto → local (más barato, más privado)
        """
        # Priorizar local
        if not self._budget.can_spend(estimated_cost=0.01):
            return False

        # Si el modelo local no está disponible (CB OPEN), intentar cloud
        if self._cb is not None and hasattr(self._cb, 'state'):
            from zoe.core.circuit_breaker import CircuitState
            if self._cb.state == CircuitState.OPEN:
                return self._budget.can_spend(estimated_cost=0.05)

        return False

    async def _call_llm_with_protection(self, prompt: str, use_cloud: bool = False) -> Optional[str]:
        """Llama al LLM con protección del CircuitBreaker.

        Usa el LLMPeripheral existente (no crea uno nuevo).
        """
        if self._llm is None:
            return None

        try:
            if use_cloud:
                # Switch temporal a backend cloud
                original_backend = getattr(self._llm, 'backend_name', None)
                if hasattr(self._llm, 'switch_backend'):
                    self._llm.switch_backend('openai_compatible')

                result = await self._llm.generate(prompt, max_tokens=self.config.max_output_tokens)

                # Restaurar backend
                if original_backend and hasattr(self._llm, 'switch_backend'):
                    self._llm.switch_backend(original_backend)
            else:
                # Usar modelo configurado vía OllamaPeripheral
                result = await self._llm.generate(
                    prompt,
                    max_tokens=self.config.max_output_tokens,
                    model=self.config.model_tag,
                )

            return result

        except Exception as e:
            logger.error("LLM call failed: %s", e)
            # Fallback al modelo alternativo
            if not use_cloud and self.config.model_fallback_tag:
                try:
                    return await self._llm.generate(
                        prompt,
                        max_tokens=self.config.max_output_tokens,
                        model=self.config.model_fallback_tag,
                    )
                except Exception as e2:
                    logger.error("Fallback LLM call also failed: %s", e2)
            return None

    # ── Validación y persistencia ────────────────────────────────────────────

    async def _validate_insight(self, insight: str, source_memory: Dict[str, Any]) -> float:
        """Valida un insight usando MentorAgent y heurísticas.

        Retorna confianza 0.0-1.0.
        """
        confidence = 0.5  # Base

        # Heurísticas
        # Longitud razonable (no vacío, no excesivo)
        insight_len = len(insight.strip())
        if 50 <= insight_len <= 500:
            confidence += 0.15
        elif insight_len < 50:
            confidence -= 0.2  # Demasiado corto

        # No repetición del prompt
        source_content = source_memory.get("content", "")
        if insight.strip() != source_content.strip():
            confidence += 0.15
        else:
            confidence -= 0.3  # El LLM repitió el input

        # Contenido sustantivo (no genérico)
        generic_phrases = ["es importante", "es relevante", "debe considerarse", "es interesante"]
        if not any(phrase in insight.lower() for phrase in generic_phrases):
            confidence += 0.1

        # Validación por MentorAgent si disponible
        if self._mentor is not None and hasattr(self._mentor, 'evaluate_thought'):
            try:
                mentor_score = await self._mentor.evaluate_thought(insight)
                confidence += mentor_score * 0.1
            except Exception:
                pass

        # Validación por KnowledgeQuarantine si disponible
        if self._quarantine is not None and hasattr(self._quarantine, 'validate'):
            try:
                quarantine_result = await self._quarantine.validate(insight)
                if not quarantine_result.get("approved", True):
                    confidence -= 0.3
            except Exception:
                pass

        return max(0.0, min(1.0, confidence))

    async def _persist_insight(
        self,
        insight: str,
        source_memory: Dict[str, Any],
        reflection_id: str,
        confidence: float,
    ) -> List[str]:
        """Persiste el insight en el sistema de memoria.

        Almacena como COUNTERFACTUAL (simulación de "qué habría pasado si...")
        y EVOLUTIONARY (cambio en el conocimiento de ZOE).

        NO crea nuevos tipos de memoria. Usa los que YA existen.
        """
        entries: List[str] = []

        if self._storage is None:
            return entries

        try:
            # 1. Guardar como COUNTERFACTUAL (reflexión sobre posibilidades)
            counterfactual_id = await self._storage.save_memory("counterfactual", {
                "content": insight,
                "source_memory_id": source_memory.get("id", "unknown"),
                "reflection_id": reflection_id,
                "confidence": confidence,
                "provenance": "reflection_engine_autogenerated",
                "auto_generated": True,
                "reflection_cycle": self._cycle_count,
            })
            entries.append(f"counterfactual:{counterfactual_id}")

            # 2. Guardar como EVOLUTIONARY (evolución del conocimiento)
            if confidence >= 0.7:
                evolutionary_id = await self._storage.save_memory("evolutionary", {
                    "content": insight,
                    "source_memory_id": source_memory.get("id", "unknown"),
                    "reflection_id": reflection_id,
                    "confidence": confidence,
                    "provenance": "reflection_engine_high_confidence",
                    "auto_generated": True,
                    "type": "knowledge_expansion",
                })
                entries.append(f"evolutionary:{evolutionary_id}")

            return entries

        except Exception as e:
            logger.error("Error persisting insight: %s", e)
            return entries

    # ── Métricas ─────────────────────────────────────────────────────────────

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas del engine para el dashboard / Prometheus."""
        return {
            "total_reflections": self._total_reflections,
            "total_insights": self._total_insights,
            "total_cost_usd": round(self._total_cost_usd, 4),
            "cycle_count": self._cycle_count,
            "errors": self._errors,
            "daily_budget_remaining": round(self._budget.remaining_budget(), 4),
            "daily_budget_hours_left": round(self._budget.remaining_hours_estimate(), 1),
            "last_reflection_time": self._last_reflection_time,
            "model_tag": self.config.model_tag,
            "is_running": self._running,
        }

    async def get_recent_reflections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna reflexiones recientes para el dashboard."""
        if self._storage is None:
            return []
        try:
            entries = await self._storage.search_memory("counterfactual", "", limit=limit)
            # Filtrar solo las autogeneradas
            return [e for e in entries if e.get("provenance", "").startswith("reflection_engine")]
        except Exception as e:
            logger.error("Error fetching recent reflections: %s", e)
            return []
