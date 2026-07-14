"""
ZOE Structured Logging — Sprint 5.17 F3.1

Proporciona logging estructurado en formato JSON para producción.
En desarrollo, usa formato legible humano.

Uso:
    from zoe.core.structured_logging import setup_logging, get_logger
    setup_logging(level="INFO", json_output=True)
    logger = get_logger(__name__)
    logger.info("event", extra={"key": "value"})

Formato JSON (producción):
    {"timestamp": "2026-07-15T12:34:56.789Z", "level": "INFO",
     "logger": "zoe.cli_chat", "message": "ZOE initialized",
     "identity_hash": "abc123...", "extra": {...}}

Formato humano (desarrollo):
    2026-07-15 12:34:56 [INFO] zoe.cli_chat: ZOE initialized
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Formatter que produce JSON para log aggregators (Loki, ELK, CloudWatch)."""

    # Campos sensibles que NUNCA deben aparecer en logs
    _SENSITIVE_KEYS = {
        "auth_token", "token", "api_key", "api_keys",
        "openai_api_key", "anthropic_api_key", "deepseek_api_key",
        "password", "passwd", "secret", "authorization",
        "bearer", "cookie", "session_id",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Base log entry
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Extra fields from record.__dict__
        extra: Dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno",
                "pathname", "filename", "module", "exc_info",
                "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "message",
                "taskName",
            ):
                # Redact sensitive keys
                if key.lower() in self._SENSITIVE_KEYS:
                    extra[key] = "[REDACTED]"
                else:
                    try:
                        json.dumps(value)  # check serializable
                        extra[key] = value
                    except (TypeError, ValueError):
                        extra[key] = str(value)

        if extra:
            entry["extra"] = extra

        # Exception info
        if record.exc_info and record.exc_info[1] is not None:
            entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(entry, ensure_ascii=False, default=str)


class HumanFormatter(logging.Formatter):
    """Formatter legible para desarrollo."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        msg = f"{ts} [{record.levelname:5s}] {record.name}: {record.getMessage()}"
        if record.exc_info and record.exc_info[1] is not None:
            msg += f"\n{self.formatException(record.exc_info)}"
        return msg


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    json_output: Optional[bool] = None,
) -> None:
    """Configura logging global para ZOE.

    Args:
        level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Si se especifica, escribe logs a archivo con rotacion.
        max_bytes: Tamaño maximo del archivo antes de rotar (default 10MB).
        backup_count: Numero de archivos de backup a mantener (default 5).
        json_output: Si True, usa JSON format. Si False, usa humano.
                     Si None, detecta automaticamente (ZOE_JSON_LOGS env var
                     o ZOE_ENV=production).
    """
    # Detectar JSON output automaticamente
    if json_output is None:
        json_output = (
            os.environ.get("ZOE_JSON_LOGS", "").lower() in ("1", "true", "yes")
            or os.environ.get("ZOE_ENV", "").lower() == "production"
        )

    formatter = JsonFormatter() if json_output else HumanFormatter()

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    handlers[0].setFormatter(formatter)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=handlers,
        force=True,  # Override any previous config
    )

    # Reducir verbosidad de librerias externas
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logger = logging.getLogger("zoe")
    logger.info(
        "logging_configured",
        extra={
            "level": level,
            "json_output": json_output,
            "log_file": log_file,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre dado. Wrapper de logging.getLogger."""
    return logging.getLogger(name)
