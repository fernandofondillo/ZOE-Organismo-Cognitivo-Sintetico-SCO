"""
Sprint 5.13 B1-B8 — Tests de los 8 fixes criticos de produccion.

Cada test verifica un fix especifico:
- B1: loop._storage_backend UnboundLocalError (postgres path)
- B2: ReflectionEngine cableado en cli_chat
- B3: mentor.evaluate_thought SIN await (sync)
- B4: serve.py sirve HTTP en /health, /ready, /live, /metrics
- B4-bis: thoughts y conversation_history bounded (deque maxlen)
- B5: k8s/secret.yaml NO en git, .example SI
- B6: token NO aparece en logs ni stdout
- B7: hmac.compare_digest en auth middleware (timing-safe)
- B8: tests rotos arreglados (postgres skipif, Proposal(action=), hardware handlers, PWA manifest, v4 thoughts)
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ============================================================
# B1: loop._storage_backend UnboundLocalError fixed
# ============================================================

class TestB1StorageBackendFix:
    """Sprint 5.13 B1 — El UnboundLocalError cuando storage_type=postgres esta corregido."""

    def test_storage_backend_assignment_is_after_loop_creation(self):
        """La asignacion loop._storage_backend = storage_backend debe estar
        DESPUES de la creacion del loop, no antes."""
        cli_chat_path = Path(__file__).parent.parent / "cli_chat.py"
        content = cli_chat_path.read_text()
        # Buscar la posicion de 'loop = CognitiveLoopV5(' y 'loop._storage_backend'
        loop_creation_pos = content.find("loop = CognitiveLoopV5(")
        # Buscar la ASIGNACION real (no el comentario). Debe estar en una linea
        # que empiece con whitespace + 'loop._storage_backend = storage_backend'
        # y NO contenga '#' al inicio.
        storage_assign_pos = -1
        for line in content.split('\n'):
            stripped = line.lstrip()
            if stripped == "loop._storage_backend = storage_backend" and not stripped.startswith('#'):
                storage_assign_pos = content.find('\n' + line + '\n')
                break
        assert loop_creation_pos > 0, "loop = CognitiveLoopV5( must exist"
        assert storage_assign_pos > 0, \
            "loop._storage_backend = storage_backend assignment must exist (not in a comment)"
        assert storage_assign_pos > loop_creation_pos, \
            f"storage_backend assignment (pos {storage_assign_pos}) must be AFTER loop creation (pos {loop_creation_pos})"

    def test_zoechat_initializes_without_unbound_local_error(self):
        """Al inicializar ZoeChat con sqlite (default), no debe haber UnboundLocalError.

        Sprint 5.14: este test es sync (verifica codigo fuente) para evitar
        contaminacion del event loop con asyncio.run() que rompia otros tests.
        El test runtime esta cubierto por TestB2::test_zoechat_has_reflection_engine_after_init
        que si usa @pytest.mark.asyncio correctamente.
        """
        from pathlib import Path
        cli_chat_path = Path(__file__).parent.parent / "cli_chat.py"
        content = cli_chat_path.read_text()
        loop_creation_pos = content.find("loop = CognitiveLoopV5(")
        storage_assign_pos = -1
        for line in content.split('\n'):
            stripped = line.lstrip()
            if stripped == "loop._storage_backend = storage_backend" and not stripped.startswith('#'):
                storage_assign_pos = content.find('\n' + line + '\n')
                break
        assert loop_creation_pos > 0
        assert storage_assign_pos > loop_creation_pos, \
            "storage_backend assignment must be AFTER loop creation to avoid UnboundLocalError"


# ============================================================
# B2: ReflectionEngine wired in cli_chat
# ============================================================

class TestB2ReflectionEngineWired:
    """Sprint 5.13 B2 — ReflectionEngine esta cableado en cli_chat, no solo en tests."""

    def test_cli_chat_imports_reflection_engine(self):
        """cli_chat.py debe importar e instanciar ReflectionEngine."""
        cli_chat_path = Path(__file__).parent.parent / "cli_chat.py"
        content = cli_chat_path.read_text()
        assert "from .core.reflection_engine import ReflectionEngine" in content, \
            "cli_chat.py must import ReflectionEngine"
        assert "ReflectionEngine(" in content, \
            "cli_chat.py must instantiate ReflectionEngine"
        assert "attach_reflection_hook" in content, \
            "cli_chat.py must call metabolism.attach_reflection_hook"

    @pytest.mark.asyncio
    async def test_zoechat_has_reflection_engine_after_init(self):
        """Al inicializar ZoeChat, reflection_engine debe estar cableado al metabolism.

        Sprint 5.14: usa @pytest.mark.asyncio en vez de asyncio.run() para
        evitar contaminacion del event loop que rompia otros tests.
        """
        from zoe.cli_chat import ZoeChat

        db_path = tempfile.mktemp(suffix=".db")
        zc = ZoeChat(backend="mock", db_path=db_path)
        await zc.initialize()
        try:
            assert zc.reflection_engine is not None, "reflection_engine must be wired"
            assert zc.metabolism._reflection_hook is not None, \
                "metabolism must have _reflection_hook attached"
        finally:
            await zc.shutdown()


# ============================================================
# B3: mentor.evaluate_thought SIN await
# ============================================================

class TestB3MentorEvaluateSync:
    """Sprint 5.13 B3 — mentor.evaluate_thought es SINCRONO, no se debe await."""

    def test_no_await_on_evaluate_thought_in_reflection_engine(self):
        """reflection_engine.py no debe hacer 'await self._mentor.evaluate_thought'
        en codigo ejecutable (puede aparecer en comentarios explicativos)."""
        re_path = Path(__file__).parent.parent / "core" / "reflection_engine.py"
        content = re_path.read_text()
        # Buscar lineas que contengan 'await self._mentor.evaluate_thought' y
        # NO sean comentarios (no empiezan con # despues de lstrip).
        for line in content.split('\n'):
            stripped = line.lstrip()
            if 'await self._mentor.evaluate_thought' in stripped and not stripped.startswith('#'):
                pytest.fail(f"Found 'await self._mentor.evaluate_thought' in executable code: {line}")
        # Debe llamarse sin await en codigo ejecutable
        found_sync_call = False
        for line in content.split('\n'):
            stripped = line.lstrip()
            if 'self._mentor.evaluate_thought(insight)' in stripped and not stripped.startswith('#'):
                if 'await' not in stripped:
                    found_sync_call = True
                    break
        assert found_sync_call, \
            "reflection_engine.py must call mentor.evaluate_thought WITHOUT await"

    def test_no_dead_validate_call_in_reflection_engine(self):
        """KnowledgeQuarantine no tiene metodo validate(). El bloque muerto debe estar eliminado."""
        re_path = Path(__file__).parent.parent / "core" / "reflection_engine.py"
        content = re_path.read_text()
        assert "await self._quarantine.validate" not in content, \
            "reflection_engine.py must NOT call quarantine.validate (method doesn't exist)"


# ============================================================
# B4: serve.py serves HTTP for k8s probes
# ============================================================

class TestB4ServeHttpProbes:
    """Sprint 5.13 B4 — serve.py sirve HTTP /health, /ready, /live, /metrics."""

    def test_serve_py_has_health_endpoints(self):
        """serve.py debe tener handlers para /health, /ready, /live, /metrics."""
        serve_path = Path(__file__).parent.parent / "serve.py"
        content = serve_path.read_text()
        for endpoint in ["/health", "/ready", "/live", "/metrics"]:
            assert endpoint in content, f"serve.py must serve {endpoint}"

    def test_serve_py_starts_health_server_on_port_8080(self):
        """serve.py debe iniciar un servidor HTTP en puerto 8080 (default)."""
        serve_path = Path(__file__).parent.parent / "serve.py"
        content = serve_path.read_text()
        assert "ZOE_HEALTH_PORT" in content, \
            "serve.py must read ZOE_HEALTH_PORT env var"
        assert "8080" in content, "serve.py must default to port 8080"


# ============================================================
# B4-bis: thoughts and conversation_history bounded
# ============================================================

class TestB4BisBoundedMemory:
    """Sprint 5.13 B4-bis — thoughts y conversation_history estan bounded."""

    def test_thoughts_is_deque_with_maxlen(self):
        """cognitive_loop_v05.py debe tener _max_thoughts = 1000 para bound thoughts."""
        loop_path = Path(__file__).parent.parent / "core" / "cognitive_loop_v05.py"
        content = loop_path.read_text()
        # NO usamos deque (no soporta slicing). Usamos list + truncado manual.
        assert "_max_thoughts = 1000" in content, \
            "cognitive_loop_v05.py must have _max_thoughts = 1000 to bound thoughts"
        assert "del self.thoughts[:-self._max_thoughts]" in content, \
            "cognitive_loop_v05.py must truncate thoughts when exceeding _max_thoughts"

    def test_conversation_history_is_deque_with_maxlen(self):
        """dashboard/server.py debe usar deque(maxlen=500) para _conversation_history."""
        server_path = Path(__file__).parent.parent / "dashboard" / "server.py"
        content = server_path.read_text()
        assert "deque(maxlen=500)" in content, \
            "dashboard/server.py must use deque(maxlen=500) for _conversation_history"

    @pytest.mark.asyncio
    async def test_thoughts_bounded_at_runtime(self):
        """En runtime, thoughts debe tener _max_thoughts configurado.

        Sprint 5.14: usa @pytest.mark.asyncio en vez de asyncio.run().
        """
        from zoe.cli_chat import ZoeChat

        db_path = tempfile.mktemp(suffix=".db")
        zc = ZoeChat(backend="mock", db_path=db_path)
        await zc.initialize()
        try:
            assert hasattr(zc.loop, '_max_thoughts'), \
                "loop must have _max_thoughts attribute"
            assert zc.loop._max_thoughts == 1000, \
                f"_max_thoughts must be 1000, got {zc.loop._max_thoughts}"
            # thoughts sigue siendo list (soporta slicing)
            assert isinstance(zc.loop.thoughts, list), \
                f"thoughts must be list (for slicing), got {type(zc.loop.thoughts)}"
        finally:
            await zc.shutdown()


# ============================================================
# B5: k8s/secret.yaml removed from git
# ============================================================

class TestB5SecretRemovedFromGit:
    """Sprint 5.13 B5 — k8s/secret.yaml no esta en git, .example si."""

    def test_secret_yaml_is_gitignored(self):
        """k8s/secret.yaml debe estar en .gitignore."""
        gitignore_path = Path(__file__).parent.parent.parent / ".gitignore"
        content = gitignore_path.read_text()
        assert "k8s/secret.yaml" in content, \
            ".gitignore must exclude k8s/secret.yaml"

    def test_secret_yaml_example_exists(self):
        """k8s/secret.yaml.example debe existir como template."""
        example_path = Path(__file__).parent.parent.parent / "k8s" / "secret.yaml.example"
        assert example_path.exists(), "k8s/secret.yaml.example must exist"
        content = example_path.read_text()
        assert "REPLACE_WITH_STRONG_PASSWORD" in content, \
            "secret.yaml.example must have placeholder password"

    def test_secret_yaml_not_tracked_by_git(self):
        """k8s/secret.yaml no debe estar trackeado por git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "k8s/secret.yaml"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True, text=True,
        )
        assert "k8s/secret.yaml" not in result.stdout, \
            "k8s/secret.yaml must NOT be tracked by git"


# ============================================================
# B6: Token not logged
# ============================================================

class TestB6TokenNotLogged:
    """Sprint 5.13 B6 — El auth_token no aparece en logs ni stdout."""

    def test_server_py_does_not_log_token(self):
        """server.py no debe logear el token literal."""
        server_path = Path(__file__).parent.parent / "dashboard" / "server.py"
        content = server_path.read_text()
        # No debe haber logger.warning con %s que incluya self.auth_token
        assert "Auto-generated token: %s" not in content, \
            "server.py must NOT log token with format string"
        assert 'self.auth_token' not in content.split('logger.warning')[1].split(')')[0] if 'logger.warning' in content else True, \
            "server.py logger.warning must not reference self.auth_token"

    def test_web_dashboard_py_does_not_print_token(self):
        """web_dashboard.py no debe IMPRIMIR el token a stdout con print().
        El token puede aparecer en webbrowser.open() (no se imprime)."""
        wd_path = Path(__file__).parent.parent / "web_dashboard.py"
        content = wd_path.read_text()
        # Buscar lineas con 'print(' que contengan 'auth_token' o 'server.auth_token'
        for line in content.split('\n'):
            stripped = line.lstrip()
            if 'print(' in stripped and ('auth_token' in stripped or 'server.auth_token' in stripped):
                # Si es dentro de un comentario, OK
                if stripped.startswith('#'):
                    continue
                pytest.fail(f"Found print() with token: {line}")
        # Verificar especificamente que no hay 'print(f"  Auth token'
        assert 'print(f"  Auth token' not in content, \
            "web_dashboard.py must NOT print 'Auth token ...'"


# ============================================================
# B7: hmac.compare_digest for timing-safe token comparison
# ============================================================

class TestB7TimingSafeAuth:
    """Sprint 5.13 B7 — Token comparison usa hmac.compare_digest."""

    def test_auth_py_imports_hmac(self):
        """auth.py debe importar hmac."""
        auth_path = Path(__file__).parent.parent / "dashboard" / "middleware" / "auth.py"
        content = auth_path.read_text()
        assert "import hmac" in content, "auth.py must import hmac"
        assert "hmac.compare_digest" in content, \
            "auth.py must use hmac.compare_digest"

    def test_tokens_match_function_exists(self):
        """La funcion _tokens_match debe existir y ser timing-safe."""
        from zoe.dashboard.middleware.auth import _tokens_match
        # Mismo token → True
        assert _tokens_match("abc123", "abc123") is True
        # Token distinto → False
        assert _tokens_match("abc123", "xyz789") is False
        # Token vacio → False
        assert _tokens_match("", "abc123") is False
        assert _tokens_match("abc123", "") is False
        # Longitudes distintas → False (sin crash)
        assert _tokens_match("short", "much_longer_token") is False

    def test_auth_middleware_uses_timing_safe_comparison(self):
        """create_auth_middleware debe usar _tokens_match, no !=."""
        auth_path = Path(__file__).parent.parent / "dashboard" / "middleware" / "auth.py"
        content = auth_path.read_text()
        assert "_tokens_match" in content, \
            "auth.py must use _tokens_match function"
        # No debe usar comparacion directa con !=
        assert "auth_header != expected" not in content, \
            "auth.py must NOT use != for token comparison"


# ============================================================
# B8: Tests rotos arreglados
# ============================================================

class TestB8BrokenTestsFixed:
    """Sprint 5.13 B8 — Los tests rotos estan arreglados."""

    def test_postgres_backend_tests_skip_when_asyncpg_missing(self):
        """test_postgres_backend.py debe skiparse correctamente cuando asyncpg no esta."""
        test_path = Path(__file__).parent / "test_postgres_backend.py"
        content = test_path.read_text()
        assert "HAS_ASYNCPG" in content, \
            "test_postgres_backend.py must use HAS_ASYNCPG (not HAS_ASYNCpg typo)"
        assert "pytest.mark.skipif(not HAS_ASYNCPG" in content, \
            "test_postgres_backend.py must skipif on HAS_ASYNCPG"

    def test_phase2_tests_dont_use_action_kwarg(self):
        """test_phase2.py no debe usar action= kwarg en Proposal()."""
        test_path = Path(__file__).parent / "test_phase2.py"
        content = test_path.read_text()
        # No debe haber Proposal(... action="..." ...)
        assert 'action="' not in content, \
            "test_phase2.py must NOT use action= kwarg in Proposal()"

    def test_hardware_endpoints_tests_use_modular_handlers(self):
        """test_phase7g_hardware_endpoints.py debe importar de dashboard.handlers.hardware."""
        test_path = Path(__file__).parent / "test_phase7g_hardware_endpoints.py"
        content = test_path.read_text()
        assert "from zoe.dashboard.handlers.hardware import" in content, \
            "test_phase7g_hardware_endpoints.py must import from dashboard.handlers.hardware"

    def test_pwa_manifest_tests_use_modular_routes(self):
        """test_sprint1_windows_pwa_telegram.py debe importar de dashboard.routes."""
        test_path = Path(__file__).parent / "test_sprint1_windows_pwa_telegram.py"
        content = test_path.read_text()
        assert "from zoe.dashboard.routes import register_routes" in content or \
               "from zoe.dashboard.handlers.hardware import _handle_manifest" in content, \
            "test_sprint1_windows_pwa_telegram.py must use modular dashboard API"

    def test_v4_thoughts_test_uses_sufficient_duration(self):
        """test_phase4.py::test_v4_generates_thoughts debe usar duration_seconds >= 6.0
        (tick_interval default es 5.0s)."""
        test_path = Path(__file__).parent / "test_phase4.py"
        content = test_path.read_text()
        assert "duration_seconds=8.0" in content or "duration_seconds=6.0" in content, \
            "test_v4_generates_thoughts must use duration >= 6.0s (tick_interval is 5.0s)"
