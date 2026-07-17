"""
ZOE v1.0 — Storage Backends

Capa de persistencia abstracta con soporte para SQLite (default) y PostgreSQL.

Uso:
    from zoe.storage.factory import get_storage_backend

    backend = get_storage_backend()  # SQLite por defecto
    await backend.connect()
    entry_id = await backend.save_memory("episodic", {"content": "evento"})
    await backend.disconnect()

Cambio a PostgreSQL:
    backend = get_storage_backend({
        "type": "postgres",
        "host": "localhost",
        "database": "zoe",
        "user": "zoe",
        "password": "secret"
    })
"""

from .base import StorageBackend
from .factory import get_storage_backend
from .sqlite_backend import SQLiteBackend

__all__ = ["StorageBackend", "get_storage_backend", "SQLiteBackend"]

# PostgreSQLBackend se importa lazy en factory para no requerir asyncpg
