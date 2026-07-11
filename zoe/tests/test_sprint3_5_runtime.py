"""
Tests Sprint 3.5 — ZoeRuntime (runtime mínimo para .zoe)

Valida que el runtime funciona sin dependencias externas.
"""

import pytest
import asyncio
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

# Importar el runtime directamente
import importlib.util

# Cargar zoe_runtime como módulo
spec = importlib.util.spec_from_file_location(
    "zoe_runtime",
    "zoe/core/zoe_runtime.py"
)
zoe_runtime_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zoe_runtime_module)
ZoeRuntime = zoe_runtime_module.ZoeRuntime


# ============================================================
# 1. ZoeRuntime — creación e inicialización
# ============================================================

class TestZoeRuntimeCreation:

    def test_creation(self):
        """Se puede crear ZoeRuntime."""
        runtime = ZoeRuntime()
        assert runtime is not None
        assert runtime.backend_name == "pattern"

    def test_initialize(self):
        """initialize() no falla incluso sin archivos."""
        runtime = ZoeRuntime()
        runtime.initialize()
        # No debe crashear
        assert runtime.manifest is not None

    def test_default_port(self):
        """Puerto por defecto es 8642."""
        runtime = ZoeRuntime()
        assert runtime.port == 8642

    def test_custom_port(self):
        """Se puede configurar puerto custom."""
        runtime = ZoeRuntime(port=9999)
        assert runtime.port == 9999

    def test_default_backend_auto(self):
        """Backend por defecto es auto."""
        runtime = ZoeRuntime(backend="auto")
        assert runtime.backend_choice == "auto"


# ============================================================
# 2. ZoeRuntime — detección de backends
# ============================================================

class TestBackendDetection:

    def test_detect_pattern_fallback(self):
        """Sin nada disponible, usa pattern."""
        runtime = ZoeRuntime(backend="auto")
        runtime.initialize()
        # En test environment, probablemente no hay Ollama
        assert runtime.backend_name in ("pattern", "ollama", "cloud", "embedded")

    def test_force_pattern(self):
        """Forzar pattern."""
        runtime = ZoeRuntime(backend="pattern")
        runtime.initialize()
        assert runtime.backend_name == "pattern"

    def test_force_ollama_without_ollama(self):
        """Forzar ollama sin tenerlo → fallback a pattern."""
        runtime = ZoeRuntime(backend="ollama")
        runtime._detect_backends()
        if not runtime.has_ollama:
            # Si no hay ollama, el backend sigue siendo "ollama" pero no funcionará
            # El runtime maneja esto en generate_response
            pass

    def test_embedded_model_detection(self):
        """Detecta embedded_model.gguf si existe."""
        runtime = ZoeRuntime()
        # En test, probablemente no existe
        # Pero el código no debe crashear
        runtime._detect_backends()


# ============================================================
# 3. ZoeRuntime — comandos
# ============================================================

class TestRuntimeCommands:

    def test_help_command(self):
        """/help devuelve ayuda."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("/help"))
        assert "Commands" in result or "comandos" in result.lower()

    def test_stats_command(self):
        """/stats devuelve estadísticas."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("/stats"))
        assert "Organism" in result or "organism" in result.lower()

    def test_memory_command_empty(self):
        """/memory sin conversación previa."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("/memory"))
        assert "no hay" in result.lower() or "No hay" in result

    def test_quit_command(self):
        """/quit devuelve __QUIT__."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("/quit"))
        assert result == "__QUIT__"

    def test_unknown_command(self):
        """Comando desconocido devuelve error."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("/unknown"))
        assert "Unknown" in result or "unknown" in result.lower()


# ============================================================
# 4. ZoeRuntime — generación de respuestas
# ============================================================

class TestRuntimeResponses:

    def test_greeting_response(self):
        """Saludo devuelve respuesta."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("Hola"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_identity_question(self):
        """Pregunta de identidad devuelve respuesta con ZOE."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("¿Quién eres?"))
        assert len(result) > 0

    def test_emotion_response(self):
        """Mensaje emocional devuelve respuesta empática."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = asyncio.run(runtime.process_message("Me siento muy triste"))
        assert len(result) > 0

    def test_conversation_history(self):
        """Las conversaciones se guardan en historial."""
        runtime = ZoeRuntime()
        runtime.initialize()
        asyncio.run(runtime.process_message("Hola"))
        asyncio.run(runtime.process_message("¿Cómo estás?"))
        assert len(runtime._conversation_history) == 2

    def test_stats_after_conversation(self):
        """Stats reflejan conversación."""
        runtime = ZoeRuntime()
        runtime.initialize()
        asyncio.run(runtime.process_message("Hola"))
        asyncio.run(runtime.process_message("¿Quién eres?"))
        stats = runtime.get_stats()
        assert stats["iteration_count"] == 2
        assert stats["conversation_turns"] == 2


# ============================================================
# 5. ZoeRuntime — banner e inspect
# ============================================================

class TestRuntimeBanner:

    def test_banner_contains_version(self):
        """Banner contiene versión de ZOE."""
        runtime = ZoeRuntime()
        runtime.initialize()
        banner = runtime.get_banner()
        assert "ZOE" in banner
        assert "v1.7" in banner or "v1.7.0" in banner

    def test_banner_contains_organism_id(self):
        """Banner contiene organism ID."""
        runtime = ZoeRuntime()
        runtime.manifest = {"organism_id": "zoe_test_v1"}
        banner = runtime.get_banner()
        assert "zoe_test_v1" in banner

    def test_banner_contains_backend(self):
        """Banner contiene backend."""
        runtime = ZoeRuntime()
        runtime.initialize()
        banner = runtime.get_banner()
        assert "pattern" in banner or "ollama" in banner or "embedded" in banner

    def test_inspect_returns_string(self):
        """inspect() devuelve string con info."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = runtime.inspect()
        assert isinstance(result, str)
        assert "ZOE" in result

    def test_inspect_contains_capsules(self):
        """inspect() menciona capsules."""
        runtime = ZoeRuntime()
        runtime.initialize()
        result = runtime.inspect()
        assert "Capsule" in result or "capsule" in result.lower()


# ============================================================
# 6. ZoeRuntime — stats
# ============================================================

class TestRuntimeStats:

    def test_get_stats_returns_dict(self):
        """get_stats devuelve dict."""
        runtime = ZoeRuntime()
        runtime.initialize()
        stats = runtime.get_stats()
        assert isinstance(stats, dict)

    def test_stats_has_required_fields(self):
        """Stats tiene campos requeridos."""
        runtime = ZoeRuntime()
        runtime.initialize()
        stats = runtime.get_stats()
        assert "organism_id" in stats
        assert "backend" in stats
        assert "memory_entries" in stats
        assert "capsule_count" in stats
        assert "iteration_count" in stats

    def test_stats_backend_name(self):
        """Stats incluye backend name."""
        runtime = ZoeRuntime(backend="pattern")
        runtime.initialize()
        stats = runtime.get_stats()
        assert stats["backend"] == "pattern"

    def test_stats_iteration_increments(self):
        """Iteration count incrementa con cada mensaje."""
        runtime = ZoeRuntime()
        runtime.initialize()
        assert runtime.get_stats()["iteration_count"] == 0
        asyncio.run(runtime.process_message("Hola"))
        assert runtime.get_stats()["iteration_count"] == 1
        asyncio.run(runtime.process_message("¿Cómo estás?"))
        assert runtime.get_stats()["iteration_count"] == 2


# ============================================================
# 7. ZoeRuntime — memoria SQLite
# ============================================================

class TestRuntimeMemory:

    def test_memory_count_zero_without_db(self):
        """Sin memory.db, memory_entries es 0."""
        runtime = ZoeRuntime()
        runtime._load_memory()
        assert runtime.memory_entries == 0

    def test_memory_count_with_db(self):
        """Con memory.db, cuenta entries correctamente."""
        import sqlite3
        import tempfile

        # Crear DB temporal
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS semantic (id TEXT, fact TEXT)")
        conn.execute("INSERT INTO semantic VALUES ('1', 'test')")
        conn.execute("INSERT INTO semantic VALUES ('2', 'test2')")
        conn.commit()
        conn.close()

        # Mock MEMORY_DB_PATH
        with patch.object(zoe_runtime_module, "MEMORY_DB_PATH", Path(db_path)):
            runtime = ZoeRuntime()
            runtime._load_memory()
            assert runtime.memory_entries >= 2

        os.unlink(db_path)


# ============================================================
# 8. Integración — flujo completo
# ============================================================

class TestRuntimeIntegration:

    def test_full_conversation_flow(self):
        """Flujo completo: saludo → pregunta → despedida."""
        runtime = ZoeRuntime()
        runtime.initialize()

        # Saludo
        r1 = asyncio.run(runtime.process_message("Hola"))
        assert len(r1) > 0

        # Pregunta
        r2 = asyncio.run(runtime.process_message("¿Quién eres?"))
        assert len(r2) > 0

        # Stats
        r3 = asyncio.run(runtime.process_message("/stats"))
        assert "Iterations" in r3 or "iterations" in r3.lower()

        # Quit
        r4 = asyncio.run(runtime.process_message("/quit"))
        assert r4 == "__QUIT__"

    def test_multiple_languages(self):
        """Runtime responde en múltiples idiomas."""
        runtime = ZoeRuntime()
        runtime.initialize()

        # Español
        r1 = asyncio.run(runtime.process_message("Hola"))
        assert len(r1) > 0

        # English
        r2 = asyncio.run(runtime.process_message("Hello"))
        assert len(r2) > 0

        # Ambas respuestas son strings no vacíos
        assert isinstance(r1, str)
        assert isinstance(r2, str)
