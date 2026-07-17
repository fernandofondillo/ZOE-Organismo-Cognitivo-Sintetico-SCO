"""
ZOE v1.0 — PostgreSQL Backend

Implementación de StorageBackend usando PostgreSQL con asyncpg.
Diseñado para deployments en Kubernetes y alta disponibilidad.

Características:
- Connection pooling con asyncpg.Pool
- JSONB para datos flexibles (metadatos, payload, extra_data)
- Schema idéntico a SQLite (misma API, motor diferente)
- Health check con SELECT 1
- Soporte para migraciones alembic-compatible
- Índices GIN sobre JSONB para búsquedas eficientes
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

try:
    import asyncpg
except ImportError:
    asyncpg = None

from .base import StorageBackend

logger = logging.getLogger(__name__)

# Los 11 tipos de memoria soportados
MEMORY_TYPES = [
    "episodic", "semantic", "procedural", "causal", "emotional",
    "corporeal", "social", "prospective", "counterfactual",
    "evolutionary", "cultural",
]


class PostgreSQLBackend(StorageBackend):
    """
    Backend PostgreSQL para ZOE con asyncpg y JSONB.

    Requiere: pip install asyncpg

    Ideal para:
    - Deployments en Kubernetes
    - Múltiples réplicas de ZOE compartiendo estado
    - Backups automatizados
    - Replicación y alta disponibilidad
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "zoe",
        user: str = "zoe",
        password: str = "",
        min_pool_size: int = 2,
        max_pool_size: int = 10,
        ssl: bool = False,
    ):
        if asyncpg is None:
            raise ImportError(
                "asyncpg is required for PostgreSQL backend. "
                "Install: pip install asyncpg"
            )

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.ssl = ssl

        self._pool: Optional[Any] = None
        self._initialized: bool = False

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Crea el connection pool y las tablas."""
        if self._pool is not None:
            return

        ssl_context = None
        if self.ssl:
            import ssl as ssl_module
            ssl_context = ssl_module.create_default_context()

        self._pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            min_size=self.min_pool_size,
            max_size=self.max_pool_size,
            ssl=ssl_context,
        )

        if not self._initialized:
            await self._create_tables()
            self._initialized = True

        logger.info(
            f"PostgreSQLBackend connected: {self.user}@{self.host}:{self.port}/{self.database} "
            f"(pool: {self.min_pool_size}-{self.max_pool_size})"
        )

    async def disconnect(self) -> None:
        """Cierra el connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._initialized = False
            logger.info("PostgreSQLBackend disconnected")

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    async def _create_tables(self) -> None:
        """Crea todas las tablas e índices PostgreSQL."""
        if self._pool is None:
            return

        async with self._pool.acquire() as conn:
            # Tabla principal: entries de memoria
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id SERIAL PRIMARY KEY,
                    entry_id TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    salience REAL DEFAULT 0.5,
                    provenance TEXT DEFAULT '',
                    timestamp DOUBLE PRECISION DEFAULT 0,
                    last_access DOUBLE PRECISION DEFAULT 0,
                    access_count INTEGER DEFAULT 0,
                    merged_from JSONB DEFAULT '[]'::jsonb,
                    contradictions JSONB DEFAULT '[]'::jsonb,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    extra_data JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

            # Tabla de identidad (solo una fila)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS identity (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT NOT NULL DEFAULT 'Zoe',
                    vectors JSONB NOT NULL DEFAULT '[]'::jsonb,
                    values JSONB NOT NULL DEFAULT '[]'::jsonb,
                    purpose TEXT NOT NULL DEFAULT '',
                    birth_timestamp DOUBLE PRECISION DEFAULT 0,
                    identity_hash TEXT DEFAULT '',
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

            # Tabla de trayectoria (mutaciones)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trajectory (
                    id SERIAL PRIMARY KEY,
                    mutation_id TEXT UNIQUE NOT NULL,
                    mutation_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    payload JSONB DEFAULT '{}'::jsonb,
                    justification TEXT DEFAULT '',
                    provenance TEXT DEFAULT '',
                    cost REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 0.5,
                    mutation_timestamp DOUBLE PRECISION DEFAULT 0,
                    signature TEXT DEFAULT '',
                    prev_hash TEXT DEFAULT '',
                    mutation_hash TEXT DEFAULT '',
                    applied BOOLEAN DEFAULT TRUE,
                    rolled_back BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

            # Tabla de metadatos del backend
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS storage_metadata (
                    key TEXT PRIMARY KEY,
                    value JSONB NOT NULL DEFAULT '{}'::jsonb,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

            # Sprint 5.24 F3v2-4 (BUG-020 fix): crear extensión pg_trgm ANTES
            # del índice GIN que la requiere. Antes el orden era inverso:
            # se creaba el índice `gin_trgm_ops` primero, y luego la
            # extensión, lo que causaba que el CREATE INDEX fallara si
            # la extensión no estaba pre-instalada.
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            except Exception as e:
                logger.warning(f"pg_trgm extension creation failed: {e}")

            # Índices optimizados
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_me_type ON memory_entries(type)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_me_salience ON memory_entries(salience DESC)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_me_timestamp ON memory_entries(timestamp DESC)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_me_content_trgm ON memory_entries
                USING gin (content gin_trgm_ops)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_me_metadata ON memory_entries
                USING gin (metadata)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_traj_type ON trajectory(mutation_type)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_traj_ts ON trajectory(mutation_timestamp DESC)
            """)

        logger.debug("PostgreSQLBackend: all tables and indexes created")

    # ------------------------------------------------------------------
    # Memoria
    # ------------------------------------------------------------------

    async def save_memory(self, entry_type: str, data: Dict[str, Any]) -> int:
        """Guarda una entry de memoria."""
        if self._pool is None:
            raise RuntimeError("Backend not connected. Call connect() first.")

        now = time.time()
        entry_id = data.get("id", f"{entry_type}_{int(now * 1000)}")

        # Separar campos base de extra_data
        base_fields = {"content", "confidence", "salience", "provenance",
                       "timestamp", "last_access", "access_count",
                       "merged_from", "contradictions", "metadata"}
        extra = {k: v for k, v in data.items() if k not in base_fields and k != "id"}

        row = await self._pool.fetchrow("""
            INSERT INTO memory_entries
            (entry_id, type, content, confidence, salience, provenance, timestamp,
             last_access, access_count, merged_from, contradictions, metadata, extra_data)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (entry_id) DO UPDATE SET
                content = EXCLUDED.content,
                confidence = EXCLUDED.confidence,
                salience = EXCLUDED.salience,
                provenance = EXCLUDED.provenance,
                timestamp = EXCLUDED.timestamp,
                last_access = EXCLUDED.last_access,
                access_count = EXCLUDED.access_count,
                merged_from = EXCLUDED.merged_from,
                contradictions = EXCLUDED.contradictions,
                metadata = EXCLUDED.metadata,
                extra_data = EXCLUDED.extra_data
            RETURNING id
        """,
            entry_id,
            entry_type,
            data.get("content", ""),
            data.get("confidence", 0.5),
            data.get("salience", 0.5),
            data.get("provenance", ""),
            data.get("timestamp", now),
            data.get("last_access", now),
            data.get("access_count", 0),
            json.dumps(data.get("merged_from", [])),
            json.dumps(data.get("contradictions", [])),
            json.dumps(data.get("metadata", {})),
            json.dumps(extra),
        )
        return row["id"]

    async def get_memory(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Recupera una entry por ID numérico."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        row = await self._pool.fetchrow(
            "SELECT * FROM memory_entries WHERE id = $1", entry_id
        )
        if row is None:
            return None
        return self._row_to_entry(dict(row))

    async def search_memory(
        self, entry_type: str, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Búsqueda por contenido (ILIKE) dentro de un tipo."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        rows = await self._pool.fetch("""
            SELECT * FROM memory_entries
            WHERE type = $1 AND content ILIKE $2
            ORDER BY salience DESC, timestamp DESC
            LIMIT $3
        """, entry_type, f"%{query}%", limit)

        return [self._row_to_entry(dict(r)) for r in rows]

    async def delete_memory(self, entry_id: int) -> bool:
        """Elimina una entry por ID numérico."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        result = await self._pool.execute(
            "DELETE FROM memory_entries WHERE id = $1", entry_id
        )
        # asyncpg devuelve "DELETE <count>"
        return "DELETE 1" in result or result.endswith(" 1")

    async def list_by_type(self, entry_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Lista entries de un tipo específico."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        rows = await self._pool.fetch("""
            SELECT * FROM memory_entries WHERE type = $1
            ORDER BY timestamp DESC LIMIT $2
        """, entry_type, limit)

        return [self._row_to_entry(dict(r)) for r in rows]

    async def update_memory(self, entry_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza campos de una entry existente."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        now = time.time()
        allowed = {"content", "confidence", "salience", "provenance",
                   "access_count", "metadata", "extra_data"}
        updates = {k: v for k, v in data.items() if k in allowed}
        if not updates:
            return False

        # Serializar JSON
        for json_field in ("metadata", "extra_data"):
            if json_field in updates and isinstance(updates[json_field], (dict, list)):
                updates[json_field] = json.dumps(updates[json_field])

        set_clauses = []
        values = []
        param_idx = 1
        for k, v in updates.items():
            set_clauses.append(f"{k} = ${param_idx}")
            values.append(v)
            param_idx += 1

        # last_access
        set_clauses.append(f"last_access = ${param_idx}")
        values.append(now)
        param_idx += 1

        values.append(entry_id)

        result = await self._pool.execute(
            f"UPDATE memory_entries SET {', '.join(set_clauses)} WHERE id = ${param_idx}",
            *values
        )
        return "UPDATE 1" in result or result.endswith(" 1")

    # ------------------------------------------------------------------
    # Identidad
    # ------------------------------------------------------------------

    async def save_identity(self, identity: Dict[str, Any]) -> None:
        """Persiste el IdentityVault (upsert, siempre una fila)."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        now = time.time()

        await self._pool.execute("""
            INSERT INTO identity
            (id, name, vectors, values, purpose, birth_timestamp, identity_hash, updated_at)
            VALUES (1, $1, $2, $3, $4, $5, $6, NOW())
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                vectors = EXCLUDED.vectors,
                values = EXCLUDED.values,
                purpose = EXCLUDED.purpose,
                birth_timestamp = EXCLUDED.birth_timestamp,
                identity_hash = EXCLUDED.identity_hash,
                updated_at = NOW()
        """,
            identity.get("name", "Zoe"),
            json.dumps(identity.get("vectors", [])),
            json.dumps(identity.get("values", [])),
            identity.get("purpose", ""),
            identity.get("birth_timestamp", now),
            identity.get("identity_hash", ""),
        )
        logger.info("Identity saved to PostgreSQL")

    async def get_identity(self) -> Optional[Dict[str, Any]]:
        """Recupera el IdentityVault."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        row = await self._pool.fetchrow("SELECT * FROM identity WHERE id = 1")
        if row is None:
            return None

        row = dict(row)
        return {
            "name": row["name"],
            "vectors": json.loads(row["vectors"]),
            "values": json.loads(row["values"]),
            "purpose": row["purpose"],
            "birth_timestamp": row["birth_timestamp"],
            "identity_hash": row["identity_hash"],
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }

    # ------------------------------------------------------------------
    # Trayectoria
    # ------------------------------------------------------------------

    async def save_trajectory(self, entry: Dict[str, Any]) -> None:
        """Añade una mutación a la trayectoria."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        await self._pool.execute("""
            INSERT INTO trajectory
            (mutation_id, mutation_type, target, payload, justification,
             provenance, cost, confidence, mutation_timestamp, signature,
             prev_hash, mutation_hash, applied, rolled_back)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            ON CONFLICT (mutation_id) DO UPDATE SET
                applied = EXCLUDED.applied,
                rolled_back = EXCLUDED.rolled_back,
                mutation_hash = EXCLUDED.mutation_hash
        """,
            entry.get("id", ""),
            entry.get("type", ""),
            entry.get("target", ""),
            json.dumps(entry.get("payload", {})),
            entry.get("justification", ""),
            entry.get("provenance", ""),
            entry.get("cost", 0.0),
            entry.get("confidence", 0.5),
            entry.get("timestamp", time.time()),
            entry.get("signature", ""),
            entry.get("prev_hash", ""),
            entry.get("hash", ""),
            entry.get("applied", True),
            entry.get("rolled_back", False),
        )

    async def get_trajectory(self) -> List[Dict[str, Any]]:
        """Recupera toda la cadena de mutaciones."""
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        rows = await self._pool.fetch(
            "SELECT * FROM trajectory ORDER BY mutation_timestamp ASC"
        )

        result = []
        for row in rows:
            row = dict(row)
            result.append({
                "id": row["mutation_id"],
                "type": row["mutation_type"],
                "target": row["target"],
                "payload": json.loads(row["payload"]),
                "justification": row["justification"],
                "provenance": row["provenance"],
                "cost": row["cost"],
                "confidence": row["confidence"],
                "timestamp": row["mutation_timestamp"],
                "signature": row["signature"],
                "prev_hash": row["prev_hash"],
                "hash": row["mutation_hash"],
                "applied": row["applied"],
                "rolled_back": row["rolled_back"],
            })
        return result

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """SELECT 1 para verificar que PostgreSQL responde."""
        try:
            if self._pool is None:
                return False
            result = await self._pool.fetchrow("SELECT 1 as alive")
            return result is not None and result.get("alive") == 1
        except Exception as e:
            logger.warning(f"PostgreSQL health check failed: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del backend."""
        if self._pool is None:
            return {"connected": False}

        total = await self._pool.fetchval("SELECT COUNT(*) FROM memory_entries")

        rows = await self._pool.fetch(
            "SELECT type, COUNT(*) as c FROM memory_entries GROUP BY type"
        )
        by_type: Dict[str, int] = {r["type"]: r["c"] for r in rows}
        for t in MEMORY_TYPES:
            if t not in by_type:
                by_type[t] = 0

        mutations = await self._pool.fetchval("SELECT COUNT(*) FROM trajectory")
        has_identity = await self._pool.fetchval(
            "SELECT COUNT(*) FROM identity"
        ) > 0

        # Pool stats
        pool_size = self._pool.get_size()
        # Sprint 5.24 F3v2-3 (BUG-019 fix): asyncpg Pool usa get_idle_size
        # (no get_free_size que no existe). Antes esto crasheaba con
        # AttributeError cuando se llamaba get_stats().
        pool_free = self._pool.get_idle_size() if hasattr(self._pool, 'get_idle_size') else 0

        return {
            "backend": "postgresql",
            "host": f"{self.host}:{self.port}",
            "database": self.database,
            "connected": True,
            "total_entries": total,
            "by_type": by_type,
            "types_active": sum(1 for c in by_type.values() if c > 0),
            "total_mutations": mutations,
            "has_identity": has_identity,
            "pool_size": pool_size,
            "pool_free": pool_free,
        }

    # ------------------------------------------------------------------
    # Migraciones (alembic-compatible)
    # ------------------------------------------------------------------

    async def get_schema_version(self) -> Optional[str]:
        """Devuelve la versión actual del schema (para migraciones)."""
        if self._pool is None:
            return None
        try:
            row = await self._pool.fetchrow(
                "SELECT value FROM storage_metadata WHERE key = 'schema_version'"
            )
            if row:
                val = json.loads(row["value"])
                return val.get("version")
            return None
        except Exception:
            return None

    async def set_schema_version(self, version: str) -> None:
        """Actualiza la versión del schema."""
        if self._pool is None:
            return
        await self._pool.execute("""
            INSERT INTO storage_metadata (key, value, updated_at)
            VALUES ('schema_version', $1, NOW())
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                updated_at = NOW()
        """, json.dumps({"version": version}))

    # ------------------------------------------------------------------
    # Búsquedas avanzadas (PostgreSQL-specific)
    # ------------------------------------------------------------------

    async def search_memory_fulltext(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda full-text PostgreSQL (requiere pg_trgm).

        Más potente que search_memory: usa índices GIN para
        búsqueda rápida en contenido.
        """
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        rows = await self._pool.fetch("""
            SELECT * FROM memory_entries
            WHERE content ILIKE $1
            ORDER BY salience DESC, timestamp DESC
            LIMIT $2
        """, f"%{query}%", limit)

        return [self._row_to_entry(dict(r)) for r in rows]

    async def search_memory_jsonb(
        self, key: str, value: Any, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda dentro de JSONB metadata.

        Args:
            key: clave dentro de metadata
            value: valor a buscar
            limit: máximo resultados
        """
        if self._pool is None:
            raise RuntimeError("Backend not connected")

        rows = await self._pool.fetch("""
            SELECT * FROM memory_entries
            WHERE metadata @> $1::jsonb
            LIMIT $2
        """, json.dumps({key: value}), limit)

        return [self._row_to_entry(dict(r)) for r in rows]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _row_to_entry(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte una row asyncpg a dict Python."""
        extra_data = row.get("extra_data")
        if isinstance(extra_data, str):
            extra = json.loads(extra_data) if extra_data else {}
        elif isinstance(extra_data, dict):
            extra = extra_data
        else:
            extra = {}

        # Manejar JSONB (asyncpg lo devuelve como dict/list nativo)
        merged_from = row.get("merged_from", [])
        if isinstance(merged_from, str):
            merged_from = json.loads(merged_from)

        contradictions = row.get("contradictions", [])
        if isinstance(contradictions, str):
            contradictions = json.loads(contradictions)

        metadata = row.get("metadata", {})
        if isinstance(metadata, str):
            metadata = json.loads(metadata)

        result = {
            "id": row["id"],
            "entry_id": row["entry_id"],
            "type": row["type"],
            "content": row["content"],
            "confidence": row["confidence"],
            "salience": row["salience"],
            "provenance": row["provenance"],
            "timestamp": row["timestamp"],
            "last_access": row["last_access"],
            "access_count": row["access_count"],
            "merged_from": merged_from,
            "contradictions": contradictions,
            "metadata": metadata,
            "created_at": row.get("created_at"),
        }
        result.update(extra)
        return result
