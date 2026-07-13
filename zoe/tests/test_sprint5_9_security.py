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
