"""
ZOE v1.1 — Capsule Manager

Gestiona la carga, descarga e inyección de cápsulas en un organismo ZOE en runtime.
Es el componente que usan CLI Chat, Web Dashboard y run_use_case para integrar
cápsulas con el resto del sistema.

Funcionalidades:
- Carga cápsulas al iniciar ZOE (según YAML del caso de uso)
- Carga cápsulas en caliente (runtime) bajo demanda
- Descarga cápsulas
- Inyecta contenido en componentes: LivingMemory, CausalEngine, EmotionalMotor, EthicalMotor
- Registra validators en Speaker, Learner, ScientificEngine
- Registra tools en ActuatorManager
- Firma mutaciones capsule_loaded / capsule_unloaded en TrajectoryChain
- Integra con EpistemicValidator para registrar cápsulas como fuente confiable
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

from ..capsules import (
    CapsuleLoader, LoadedCapsule, CapsuleRegistry, CapsuleLoadError,
    TrustLevel, TRUST_TO_CONFIDENCE,
)
from .epistemic_validator import EpistemicValidator, ValidationStatus

logger = logging.getLogger(__name__)


@dataclass
class CapsuleLoadResult:
    """Resultado de cargar una cápsula."""
    capsule_name: str
    success: bool
    entries_loaded: int = 0
    components_injected: List[str] = field(default_factory=list)
    error: Optional[str] = None
    duration_ms: float = 0.0
    trajectory_hash: Optional[str] = None


class CapsuleManager:
    """
    Gestiona cápsulas activas en un organismo ZOE.
    
    Uso típico:
        manager = CapsuleManager(organism=loop)
        manager.load_for_use_case("cuidado_personas_mayores", config)
        # o cargar individual:
        manager.load("elder_care_knowledge")
        # descargar:
        manager.unload("elder_care_knowledge")
        # listar cargadas:
        manager.list_loaded()
    """
    
    def __init__(
        self,
        organism: Any = None,
        loader: Optional[CapsuleLoader] = None,
        registry: Optional[CapsuleRegistry] = None,
        epistemic_validator: Optional[EpistemicValidator] = None,
    ):
        self.organism = organism
        self.loader = loader or CapsuleLoader()
        self.registry = registry or CapsuleRegistry()
        self.validator = epistemic_validator
        
        # Cápsulas cargadas actualmente
        self._loaded: Dict[str, LoadedCapsule] = {}
        
        # Mapa de entries cargados por cápsula (para descarga selectiva)
        self._entries_by_capsule: Dict[str, List[str]] = {}
        
        # Stats
        self.total_loads = 0
        self.total_unloads = 0
        self.total_entries_injected = 0
    
    def load_for_use_case(
        self, use_case_name: str, config: Dict[str, Any]
    ) -> List[CapsuleLoadResult]:
        """Carga todas las cápsulas compatibles con un caso de uso."""
        capsules = self.loader.load_for_use_case(use_case_name, config)
        results = []
        for cap in capsules:
            if cap.name not in self._loaded:
                result = self._inject(cap)
                results.append(result)
        return results
    
    def load(self, capsule_name: str) -> CapsuleLoadResult:
        """Carga una cápsula individual en runtime."""
        start = time.time()
        
        if capsule_name in self._loaded:
            return CapsuleLoadResult(
                capsule_name=capsule_name,
                success=False,
                error="already_loaded",
            )
        
        try:
            cap = self.loader._load_capsule(capsule_name)
            if not cap:
                return CapsuleLoadResult(
                    capsule_name=capsule_name,
                    success=False,
                    error="capsule_not_found",
                )
            
            # Verificar dependencias
            for dep in cap.meta.depends_on:
                if dep not in self._loaded:
                    # Cargar dependencia primero
                    dep_result = self.load(dep)
                    if not dep_result.success:
                        return CapsuleLoadResult(
                            capsule_name=capsule_name,
                            success=False,
                            error=f"dependency_failed:{dep}:{dep_result.error}",
                        )
            
            result = self._inject(cap)
            result.duration_ms = (time.time() - start) * 1000
            return result
            
        except Exception as e:
            logger.error(f"Failed to load capsule {capsule_name}: {e}")
            return CapsuleLoadResult(
                capsule_name=capsule_name,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000,
            )
    
    def _inject(self, cap: LoadedCapsule) -> CapsuleLoadResult:
        """Inyecta el contenido de una cápsula en el organismo."""
        components_injected = []
        entries_loaded = 0
        entry_ids = []
        
        if not self.organism:
            # Modo standalone (tests, registro solo)
            self._loaded[cap.name] = cap
            self.total_loads += 1
            return CapsuleLoadResult(
                capsule_name=cap.name,
                success=True,
                entries_loaded=cap.total_entries,
                components_injected=list(cap.meta.components.keys()),
            )
        
        # 1. Inyectar en memoria viva (LivingMemory)
        if hasattr(self.organism, 'memory') and self.organism.memory:
            for entry in cap.semantic_memory:
                try:
                    entry_id = self.organism.memory.add(
                        content=entry.get("content", ""),
                        type="semantic",
                        confidence=entry.get("confidence", cap.meta.effective_confidence),
                        salience=entry.get("salience", 0.6),
                        provenance=f"capsule:{cap.name}",
                        metadata={
                            "capsule": cap.name,
                            "capsule_version": cap.meta.version,
                            "trust_level": cap.meta.trust_level.value,
                            "domain": cap.meta.domain,
                            "category": entry.get("category"),
                            "tags": entry.get("tags", []),
                            "capsule_loaded": True,
                        }
                    )
                    entry_ids.append(entry_id)
                    entries_loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to inject semantic entry: {e}")
            
            for entry in cap.procedural_skills:
                try:
                    entry_id = self.organism.memory.add(
                        content=entry.get("skill", ""),
                        type="procedural",
                        confidence=entry.get("confidence", cap.meta.effective_confidence),
                        salience=0.7,
                        provenance=f"capsule:{cap.name}",
                        metadata={
                            "capsule": cap.name,
                            "steps": entry.get("steps", []),
                            "when_to_apply": entry.get("when_to_apply"),
                        }
                    )
                    entry_ids.append(entry_id)
                    entries_loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to inject procedural entry: {e}")
            
            components_injected.append("memory")
        
        # 2. Inyectar en CausalEngine
        if hasattr(self.organism, 'causal_engine') and self.organism.causal_engine and cap.causal_models:
            for model in cap.causal_models:
                try:
                    if hasattr(self.organism.causal_engine, 'add_prevalidated_model'):
                        self.organism.causal_engine.add_prevalidated_model(model)
                    entries_loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to inject causal model: {e}")
            components_injected.append("causal_engine")
        
        # 3. Inyectar en EmotionalMotor
        if hasattr(self.organism, 'emotional_motor') and self.organism.emotional_motor and cap.emotional_patterns:
            for pattern in cap.emotional_patterns:
                try:
                    if hasattr(self.organism.emotional_motor, 'add_pattern'):
                        self.organism.emotional_motor.add_pattern(pattern)
                    entries_loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to inject emotional pattern: {e}")
            components_injected.append("emotional_motor")
        
        # 4. Inyectar en EthicalMotor
        if hasattr(self.organism, 'ethical_motor') and self.organism.ethical_motor and cap.ethical_guidelines:
            for guideline in cap.ethical_guidelines:
                try:
                    if hasattr(self.organism.ethical_motor, 'add_guideline'):
                        self.organism.ethical_motor.add_guideline(guideline)
                    entries_loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to inject ethical guideline: {e}")
            components_injected.append("ethical_motor")
        
        # 5. Registrar validators
        if cap.validators and hasattr(self.organism, 'speaker'):
            try:
                if hasattr(self.organism.speaker, 'register_validators'):
                    self.organism.speaker.register_validators(cap.name, cap.validators)
                components_injected.append("validators_speaker")
            except Exception as e:
                logger.warning(f"Failed to register validators in Speaker: {e}")
        
        if cap.validators and hasattr(self.organism, 'learner'):
            try:
                if hasattr(self.organism.learner, 'register_validators'):
                    self.organism.learner.register_validators(cap.name, cap.validators)
                components_injected.append("validators_learner")
            except Exception as e:
                logger.warning(f"Failed to register validators in Learner: {e}")
        
        # Fase 6A: inyectar EpistemicValidator en Learner la primera vez que se carga una cápsula
        # (solo si el Learner lo soporta y aún no lo tiene)
        if (hasattr(self.organism, 'learner') and 
            hasattr(self.organism.learner, 'set_epistemic_validator') and
            self.validator):
            try:
                # Buscar si hay Quarantine disponible
                quarantine = getattr(self.organism, 'knowledge_quarantine', None)
                self.organism.learner.set_epistemic_validator(self.validator, quarantine)
                components_injected.append("epistemic_validator_in_learner")
            except Exception as e:
                logger.warning(f"Failed to inject EpistemicValidator in Learner: {e}")
        
        # Fase 6A Punto 3: inyectar KnowledgeQuarantine en Curator, DeepConsolidation y Critic
        # la primera vez que se carga una cápsula
        quarantine = getattr(self.organism, 'knowledge_quarantine', None)
        if quarantine:
            # Curator
            if (hasattr(self.organism, 'curator') and
                hasattr(self.organism.curator, 'set_quarantine')):
                try:
                    self.organism.curator.set_quarantine(quarantine)
                    components_injected.append("quarantine_in_curator")
                except Exception as e:
                    logger.warning(f"Failed to inject Quarantine in Curator: {e}")
            
            # DeepConsolidation
            if (hasattr(self.organism, 'deep_consolidation') and
                hasattr(self.organism.deep_consolidation, 'set_quarantine')):
                try:
                    self.organism.deep_consolidation.set_quarantine(quarantine)
                    components_injected.append("quarantine_in_deep_consolidation")
                except Exception as e:
                    logger.warning(f"Failed to inject Quarantine in DeepConsolidation: {e}")
            
            # Critic
            if (hasattr(self.organism, 'critic_agent') and
                hasattr(self.organism.critic_agent, 'set_quarantine')):
                try:
                    self.organism.critic_agent.set_quarantine(quarantine)
                    components_injected.append("quarantine_in_critic")
                except Exception as e:
                    logger.warning(f"Failed to inject Quarantine in Critic: {e}")
            # También intentar con el subagent Critic si está en subagents
            for sub in getattr(self.organism, 'subagents', []):
                if sub.__class__.__name__ == 'Critic' and hasattr(sub, 'set_quarantine'):
                    try:
                        sub.set_quarantine(quarantine)
                        components_injected.append("quarantine_in_critic_subagent")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to inject Quarantine in Critic subagent: {e}")
        
        # 6. Registrar tools
        if cap.tools and hasattr(self.organism, 'actuator_manager'):
            for tool in cap.tools:
                try:
                    if hasattr(self.organism.actuator_manager, 'register_tool'):
                        self.organism.actuator_manager.register_tool(tool)
                    components_injected.append("tools")
                except Exception as e:
                    logger.warning(f"Failed to register tool: {e}")
        
        # 7. Registrar prompts
        if cap.prompts and hasattr(self.organism, 'speaker'):
            for prompt_name, prompt_content in cap.prompts.items():
                try:
                    if hasattr(self.organism.speaker, 'add_specialized_prompt'):
                        self.organism.speaker.add_specialized_prompt(prompt_name, prompt_content)
                    components_injected.append("prompts")
                except Exception as e:
                    logger.warning(f"Failed to register prompt: {e}")
        
        # 8. Registrar en EpistemicValidator como fuente confiable
        if self.validator and cap.meta.trust_level == TrustLevel.VERIFIED:
            source_name = f"capsule:{cap.name}"
            self.validator.source_trust[source_name] = cap.meta.effective_confidence
        
        # 9. Mutación firmada en trayectoria
        trajectory_hash = None
        if hasattr(self.organism, 'ontogenetic_motor') and self.organism.ontogenetic_motor:
            try:
                mutation = self.organism.ontogenetic_motor.propose_mutation(
                    type="capsule_loaded",
                    target="memory",
                    payload={
                        "capsule": cap.name,
                        "version": cap.meta.version,
                        "trust_level": cap.meta.trust_level.value,
                        "entries_loaded": entries_loaded,
                        "components_injected": components_injected,
                    },
                    justification=f"Capsule {cap.name} v{cap.meta.version} loaded",
                    provenance=f"capsule:{cap.name}",
                    cost=cap.meta.load_cost,
                    confidence=cap.meta.effective_confidence,
                )
                self.organism.ontogenetic_motor.apply_mutation(mutation)
                trajectory_hash = mutation.hash
            except Exception as e:
                logger.warning(f"Failed to sign capsule_loaded mutation: {e}")
        
        # Guardar referencias
        self._loaded[cap.name] = cap
        self._entries_by_capsule[cap.name] = entry_ids
        self.total_loads += 1
        self.total_entries_injected += entries_loaded
        
        logger.info(
            f"Capsule loaded: {cap.name} ({entries_loaded} entries, "
            f"{len(components_injected)} components injected)"
        )
        
        return CapsuleLoadResult(
            capsule_name=cap.name,
            success=True,
            entries_loaded=entries_loaded,
            components_injected=components_injected,
            trajectory_hash=trajectory_hash,
        )
    
    def unload(self, capsule_name: str) -> bool:
        """Descarga una cápsula y elimina sus entries de memoria."""
        if capsule_name not in self._loaded:
            return False
        
        cap = self._loaded[capsule_name]
        entry_ids = self._entries_by_capsule.get(capsule_name, [])
        
        # Eliminar entries de memoria
        if hasattr(self.organism, 'memory') and self.organism.memory:
            for entry_id in entry_ids:
                try:
                    if hasattr(self.organism.memory, 'remove'):
                        self.organism.memory.remove(entry_id)
                except Exception as e:
                    logger.warning(f"Failed to remove entry {entry_id}: {e}")
        
        # Mutación firmada
        if hasattr(self.organism, 'ontogenetic_motor') and self.organism.ontogenetic_motor:
            try:
                mutation = self.organism.ontogenetic_motor.propose_mutation(
                    type="capsule_unloaded",
                    target="memory",
                    payload={
                        "capsule": cap.name,
                        "entries_removed": len(entry_ids),
                    },
                    justification=f"Capsule {cap.name} unloaded",
                    provenance=f"capsule_unload:{cap.name}",
                    cost=0.05,
                    confidence=0.9,
                )
                self.organism.ontogenetic_motor.apply_mutation(mutation)
            except Exception as e:
                logger.warning(f"Failed to sign capsule_unloaded mutation: {e}")
        
        del self._loaded[capsule_name]
        if capsule_name in self._entries_by_capsule:
            del self._entries_by_capsule[capsule_name]
        self.total_unloads += 1
        
        logger.info(f"Capsule unloaded: {capsule_name} ({len(entry_ids)} entries removed)")
        return True
    
    def list_loaded(self) -> List[Dict[str, Any]]:
        """Lista cápsulas cargadas actualmente."""
        result = []
        for name, cap in self._loaded.items():
            entry_count = len(self._entries_by_capsule.get(name, []))
            result.append({
                "name": name,
                "version": cap.meta.version,
                "trust_level": cap.meta.trust_level.value,
                "domain": cap.meta.domain,
                "entries_injected": entry_count,
                "total_entries": cap.total_entries,
                "description": cap.meta.description,
                "provenance": cap.meta.provenance,
                "loaded_at": cap.path.stat().st_mtime if cap.path.exists() else None,
            })
        return result
    
    def list_available(self) -> List[Dict[str, Any]]:
        """Lista cápsulas disponibles (cargadas y no cargadas)."""
        all_caps = self.registry.list_all()
        loaded_names = set(self._loaded.keys())
        result = []
        for meta in all_caps:
            result.append({
                "name": meta.name,
                "version": meta.version,
                "trust_level": meta.trust_level.value,
                "domain": meta.domain,
                "description": meta.description,
                "compatible_use_cases": meta.compatible_use_cases,
                "depends_on": meta.depends_on,
                "is_loaded": meta.name in loaded_names,
                "default_confidence": meta.effective_confidence,
            })
        return result
    
    def get_info(self, capsule_name: str) -> Optional[Dict[str, Any]]:
        """Info detallada de una cápsula."""
        meta = self.registry.get(capsule_name)
        if not meta:
            return None
        
        is_loaded = capsule_name in self._loaded
        entry_count = 0
        if is_loaded:
            entry_count = len(self._entries_by_capsule.get(capsule_name, []))
        
        return {
            "name": meta.name,
            "version": meta.version,
            "description": meta.description,
            "domain": meta.domain,
            "trust_level": meta.trust_level.value,
            "effective_confidence": meta.effective_confidence,
            "provenance": meta.provenance,
            "last_updated": meta.last_updated,
            "depends_on": meta.depends_on,
            "compatible_use_cases": meta.compatible_use_cases,
            "components": meta.components,
            "capabilities": meta.capabilities,
            "restrictions": meta.restrictions,
            "is_loaded": is_loaded,
            "entries_injected": entry_count,
        }
    
    def get_loaded_validators(self) -> Dict[str, Any]:
        """Recopila validators de todas las cápsulas cargadas."""
        validators = {}
        for name, cap in self._loaded.items():
            if cap.validators:
                validators[name] = cap.validators
        return validators
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "loaded_count": len(self._loaded),
            "loaded_names": list(self._loaded.keys()),
            "total_loads": self.total_loads,
            "total_unloads": self.total_unloads,
            "total_entries_injected": self.total_entries_injected,
            "available_count": len(self.registry.list_all()),
        }

    # ============================================================
    # Sprint 5.8 — Persistencia de cápsulas cargadas
    # ============================================================

    def save_loaded_state(self, path: str) -> None:
        """Sprint 5.8 — Persiste la lista de cápsulas cargadas a disco.

        Permite que las cápsulas cargadas se recarguen automaticamente
        al iniciar ZOE en la siguiente sesion.

        Args:
            path: ruta del archivo JSON a escribir
        """
        import json
        from pathlib import Path
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "loaded": list(self._loaded.keys()),
            "version": 1,
        }
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"CapsuleManager: saved loaded state to {path} ({len(self._loaded)} capsules)")

    @staticmethod
    def load_loaded_state(path: str) -> List[str]:
        """Sprint 5.8 — Carga la lista de cápsulas cargadas desde disco.

        Args:
            path: ruta del archivo JSON

        Returns:
            Lista de nombres de cápsulas cargadas, o [] si no existe
        """
        import json
        from pathlib import Path
        p = Path(path)
        if not p.exists():
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            loaded = data.get("loaded", [])
            logger.info(f"CapsuleManager: loaded state from {path} ({len(loaded)} capsules)")
            return loaded
        except Exception as e:
            logger.warning(f"CapsuleManager: load state failed from {path}: {e}")
            return []
