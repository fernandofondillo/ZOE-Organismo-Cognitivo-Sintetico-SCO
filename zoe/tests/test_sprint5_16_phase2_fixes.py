"""
Sprint 5.16 F2.1-F2.6 — Tests de los fixes de Fase 2 (errores importantes).

F2.1: L0_REFLEX classification bug
F2.2: Pagination en /memory
F2.3: File upload limits
F2.4: Argument injection prevention in capsules
F2.5: Version unification
F2.6: Async SQLite ops
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest


# ============================================================
# F2.1: L0_REFLEX classification bug
# ============================================================

class TestF21L0ReflexClassification:
    """Sprint 5.16 F2.1 — 'no me gusta' NO debe clasificarse como L0_REFLEX."""

    def test_no_me_gusta_not_l0(self):
        """'no me gusta' debe ser L1+ no L0_REFLEX."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("no me gusta")
        assert result.level.value != "L0_REFLEX", \
            f"'no me gusta' should NOT be L0_REFLEX, got {result.level.value}"

    def test_si_pero_estoy_triste_not_l0(self):
        """'si, pero estoy triste' debe ser L1+ no L0_REFLEX."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("si, pero estoy triste")
        assert result.level.value != "L0_REFLEX", \
            f"'si, pero estoy triste' should NOT be L0_REFLEX, got {result.level.value}"

    def test_no_entiendo_not_l0(self):
        """'no entiendo esto' debe ser L1+ no L0_REFLEX."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("no entiendo esto")
        assert result.level.value != "L0_REFLEX"

    def test_single_word_no_is_l0(self):
        """'no' como unica palabra SI debe ser L0_REFLEX."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("no")
        assert result.level.value == "L0_REFLEX"

    def test_single_word_si_is_l0(self):
        """'si' como unica palabra SI debe ser L0_REFLEX."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("si")
        assert result.level.value == "L0_REFLEX"

    def test_hola_still_l0(self):
        """'hola' sigue siendo L0_REFLEX (strict token)."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("hola")
        assert result.level.value == "L0_REFLEX"

    def test_hola_zoe_still_l0(self):
        """'hola zoe' sigue siendo L0_REFLEX (strict token + short)."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("hola zoe")
        assert result.level.value == "L0_REFLEX"

    def test_l0_tokens_separated(self):
        """_L0_TOKENS_STRICT y _L0_TOKENS_AMBIGUOUS existen como sets separados."""
        from zoe.core.depth_classifier import _L0_TOKENS_STRICT, _L0_TOKENS_AMBIGUOUS
        assert isinstance(_L0_TOKENS_STRICT, set)
        assert isinstance(_L0_TOKENS_AMBIGUOUS, set)
        # "no", "si", "sí" deben estar en AMBIGUOUS, no en STRICT
        assert "no" in _L0_TOKENS_AMBIGUOUS
        assert "si" in _L0_TOKENS_AMBIGUOUS
        assert "no" not in _L0_TOKENS_STRICT
        # "hola", "gracias" deben estar en STRICT
        assert "hola" in _L0_TOKENS_STRICT
        assert "gracias" in _L0_TOKENS_STRICT


# ============================================================
# F2.2: Pagination en /memory
# ============================================================

class TestF22MemoryPagination:
    """Sprint 5.16 F2.2 — /memory soporta limit/offset."""

    def test_memory_handler_accepts_limit_offset(self):
        """El handler _handle_memory acepta limit y offset params."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "core.py"
        content = handler_path.read_text()
        assert 'request.query.get("limit"' in content, \
            "handler must accept limit param"
        assert 'request.query.get("offset"' in content, \
            "handler must accept offset param"
        assert "has_more" in content, \
            "handler must return has_more field"

    def test_memory_handler_caps_limit(self):
        """El handler debe cappear limit a 200 maximo."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "core.py"
        content = handler_path.read_text()
        assert "min(limit, 200)" in content or "min(limit,200)" in content, \
            "handler must cap limit to 200"


# ============================================================
# F2.3: File upload limits
# ============================================================

class TestF23FileUploadLimits:
    """Sprint 5.16 F2.3 — File upload con limites de seguridad."""

    def test_feed_handler_has_max_file_size(self):
        """El handler _handle_feed_upload debe tener MAX_FILE_SIZE."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        content = handler_path.read_text()
        assert "MAX_FILE_SIZE" in content, \
            "handler must define MAX_FILE_SIZE"
        assert "10 * 1024 * 1024" in content, \
            "MAX_FILE_SIZE must be 10MB"

    def test_feed_handler_has_filename_sanitization(self):
        """El handler debe sanitizar filename (path traversal prevention)."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        content = handler_path.read_text()
        assert "os.path.basename" in content, \
            "handler must use os.path.basename for filename sanitization"

    def test_feed_handler_has_extension_whitelist(self):
        """El handler debe validar extensiones permitidas."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        content = handler_path.read_text()
        assert "ALLOWED_EXTENSIONS" in content, \
            "handler must have ALLOWED_EXTENSIONS whitelist"

    def test_feed_handler_returns_413_for_large_files(self):
        """El handler debe retornar 413 para archivos > 10MB."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "chat.py"
        content = handler_path.read_text()
        assert "413" in content, \
            "handler must return 413 for files exceeding MAX_FILE_SIZE"


# ============================================================
# F2.4: Argument injection prevention
# ============================================================

class TestF24ArgumentInjectionPrevention:
    """Sprint 5.16 F2.4 — Validacion de name para prevenir argument injection."""

    def test_capsule_validate_handler_validates_name(self):
        """El handler _handle_capsule_validate debe validar name."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "capsules.py"
        content = handler_path.read_text()
        assert "invalid_capsule_name" in content, \
            "handler must reject invalid capsule names"

    def test_capsule_create_handler_validates_all_fields(self):
        """El handler _handle_capsule_create debe validar todos los campos."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "capsules.py"
        content = handler_path.read_text()
        assert "_SAFE_PATTERN" in content, \
            "handler must define _SAFE_PATTERN for field validation"

    def test_name_must_start_with_letter(self):
        """El name debe empezar con letra (no '-' que seria flag injection)."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "capsules.py"
        content = handler_path.read_text()
        assert r'^[a-zA-Z][a-zA-Z0-9_-]*$' in content, \
            "handler must require name to start with letter"


# ============================================================
# F2.5: Version unification
# ============================================================

class TestF25VersionUnification:
    """Sprint 5.16 F2.5 — Version unificada en todo el proyecto."""

    def test_setup_py_version_is_2_1_2(self):
        """setup.py debe tener version 2.1.2."""
        setup_path = Path(__file__).parent.parent.parent / "setup.py"
        content = setup_path.read_text()
        assert 'version="2.1.2"' in content, \
            "setup.py must have version='2.1.2'"

    def test_init_py_version_is_2_1_2(self):
        """zoe/__init__.py debe tener __version__ = '2.1.2'."""
        import zoe
        assert zoe.__version__ == "2.1.2", \
            f"zoe.__version__ must be '2.1.2', got '{zoe.__version__}'"

    def test_readme_badge_version_is_2_1_2(self):
        """README.md badge debe decir version-2.1.2."""
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        content = readme_path.read_text()
        assert "version-2.1.2" in content, \
            "README badge must show version-2.1.2"


# ============================================================
# F2.6: Async SQLite ops
# ============================================================

class TestF26AsyncSqlite:
    """Sprint 5.16 F2.6 — SQLite ops no bloquean el event loop."""

    def test_health_handler_uses_asyncio_to_thread(self):
        """El handler /health debe usar asyncio.to_thread para SQLite."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = handler_path.read_text()
        assert "asyncio.to_thread" in content, \
            "health handler must use asyncio.to_thread for SQLite ops"

    def test_ready_handler_uses_asyncio_to_thread(self):
        """El handler /ready debe usar asyncio.to_thread para SQLite."""
        handler_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = handler_path.read_text()
        # Debe haber al menos 2 usos de asyncio.to_thread (health + ready)
        assert content.count("asyncio.to_thread") >= 2, \
            "health.py must use asyncio.to_thread at least twice (health + ready)"
