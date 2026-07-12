"""
Tests Fase 6A — Puntos 1-4 (cápsulas V1.2 + Learner integrado + Dashboard)

Cubre:
1. Carga de las 9 nuevas cápsulas V1.2
2. Integración EpistemicValidator en Learner
3. WebSocket events de cápsulas (no se puede testear directamente, se testea la lógica)
4. Endpoint /api/capsules/{name}/validate
"""

import asyncio
import pytest

from zoe.capsules.loader import CapsuleLoader
from zoe.capsules.registry import CapsuleRegistry
from zoe.core.capsule_manager import CapsuleManager
from zoe.core.epistemic_validator import EpistemicValidator, ValidationStatus
from zoe.core.knowledge_quarantine import KnowledgeQuarantine
from zoe.core.subagents.phase2_subagents import Learner


# ============================================================
# 1. Las 9 nuevas cápsulas V1.2 cargan correctamente
# ============================================================

NEW_CAPSULES = [
    "elder_care_skills",
    "company_loneliness_knowledge",
    "vigilance_devops_knowledge",
    "research_methodology",
    "federation_b2b_skills",
    "b2c_assistant_growth",
    "pharmacy_interactions",
    "ia_heredable_legal",
    "base_ethics",
]


class TestNewCapsulesV12:

    def setup_method(self):
        self.loader = CapsuleLoader()
        self.registry = CapsuleRegistry()

    @pytest.mark.parametrize("cap_name", NEW_CAPSULES)
    def test_capsule_loads(self, cap_name):
        """Cada cápsula nueva carga sin errores."""
        cap = self.loader._load_capsule(cap_name)
        assert cap is not None, f"Failed to load {cap_name}"
        assert cap.meta.name == cap_name

    @pytest.mark.parametrize("cap_name", NEW_CAPSULES)
    def test_capsule_has_metadata(self, cap_name):
        """Cada cápsula tiene metadata válida."""
        meta = self.registry.get(cap_name)
        assert meta is not None
        assert meta.version
        assert meta.trust_level.value in ("verified", "curated", "community", "experimental")
        assert meta.domain
        assert meta.provenance

    def test_total_capsules_now_15(self):
        """Debe haber 15 cápsulas registradas (Sprint 5.7.3: actualizado de 12 a 15)."""
        all_caps = self.registry.list_all()
        assert len(all_caps) == 15

    def test_pharmacy_interactions_has_content(self):
        """pharmacy_interactions tiene entradas semánticas."""
        cap = self.loader._load_capsule("pharmacy_interactions")
        assert len(cap.semantic_memory) >= 15
        assert len(cap.causal_models) >= 5
        assert cap.validators is not None

    def test_elder_care_skills_has_tools(self):
        """elder_care_skills tiene tools cargadas."""
        cap = self.loader._load_capsule("elder_care_skills")
        # Tools se cargan dinámicamente; verificar que tiene directorio
        assert cap.meta.components.get("tools") is True
        assert cap.meta.components.get("prompts") is True
        # Verificar que prompts cargan
        assert len(cap.prompts) >= 1

    def test_research_methodology_has_procedural(self):
        """research_methodology tiene skills procedimentales."""
        cap = self.loader._load_capsule("research_methodology")
        assert len(cap.procedural_skills) >= 5
        assert cap.validators is not None

    def test_federation_b2b_skills_has_tools_and_procedural(self):
        """federation_b2b_skills tiene tools, procedimentales y prompts."""
        cap = self.loader._load_capsule("federation_b2b_skills")
        assert cap.meta.components.get("tools") is True
        assert len(cap.procedural_skills) >= 2

    def test_base_ethics_loadable_in_all_use_cases(self):
        """base_ethics es compatible con todos los casos de uso."""
        meta = self.registry.get("base_ethics")
        use_cases = [
            "cuidado_personas_mayores",
            "compania_personas_solas",
            "vigilancia_cognitiva",
            "investigacion_autonoma",
            "federacion_b2b",
            "asistente_crece_contigo",
            "ia_heredable",
        ]
        for uc in use_cases:
            assert uc in meta.compatible_use_cases

    def test_capsule_validators_callable(self):
        """Los validators de las nuevas cápsulas son llamables."""
        for name in ["pharmacy_interactions", "research_methodology", "base_ethics"]:
            cap = self.loader._load_capsule(name)
            assert cap.validators is not None
            assert hasattr(cap.validators, "validate_response")
            assert hasattr(cap.validators, "validate_new_knowledge")

    def test_pharmacy_validators_block_medication_modification(self):
        """pharmacy_interactions bloquea sugerencias de modificación de medicación."""
        cap = self.loader._load_capsule("pharmacy_interactions")
        ok, reason = cap.validators.validate_response(
            "Deberías suspender la medicación.", context={}
        )
        assert ok is False
        assert "medication_modification" in reason

    def test_pharmacy_validators_require_disclaimer(self):
        """pharmacy_interactions exige disclaimer en respuestas médicas."""
        cap = self.loader._load_capsule("pharmacy_interactions")
        ok, reason = cap.validators.validate_response(
            "El paracetamol es un medicamento.", context={}
        )
        assert ok is False
        assert "disclaimer" in reason

    def test_research_validators_block_overclaiming(self):
        """research_methodology bloquea overclaiming."""
        cap = self.loader._load_capsule("research_methodology")
        ok, reason = cap.validators.validate_response(
            "Esto demuestra que la teoría es correcta.", context={}
        )
        assert ok is False
        assert "overclaiming" in reason

    def test_base_ethics_detects_vulnerability(self):
        """base_ethics detecta indicadores de vulnerabilidad."""
        cap = self.loader._load_capsule("base_ethics")
        indicators = cap.validators.detect_vulnerability_indicators(
            "Mi madre es mayor de 80 y está diagnosticada con demencia."
        )
        assert "elderly" in indicators
        assert "health_vulnerable" in indicators

    def test_vigilance_devops_detects_severity(self):
        """vigilance_devops detecta severidad de incidente."""
        cap = self.loader._load_capsule("vigilance_devops_knowledge")
        severity = cap.validators.detect_incident_severity("El servicio está en caída total.")
        assert severity == "P0"


# ============================================================
# 2. Learner con EpistemicValidator integrado
# ============================================================

class TestLearnerEpistemicIntegration:

    def test_learner_without_validator_compat(self):
        """Learner sin EpistemicValidator funciona como antes (backward compat)."""
        learner = Learner()
        mutation = learner.propose_learning(
            content="algo aprendido",
            source="test",
        )
        assert mutation["type"] == "add_memory"
        assert mutation["confidence"] == 0.5
        assert mutation["metadata"]["quarantine"] is False

    def test_learner_with_validator_quarantines_llm_source(self):
        """Learner con validator cuarentena conocimiento de fuente LLM."""
        validator = EpistemicValidator()
        learner = Learner(epistemic_validator=validator)
        
        mutation = learner.propose_learning(
            content="Algo nuevo aprendido de GPT-4o.",
            source="llm:gpt-4o",
        )
        assert mutation["confidence"] <= 0.50  # capped
        assert mutation["metadata"]["quarantine"] is True

    def test_learner_with_validator_accepts_capsule_source(self):
        """Learner con validator acepta cápsula verificada con confianza alta."""
        validator = EpistemicValidator()
        learner = Learner(epistemic_validator=validator)
        
        mutation = learner.propose_learning(
            content="Hecho de cápsula verificada.",
            source="capsule:verified",
        )
        assert mutation["confidence"] == 0.95
        assert mutation["metadata"]["quarantine"] is False

    def test_learner_rejects_contradiction(self):
        """Learner rechaza conocimiento que contradice cápsula verificada."""
        validator = EpistemicValidator()
        learner = Learner(epistemic_validator=validator)
        
        # Configurar context con cápsula verificada
        learner._capsule_semantic = [{
            "content": "Las benzodiacepinas son peligrosas en mayores.",
            "confidence": 0.92,
            "provenance": "capsule:verified:elder_care",
        }]
        
        mutation = learner.propose_learning(
            content="Las benzodiacepinas no son peligrosas en mayores.",
            source="llm:gpt-4o",
        )
        assert mutation.get("rejected") is True
        assert "contradicts_verified" in mutation.get("rejection_reason", "")

    def test_learner_sensitive_domain_triggers_triple(self):
        """Learner marca como NEEDS_TRIPLE en dominio sensible."""
        validator = EpistemicValidator()
        learner = Learner(epistemic_validator=validator)
        
        mutation = learner.propose_learning(
            content="La dosis recomendada de paracetamol es 1g cada 6 horas.",
            source="llm:gpt-4o",
        )
        # Sensible → NEEDS_TRIPLE_VALIDATION → quarantine
        assert mutation["metadata"]["quarantine"] is True
        assert "triple" in mutation["metadata"]["validation_reason"]

    def test_learner_stats_track_validations(self):
        """Las stats del Learner registran validaciones."""
        validator = EpistemicValidator()
        learner = Learner(epistemic_validator=validator)
        
        learner.propose_learning("hecho 1", source="llm:gpt-4o")
        learner.propose_learning("hecho 2", source="capsule:verified")
        
        stats = learner.get_stats()
        assert stats["validator_active"] is True
        assert stats["validation_attempts"] == 2
        assert stats["validation_quarantined"] >= 1

    def test_learner_with_quarantine_registers_entry(self):
        """Learner con KnowledgeQuarantine registra entries en cuarentena."""
        validator = EpistemicValidator()
        quarantine = KnowledgeQuarantine()
        learner = Learner(epistemic_validator=validator, quarantine=quarantine)
        
        mutation = learner.propose_learning(
            content="Claim nuevo a cuarentena.",
            source="llm:gpt-4o",
        )
        
        if mutation["metadata"]["quarantine"]:
            qid = mutation["metadata"].get("quarantine_entry_id")
            assert qid is not None
            # Verificar que está en cuarentena
            entry = quarantine._entries.get(qid)
            assert entry is not None
            assert entry.status == "active"


# ============================================================
# 3. CapsuleManager carga todas las 12 cápsulas
# ============================================================

class TestCapsuleManagerV12:

    def test_load_all_15_capsules(self):
        """Carga las 15 cápsulas sin organismo (standalone). Sprint 5.7.3: actualizado de 12 a 15."""
        manager = CapsuleManager(organism=None)
        # Cargar primero las que no tienen dependencias, luego las dependientes
        order = [
            "zoe_basal_knowledge",         # no deps (cápsula basal)
            "base_ethics",                # no deps
            "vigilance_devops_knowledge", # no deps
            "research_methodology",       # no deps
            "federation_b2b_skills",      # no deps
            "pharmacy_interactions",      # no deps
            "ia_heredable_legal",         # no deps
            "language_patterns",          # no deps (Sprint 3)
            "multimodal_perception",      # no deps (Sprint 2)
            "basic_psychology",           # no deps
            "communication_skills",       # no deps
            "elder_care_knowledge",       # depends on basic_psychology
            "elder_care_skills",          # depends on elder_care_knowledge
            "company_loneliness_knowledge",  # depends on basic_psychology + communication_skills
            "b2c_assistant_growth",       # depends on basic_psychology
        ]
        results = []
        for name in order:
            r = manager.load(name)
            results.append((name, r.success, r.entries_loaded))
        
        # Todas deben cargar
        for name, ok, _ in results:
            assert ok, f"Failed to load {name}"
        
        assert len(manager.list_loaded()) == 15

    def test_load_pharmacy_increases_memory_entries(self):
        """Cargar pharmacy_interactions inyecta entries."""
        manager = CapsuleManager(organism=None)
        result = manager.load("pharmacy_interactions")
        assert result.success
        assert result.entries_loaded >= 20  # 20 semantic + 8 causal = 28, pero contamos solo semánticas en standalone

    def test_load_research_methodology(self):
        """research_methodology carga correctamente."""
        manager = CapsuleManager(organism=None)
        result = manager.load("research_methodology")
        assert result.success
        assert result.entries_loaded > 0

    def test_load_base_ethics(self):
        """base_ethics carga correctamente."""
        manager = CapsuleManager(organism=None)
        result = manager.load("base_ethics")
        assert result.success
        assert result.entries_loaded >= 20  # 20 semantic + 14 ethical

    def test_dependencies_pharmacy_no_deps(self):
        """pharmacy_interactions no tiene dependencias (se carga standalone)."""
        from zoe.capsules.registry import CapsuleRegistry
        registry = CapsuleRegistry()
        meta = registry.get("pharmacy_interactions")
        assert meta.depends_on == []


# ============================================================
# 4. Endpoint /api/capsules/{name}/validate (validación lógica)
# ============================================================

class TestCapsuleValidateLogic:

    def test_validate_pharmacy_returns_valid(self):
        """Validar pharmacy_interactions pasa."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("pharmacy_interactions")
        assert cap is not None
        assert cap.total_entries > 0

    def test_validate_research_methodology(self):
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("research_methodology")
        assert cap is not None
        assert cap.validators is not None

    def test_validate_federation_b2b_skills(self):
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("federation_b2b_skills")
        assert cap is not None
        assert len(cap.procedural_skills) >= 2

    def test_validate_elder_care_skills_has_tools_dir(self):
        """elder_care_skills tiene directorio tools con archivos .py."""
        from pathlib import Path
        cap_path = Path(__file__).parent.parent / "capsules" / "elder_care_skills" / "tools"
        assert cap_path.exists()
        tools = list(cap_path.glob("*.py"))
        # Al menos routine_tracker.py
        assert any("routine_tracker" in t.name for t in tools)

    def test_validate_elder_care_skills_has_prompts(self):
        """elder_care_skills tiene prompts."""
        from pathlib import Path
        prompts_path = Path(__file__).parent.parent / "capsules" / "elder_care_skills" / "prompts"
        assert prompts_path.exists()
        prompts = list(prompts_path.glob("*.md"))
        assert len(prompts) >= 2  # system_caretaker.md + emergency_protocol.md

    def test_validate_all_12_capsules_schema(self):
        """Las 12 cápsulas pasan schema validation."""
        from zoe.capsules.schema import validate_capsule_yaml
        import yaml
        from pathlib import Path
        
        capsules_dir = Path(__file__).parent.parent / "capsules"
        for cap_dir in capsules_dir.iterdir():
            if not cap_dir.is_dir() or not (cap_dir / "capsule.yaml").exists():
                continue
            with open(cap_dir / "capsule.yaml") as f:
                data = yaml.safe_load(f)
            if "capsule" in data and "name" not in data:
                data = data["capsule"]
            errors = validate_capsule_yaml(data)
            assert errors == [], f"{cap_dir.name} invalid: {errors}"

    def test_validate_capsule_hash_deterministic(self):
        """El hash de contenido es determinista."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("base_ethics")
        h1 = loader.compute_content_hash(cap)
        h2 = loader.compute_content_hash(cap)
        assert h1 == h2
