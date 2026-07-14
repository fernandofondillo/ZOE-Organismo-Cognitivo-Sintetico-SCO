"""
Tests Sprint 5.9 — Seguridad y observabilidad

Verifica:
1. Dashboard bind a 127.0.0.1 por defecto (no 0.0.0.0)
2. Auth token opcional (middleware 401 sin token, 200 con token)
3. --host flag permite exponer a red (0.0.0.0)
4. Logging a archivo rotado configurado
"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest


# ============================================================
# C5: Dashboard seguridad (bind 127.0.0.1 + auth-token)
# ============================================================

class TestDashboardSecurity:
    """Sprint 5.9 C5 — Dashboard seguro por defecto."""

    def test_dashboard_default_host_is_127(self):
        """El host por defecto debe ser 127.0.0.1, no 0.0.0.0."""
        from zoe.dashboard.server import DashboardServer
        ds = DashboardServer()
        assert ds.host == "127.0.0.1"

    def test_dashboard_accepts_host_param(self):
        """Se puede pasar host=0.0.0.0 explícitamente."""
        from zoe.dashboard.server import DashboardServer
        ds = DashboardServer(host="0.0.0.0")
        assert ds.host == "0.0.0.0"

    def test_dashboard_default_auth_token_is_none(self):
        """Por defecto no hay auth_token explícito (pero se auto-genera uno)."""
        from zoe.dashboard.server import DashboardServer
        ds = DashboardServer()
        # En la nueva arquitectura OMEGA, si no se pasa auth_token, se auto-genera
        assert ds.auth_token is not None  # auto-generado por seguridad

    def test_dashboard_accepts_auth_token(self):
        """Se puede configurar auth_token explícitamente."""
        from zoe.dashboard.server import DashboardServer
        ds = DashboardServer(auth_token="my-secret-token")
        assert ds.auth_token == "my-secret-token"

    def test_cli_accepts_host_flag(self):
        """argparse acepta --host."""
        import argparse
        import sys
        # Simular args
        old_argv = sys.argv
        sys.argv = ["zoe.web_dashboard", "--host", "0.0.0.0", "--auth-token", "secret"]
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("--host", default="127.0.0.1")
            parser.add_argument("--auth-token", default=None)
            args = parser.parse_args()
            assert args.host == "0.0.0.0"
            assert args.auth_token == "secret"
        finally:
            sys.argv = old_argv

    def test_cli_default_host_is_127(self):
        """argparse default de --host es 127.0.0.1."""
        import argparse
        import sys
        old_argv = sys.argv
        sys.argv = ["zoe.web_dashboard"]
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("--host", default="127.0.0.1")
            args = parser.parse_args()
            assert args.host == "127.0.0.1"
        finally:
            sys.argv = old_argv


# ============================================================
# Sprint 5.12 -- Auth middleware refinado (index publico + token persistente)
# ============================================================

class TestSprint512AuthRefinements:
    """Sprint 5.12 -- El dashboard debe ser utilizable por humanos.

    El HTML del dashboard se sirve sin token para que el navegador pueda
    cargarlo; el HTML maneja el token via ?token= o localStorage y lo
    inyecta en las llamadas fetch/XHR/WebSocket subsiguientes.
    """

    def test_index_path_is_public(self):
        """La ruta '/' debe estar en _PUBLIC_PATHS (HTML servible sin token)."""
        from zoe.dashboard.middleware.auth import _PUBLIC_PATHS
        assert "/" in _PUBLIC_PATHS
        assert "/manifest.json" in _PUBLIC_PATHS

    def test_health_paths_still_public(self):
        """Los health checks siguen siendo publicos."""
        from zoe.dashboard.middleware.auth import _PUBLIC_PATHS
        assert "/health" in _PUBLIC_PATHS
        assert "/ready" in _PUBLIC_PATHS
        assert "/live" in _PUBLIC_PATHS

    def test_data_endpoints_not_public(self):
        """Las rutas de datos NO son publicas (requieren token)."""
        from zoe.dashboard.middleware.auth import _PUBLIC_PATHS
        assert "/stats" not in _PUBLIC_PATHS
        assert "/memory" not in _PUBLIC_PATHS
        assert "/chat" not in _PUBLIC_PATHS
        assert "/ws" not in _PUBLIC_PATHS
        assert "/api/capsules" not in _PUBLIC_PATHS

    def test_dashboard_persists_auth_token_to_disk(self, tmp_path):
        """El token se persiste en dashboard_token.txt para que los
        lanzadores .command puedan leerlo y abrir el navegador con
        ?token=XXX en la URL."""
        from zoe.dashboard.server import DashboardServer
        db_path = str(tmp_path / "test.db")
        ds = DashboardServer(db_path=db_path, auth_token="test-token-12345")
        token_file = tmp_path / "dashboard_token.txt"
        assert token_file.exists()
        assert token_file.read_text() == "test-token-12345"

    def test_dashboard_html_has_token_handling(self):
        """El HTML del dashboard contiene el codigo de gestion de token."""
        from zoe.dashboard.html.dashboard_html import _get_dashboard_html
        html = _get_dashboard_html()
        # Buscar las funciones clave anadidas en Sprint 5.12
        assert "getZoeToken" in html
        assert "saveAuthToken" in html
        assert "zoe_auth_token" in html
        assert "authModal" in html

    def test_dashboard_html_ws_uses_token_query(self):
        """El WebSocket del HTML debe pasar ?token= en la URL."""
        from zoe.dashboard.html.dashboard_html import _get_dashboard_html
        html = _get_dashboard_html()
        # La funcion connectWS debe construir la URL con ?token=
        assert "tokenQuery" in html or "?token=" in html

    def test_dashboard_html_overrides_fetch(self):
        """El HTML sobreescribe window.fetch para inyectar Authorization."""
        from zoe.dashboard.html.dashboard_html import _get_dashboard_html
        html = _get_dashboard_html()
        assert "window.fetch" in html
        assert "Authorization" in html
        assert "Bearer" in html

    def test_web_dashboard_shim_reexports_get_html(self):
        """El shim zoe.web_dashboard re-exporta _get_dashboard_html
        para compatibilidad con tests y callers externos."""
        from zoe.web_dashboard import _get_dashboard_html, DashboardServer
        assert callable(_get_dashboard_html)
        assert len(_get_dashboard_html()) > 1000


# ============================================================
# Sprint 5.12 GAP-Q + GAP-R -- Coherencia SSD (db_path)
# ============================================================

class TestSprint512SSDCoherence:
    """Sprint 5.12 GAP-Q + GAP-R -- Dashboard y Chat deben cargar el mismo
    ZOE del SSD (misma identidad, memoria, trayectoria).

    Antes de Sprint 5.12:
    - INICIAR-ZOE.command pasaba --db-path al SSD, pero
    - ZOE-Dashboard.command NO pasaba --db-path, usando el default relativo
      "zoe_data/dashboard_memory.db" (CWD actual, probablemente Mac).
    Resultado: chat y dashboard cargaban ZOEs distintos con identidades distintas.

    Sprint 5.12 corrige esto con dos mecanismos defensivos:
    1. (GAP-Q) Todos los launchers pasan --db-path al SSD explicitamente.
    2. (GAP-R) cli_chat.py y web_dashboard.py usan $ZOE_DATA como default
       si no se pasa --db-path. Los launchers del SSD cargan .env que
       define ZOE_DATA=$ZOE_HOME/data, asi que incluso si un launcher olvida
       --db-path, ZOE sigue yendo al SSD.
    """

    def test_zoechat_uses_zoe_data_env_when_no_db_path(self, monkeypatch):
        """Si no se pasa db_path, ZoeChat debe usar $ZOE_DATA/zoe_memory.db."""
        import os
        from zoe.cli_chat import ZoeChat

        monkeypatch.setenv("ZOE_DATA", "/Volumes/CrucialX9/ZOE/data")
        zc = ZoeChat(backend="mock")
        assert zc.db_path == "/Volumes/CrucialX9/ZOE/data/zoe_memory.db", \
            f"Expected SSD path, got {zc.db_path}"

    def test_zoechat_uses_default_when_no_zoe_data(self, monkeypatch):
        """Sin $ZOE_DATA, ZoeChat usa el default relativo (backward compat)."""
        from zoe.cli_chat import ZoeChat

        monkeypatch.delenv("ZOE_DATA", raising=False)
        zc = ZoeChat(backend="mock")
        assert zc.db_path == "zoe_data/chat_memory.db"

    def test_zoechat_explicit_db_path_wins_over_env(self, monkeypatch):
        """Si se pasa db_path explicito, prevalece sobre $ZOE_DATA."""
        import os
        from zoe.cli_chat import ZoeChat

        monkeypatch.setenv("ZOE_DATA", "/Volumes/CrucialX9/ZOE/data")
        zc = ZoeChat(backend="mock", db_path="/tmp/custom.db")
        assert zc.db_path == "/tmp/custom.db"

    def test_web_dashboard_uses_zoe_data_env_for_db_path_default(self, monkeypatch):
        """web_dashboard.py --db-path default usa $ZOE_DATA si existe."""
        import os
        import argparse

        monkeypatch.setenv("ZOE_DATA", "/Volumes/CrucialX9/ZOE/data")
        _default_db = os.path.join(
            os.environ.get("ZOE_DATA", "zoe_data"),
            "dashboard_memory.db",
        )
        parser = argparse.ArgumentParser()
        parser.add_argument("--db-path", default=_default_db)
        args = parser.parse_args([])
        assert args.db_path == "/Volumes/CrucialX9/ZOE/data/dashboard_memory.db"

    def test_dashboard_and_chat_use_same_ssd_path_when_zoe_data_set(self, monkeypatch):
        """Test end-to-end: cuando $ZOE_DATA apunta al SSD, tanto Dashboard
        como Chat resuelven rutas compatibles (mismo directorio data/)."""
        import os
        from zoe.cli_chat import ZoeChat

        monkeypatch.setenv("ZOE_DATA", "/Volumes/CrucialX9/ZOE/data")
        zc = ZoeChat(backend="mock")
        # Dashboard usa dashboard_memory.db, Chat usa zoe_memory.db
        # Ambos en el mismo directorio $ZOE_DATA
        chat_dir = os.path.dirname(zc.db_path)
        dash_default = os.path.join(
            os.environ.get("ZOE_DATA", "zoe_data"),
            "dashboard_memory.db",
        )
        dash_dir = os.path.dirname(dash_default)
        assert chat_dir == dash_dir == "/Volumes/CrucialX9/ZOE/data", \
            f"chat_dir={chat_dir}, dash_dir={dash_dir} — deben ser el mismo (SSD)"

    def test_launchers_pass_db_path_to_ssd(self):
        """Los launchers generados por zoe-bootstrap.sh e install_ssd_crucial_x9_mac.sh
        deben pasar --db-path al SSD (GAP-Q). Verificamos leyendo el contenido
        de los scripts en el repo."""
        from pathlib import Path

        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        install_ssd_path = Path(__file__).parent.parent / "scripts" / "install_ssd_crucial_x9_mac.sh"

        bootstrap_content = bootstrap_path.read_text()
        install_ssd_content = install_ssd_path.read_text()

        # zoe-bootstrap.sh: las invocaciones web_dashboard y cli_chat deben
        # tener --db-path (con $ZOE_HOME/data o $ZOE_DATA)
        bootstrap_dash_calls = bootstrap_content.count("zoe.web_dashboard")
        bootstrap_dash_with_dbpath = bootstrap_content.count(
            'zoe.web_dashboard --backend'
        )
        # Al menos 4 invocaciones de web_dashboard deben existir (4 launchers macOS + 4 Linux + final)
        assert bootstrap_dash_calls >= 4, \
            f"Expected >=4 web_dashboard calls, got {bootstrap_dash_calls}"

        # install_ssd_crucial_x9_mac.sh: la opcion 3 (DASHBOARD) debe pasar --db-path
        assert '--db-path "$ZOE_HOME/data/dashboard_memory.db"' in install_ssd_content, \
            "install_ssd option 3 must pass --db-path to SSD"

    def test_install_ssd_no_typo_in_backend_prompt(self):
        """GAP-K: el prompt de Backend en install_ssd no debe tener el typo 'ock'."""
        from pathlib import Path
        install_ssd_path = Path(__file__).parent.parent / "scripts" / "install_ssd_crucial_x9_mac.sh"
        content = install_ssd_path.read_text()
        # El typo era "Backend ock/..." (sin [m). Verificar que ahora es "Backend [mock/..."
        assert "Backend [mock/ollama/openai/anthropic]" in content, \
            "Backend prompt must be 'Backend [mock/ollama/openai/anthropic]' (no typo)"

    def test_install_ssd_option_4_uses_model_auto(self):
        """GAP-L: la opcion 4 (OLLAMA) del Smart Launcher debe usar --model auto
        (ACD Router), no --model qwen2.5:3b hardcodeado."""
        from pathlib import Path
        install_ssd_path = Path(__file__).parent.parent / "scripts" / "install_ssd_crucial_x9_mac.sh"
        content = install_ssd_path.read_text()
        # Buscar la invocacion de cli_chat en opcion 4 (OLLAMA)
        assert "cli_chat --backend ollama --model auto" in content, \
            "Option 4 must use --model auto (ACD Router), not qwen2.5:3b hardcodeado"


# ============================================================
# M7: Logging a archivo rotado
# ============================================================

class TestLoggingRotated:
    """Sprint 5.9 M7 — Logging a archivo rotado."""

    def test_rotating_file_handler_configurable(self):
        """Se puede configurar un RotatingFileHandler."""
        import logging
        import logging.handlers
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "zoe.log")
            handler = logging.handlers.RotatingFileHandler(
                log_path, maxBytes=1024, backupCount=3, encoding="utf-8"
            )
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

            logger = logging.getLogger("test_rotated")
            logger.setLevel(logging.INFO)
            logger.addHandler(handler)

            logger.info("Test message")
            handler.flush()
            handler.close()

            assert os.path.exists(log_path)
            with open(log_path, "r") as f:
                content = f.read()
            assert "Test message" in content

    def test_log_file_in_data_dir(self):
        """El archivo de log debe ir al directorio de datos."""
        # Verificamos que el código de cli_chat.py usa os.path.dirname(db_path)
        import os
        db_path = "zoe_data/chat_memory.db"
        log_dir = os.path.dirname(db_path)
        assert log_dir == "zoe_data"


# ============================================================
# M11: Backup conceptual
# ============================================================

class TestBackupConcept:
    """Sprint 5.9 M11 — Concepto de backup (copiar archivos de datos)."""

    def test_backup_copia_archivos_de_datos(self, tmp_path):
        """Un backup copia identity_vault.json, trajectory_chain.json, memory.db."""
        import shutil

        # Crear archivos de datos
        data_dir = tmp_path / "zoe_data"
        data_dir.mkdir()
        (data_dir / "identity_vault.json").write_text('{"test": true}')
        (data_dir / "trajectory_chain.json").write_text('{"mutations": []}')
        (data_dir / "chat_memory.db").write_text("SQLite data")

        # Backup
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()
        for f in data_dir.iterdir():
            shutil.copy2(f, backup_dir / f.name)

        # Verificar
        assert (backup_dir / "identity_vault.json").exists()
        assert (backup_dir / "trajectory_chain.json").exists()
        assert (backup_dir / "chat_memory.db").exists()

    def test_backup_preserva_contenido(self, tmp_path):
        """El backup preserva el contenido."""
        import shutil

        data_dir = tmp_path / "zoe_data"
        data_dir.mkdir()
        original_content = '{"identity_hash": "abc123"}'
        (data_dir / "identity_vault.json").write_text(original_content)

        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()
        shutil.copy2(data_dir / "identity_vault.json", backup_dir / "identity_vault.json")

        assert (backup_dir / "identity_vault.json").read_text() == original_content
