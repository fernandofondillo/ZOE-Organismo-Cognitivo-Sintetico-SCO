"""
ZOE v1.0 — Storage Backend Factory

Patrón Factory para crear el backend de persistencia adecuado
según la configuración (SQLite por defecto, PostgreSQL opcional).

Uso:
    # SQLite (default)
    backend = get_storage_backend()

    # PostgreSQL
    backend = get_storage_backend({"type": "postgres", ...})

    # Desde variables de entorno
    backend = get_storage_backend()  # lee ZOE_STORAGE_TYPE, POSTGRES_*, etc.

Variables de entorno:
    ZOE_STORAGE_TYPE: sqlite | postgres (default: sqlite)
    POSTGRES_HOST: host de PostgreSQL (default: localhost)
    POSTGRES_PORT: puerto (default: 5432)
    POSTGRES_DB: nombre de base de datos (default: zoe)
    POSTGRES_USER: usuario (default: zoe)
    POSTGRES_PASSWORD: contraseña (default: vacío)
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Any

from .base import StorageBackend
from .sqlite_backend import SQLiteBackend

logger = logging.getLogger(__name__)


def get_storage_backend(config: Dict[str, Any] = None) -> StorageBackend:
    """
    Factory: crea el backend de persistencia según configuración.

    Args:
        config: dict con opciones. Si es None, se leen variables de entorno.

    Returns:
        Instancia de StorageBackend (SQLiteBackend o PostgreSQLBackend)

    Raises:
        ImportError: si se pide postgres pero asyncpg no está instalado
    """
    config = config or {}

    backend_type = config.get(
        "type",
        os.environ.get("ZOE_STORAGE_TYPE", "sqlite"),
    )

    if backend_type == "postgres":
        logger.info("Storage factory: creating PostgreSQLBackend")
        return _create_postgres_backend(config)

    logger.info("Storage factory: creating SQLiteBackend")
    return _create_sqlite_backend(config)


def _create_sqlite_backend(config: Dict[str, Any]) -> SQLiteBackend:
    """Crea un SQLiteBackend con la configuración proporcionada."""
    db_path = config.get(
        "db_path",
        os.environ.get("ZOE_DB_PATH", "zoe_data/memory.db"),
    )
    auto_save = config.get(
        "auto_save_interval",
        int(os.environ.get("ZOE_AUTO_SAVE_INTERVAL", "50")),
    )
    return SQLiteBackend(db_path=db_path, auto_save_interval=auto_save)


def _create_postgres_backend(config: Dict[str, Any]) -> StorageBackend:
    """Crea un PostgreSQLBackend con la configuración proporcionada."""
    # Import lazy para no requerir asyncpg si no se usa postgres
    try:
        from .postgres_backend import PostgreSQLBackend
    except ImportError as e:
        raise ImportError(
            "PostgreSQL backend requires asyncpg. "
            "Install: pip install asyncpg"
        ) from e

    host = config.get("host", os.environ.get("POSTGRES_HOST", "localhost"))
    port = config.get("port", int(os.environ.get("POSTGRES_PORT", "5432")))
    database = config.get("database", os.environ.get("POSTGRES_DB", "zoe"))
    user = config.get("user", os.environ.get("POSTGRES_USER", "zoe"))
    password = config.get("password", os.environ.get("POSTGRES_PASSWORD", ""))
    min_pool = config.get(
        "min_pool_size",
        int(os.environ.get("POSTGRES_MIN_POOL", "2")),
    )
    max_pool = config.get(
        "max_pool_size",
        int(os.environ.get("POSTGRES_MAX_POOL", "10")),
    )
    ssl = config.get("ssl", os.environ.get("POSTGRES_SSL", "").lower() == "true")

    return PostgreSQLBackend(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        min_pool_size=min_pool,
        max_pool_size=max_pool,
        ssl=ssl,
    )


# Helper para inyectar el backend en el runtime existente
def inject_into_runtime(runtime: Any, config: Dict[str, Any] = None) -> StorageBackend:
    """
    Crea un backend y lo inyecta en un ZoeRuntime existente.

    Args:
        runtime: instancia de ZoeRuntime
        config: configuración del backend

    Returns:
        El backend creado y conectado
    """
    import asyncio

    backend = get_storage_backend(config)

    async def _inject() -> StorageBackend:
        await backend.connect()
        runtime.storage = backend
        logger.info(f"Storage backend injected into runtime: {backend.__class__.__name__}")
        return backend

    try:
        loop = asyncio.get_running_loop()
        return loop.create_task(_inject())
    except RuntimeError:
        return asyncio.run(_inject())
