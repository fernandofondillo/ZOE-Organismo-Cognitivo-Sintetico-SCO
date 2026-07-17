"""
Sprint 5.17 F3.1-F3.4 — Tests de Fase 3 (mejoras de observabilidad).

F3.1: Structured logging (JSON)
F3.2: /live check real (CPU, memory, disk, cognitive loop)
F3.3: /health y /ready detectan backend postgres vs sqlite
F3.4: PrometheusRule manifest con alertas basicas
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest


# ============================================================
# F3.1: Structured logging
# ============================================================

class TestF31StructuredLogging:
    """Sprint 5.17 F3.1 — Structured logging en formato JSON."""

    def test_structured_logging_module_exists(self):
        """zoe/core/structured_logging.py existe."""
        path = Path(__file__).parent.parent / "core" / "structured_logging.py"
        assert path.exists(), "structured_logging.py must exist"

    def test_json_formatter_exists(self):
        """JsonFormatter class existe."""
        from zoe.core.structured_logging import JsonFormatter
        assert JsonFormatter is not None

    def test_human_formatter_exists(self):
        """HumanFormatter class existe."""
        from zoe.core.structured_logging import HumanFormatter
        assert HumanFormatter is not None

    def test_setup_logging_function_exists(self):
        """setup_logging function existe."""
        from zoe.core.structured_logging import setup_logging
        assert callable(setup_logging)

    def test_sensitive_keys_are_redacted(self):
        """Las keys sensibles se redactan en JSON output."""
        import logging
        from zoe.core.structured_logging import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test_event", args=(), exc_info=None,
        )
        record.auth_token = "secret123"
        record.api_key = "sk-abc"

        output = formatter.format(record)
        data = json.loads(output)
        assert data["extra"]["auth_token"] == "[REDACTED]"
        assert data["extra"]["api_key"] == "[REDACTED]"

    def test_json_output_includes_timestamp_level_logger(self):
        """JSON output incluye timestamp, level, logger, message."""
        import logging
        from zoe.core.structured_logging import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="zoe.test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)
        assert "timestamp" in data
        assert data["level"] == "INFO"
        assert data["logger"] == "zoe.test"
        assert data["message"] == "test message"

    def test_serve_py_uses_structured_logging(self):
        """serve.py delega a structured_logging."""
        serve_path = Path(__file__).parent.parent / "serve.py"
        content = serve_path.read_text()
        assert "from .core.structured_logging import setup_logging" in content, \
            "serve.py must use structured_logging"

    def test_web_dashboard_uses_structured_logging(self):
        """web_dashboard.py usa structured_logging."""
        wd_path = Path(__file__).parent.parent / "web_dashboard.py"
        content = wd_path.read_text()
        assert "from .core.structured_logging import setup_logging" in content, \
            "web_dashboard.py must use structured_logging"


# ============================================================
# F3.2: /live check real
# ============================================================

class TestF32LiveCheckReal:
    """Sprint 5.17 F3.2 — /live hace checks reales (no siempre 200)."""

    def test_live_handler_checks_cognitive_loop(self):
        """El handler /live verifica el cognitive loop."""
        health_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = health_path.read_text()
        assert "cognitive_loop_iterations" in content, \
            "/live must check cognitive loop iteration count"

    def test_live_handler_checks_memory(self):
        """El handler /live verifica memoria disponible."""
        health_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = health_path.read_text()
        assert "memory_percent" in content or "virtual_memory" in content, \
            "/live must check memory usage"

    def test_live_handler_checks_disk(self):
        """El handler /live verifica disco disponible."""
        health_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = health_path.read_text()
        assert "disk_usage" in content or "disk_percent" in content, \
            "/live must check disk usage"

    def test_live_handler_can_return_503(self):
        """El handler /live puede retornar 503 si los checks fallan."""
        health_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = health_path.read_text()
        # Buscar que /live puede retornar 503
        live_section = content[content.find("async def _handle_live"):]
        assert "503" in live_section, \
            "/live must be able to return 503 when checks fail"

    def test_server_has_start_time(self):
        """DashboardServer tiene _start_time para /live uptime check."""
        server_path = Path(__file__).parent.parent / "dashboard" / "server.py"
        content = server_path.read_text()
        assert "_start_time" in content, \
            "DashboardServer must have _start_time for /live uptime tracking"


# ============================================================
# F3.3: /health y /ready detectan postgres vs sqlite
# ============================================================

class TestF33StorageTypeDetection:
    """Sprint 5.17 F3.3 — /health y /ready detectan backend postgres vs sqlite."""

    def test_health_handler_checks_storage_type(self):
        """El handler /health verifica ZOE_STORAGE_TYPE."""
        health_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = health_path.read_text()
        assert "ZOE_STORAGE_TYPE" in content, \
            "/health must check ZOE_STORAGE_TYPE env var"

    def test_health_handler_has_postgres_path(self):
        """El handler /health tiene path para PostgreSQL."""
        health_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = health_path.read_text()
        assert "postgres" in content.lower(), \
            "/health must have PostgreSQL check path"

    def test_ready_handler_checks_storage_type(self):
        """El handler /ready verifica ZOE_STORAGE_TYPE."""
        health_path = Path(__file__).parent.parent / "dashboard" / "handlers" / "health.py"
        content = health_path.read_text()
        # Buscar en la sección de /ready
        ready_section = content[content.find("async def _handle_ready"):]
        assert "ZOE_STORAGE_TYPE" in ready_section, \
            "/ready must check ZOE_STORAGE_TYPE env var"


# ============================================================
# F3.4: PrometheusRule manifest
# ============================================================

class TestF34PrometheusRules:
    """Sprint 5.17 F3.4 — PrometheusRule con alertas basicas."""

    def test_prometheus_rules_yaml_exists(self):
        """k8s/prometheus-rules.yaml existe."""
        path = Path(__file__).parent.parent.parent / "k8s" / "prometheus-rules.yaml"
        assert path.exists(), "k8s/prometheus-rules.yaml must exist"

    def test_prometheus_rules_valid_yaml(self):
        """El YAML es valido."""
        import yaml
        path = Path(__file__).parent.parent.parent / "k8s" / "prometheus-rules.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["kind"] == "PrometheusRule"
        assert "groups" in data["spec"]

    def test_prometheus_rules_has_zoe_down_alert(self):
        """Tiene alerta ZoeDown."""
        path = Path(__file__).parent.parent.parent / "k8s" / "prometheus-rules.yaml"
        content = path.read_text()
        assert "ZoeDown" in content, "Must have ZoeDown alert"

    def test_prometheus_rules_has_memory_alert(self):
        """Tiene alerta de memoria alta."""
        path = Path(__file__).parent.parent.parent / "k8s" / "prometheus-rules.yaml"
        content = path.read_text()
        assert "ZoeHighMemory" in content, "Must have ZoeHighMemory alert"

    def test_prometheus_rules_has_stalled_alert(self):
        """Tiene alerta de cognitive loop estancado."""
        path = Path(__file__).parent.parent.parent / "k8s" / "prometheus-rules.yaml"
        content = path.read_text()
        assert "ZoeCognitiveLoopStalled" in content, "Must have ZoeCognitiveLoopStalled alert"

    def test_prometheus_rules_has_error_rate_alert(self):
        """Tiene alerta de rate de errores alto."""
        path = Path(__file__).parent.parent.parent / "k8s" / "prometheus-rules.yaml"
        content = path.read_text()
        assert "ZoeHighErrorRate" in content, "Must have ZoeHighErrorRate alert"
