"""
ZOE v1.0 — SQLite Backend

Implementación de StorageBackend usando SQLite con WAL mode.
Extraído y refactorizado desde zoe/memory/persistent_store.py.

Mantiene compatibilidad total con el schema existente:
- Tabla memory_entries (todas las entries con columna type)
- Tablas identity y trajectory para persistencia de alma y cadena
- WAL mode para concurrencia
- Índices optimizados
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import StorageBackend

logger = logging.getLogger(__name__)

# Los 11 tipos de memoria soportados
MEMORY_TYPES = [
    "episodic", "semantic", "procedural", "causal", "emotional",
    "corporeal", "social", "prospective", "counterfactual",
    "evolutionary", "cultural",
]


class SQLiteBackend(StorageBackend):
    """
    Backend SQLite para ZOE con WAL mode y operaciones async-friendly.

    Es el backend por defecto: no requiere servidor externo,
    es zero-config, y suficiente para deployments locales.
    """

    def __init__(
        self,
        db_path: str = "zoe_data/memory.db",
        auto_save_interval: int = 50,
    ):
        self.db_path = db_path
        self.auto_save_interval = auto_save_interval
        self._operation_count: int = 0
        self._conn: Optional[sqlite3.Connection] = None
        self._initialized: bool = False

    # ------------------------------------------------------------------
    # Ciclo de vida (async)
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Abre conexión SQLite, crea tablas e índices."""
        if self._conn is not None:
            return

        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.row_factory = sqlite3.Row

        if not self._initialized:
            self._create_tables()
            self._initialized = True

        logger.info(f"SQLiteBackend connected: {self.db_path} (WAL mode)")

    async def disconnect(self) -> None:
        """Cierra la conexión."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._initialized = False
            logger.info("SQLiteBackend disconnected")

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _create_tables(self) -> None:
        """Crea todas las tablas e índices."""
        conn = self._conn
        if conn is None:
            return
        cursor = conn.cursor()

        # Tabla principal: entries de memoria (todos los tipos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                salience REAL DEFAULT 0.5,
                provenance TEXT DEFAULT '',
                timestamp REAL DEFAULT 0,
                last_access REAL DEFAULT 0,
                access_count INTEGER DEFAULT 0,
                merged_from TEXT DEFAULT '[]',
                contradictions TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                extra_data TEXT DEFAULT '{}'
            )
        """)

        # Tabla de identidad (solo una fila, siempre)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS identity (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL DEFAULT 'Zoe',
                vectors TEXT NOT NULL DEFAULT '[]',
                values TEXT NOT NULL DEFAULT '[]',
                purpose TEXT NOT NULL DEFAULT '',
                birth_timestamp REAL DEFAULT 0,
                identity_hash TEXT DEFAULT '',
                updated_at REAL DEFAULT 0
            )
        """)

        # Tabla de trayectoria (mutaciones)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trajectory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mutation_id TEXT UNIQUE NOT NULL,
                mutation_type TEXT NOT NULL,
                target TEXT NOT NULL,
                payload TEXT DEFAULT '{}',
                justification TEXT DEFAULT '',
                provenance TEXT DEFAULT '',
                cost REAL DEFAULT 0.0,
                confidence REAL DEFAULT 0.5,
                mutation_timestamp REAL DEFAULT 0,
                signature TEXT DEFAULT '',
                prev_hash TEXT DEFAULT '',
                mutation_hash TEXT DEFAULT '',
                applied INTEGER DEFAULT 1,
                rolled_back INTEGER DEFAULT 0
            )
        """)

        # Tabla de metadatos del backend
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL DEFAULT 0
            )
        """)

        # Índices optimizados
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_me_type ON memory_entries(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_me_salience ON memory_entries(salience DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_me_timestamp ON memory_entries(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_me_content ON memory_entries(content)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_traj_type ON trajectory(mutation_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_traj_ts ON trajectory(mutation_timestamp DESC)")

        conn.commit()
        logger.debug("SQLiteBackend: all tables and indexes created")

    # ------------------------------------------------------------------
    # Memoria
    # ------------------------------------------------------------------

    async def save_memory(self, entry_type: str, data: Dict[str, Any]) -> int:
        """Guarda una entry de memoria."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected. Call connect() first.")

        cursor = conn.cursor()
        now = time.time()
        entry_id = data.get("id", f"{entry_type}_{int(now * 1000)}")

        cursor.execute("""
            INSERT OR REPLACE INTO memory_entries
            (entry_id, type, content, confidence, salience, provenance, timestamp,
             last_access, access_count, merged_from, contradictions, metadata, extra_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
            json.dumps({k: v for k, v in data.items()
                        if k not in {"id", "content", "type", "confidence", "salience",
                                     "provenance", "timestamp", "last_access", "access_count",
                                     "merged_from", "contradictions", "metadata"}}),
        ))
        conn.commit()
        row_id = cursor.lastrowid
        self._increment_operation()
        return row_id

    async def get_memory(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Recupera una entry por ID numérico."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memory_entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_entry(dict(row))

    async def search_memory(
        self, entry_type: str, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Búsqueda por contenido (LIKE) dentro de un tipo."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_entries
            WHERE type = ? AND content LIKE ?
            ORDER BY salience DESC, timestamp DESC
            LIMIT ?
        """, (entry_type, f"%{query}%", limit))
        rows = cursor.fetchall()
        return [self._row_to_entry(dict(r)) for r in rows]

    async def delete_memory(self, entry_id: int) -> bool:
        """Elimina una entry por ID numérico."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory_entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0

    async def list_by_type(self, entry_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Lista entries de un tipo específico."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_entries WHERE type = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (entry_type, limit))
        rows = cursor.fetchall()
        return [self._row_to_entry(dict(r)) for r in rows]

    async def update_memory(self, entry_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza campos de una entry existente."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        now = time.time()

        # Campos permitidos para update
        allowed = {"content", "confidence", "salience", "provenance",
                   "last_access", "access_count", "metadata", "extra_data"}
        updates = {k: v for k, v in data.items() if k in allowed}
        if not updates:
            return False

        # Serializar JSON
        for json_field in ("metadata", "extra_data"):
            if json_field in updates and isinstance(updates[json_field], (dict, list)):
                updates[json_field] = json.dumps(updates[json_field])

        updates["last_access"] = now
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [entry_id]

        cursor.execute(f"UPDATE memory_entries SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Identidad
    # ------------------------------------------------------------------

    async def save_identity(self, identity: Dict[str, Any]) -> None:
        """Persiste el IdentityVault (siempre una sola fila)."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        now = time.time()

        cursor.execute("""
            INSERT OR REPLACE INTO identity
            (id, name, vectors, values, purpose, birth_timestamp, identity_hash, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """, (
            identity.get("name", "Zoe"),
            json.dumps(identity.get("vectors", [])),
            json.dumps(identity.get("values", [])),
            identity.get("purpose", ""),
            identity.get("birth_timestamp", now),
            identity.get("identity_hash", ""),
            now,
        ))
        conn.commit()
        logger.info("Identity saved to SQLite")

    async def get_identity(self) -> Optional[Dict[str, Any]]:
        """Recupera el IdentityVault."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM identity WHERE id = 1")
        row = cursor.fetchone()
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
            "updated_at": row["updated_at"],
        }

    # ------------------------------------------------------------------
    # Trayectoria
    # ------------------------------------------------------------------

    async def save_trajectory(self, entry: Dict[str, Any]) -> None:
        """Añade una mutación a la trayectoria."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO trajectory
            (mutation_id, mutation_type, target, payload, justification,
             provenance, cost, confidence, mutation_timestamp, signature,
             prev_hash, mutation_hash, applied, rolled_back)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
            1 if entry.get("applied", False) else 0,
            1 if entry.get("rolled_back", False) else 0,
        ))
        conn.commit()

    async def get_trajectory(self) -> List[Dict[str, Any]]:
        """Recupera toda la cadena de mutaciones."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM trajectory ORDER BY mutation_timestamp ASC
        """)
        rows = cursor.fetchall()

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
                "applied": bool(row["applied"]),
                "rolled_back": bool(row["rolled_back"]),
            })
        return result

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """SELECT 1 para verificar que SQLite responde."""
        try:
            conn = self._conn
            if conn is None:
                return False
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return cursor.fetchone() is not None
        except Exception as e:
            logger.warning(f"SQLite health check failed: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del backend."""
        conn = self._conn
        if conn is None:
            return {"connected": False}

        cursor = conn.cursor()

        # Total entries
        cursor.execute("SELECT COUNT(*) as c FROM memory_entries")
        total = cursor.fetchone()["c"]

        # Por tipo
        cursor.execute("SELECT type, COUNT(*) as c FROM memory_entries GROUP BY type")
        by_type = {row["type"]: row["c"] for row in cursor.fetchall()}

        # Asegurar que todos los tipos aparezcan
        for t in MEMORY_TYPES:
            if t not in by_type:
                by_type[t] = 0

        # Mutations
        cursor.execute("SELECT COUNT(*) as c FROM trajectory")
        mutations = cursor.fetchone()["c"]

        # Identity
        cursor.execute("SELECT COUNT(*) as c FROM identity")
        has_identity = cursor.fetchone()["c"] > 0

        return {
            "backend": "sqlite",
            "db_path": self.db_path,
            "connected": True,
            "total_entries": total,
            "by_type": by_type,
            "types_active": sum(1 for c in by_type.values() if c > 0),
            "total_mutations": mutations,
            "has_identity": has_identity,
            "operations": self._operation_count,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _row_to_entry(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte una row de sqlite3.Row a dict Python."""
        extra = json.loads(row.get("extra_data", "{}"))
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
            "merged_from": json.loads(row.get("merged_from", "[]")),
            "contradictions": json.loads(row.get("contradictions", "[]")),
            "metadata": json.loads(row.get("metadata", "{}")),
        }
        result.update(extra)
        return result

    def _increment_operation(self) -> None:
        """Incrementa contador de operaciones."""
        self._operation_count += 1
        if self.auto_save_interval > 0 and self._operation_count % self.auto_save_interval == 0:
            logger.debug(f"SQLiteBackend: {self._operation_count} operations")

    # ------------------------------------------------------------------
    # Compatibilidad hacia atrás (métodos sincrónicos)
    # ------------------------------------------------------------------

    def save_entry_sync(self, entry: Any) -> None:
        """Método sincrónico para compatibilidad con código existente."""
        import asyncio
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        now = time.time()
        merged_from = json.dumps(getattr(entry, "merged_from", []))
        contradictions = json.dumps(getattr(entry, "contradictions", []))
        metadata = json.dumps(getattr(entry, "metadata", {}))

        cursor.execute("""
            INSERT OR REPLACE INTO memory_entries
            (entry_id, type, content, confidence, salience, provenance, timestamp,
             last_access, access_count, merged_from, contradictions, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            getattr(entry, "id", f"entry_{int(now * 1000)}"),
            getattr(entry, "type", "unknown"),
            getattr(entry, "content", ""),
            getattr(entry, "confidence", 0.5),
            getattr(entry, "salience", 0.5),
            getattr(entry, "provenance", ""),
            getattr(entry, "timestamp", now),
            getattr(entry, "last_access", now),
            getattr(entry, "access_count", 0),
            merged_from,
            contradictions,
            metadata,
        ))
        conn.commit()
        self._increment_operation()

    def load_all_sync(self) -> List[Dict[str, Any]]:
        """Carga todas las entries (método sincrónico)."""
        conn = self._conn
        if conn is None:
            raise RuntimeError("Backend not connected")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memory_entries ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        return [self._row_to_entry(dict(r)) for r in rows]
