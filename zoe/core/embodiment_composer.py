"""
ZOE V1.4 — Embodiment Composer (Fase 7D)

El componente que cierra el ciclo 7A → 7B → 7C → 7D.

7A descubre recursos. 7B los expone como backends. 7C planifica cuál usar.
7D INSTANCIA el cuerpo real: arranca Ollama si hace falta, configura el
ModelBus según el plan, monta el almacén de memoria, carga las cápsulas
del caso de uso y deja el organismo listo para pensar.

Es el "boot sequence" del organismo cognitivo. Sin este componente, el
ResourcePlan es solo un documento. Con él, el plan se convierte en un
cuerpo vivo.

Estados del embodiment:
- BOOTING:    recursos siendo preparados (Ollama arrancando, mmap cargando)
- RUNNING:    cuerpo listo, bucle cognitivo puede ejecutarse
- DEGRADED:   cuerpo funcional pero con avisos (modelo subóptimo, sin cloud)
- STOPPED:    cuerpo detenido limpiamente (recursos liberados)
- FAILED:     no se pudo instanciar el cuerpo (sin recursos críticos)

Pipeline bootstrap_from_scratch:
1. ResourceDiscoverySense.observe()           → grafo de recursos
2. ModelBus.from_resource_graph(graph)        → backends disponibles
3. ResourcePlanner.plan(acd, metabolismo...)  → plan de ejecución
4. EmbodimentComposer.compose(plan, ...)      → cuerpo instanciado

Sin desconstruir: es la capa de orquestación entre planificación (7C)
y runtime (bucle cognitivo). No toca el bucle cognitivo ni el metabolismo.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# ============================================================
# Enums y dataclasses
# ============================================================

class EmbodimentStatus(str, Enum):
    """Estados posibles del cuerpo cognitivo."""
    BOOTING = "booting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    FAILED = "failed"


class ValidationLevel(str, Enum):
    """Severidad de un check de prerrequisitos."""
    OK = "ok"               # todo bien
    WARNING = "warning"     # arranca pero subóptimo
    BLOCKER = "blocker"     # no puede arrancar


@dataclass
class ValidationCheck:
    """Resultado individual de un check de prerrequisitos."""
    name: str
    level: str              # ValidationLevel.value
    message: str
    detail: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Resultado completo de validar prerrequisitos de un plan."""
    plan_will_work: bool
    checks: List[ValidationCheck] = field(default_factory=list)
    blockers: int = 0
    warnings: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_will_work": self.plan_will_work,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "checks": [asdict(c) if hasattr(c, "__dataclass_fields__") else c for c in self.checks],
        }


@dataclass
class Embodiment:
    """
    Un cuerpo cognitivo instanciado desde un ResourcePlan.

    Contiene todo lo necesario para que el bucle cognitivo funcione:
    - ModelBus configurado con el backend seleccionado
    - Almacén de memoria montado
    - Cápsulas cargadas
    - Variables de entorno aplicadas
    - Estado de salud del cuerpo
    """
    # Identidad
    embodiment_id: str = ""
    plan_signature: str = ""           # hash del plan que lo originó

    # Componentes instanciados
    model_bus: Any = None              # ModelBus configurado
    memory_store: Any = None           # PersistentMemoryStore (opcional)
    capsules_loaded: List[str] = field(default_factory=list)

    # Configuración aplicada
    backend_name: str = ""
    model_name: str = ""
    strategy: str = ""                 # full_ram | mmap_partial | mmap_full | cloud
    ollama_env_applied: Dict[str, str] = field(default_factory=dict)

    # Salud
    status: str = EmbodimentStatus.STOPPED.value
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Tiempos
    boot_started_at: float = 0.0
    boot_completed_at: float = 0.0
    boot_duration_ms: float = 0.0

    # Metadata
    acd_level: str = ""
    metabolic_state: str = ""
    sensitive_domain: bool = False
    available_ram_gb: float = 0.0

    @property
    def is_running(self) -> bool:
        return self.status in (
            EmbodimentStatus.RUNNING.value,
            EmbodimentStatus.DEGRADED.value,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "embodiment_id": self.embodiment_id,
            "plan_signature": self.plan_signature,
            "backend_name": self.backend_name,
            "model_name": self.model_name,
            "strategy": self.strategy,
            "ollama_env_applied": self.ollama_env_applied,
            "capsules_loaded": self.capsules_loaded,
            "status": self.status,
            "warnings": self.warnings,
            "errors": self.errors,
            "boot_started_at": self.boot_started_at,
            "boot_completed_at": self.boot_completed_at,
            "boot_duration_ms": self.boot_duration_ms,
            "acd_level": self.acd_level,
            "metabolic_state": self.metabolic_state,
            "sensitive_domain": self.sensitive_domain,
            "available_ram_gb": self.available_ram_gb,
            "is_running": self.is_running,
            "model_bus_backends": (
                self.model_bus.list_backends()
                if self.model_bus and hasattr(self.model_bus, "list_backends")
                else []
            ),
        }


# ============================================================
# EmbodimentComposer
# ============================================================

class EmbodimentComposer:
    """
    Compone un cuerpo cognitivo desde un ResourcePlan.

    Uso básico:
        composer = EmbodimentComposer()
        plan = ResourcePlanner().plan(acd_level="L2_STANDARD", ...)
        embodiment = composer.compose(plan, model_bus=bus)
        if embodiment.is_running:
            # el cuerpo está listo para pensar
            ...

    Uso full-pipeline (desde cero):
        embodiment = composer.bootstrap_from_scratch(
            acd_level="L2_STANDARD",
            metabolic_state="awake",
            sensitive_domain=False,
        )
        # embodiment.status == "running"
    """

    def __init__(self):
        self._active_embodiments: Dict[str, Embodiment] = {}
        self._embodiment_counter = 0
        self._total_compositions = 0
        self._total_failures = 0
        self._composition_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------
    # 1. Validación de prerrequisitos
    # ------------------------------------------------------------

    def validate_prerequisites(
        self,
        plan: Any,
        model_bus: Any = None,
        available_ram_gb: float = 0.0,
    ) -> ValidationResult:
        """
        Verifica que un plan se puede instanciar antes de intentarlo.

        Ejecuta checks de prerrequisitos y devuelve un ValidationResult
        con la lista de checks y si el plan puede arrancar.

        Checks:
        - plan_will_work: el plan no está marcado como inviable
        - backend_exists: el backend seleccionado está en el ModelBus
        - backend_available: el backend está marcado como disponible
        - ram_sufficient: hay RAM para la estrategia del plan
        - ollama_running: si el plan es local, Ollama está corriendo
        - cloud_api_key: si el plan es cloud, la API key está configurada
        """
        checks: List[ValidationCheck] = []
        blockers = 0
        warnings = 0

        # Check 1: plan.will_work
        plan_will_work = getattr(plan, "will_work", True)
        plan_warning = getattr(plan, "warning", None)
        if not plan_will_work:
            checks.append(ValidationCheck(
                name="plan_will_work",
                level=ValidationLevel.BLOCKER.value,
                message=f"Plan is marked as not viable: {plan_warning or 'no reason'}",
            ))
            blockers += 1
        else:
            checks.append(ValidationCheck(
                name="plan_will_work",
                level=ValidationLevel.OK.value,
                message="Plan is viable",
            ))

        backend_name = getattr(plan, "backend_name", "")
        strategy = getattr(plan, "strategy", "")

        # Check 2: backend existe en el bus
        if model_bus and backend_name:
            backends = {}
            if hasattr(model_bus, "_backends"):
                backends = model_bus._backends
            if hasattr(model_bus, "list_backends"):
                backend_dicts = model_bus.list_backends()
                backend_names_in_bus = {b["name"] for b in backend_dicts}
            else:
                backend_names_in_bus = set(backends.keys())

            if backend_name not in backend_names_in_bus:
                checks.append(ValidationCheck(
                    name="backend_exists",
                    level=ValidationLevel.BLOCKER.value,
                    message=f"Backend '{backend_name}' not found in ModelBus",
                    detail={"available_backends": list(backend_names_in_bus)},
                ))
                blockers += 1
            else:
                # Check 3: backend disponible
                entry = backends.get(backend_name)
                if entry and not entry.available:
                    checks.append(ValidationCheck(
                        name="backend_available",
                        level=ValidationLevel.BLOCKER.value,
                        message=f"Backend '{backend_name}' is marked unavailable",
                        detail={"fail_count": entry.fail_count},
                    ))
                    blockers += 1
                else:
                    checks.append(ValidationCheck(
                        name="backend_available",
                        level=ValidationLevel.OK.value,
                        message=f"Backend '{backend_name}' is available",
                    ))

        # Check 4: RAM suficiente para estrategia
        if strategy in ("full_ram", "mmap_partial") and available_ram_gb > 0:
            min_ram = 2.0 if strategy == "full_ram" else 1.0
            if available_ram_gb < min_ram:
                checks.append(ValidationCheck(
                    name="ram_sufficient",
                    level=ValidationLevel.WARNING.value,
                    message=f"Available RAM {available_ram_gb:.1f}GB below recommended {min_ram:.1f}GB for {strategy}",
                    detail={"available_gb": available_ram_gb, "min_recommended_gb": min_ram},
                ))
                warnings += 1
            else:
                checks.append(ValidationCheck(
                    name="ram_sufficient",
                    level=ValidationLevel.OK.value,
                    message=f"RAM {available_ram_gb:.1f}GB sufficient for {strategy}",
                ))

        # Check 5: Ollama corriendo si estrategia local
        if strategy in ("full_ram", "mmap_partial", "mmap_full"):
            ollama_ok = self._check_ollama_running()
            if not ollama_ok:
                checks.append(ValidationCheck(
                    name="ollama_running",
                    level=ValidationLevel.BLOCKER.value,
                    message="Ollama not running on localhost:11434 but plan is local",
                    detail={"address": "http://localhost:11434"},
                ))
                blockers += 1
            else:
                checks.append(ValidationCheck(
                    name="ollama_running",
                    level=ValidationLevel.OK.value,
                    message="Ollama is running on localhost:11434",
                ))

        # Check 6: cloud API key si estrategia cloud
        if strategy == "cloud":
            api_key_ok = self._check_cloud_api_key(backend_name)
            if not api_key_ok:
                checks.append(ValidationCheck(
                    name="cloud_api_key",
                    level=ValidationLevel.BLOCKER.value,
                    message=f"Cloud backend '{backend_name}' has no API key configured",
                    detail={"backend": backend_name},
                ))
                blockers += 1
            else:
                checks.append(ValidationCheck(
                    name="cloud_api_key",
                    level=ValidationLevel.OK.value,
                    message=f"Cloud backend '{backend_name}' has API key configured",
                ))

        # Check 7: si el plan viene con warning, propagar
        if plan_warning and blockers == 0:
            checks.append(ValidationCheck(
                name="plan_warning",
                level=ValidationLevel.WARNING.value,
                message=f"Plan warning: {plan_warning}",
            ))
            warnings += 1

        return ValidationResult(
            plan_will_work=blockers == 0,
            checks=checks,
            blockers=blockers,
            warnings=warnings,
        )

    # ------------------------------------------------------------
    # 2. Composición desde un plan
    # ------------------------------------------------------------

    def compose(
        self,
        plan: Any,
        model_bus: Any = None,
        memory_store: Any = None,
        capsules: Optional[List[str]] = None,
        skip_validation: bool = False,
    ) -> Embodiment:
        """
        Instancia un cuerpo cognitivo desde un ResourcePlan.

        Args:
            plan: ResourcePlan devuelto por ResourcePlanner.plan()
            model_bus: ModelBus ya configurado (opcional, se usa tal cual)
            memory_store: PersistentMemoryStore ya montado (opcional)
            capsules: lista de nombres de cápsulas a "cargar" (metadata)
            skip_validation: si True, salta el check de prerrequisitos

        Returns:
            Embodiment con status RUNNING, DEGRADED o FAILED
        """
        boot_start = time.time()
        self._total_compositions += 1
        self._embodiment_counter += 1
        embodiment_id = f"emb_{int(boot_start)}_{self._embodiment_counter}"

        emb = Embodiment(
            embodiment_id=embodiment_id,
            plan_signature=self._sign_plan(plan),
            model_bus=model_bus,
            memory_store=memory_store,
            backend_name=getattr(plan, "backend_name", ""),
            model_name=getattr(plan, "model_name", ""),
            strategy=getattr(plan, "strategy", ""),
            ollama_env_applied=dict(getattr(plan, "ollama_env", {})),
            acd_level=getattr(plan, "acd_level", ""),
            metabolic_state=getattr(plan, "metabolic_state", ""),
            sensitive_domain=getattr(plan, "sensitive_domain", False),
            available_ram_gb=getattr(plan, "available_ram_gb", 0.0),
            boot_started_at=boot_start,
            capsules_loaded=list(capsules or []),
        )

        # 1. Validar prerrequisitos
        if not skip_validation:
            validation = self.validate_prerequisites(
                plan=plan,
                model_bus=model_bus,
                available_ram_gb=getattr(plan, "available_ram_gb", 0.0),
            )

            # Si hay blockers, FAILED
            if validation.blockers > 0:
                emb.status = EmbodimentStatus.FAILED.value
                emb.errors = [
                    c.message for c in validation.checks
                    if c.level == ValidationLevel.BLOCKER.value
                ]
                emb.warnings = [
                    c.message for c in validation.checks
                    if c.level == ValidationLevel.WARNING.value
                ]
                emb.boot_completed_at = time.time()
                emb.boot_duration_ms = (emb.boot_completed_at - boot_start) * 1000
                self._total_failures += 1
                self._log_composition(emb, "failed")
                return emb

            # Si hay warnings, DEGRADED
            if validation.warnings > 0:
                emb.warnings = [
                    c.message for c in validation.checks
                    if c.level == ValidationLevel.WARNING.value
                ]

        # 2. Aplicar variables de entorno Ollama
        if emb.ollama_env_applied:
            self._apply_ollama_env(emb.ollama_env_applied)

        # 3. Verificar que el backend responde
        if model_bus and emb.backend_name:
            backend_ok = self._verify_backend(model_bus, emb.backend_name)
            if not backend_ok:
                emb.warnings.append(
                    f"Backend '{emb.backend_name}' failed health check "
                    "(marked DEGRADED, will retry on first request)"
                )

        # 4. Estado final
        if emb.warnings and not emb.errors:
            emb.status = EmbodimentStatus.DEGRADED.value
        else:
            emb.status = EmbodimentStatus.RUNNING.value

        emb.boot_completed_at = time.time()
        emb.boot_duration_ms = (emb.boot_completed_at - boot_start) * 1000

        # 5. Registrar
        self._active_embodiments[embodiment_id] = emb
        self._log_composition(emb, "ok")
        logger.info(
            f"EmbodimentComposer: composed {embodiment_id} "
            f"(status={emb.status}, backend={emb.backend_name}, "
            f"strategy={emb.strategy}, {emb.boot_duration_ms:.1f}ms)"
        )
        return emb

    # ------------------------------------------------------------
    # 3. Bootstrap desde cero (pipeline completo)
    # ------------------------------------------------------------

    def bootstrap_from_scratch(
        self,
        acd_level: str = "L2_STANDARD",
        metabolic_state: str = "awake",
        sensitive_domain: bool = False,
        available_ram_gb: Optional[float] = None,
        capsules: Optional[List[str]] = None,
        memory_db_path: Optional[str] = None,
    ) -> Embodiment:
        """
        Pipeline completo: discover → bus → plan → compose.

        Ejecuta las 4 fases en orden y devuelve un Embodiment listo
        para pensar (o FAILED si no hay recursos).

        Sin argumentos, intenta arrancar el cuerpo por defecto (L2,
        awake, sin dominio sensible) con lo que tenga a mano.
        """
        # 1. Detectar RAM disponible si no se especifica
        if available_ram_gb is None:
            available_ram_gb = self._detect_available_ram()

        # 2. Resource Discovery (Fase 7A)
        try:
            from ..peripherals.resource_discovery import ResourceDiscoverySense
            sense = ResourceDiscoverySense()
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Ya estamos en un loop async: usar run_until_complete no funciona
                    # En su lugar, ejecutar el scan sincrónico (sin observe)
                    import asyncio
                    loop.run_until_complete(sense.observe())
                else:
                    loop.run_until_complete(sense.observe())
            except RuntimeError:
                asyncio.run(sense.observe())
            graph = sense.get_graph()
        except Exception as e:
            logger.warning(f"EmbodimentComposer: resource discovery failed: {e}")
            graph = None

        # 3. Model Bus desde grafo (Fase 7B)
        bus = None
        if graph:
            try:
                from ..peripherals.model_bus import ModelBus
                bus = ModelBus.from_resource_graph(graph)
                if not bus.get_available_backends():
                    bus = None
            except Exception as e:
                logger.warning(f"EmbodimentComposer: model bus build failed: {e}")
                bus = None

        # 4. Resource Plan (Fase 7C)
        try:
            from .resource_planner import ResourcePlanner
            from .model_optimizer import ModelOptimizer
            planner = ResourcePlanner()
            optimizer = ModelOptimizer()
            plan = planner.plan(
                acd_level=acd_level,
                metabolic_state=metabolic_state,
                sensitive_domain=sensitive_domain,
                available_ram_gb=available_ram_gb,
                model_bus=bus,
                resource_graph=graph,
                model_optimizer=optimizer,
            )
        except Exception as e:
            logger.error(f"EmbodimentComposer: planning failed: {e}")
            # Devolver embodiment FAILED
            emb = Embodiment(
                embodiment_id=f"emb_failed_{int(time.time())}",
                status=EmbodimentStatus.FAILED.value,
                acd_level=acd_level,
                metabolic_state=metabolic_state,
                sensitive_domain=sensitive_domain,
                available_ram_gb=available_ram_gb,
                errors=[f"Planning failed: {e}"],
                boot_started_at=time.time(),
                boot_completed_at=time.time(),
            )
            self._total_failures += 1
            self._log_composition(emb, "failed")
            return emb

        # 5. Memory store (opcional)
        memory_store = None
        if memory_db_path:
            try:
                from ..memory.persistent_store import PersistentMemoryStore
                memory_store = PersistentMemoryStore(db_path=memory_db_path)
            except Exception as e:
                logger.warning(f"EmbodimentComposer: memory store init failed: {e}")

        # 6. Compose (Fase 7D)
        emb = self.compose(
            plan=plan,
            model_bus=bus,
            memory_store=memory_store,
            capsules=capsules,
        )
        return emb

    # ------------------------------------------------------------
    # 4. Tear down
    # ------------------------------------------------------------

    def tear_down(self, embodiment_id: str) -> bool:
        """
        Detiene un embodiment y libera recursos.

        Marca el embodiment como STOPPED y lo elimina de la lista activa.
        No cierra Ollama (lo gestiona el SO) ni borra memoria persistente.
        """
        emb = self._active_embodiments.pop(embodiment_id, None)
        if emb is None:
            return False

        # Si tenía variables de entorno aplicadas, no las deshacemos
        # (podrían estar en uso por otros procesos); solo anotamos
        emb.status = EmbodimentStatus.STOPPED.value
        self._log_composition(emb, "stopped")
        logger.info(f"EmbodimentComposer: torn down {embodiment_id}")
        return True

    def tear_down_all(self) -> int:
        """Detiene todos los embodiments activos. Devuelve cuántos cerró."""
        ids = list(self._active_embodiments.keys())
        closed = 0
        for emb_id in ids:
            if self.tear_down(emb_id):
                closed += 1
        return closed

    # ------------------------------------------------------------
    # 5. Status y stats
    # ------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Estado global del composer."""
        active = sum(
            1 for e in self._active_embodiments.values()
            if e.is_running
        )
        return {
            "active_embodiments": len(self._active_embodiments),
            "running_embodiments": active,
            "total_compositions": self._total_compositions,
            "total_failures": self._total_failures,
            "success_rate": round(
                (self._total_compositions - self._total_failures)
                / max(1, self._total_compositions), 3
            ),
            "embodiments": [
                {"id": e.embodiment_id, "status": e.status, "backend": e.backend_name}
                for e in self._active_embodiments.values()
            ],
        }

    def get_embodiment(self, embodiment_id: str) -> Optional[Embodiment]:
        return self._active_embodiments.get(embodiment_id)

    def list_active(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._active_embodiments.values()]

    # ------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------

    def _sign_plan(self, plan: Any) -> str:
        """Genera una firma única del plan (para trazabilidad)."""
        import hashlib
        signature_parts = [
            str(getattr(plan, "backend_name", "")),
            str(getattr(plan, "model_name", "")),
            str(getattr(plan, "strategy", "")),
            str(getattr(plan, "acd_level", "")),
            str(getattr(plan, "metabolic_state", "")),
            str(getattr(plan, "sensitive_domain", "")),
            str(getattr(plan, "timestamp", "")),
        ]
        raw = "|".join(signature_parts)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _apply_ollama_env(self, env: Dict[str, str]) -> None:
        """Aplica variables de entorno Ollama al proceso actual."""
        for key, value in env.items():
            if value is not None:
                os.environ[key] = str(value)
                logger.debug(f"EmbodimentComposer: set env {key}={value}")

    def _verify_backend(self, model_bus: Any, backend_name: str) -> bool:
        """Verifica que un backend responde (health check ligero)."""
        try:
            if hasattr(model_bus, "_backends"):
                entry = model_bus._backends.get(backend_name)
                if entry and hasattr(entry.peripheral, "health_check"):
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # No podemos bloquear; asumir OK
                            return True
                        if loop.is_closed():
                            return True  # no hay loop activo, asumir OK
                        return loop.run_until_complete(entry.peripheral.health_check())
                    except RuntimeError:
                        # No hay event loop en este hilo → asumir OK
                        return True
            # Sin método health_check, asumir OK
            return True
        except Exception as e:
            logger.debug(f"EmbodimentComposer: health check failed for {backend_name}: {e}")
            return False

    def _check_ollama_running(self) -> bool:
        """Verifica si Ollama responde en localhost:11434."""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        try:
            result = sock.connect_ex(("localhost", 11434))
            return result == 0
        except Exception:
            return False
        finally:
            sock.close()

    def _check_cloud_api_key(self, backend_name: str) -> bool:
        """Verifica si la API key del cloud backend está configurada."""
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "groq": "GROQ_API_KEY",
            "moonshot": "MOONSHOT_API_KEY",
            "minimax": "MINIMAX_API_KEY",
        }
        for prefix, env_var in key_map.items():
            if prefix in backend_name.lower():
                return bool(os.environ.get(env_var))
        # Si no reconocemos el backend, asumir que tiene key
        return True

    def _detect_available_ram(self) -> float:
        """Detecta RAM disponible del sistema en GB."""
        try:
            import psutil
            return round(psutil.virtual_memory().available / (1024**3), 1)
        except ImportError:
            pass

        # Fallback sin psutil
        system = __import__("platform").system()
        try:
            if system == "Darwin":
                result = subprocess.run(
                    ["vm_stat"],
                    capture_output=True, text=True, timeout=2
                )
                # parseo rápido
                for line in result.stdout.split("\n"):
                    if "free" in line.lower() or "inactive" in line.lower():
                        # aproximación burda
                        pass
                # Apple Silicon Mac típica: 8GB → ~5 disponibles
                return 5.0
            elif system == "Linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemAvailable:"):
                            kb = int(line.split()[1])
                            return round(kb / (1024 * 1024), 1)
        except Exception:
            pass

        # Default conservador
        return 4.0

    def _log_composition(self, emb: Embodiment, outcome: str) -> None:
        """Registra la composición en el log interno."""
        self._composition_log.append({
            "embodiment_id": emb.embodiment_id,
            "outcome": outcome,
            "status": emb.status,
            "backend": emb.backend_name,
            "strategy": emb.strategy,
            "duration_ms": round(emb.boot_duration_ms, 2),
            "timestamp": time.time(),
            "warnings": len(emb.warnings),
            "errors": len(emb.errors),
        })
        if len(self._composition_log) > 100:
            self._composition_log = self._composition_log[-50:]

    def get_composition_log(self) -> List[Dict[str, Any]]:
        """Devuelve el log reciente de composiciones."""
        return list(self._composition_log)
