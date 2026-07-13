"""
Tests Sprint 3 — PatternSpeaker + .zoe format

Valida que ZOE puede generar lenguaje sin LLM y empaquetarse en .zoe.
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from unittest.mock import MagicMock

from zoe.peripherals.pattern_speaker import (
    PatternPeripheral,
    classify_intent,
    INTENT_KEYWORDS,
    RESPONSE_TEMPLATES,
)
from zoe.core.zoe_packager import ZoePackager, ZoePackageManifest


# ============================================================
# 1. Intent classification
# ============================================================

class TestIntentClassification:

    def test_classify_greeting(self):
        assert classify_intent("Hola, ¿cómo estás?") == "greeting"

    def test_classify_greeting_english(self):
        assert classify_intent("Hello, how are you?") == "greeting"

    def test_classify_farewell(self):
        assert classify_intent("Adiós, hasta luego") == "farewell"

    def test_classify_gratitude(self):
        assert classify_intent("Muchas gracias por todo") == "gratitude"

    def test_classify_identity(self):
        assert classify_intent("¿Quién eres?") == "identity"

    def test_classify_wellbeing(self):
        assert classify_intent("¿Cómo estás?") == "wellbeing"

    def test_classify_emotion_sad(self):
        assert classify_intent("Me siento muy triste") == "emotion"

    def test_classify_emotion_happy(self):
        assert classify_intent("Estoy muy feliz") == "emotion"

    def test_classify_question(self):
        assert classify_intent("¿Qué es la memoria episódica?") == "question"

    def test_classify_statement(self):
        """Texto sin keywords → statement."""
        assert classify_intent("El cielo es azul hoy") == "statement"


# ============================================================
# 2. PatternPeripheral — generación sin LLM
# ============================================================

class TestPatternPeripheral:

    def test_creation(self):
        """Se puede crear PatternPeripheral."""
        llm = PatternPeripheral()
        assert llm.name == "pattern"

    def test_generate_returns_string(self):
        """generate() devuelve string."""
        import asyncio
        llm = PatternPeripheral()
        result = asyncio.run(llm.generate("Hola"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_greeting(self):
        """Saludo devuelve respuesta de greeting."""
        import asyncio
        llm = PatternPeripheral()
        result = asyncio.run(llm.generate("Hola"))
        # Debe contener algo de los templates de greeting
        assert len(result) > 5

    def test_generate_identity(self):
        """Pregunta de identidad devuelve respuesta correcta."""
        import asyncio
        llm = PatternPeripheral()
        result = asyncio.run(llm.generate("¿Quién eres?"))
        assert "ZOE" in result or "organismo" in result.lower()

    def test_generate_health_check(self):
        """health_check siempre devuelve True (no depende de servicios)."""
        import asyncio
        llm = PatternPeripheral()
        result = asyncio.run(llm.health_check())
        assert result is True

    def test_generate_streaming(self):
        """generate_streaming funciona."""
        import asyncio
        llm = PatternPeripheral()
        tokens = []
        async def collect():
            async for token in llm.generate_streaming("Hola"):
                tokens.append(token)
        asyncio.run(collect())
        assert len(tokens) > 0
        assert all(isinstance(t, str) for t in tokens)

    def test_generate_deterministic(self):
        """Con temperature=0, respuesta determinista."""
        import asyncio
        llm = PatternPeripheral()
        r1 = asyncio.run(llm.generate("Hola", temperature=0))
        r2 = asyncio.run(llm.generate("Hola", temperature=0))
        assert r1 == r2

    def test_generate_with_memory(self):
        """Con memoria, puede reusar respuestas."""
        import asyncio
        mock_memory = MagicMock()
        mock_entry = MagicMock()
        mock_entry.content = "Respuesta desde memoria"
        mock_entry.similarity = 0.9
        mock_memory.search = MagicMock(return_value=[mock_entry])

        llm = PatternPeripheral(memory=mock_memory)
        result = asyncio.run(llm.generate("Hola, ¿cómo estás?"))
        assert "memoria" in result.lower()
        assert llm._memory_reused == 1

    def test_get_stats(self):
        """Stats del PatternPeripheral."""
        import asyncio
        llm = PatternPeripheral()
        asyncio.run(llm.generate("Hola"))
        stats = llm.get_stats()
        assert stats["response_count"] == 1
        assert stats["templates_used"] + stats["memory_reused"] == 1

    def test_supports_streaming(self):
        """supports_streaming es True."""
        llm = PatternPeripheral()
        assert llm.supports_streaming is True


# ============================================================
# 3. Language patterns capsule
# ============================================================

class TestLanguagePatternsCapsule:

    def test_capsule_exists(self):
        """La cápsula language_patterns existe."""
        assert os.path.exists("zoe/capsules/language_patterns/capsule.yaml")

    def test_capsule_loads(self):
        """La cápsula se carga correctamente."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("language_patterns")
        assert cap is not None
        assert cap.meta.name == "language_patterns"

    def test_capsule_has_semantic_memory(self):
        """Tiene memoria semántica."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("language_patterns")
        assert len(cap.semantic_memory) > 0

    def test_capsule_has_validators(self):
        """Tiene validators."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("language_patterns")
        assert cap.validators is not None

    def test_validator_blocks_human_claim(self):
        """Validator bloquea afirmaciones de ser humano."""
        from zoe.capsules.loader import CapsuleLoader
        loader = CapsuleLoader()
        cap = loader._load_capsule("language_patterns")
        result = cap.validators.validate_response("Soy humano de verdad", {})
        assert result["valid"] is False


# ============================================================
# 4. ZoePackager — formato .zoe
# ============================================================

class TestZoePackager:

    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp(prefix="zoe_test_")
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_creation(self):
        """Se puede crear ZoePackager."""
        packager = ZoePackager()
        assert packager is not None

    def test_package_creates_file(self, temp_dir):
        """package() crea un archivo .zoe."""
        packager = ZoePackager()
        output = os.path.join(temp_dir, "test.zoe")
        result = packager.package(
            output_path=output,
            organism_id="zoe_test",
            description="Test organism",
        )
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_package_with_capsules(self, temp_dir):
        """Empaqueta cápsulas correctamente."""
        packager = ZoePackager()
        output = os.path.join(temp_dir, "test.zoe")
        packager.package(
            output_path=output,
            organism_id="zoe_test",
            capsules_dir="zoe/capsules",
        )
        assert os.path.exists(output)

    def test_unpackage_extracts(self, temp_dir):
        """unpackage() extrae el contenido."""
        packager = ZoePackager()
        # Crear .zoe
        zoe_path = os.path.join(temp_dir, "test.zoe")
        packager.package(
            output_path=zoe_path,
            organism_id="zoe_test",
            capsules_dir="zoe/capsules",
        )
        # Desempaquetar
        extract_dir = os.path.join(temp_dir, "extracted")
        manifest = packager.unpackage(zoe_path, extract_dir)
        assert manifest.organism_id == "zoe_test"
        assert manifest.has_capsules is True
        assert manifest.capsule_count > 0

    def test_inspect_without_extracting(self, temp_dir):
        """inspect() lee manifest sin extraer."""
        packager = ZoePackager()
        zoe_path = os.path.join(temp_dir, "test.zoe")
        packager.package(
            output_path=zoe_path,
            organism_id="zoe_inspect_test",
            description="Test inspect",
        )
        manifest = packager.inspect(zoe_path)
        assert manifest.organism_id == "zoe_inspect_test"
        assert manifest.description == "Test inspect"

    def test_manifest_has_format_version(self, temp_dir):
        """Manifest tiene versión de formato."""
        packager = ZoePackager()
        zoe_path = os.path.join(temp_dir, "test.zoe")
        packager.package(output_path=zoe_path, organism_id="test")
        manifest = packager.inspect(zoe_path)
        assert manifest.format_version == "1.0"

    def test_package_with_memory(self, temp_dir):
        """Empaqueta memoria SQLite."""
        import sqlite3
        # Crear DB de test
        db_path = os.path.join(temp_dir, "test_memory.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS semantic (id TEXT, fact TEXT)")
        conn.execute("INSERT INTO semantic VALUES ('1', 'test fact')")
        conn.commit()
        conn.close()

        packager = ZoePackager()
        zoe_path = os.path.join(temp_dir, "test.zoe")
        packager.package(
            output_path=zoe_path,
            organism_id="zoe_test",
            memory_db=db_path,
        )
        manifest = packager.inspect(zoe_path)
        assert manifest.has_memory is True
        assert manifest.memory_entries >= 1

    def test_get_stats(self):
        """get_stats del packager."""
        packager = ZoePackager()
        stats = packager.get_stats()
        assert stats["format_version"] == "1.0"
        assert ".zoe" in stats["supported_extensions"]

    def test_roundtrip_preserves_organism_id(self, temp_dir):
        """Roundtrip package → unpackage preserves organism_id."""
        packager = ZoePackager()
        zoe_path = os.path.join(temp_dir, "roundtrip.zoe")
        packager.package(
            output_path=zoe_path,
            organism_id="zoe_roundtrip_v1",
            capsules_dir="zoe/capsules",
        )
        extract_dir = os.path.join(temp_dir, "extracted")
        manifest = packager.unpackage(zoe_path, extract_dir)
        assert manifest.organism_id == "zoe_roundtrip_v1"

    def test_capsule_count_correct(self, temp_dir):
        """El conteo de cápsulas es correcto."""
        packager = ZoePackager()
        zoe_path = os.path.join(temp_dir, "test.zoe")
        packager.package(
            output_path=zoe_path,
            organism_id="test",
            capsules_dir="zoe/capsules",
        )
        manifest = packager.inspect(zoe_path)
        # Debe tener al menos 13 cápsulas (las operativas + multimodal + language_patterns)
        assert manifest.capsule_count >= 13
