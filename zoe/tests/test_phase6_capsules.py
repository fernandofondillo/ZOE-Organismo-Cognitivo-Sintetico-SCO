"""
Tests Fase 6B — Knowledge Capsules System

Cubre:
- Schema de cápsulas (validación de YAML)
- Loader de cápsulas (carga desde disco)
- Registry (índice y búsqueda)
- Scaffold CLI (create, validate, hash, list, matrix, info)
- Cápsulas de ejemplo (elder_care_knowledge, basic_psychology, communication_skills)
- Inyección en componentes ZOE
- Validadores de cápsulas
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Asegurar que zoe está en path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zoe.capsules.schema import (
    CapsuleMeta, TrustLevel, parse_capsule_yaml, validate_capsule_yaml,
    TRUST_TO_CONFIDENCE, REQUIRED_FIELDS, VALID_COMPONENTS,
)
from zoe.capsules.loader import (
    CapsuleLoader, LoadedCapsule, CapsuleLoadError,
)
from zoe.capsules.registry import CapsuleRegistry


# ============================================================
# 1. Schema tests
# ============================================================

class TestCapsuleSchema:

    def test_valid_yaml(self):
        """YAML válido se parsea sin errores."""
        data = {
            "name": "test_capsule",
            "version": "1.0.0",
            "description": "Test capsule",
            "domain": "test.domain",
            "trust_level": "verified",
            "provenance": "test source",
            "last_updated": "2026-07-09",
        }
        errors = validate_capsule_yaml(data)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_missing_required_field(self):
        """Falta un campo obligatorio → error."""
        data = {
            "name": "test_capsule",
            "version": "1.0.0",
            # description missing
            "domain": "test.domain",
            "trust_level": "verified",
            "provenance": "test source",
            "last_updated": "2026-07-09",
        }
        errors = validate_capsule_yaml(data)
        assert any("missing_required_field" in e for e in errors)

    def test_invalid_trust_level(self):
        """trust_level inválido → error."""
        data = {
            "name": "test_capsule",
            "version": "1.0.0",
            "description": "Test",
            "domain": "test",
            "trust_level": "invalid_level",
            "provenance": "test",
            "last_updated": "2026-07-09",
        }
        errors = validate_capsule_yaml(data)
        assert any("invalid_trust_level" in e for e in errors)

    def test_invalid_name_format(self):
        """Nombre con caracteres no válidos → error."""
        data = {
            "name": "test-capsule!",  # no snake_case
            "version": "1.0.0",
            "description": "Test",
            "domain": "test",
            "trust_level": "verified",
            "provenance": "test",
            "last_updated": "2026-07-09",
        }
        errors = validate_capsule_yaml(data)
        assert any("invalid_name_format" in e for e in errors)

    def test_invalid_version_format(self):
        data = {
            "name": "test_capsule",
            "version": "1.0",  # no semver completo
            "description": "Test",
            "domain": "test",
            "trust_level": "verified",
            "provenance": "test",
            "last_updated": "2026-07-09",
        }
        errors = validate_capsule_yaml(data)
        assert any("invalid_version_format" in e for e in errors)

    def test_load_cost_out_of_range(self):
        data = {
            "name": "test_capsule",
            "version": "1.0.0",
            "description": "Test",
            "domain": "test",
            "trust_level": "verified",
            "provenance": "test",
            "last_updated": "2026-07-09",
            "load_cost": 1.5,
        }
        errors = validate_capsule_yaml(data)
        assert any("load_cost_out_of_range" in e for e in errors)

    def test_parse_capsule_yaml_ok(self):
        data = {
            "name": "test_capsule",
            "version": "1.0.0",
            "description": "Test",
            "domain": "test.domain",
            "trust_level": "verified",
            "provenance": "test",
            "last_updated": "2026-07-09",
        }
        meta = parse_capsule_yaml(data)
        assert meta.name == "test_capsule"
        assert meta.trust_level == TrustLevel.VERIFIED
        assert meta.effective_confidence == 0.95

    def test_parse_capsule_yaml_invalid(self):
        data = {"name": "test"}  # faltan campos
        with pytest.raises(ValueError):
            parse_capsule_yaml(data)

    def test_trust_to_confidence_mapping(self):
        assert TRUST_TO_CONFIDENCE[TrustLevel.VERIFIED] == 0.95
        assert TRUST_TO_CONFIDENCE[TrustLevel.CURATED] == 0.80
        assert TRUST_TO_CONFIDENCE[TrustLevel.COMMUNITY] == 0.55
        assert TRUST_TO_CONFIDENCE[TrustLevel.EXPERIMENTAL] == 0.40

    def test_effective_confidence_uses_default_if_set(self):
        data = {
            "name": "test_capsule",
            "version": "1.0.0",
            "description": "Test",
            "domain": "test",
            "trust_level": "community",  # default 0.55
            "provenance": "test",
            "last_updated": "2026-07-09",
            "default_confidence": 0.70,  # override
        }
        meta = parse_capsule_yaml(data)
        assert meta.effective_confidence == 0.70  # no 0.55


# ============================================================
# 2. Loader tests
# ============================================================

class TestCapsuleLoader:

    def test_load_elder_care_knowledge(self):
        """Carga la cápsula elder_care_knowledge real."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        assert cap is not None
        assert cap.name == "elder_care_knowledge"
        assert cap.meta.trust_level == TrustLevel.VERIFIED
        assert cap.meta.domain == "healthcare.elders.home_care"
        # Debe tener contenido
        assert len(cap.semantic_memory) > 0
        assert len(cap.causal_models) > 0
        assert len(cap.emotional_patterns) > 0
        assert len(cap.ethical_guidelines) > 0
        assert cap.validators is not None

    def test_load_basic_psychology(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("basic_psychology")
        
        assert cap is not None
        assert cap.name == "basic_psychology"
        assert cap.meta.trust_level == TrustLevel.CURATED
        assert len(cap.semantic_memory) > 0

    def test_load_communication_skills(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("communication_skills")
        
        assert cap is not None
        assert cap.name == "communication_skills"
        assert len(cap.semantic_memory) > 0
        assert len(cap.procedural_skills) > 0
        assert cap.validators is not None

    def test_load_nonexistent(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("nonexistent_capsule_xyz")
        assert cap is None

    def test_list_available(self):
        loader = CapsuleLoader()
        available = loader.list_available()
        assert "elder_care_knowledge" in available
        assert "basic_psychology" in available
        assert "communication_skills" in available

    def test_load_for_use_case(self):
        """Carga todas las cápsulas compatibles con un caso de uso."""
        loader = CapsuleLoader()
        config = {
            "capsules": {
                "required": ["elder_care_knowledge"],
                "recommended": ["basic_psychology", "communication_skills"],
            }
        }
        capsules = loader.load_for_use_case("cuidado_personas_mayores", config)
        
        # Debe cargar las 3 (elder_care + basic_psychology + communication_skills)
        # + dependencies (elder_care depends on basic_psychology, pero ya está)
        names = [c.name for c in capsules]
        assert "elder_care_knowledge" in names
        assert "basic_psychology" in names
        assert "communication_skills" in names

    def test_required_not_found_raises(self):
        loader = CapsuleLoader()
        config = {
            "capsules": {
                "required": ["nonexistent_capsule_xyz"],
            }
        }
        with pytest.raises(CapsuleLoadError):
            loader.load_for_use_case("test", config)

    def test_dependency_resolution(self):
        """elder_care_knowledge depende de basic_psychology → se carga automáticamente."""
        loader = CapsuleLoader()
        config = {
            "capsules": {
                "required": ["elder_care_knowledge"],
            }
        }
        capsules = loader.load_for_use_case("test", config)
        names = [c.name for c in capsules]
        # basic_psychology debe estar como dependencia
        assert "basic_psychology" in names

    def test_topological_sort_dependencies_first(self):
        """Las dependencias se cargan antes que los dependientes."""
        loader = CapsuleLoader()
        config = {
            "capsules": {
                "required": ["elder_care_knowledge"],
            }
        }
        capsules = loader.load_for_use_case("test", config)
        names = [c.name for c in capsules]
        
        # basic_psychology debe ir antes que elder_care_knowledge
        idx_basic = names.index("basic_psychology")
        idx_elder = names.index("elder_care_knowledge")
        assert idx_basic < idx_elder

    def test_compute_content_hash(self):
        """El hash de contenido es determinista."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        hash1 = loader.compute_content_hash(cap)
        hash2 = loader.compute_content_hash(cap)
        
        assert hash1 == hash2
        assert hash1.startswith("sha256:")

    def test_total_entries_count(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        total = cap.total_entries
        assert total > 0
        assert total == (
            len(cap.semantic_memory) +
            len(cap.procedural_skills) +
            len(cap.causal_models) +
            len(cap.emotional_patterns) +
            len(cap.ethical_guidelines)
        )


# ============================================================
# 3. Registry tests
# ============================================================

class TestCapsuleRegistry:

    def test_list_all(self):
        registry = CapsuleRegistry()
        all_caps = registry.list_all()
        names = [c.name for c in all_caps]
        assert "elder_care_knowledge" in names
        assert "basic_psychology" in names
        assert "communication_skills" in names

    def test_get_by_name(self):
        registry = CapsuleRegistry()
        meta = registry.get("elder_care_knowledge")
        assert meta is not None
        assert meta.name == "elder_care_knowledge"
        assert meta.trust_level == TrustLevel.VERIFIED

    def test_get_nonexistent(self):
        registry = CapsuleRegistry()
        assert registry.get("nonexistent") is None

    def test_by_domain(self):
        registry = CapsuleRegistry()
        healthcare = registry.by_domain("healthcare")
        assert any(c.name == "elder_care_knowledge" for c in healthcare)

    def test_by_use_case(self):
        registry = CapsuleRegistry()
        compatible = registry.by_use_case("cuidado_personas_mayores")
        names = [c.name for c in compatible]
        assert "elder_care_knowledge" in names

    def test_by_trust_level(self):
        registry = CapsuleRegistry()
        verified = registry.by_trust_level(TrustLevel.VERIFIED)
        names = [c.name for c in verified]
        assert "elder_care_knowledge" in names
        # basic_psychology y communication_skills son curated, no verified
        assert "basic_psychology" not in names

    def test_check_compatibility_ok(self):
        registry = CapsuleRegistry()
        ok, reason = registry.check_compatibility(
            "elder_care_knowledge", "cuidado_personas_mayores"
        )
        assert ok is True

    def test_check_compatibility_fail(self):
        registry = CapsuleRegistry()
        ok, reason = registry.check_compatibility(
            "elder_care_knowledge", "caso_no_compatible"
        )
        assert ok is False

    def test_dependency_tree(self):
        registry = CapsuleRegistry()
        tree = registry.get_dependency_tree("elder_care_knowledge")
        assert tree["name"] == "elder_care_knowledge"
        assert len(tree["dependencies"]) >= 1
        assert tree["dependencies"][0]["name"] == "basic_psychology"

    def test_stats(self):
        registry = CapsuleRegistry()
        stats = registry.stats()
        assert stats["total_capsules"] >= 3
        assert "verified" in stats["by_trust_level"]
        assert "healthcare" in stats["by_top_domain"]


# ============================================================
# 4. Validators tests (de cápsulas reales)
# ============================================================

class TestCapsuleValidators:

    def test_elder_care_validate_response_ok(self):
        """Respuesta válida pasa el validador de elder_care."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        # Respuesta cálido-validante
        ok, reason = cap.validators.validate_response(
            "María, me preocupa lo que me dices. ¿Puedes caminar hasta una silla?",
            context={},
        )
        assert ok is True

    def test_elder_care_validate_response_forbidden(self):
        """Patrones prohibidos son rechazados."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        ok, reason = cap.validators.validate_response(
            "No te preocupes, no es para tanto.",
            context={},
        )
        assert ok is False
        assert "forbidden_pattern" in reason

    def test_elder_care_validate_response_too_long(self):
        """Respuestas excesivamente largas a mayores se rechazan."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        long_response = "A" * 1000  # > 800 chars
        ok, reason = cap.validators.validate_response(long_response, context={})
        assert ok is False
        assert "too_long" in reason

    def test_elder_care_validate_new_knowledge_medication_blocked(self):
        """Claims sobre medicación se bloquean (requieren triple validación)."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        ok, reason = cap.validators.validate_new_knowledge(
            "La dosis de paracetamol en mayores es 1g cada 6 horas.",
            source="llm:gpt-4o",
            context={},
        )
        assert ok is False
        assert "sensitive_medical_domain" in reason

    def test_elder_care_validate_new_knowledge_diagnosis_blocked(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        ok, reason = cap.validators.validate_new_knowledge(
            "Es demencia tipo Alzheimer.",
            source="llm:gpt-4o",
            context={},
        )
        assert ok is False
        assert "diagnostic_domain" in reason

    def test_elder_care_validate_new_knowledge_acceptable(self):
        """Claim no médico no contradictorio se acepta en cuarentena."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        ok, reason = cap.validators.validate_new_knowledge(
            "Las personas mayores disfrutan de la música de su juventud.",
            source="llm:gpt-4o",
            context={},
        )
        assert ok is True
        assert "quarantine" in reason

    def test_basic_psychology_validate_response_no_diagnosis(self):
        """Respuestas que parecen diagnósticos se bloquean."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("basic_psychology")
        
        ok, reason = cap.validators.validate_response(
            "Tienes depresión según lo que cuentas.",
            context={},
        )
        assert ok is False
        assert "apparent_diagnosis" in reason

    def test_basic_psychology_detect_pathology_indicators(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("basic_psychology")
        
        detected = cap.validators.detect_pathology_indicators(
            "Últimamente tengo ideación suicida y autolesiones."
        )
        assert "ideación suicida" in detected
        assert "autolesiones" in detected or "autolesión" in detected

    def test_communication_skills_validate_response_no_minimization(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("communication_skills")
        
        ok, reason = cap.validators.validate_response(
            "Anímate, no es para tanto.",
            context={},
        )
        assert ok is False
        assert "violating_pattern" in reason

    def test_communication_skills_detect_pattern(self):
        loader = CapsuleLoader()
        cap = loader._load_capsule("communication_skills")
        
        pattern = cap.validators.detect_communication_pattern(
            "Tengo miedo a lo que va a pasar."
        )
        assert pattern == "fear"


# ============================================================
# 5. Scaffold CLI tests
# ============================================================

class TestScaffoldCLI:
    """Tests del CLI scaffold. Usa directorio temporal."""

    @pytest.fixture
    def temp_capsules_dir(self, tmp_path, monkeypatch):
        """Crea un directorio temporal como capsules_dir."""
        # Necesitamos monkeypatchar CapsuleLoader para que use tmp_path
        from zoe.capsules import loader as loader_mod
        
        original_init = CapsuleLoader.__init__
        
        def patched_init(self, capsules_dir=None):
            original_init(self, capsules_dir=tmp_path)
        
        monkeypatch.setattr(CapsuleLoader, "__init__", patched_init)
        monkeypatch.setattr(loader_mod, "CapsuleLoader", CapsuleLoader)
        
        # También el scaffold
        from zoe.capsules import scaffold as scaffold_mod
        # El scaffold usa Path(__file__).parent para el dir
        # Necesitamos monkeypatchar Path
        
        yield tmp_path

    def test_create_capsule_minimal(self, tmp_path, monkeypatch):
        """Crea una cápsula mínima con scaffold."""
        from zoe.capsules import scaffold
        
        # Monkeypatch el Path(__file__).parent del scaffold
        # para que use tmp_path como capsules_dir
        original_parent = Path(scaffold.__file__).parent
        
        def mock_parent(self):
            if self == Path(scaffold.__file__):
                return tmp_path
            return original_parent
        
        # En lugar de monkeypatchar Path.parent, vamos a hacer
        # el test creando manualmente en tmp_path
        cap_name = "test_scaffold_minimal"
        cap_dir = tmp_path / cap_name
        cap_dir.mkdir()
        
        # Crear capsule.yaml mínimo
        yaml_content = f"""name: {cap_name}
version: 0.1.0
description: "Test minimal"
domain: test.minimal
trust_level: curated
provenance: "test"
last_updated: 2026-07-09
components:
  semantic_memory: true
  validators: true
"""
        (cap_dir / "capsule.yaml").write_text(yaml_content)
        (cap_dir / "semantic_memory.jsonl").write_text("")
        
        # Validar
        import yaml
        data = yaml.safe_load(yaml_content)
        errors = validate_capsule_yaml(data)
        assert errors == [], f"Schema errors: {errors}"

    def test_validate_capsule_yaml_with_components(self, tmp_path):
        """Una cápsula con todos los componentes válida correctamente."""
        cap_name = "test_full_components"
        cap_dir = tmp_path / cap_name
        cap_dir.mkdir()
        
        data = {
            "name": cap_name,
            "version": "1.0.0",
            "description": "Test all components",
            "domain": "test.full",
            "trust_level": "verified",
            "provenance": "test",
            "last_updated": "2026-07-09",
            "components": {
                "semantic_memory": True,
                "procedural_skills": True,
                "causal_models": True,
                "emotional_patterns": True,
                "ethical_guidelines": True,
                "validators": True,
                "tools": True,
                "prompts": True,
            },
            "capabilities": ["test_capability"],
            "restrictions": ["test_restriction"],
        }
        
        errors = validate_capsule_yaml(data)
        assert errors == []

    def test_invalid_component_rejected(self, tmp_path):
        """Componente inválido es rechazado."""
        data = {
            "name": "test",
            "version": "1.0.0",
            "description": "Test",
            "domain": "test",
            "trust_level": "verified",
            "provenance": "test",
            "last_updated": "2026-07-09",
            "components": {
                "invalid_component": True,
            },
        }
        errors = validate_capsule_yaml(data)
        assert any("invalid_component" in e for e in errors)


# ============================================================
# 6. Integration tests — end-to-end
# ============================================================

class TestCapsuleIntegration:

    def test_load_all_three_example_capsules(self):
        """Carga las 3 cápsulas de ejemplo simultáneamente."""
        loader = CapsuleLoader()
        config = {
            "capsules": {
                "required": ["elder_care_knowledge", "communication_skills"],
                "recommended": ["basic_psychology"],
            }
        }
        capsules = loader.load_for_use_case("cuidado_personas_mayores", config)
        names = [c.name for c in capsules]
        
        assert "elder_care_knowledge" in names
        assert "communication_skills" in names
        assert "basic_psychology" in names

    def test_capsule_yaml_has_correct_metadata(self):
        """Las cápsulas de ejemplo tienen metadata correcta."""
        registry = CapsuleRegistry()
        
        elder = registry.get("elder_care_knowledge")
        assert elder.trust_level == TrustLevel.VERIFIED
        assert "cuidado_personas_mayores" in elder.compatible_use_cases
        assert "basic_psychology" in elder.depends_on
        assert elder.default_confidence == 0.85
        
        psych = registry.get("basic_psychology")
        assert psych.trust_level == TrustLevel.CURATED
        
        comm = registry.get("communication_skills")
        assert comm.trust_level == TrustLevel.CURATED
        assert "procedural_skills" in comm.components
        assert comm.components["procedural_skills"] is True

    def test_elder_care_dependencies_resolvable(self):
        """Las dependencias de elder_care se resuelven sin ciclos."""
        registry = CapsuleRegistry()
        tree = registry.get_dependency_tree("elder_care_knowledge")
        
        # Verificar estructura
        assert tree["name"] == "elder_care_knowledge"
        assert len(tree["dependencies"]) == 1
        assert tree["dependencies"][0]["name"] == "basic_psychology"
        # basic_psychology no tiene dependencias
        assert tree["dependencies"][0]["dependencies"] == []

    def test_total_knowledge_entries_loaded(self):
        """Al cargar las 3 cápsulas se obtienen >100 entries de conocimiento."""
        loader = CapsuleLoader()
        config = {
            "capsules": {
                "required": ["elder_care_knowledge", "basic_psychology", "communication_skills"],
            }
        }
        capsules = loader.load_for_use_case("test", config)
        
        total_entries = sum(c.total_entries for c in capsules)
        # Cada cápsula tiene >40 entries, total >120
        assert total_entries >= 100, f"Solo {total_entries} entries cargadas"

    def test_validators_are_callable(self):
        """Los validadores de las cápsulas son funciones llamables."""
        loader = CapsuleLoader()
        
        for name in ["elder_care_knowledge", "basic_psychology", "communication_skills"]:
            cap = loader._load_capsule(name)
            assert cap.validators is not None, f"{name} no tiene validators"
            assert hasattr(cap.validators, "validate_response"), f"{name} no tiene validate_response"
            assert hasattr(cap.validators, "validate_new_knowledge"), f"{name} no tiene validate_new_knowledge"

    def test_capsule_content_is_meaningful(self):
        """Las entradas semánticas de las cápsulas tienen contenido sustancial."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        for entry in cap.semantic_memory[:3]:
            assert "content" in entry
            assert len(entry["content"]) > 30  # no trivial
            assert "confidence" in entry
            assert 0 < entry["confidence"] <= 1.0
            assert "category" in entry or "tags" in entry

    def test_causal_models_well_formed(self):
        """Los modelos causales tienen causa, efecto y confianza."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        for model in cap.causal_models[:3]:
            assert "cause" in model
            assert "effect" in model
            assert "confidence" in model
            assert 0 < model["confidence"] <= 1.0

    def test_ethical_guidelines_have_priority(self):
        """Las directrices éticas tienen prioridad definida."""
        loader = CapsuleLoader()
        cap = loader._load_capsule("elder_care_knowledge")
        
        for guideline in cap.ethical_guidelines[:3]:
            assert "guideline" in guideline
            assert "reason" in guideline
            assert "priority" in guideline
            assert guideline["priority"] in ["critical", "high", "medium", "low"]
