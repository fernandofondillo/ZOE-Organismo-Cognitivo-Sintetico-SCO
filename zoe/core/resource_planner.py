"""
ZOE V1.3 — Metabolic Resource Planner (Fase 7C)

El metabolismo decide DÓNDE ejecutar cada tarea cognitiva.

ACD decide CUÁNTO pensar (profundidad L0-L3).
Metabolismo decide CUÁNDO pensar (AWAKE/DROWSY/SLEEPING).
ResourcePlanner decide DÓNDE pensar (qué backend, qué modelo, qué nodo).

El planner combina:
- Nivel ACD (del DepthClassifier)
- Estado del metabolismo (AWAKE/DROWSY/SLEEPING)
- Dominio sensible (del EpistemicValidator)
- ResourceGraph (recursos disponibles, Fase 7A)
- ModelOptimizer (RAM disponible, Fase 7F)
- ModelBus (backends registrados, Fase 7B)

Devuelve un ResourcePlan con:
- Backend seleccionado
- Modelo específico
- Estrategia de carga (full_ram / mmap_partial / mmap_full / cloud)
- Variables de entorno Ollama si aplica
- Razón de la selección

Sin desconstruir: es una capa de planificación entre ACD y ModelBus.
No cambia el bucle cognitivo ni el metabolismo.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MetabolicState(str, Enum):
    """Estado del metabolismo (espejo del Metabolism del proyecto)."""
    AWAKE = "awake"
    DROWSY = "drowsy"
    SLEEPING = "sleeping"
    WAKING = "waking"


class PlanReason(str, Enum):
    """Razón de la selección de plan."""
    ACD_LOCAL_FAST = "acd_local_fast"           # L0/L1 → local rápido
    ACD_LOCAL_BALANCED = "acd_local_balanced"   # L2 → local medio
    ACD_QUALITY = "acd_quality"                 # L3 → máxima calidad
    SENSITIVE_LOCAL = "sensitive_local"         # dominio sensible → local
    DROWSY_LOCAL_ONLY = "drowsy_local_only"    # DROWSY → solo local
    SLEEPING_DEFER = "sleeping_defer"           # SLEEPING → diferir
    CLOUD_FALLBACK = "cloud_fallback"           # sin local → cloud
    NO_RESOURCES = "no_resources"               # sin recursos


@dataclass
class ResourcePlan:
    """
    Plan de ejecución para una tarea cognitiva.

    El bucle cognitivo consulta al ResourcePlanner antes de generar
    una respuesta. El plan dice qué backend usar, con qué modelo,
    y con qué configuración.
    """
    # Selección
    backend_name: str = ""
    model_name: str = ""
    strategy: str = ""  # full_ram | mmap_partial | mmap_full | cloud
    reason: str = ""    # PlanReason.value

    # Contexto que motivó el plan
    acd_level: str = ""
    metabolic_state: str = ""
    sensitive_domain: bool = False
    available_ram_gb: float = 0.0

    # Configuración Ollama si aplica
    ollama_env: Dict[str, str] = field(default_factory=dict)

    # Metadata
    estimated_latency_ms: float = 0.0
    estimated_cost_eur: float = 0.0
    will_work: bool = True
    warning: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResourcePlanner:
    """
    Planifica dónde ejecutar cada tarea cognitiva.

    Combina ACD + metabolismo + dominio + recursos + optimizador.

    Uso:
        planner = ResourcePlanner()
        plan = planner.plan(
            acd_level="L3_DEEP",
            metabolic_state="awake",
            sensitive_domain=False,
            available_ram_gb=5.0,
            model_bus=model_bus,
            resource_graph=resource_graph,
        )
        # plan.backend_name = "anthropic"
        # plan.model_name = "claude-sonnet-4-20250514"
        # plan.strategy = "cloud"
        # plan.reason = "acd_quality"
    """

    # Mapeo de nivel ACD a preferencia de modelo
    ACD_MODEL_PREFERENCES = {
        "L0_REFLEX": {
            "max_params_b": 3.0,    # hasta 3B en RAM
            "prefer_local": True,
            "prefer_free": True,
            "max_latency_ms": 1000,
            "allow_cloud": False,   # L0 nunca usa cloud (demasiado lento)
        },
        "L1_FAST": {
            "max_params_b": 7.0,
            "prefer_local": True,
            "prefer_free": True,
            "max_latency_ms": 4000,
            "allow_cloud": False,
        },
        "L2_STANDARD": {
            "max_params_b": 14.0,
            "prefer_local": True,
            "prefer_free": True,
            "max_latency_ms": 15000,
            "allow_cloud": True,    # L2 puede usar cloud si local no disponible
        },
        "L3_DEEP": {
            "max_params_b": 999.0,  # cualquier tamaño
            "prefer_local": False,   # L3 prefiere calidad sobre localidad
            "prefer_free": False,
            "max_latency_ms": 120000,
            "allow_cloud": True,
        },
    }

    def __init__(self):
        self._plans_generated = 0
        self._plan_log: List[Dict[str, Any]] = []

    def plan(
        self,
        acd_level: str = "L2_STANDARD",
        metabolic_state: str = "awake",
        sensitive_domain: bool = False,
        available_ram_gb: float = 5.0,
        model_bus: Any = None,
        resource_graph: Any = None,
        model_optimizer: Any = None,
    ) -> ResourcePlan:
        """
        Genera un plan de ejecución para una tarea cognitiva.

        Args:
            acd_level: L0_REFLEX | L1_FAST | L2_STANDARD | L3_DEEP
            metabolic_state: awake | drowsy | sleeping | waking
            sensitive_domain: si el dominio es médico/psicológico/legal
            available_ram_gb: RAM disponible para modelos locales
            model_bus: ModelBus con backends registrados
            resource_graph: ResourceGraph con recursos descubiertos
            model_optimizer: ModelOptimizer para analizar viabilidad

        Returns:
            ResourcePlan con backend, modelo, estrategia y razón
        """
        self._plans_generated += 1
        prefs = self.ACD_MODEL_PREFERENCES.get(acd_level, self.ACD_MODEL_PREFERENCES["L2_STANDARD"])

        plan = ResourcePlan(
            acd_level=acd_level,
            metabolic_state=metabolic_state,
            sensitive_domain=sensitive_domain,
            available_ram_gb=available_ram_gb,
        )

        # 1. Si SLEEPING → diferir
        if metabolic_state == MetabolicState.SLEEPING.value:
            plan.reason = PlanReason.SLEEPING_DEFER.value
            plan.will_work = False
            plan.warning = "Organismo en SLEEPING. Diferir tarea."
            self._log_plan(plan)
            return plan

        # 2. Si DROWSY → solo local, no cloud
        drowsy_local_only = False
        if metabolic_state == MetabolicState.DROWSY.value:
            prefs = {**prefs, "allow_cloud": False, "prefer_local": True}
            drowsy_local_only = True

        # 3. Si dominio sensible → excluir cloud
        if sensitive_domain:
            prefs = {**prefs, "allow_cloud": False, "prefer_local": True}

        # 4. Seleccionar backend desde ModelBus
        if model_bus:
            # Pasar sensitive_domain=True al bus si DROWSY o dominio sensible
            effective_sensitive = sensitive_domain or drowsy_local_only
            selected = model_bus.select_backend(
                acd_level=acd_level,
                sensitive_domain=effective_sensitive,
                prefer_local=prefs.get("prefer_local", True),
            )

            if selected:
                plan.backend_name = selected.name
                plan.model_name = selected.models[0] if selected.models else ""
                plan.estimated_latency_ms = selected.latency_ms
                plan.estimated_cost_eur = selected.cost_per_1k

                # Determinar estrategia
                if selected.privacy == "local":
                    # Verificar con ModelOptimizer si tenemos uno
                    if model_optimizer and plan.model_name:
                        opt_result = model_optimizer.optimize(plan.model_name, available_ram_gb)
                        plan.strategy = opt_result.strategy.value
                        plan.ollama_env = model_optimizer.generate_ollama_env(opt_result)
                        if opt_result.warning:
                            plan.warning = opt_result.warning
                        if not opt_result.will_work:
                            # Modelo local no viable → cloud fallback si permitido
                            if prefs.get("allow_cloud") and not sensitive_domain:
                                cloud_plan = self._find_cloud_fallback(
                                    model_bus, acd_level, plan
                                )
                                if cloud_plan:
                                    self._log_plan(cloud_plan)
                                    return cloud_plan
                            plan.will_work = False
                            plan.warning = f"Local model {plan.model_name} not viable: {opt_result.warning}"
                    else:
                        plan.strategy = "full_ram"  # asumir que cabe

                    # Razón según ACD
                    if acd_level in ("L0_REFLEX", "L1_FAST"):
                        plan.reason = PlanReason.ACD_LOCAL_FAST.value
                    elif acd_level == "L2_STANDARD":
                        plan.reason = PlanReason.ACD_LOCAL_BALANCED.value
                    else:
                        plan.reason = PlanReason.ACD_QUALITY.value if "quality" in selected.tags else PlanReason.ACD_LOCAL_BALANCED.value

                    if sensitive_domain:
                        plan.reason = PlanReason.SENSITIVE_LOCAL.value
                    elif metabolic_state == MetabolicState.DROWSY.value:
                        plan.reason = PlanReason.DROWSY_LOCAL_ONLY.value

                else:
                    # Cloud backend
                    plan.strategy = "cloud"
                    plan.reason = PlanReason.ACD_QUALITY.value if acd_level == "L3_DEEP" else PlanReason.CLOUD_FALLBACK.value

                self._log_plan(plan)
                return plan

        # 5. Sin ModelBus o sin backends disponibles
        # Intentar construir desde ResourceGraph
        if resource_graph and model_bus:
            # Reconstruir bus desde graph
            from ..peripherals.model_bus import ModelBus
            new_bus = ModelBus.from_resource_graph(resource_graph)
            if new_bus.get_available_backends():
                return self.plan(
                    acd_level=acd_level,
                    metabolic_state=metabolic_state,
                    sensitive_domain=sensitive_domain,
                    available_ram_gb=available_ram_gb,
                    model_bus=new_bus,
                    resource_graph=resource_graph,
                    model_optimizer=model_optimizer,
                )

        # 6. Sin recursos
        plan.reason = PlanReason.NO_RESOURCES.value
        plan.will_work = False
        plan.warning = "No backends or resources available for this task."
        self._log_plan(plan)
        return plan

    def _find_cloud_fallback(
        self, model_bus: Any, acd_level: str, current_plan: ResourcePlan
    ) -> Optional[ResourcePlan]:
        """Busca un backend cloud como fallback cuando local no es viable."""
        # Obtener backends cloud disponibles
        from ..peripherals.model_bus import BackendEntry
        available = model_bus.get_available_backends()
        cloud_backends = [b for b in available if b.privacy == "cloud"]

        if not cloud_backends:
            return None

        # Seleccionar el de mayor prioridad
        cloud_backends.sort(key=lambda b: b.priority, reverse=True)
        selected = cloud_backends[0]

        new_plan = ResourcePlan(
            backend_name=selected.name,
            model_name=selected.models[0] if selected.models else "",
            strategy="cloud",
            reason=PlanReason.CLOUD_FALLBACK.value,
            acd_level=acd_level,
            metabolic_state=current_plan.metabolic_state,
            sensitive_domain=current_plan.sensitive_domain,
            available_ram_gb=current_plan.available_ram_gb,
            estimated_latency_ms=selected.latency_ms,
            estimated_cost_eur=selected.cost_per_1k,
            warning=f"Local model not viable. Falling back to cloud: {selected.name}",
        )
        return new_plan

    def _log_plan(self, plan: ResourcePlan) -> None:
        self._plan_log.append(plan.to_dict())
        if len(self._plan_log) > 100:
            self._plan_log = self._plan_log[-50:]

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del planner."""
        reason_counts: Dict[str, int] = {}
        strategy_counts: Dict[str, int] = {}
        for entry in self._plan_log:
            reason_counts[entry.get("reason", "unknown")] = reason_counts.get(entry.get("reason", "unknown"), 0) + 1
            strategy_counts[entry.get("strategy", "unknown")] = strategy_counts.get(entry.get("strategy", "unknown"), 0) + 1

        return {
            "plans_generated": self._plans_generated,
            "reason_distribution": reason_counts,
            "strategy_distribution": strategy_counts,
            "recent_plans": self._plan_log[-10:],
        }

    def recommend_model_setup(
        self,
        available_ram_gb: float,
        model_optimizer: Any = None,
    ) -> Dict[str, Any]:
        """
        Recomienda configuración de modelos por nivel ACD.

        Usa el ModelOptimizer para sugerir qué modelo instalar
        para cada nivel ACD según la RAM disponible.
        """
        if model_optimizer is None:
            from .model_optimizer import ModelOptimizer
            model_optimizer = ModelOptimizer()

        recs = model_optimizer.recommend_for_acd(ram_gb=available_ram_gb)

        # Añadir recomendaciones del planner
        planner_recs = {}
        for level, rec in recs.get("recommendations", {}).items():
            model = rec.get("model", "cloud_api")
            if model == "cloud_api":
                planner_recs[level] = {
                    **rec,
                    "planner_note": "Sin modelo local viable. Usar cloud API para este nivel.",
                }
            else:
                opt = model_optimizer.optimize(model, available_ram_gb)
                planner_recs[level] = {
                    **rec,
                    "strategy": opt.strategy.value,
                    "speed": opt.estimated_speed,
                    "ram_usage_gb": round(opt.estimated_ram_usage_gb, 1),
                    "warning": opt.warning,
                }

        return {
            "available_ram_gb": recs.get("available_ram_gb"),
            "total_ram_gb": recs.get("total_ram_gb"),
            "is_apple_silicon": recs.get("is_apple_silicon"),
            "cpu_cores": recs.get("cpu_cores"),
            "recommendations": planner_recs,
        }
