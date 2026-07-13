"""
ZOE v1.0 — Persistent Memory Store (Fase 3.4)

Backing store SQLite para LivingMemory. Permite que la memoria
persista entre sesiones del organismo.

- save_to_disk(): guarda todas las entries en SQLite
- load_from_disk(): carga entries desde SQLite
- Auto-save opcional (cada N operaciones)
- Formato: una tabla por tipo de memoria (11 tablas)

La persistencia es transparente para LivingMemory: se añade como
capa inferior sin modificar la API existente.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PersistentMemoryStore:
    """
    Almacén persistente para LivingMemory usando SQLite.

    Mantiene las entries del organismo entre sesiones.
    Cada tipo de memoria (11 tipos) se almacena en una tabla separada.
    """

    def __init__(self, db_path: str = "zoe_data/memory.db", auto_save_interval: int = 50):
        """
        Args:
            db_path: ruta al archivo SQLite
            auto_save_interval: cada cuántas operaciones hacer auto-save (0 = desactivado)
        """
        self.db_path = db_path
        self.auto_save_interval = auto_save_interval
        self._operation_count: int = 0
        self._conn: Optional[sqlite3.Connection] = None
        self._initialized: bool = False

    def _ensure_connection(self) -> sqlite3.Connection:
        """Asegura que la conexión está abierta y las tablas creadas."""
        if self._conn is None:
            # Crear directorio si no existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.row_factory = sqlite3.Row

        if not self._initialized:
            self._create_tables_internal()
            self._initialized = True

        return self._conn

    def _create_tables_internal(self) -> None:
        """Crea las tablas (interna, sin llamar _ensure_connection)."""
        conn = self._conn
        if conn is None:
            return
        cursor = conn.cursor()

        # Tabla general de entries (todas los tipos en una tabla con columna type)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
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
                metadata TEXT DEFAULT '{}'
            )
        """)

        # Índice por tipo para búsquedas rápidas
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON memory_entries(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_salience ON memory_entries(salience DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp DESC)")

        conn.commit()
        logger.debug(f"PersistentMemoryStore tables created at {self.db_path}")

    def save_entry(self, entry: Any) -> None:
        """Guarda una entry en SQLite."""
        conn = self._ensure_connection()
        cursor = conn.cursor()

        # Serializar campos complejos
        merged_from = json.dumps(getattr(entry, "merged_from", []))
        contradictions = json.dumps(getattr(entry, "contradictions", []))
        metadata = json.dumps(getattr(entry, "metadata", {}))

        cursor.execute("""
            INSERT OR REPLACE INTO memory_entries
            (id, type, content, confidence, salience, provenance, timestamp,
             last_access, access_count, merged_from, contradictions, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.type,
            entry.content,
            getattr(entry, "confidence", 0.5),
            getattr(entry, "salience", 0.5),
            getattr(entry, "provenance", ""),
            getattr(entry, "timestamp", 0.0),
            getattr(entry, "last_access", 0.0),
            getattr(entry, "access_count", 0),
            merged_from,
            contradictions,
            metadata,
        ))

        conn.commit()
        self._increment_operation()

    def save_all(self, entries: Dict[str, Any]) -> int:
        """
        Guarda todas las entries en SQLite.

        Args:
            entries: dict de {entry_id: MemoryEntry}

        Returns:
            Número de entries guardadas
        """
        conn = self._ensure_connection()
        cursor = conn.cursor()
        count = 0

        for entry_id, entry in entries.items():
            merged_from = json.dumps(getattr(entry, "merged_from", []))
            contradictions = json.dumps(getattr(entry, "contradictions", []))
            metadata = json.dumps(getattr(entry, "metadata", {}))

            cursor.execute("""
                INSERT OR REPLACE INTO memory_entries
                (id, type, content, confidence, salience, provenance, timestamp,
                 last_access, access_count, merged_from, contradictions, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id,
                entry.type,
                entry.content,
                getattr(entry, "confidence", 0.5),
                getattr(entry, "salience", 0.5),
                getattr(entry, "provenance", ""),
                getattr(entry, "timestamp", 0.0),
                getattr(entry, "last_access", 0.0),
                getattr(entry, "access_count", 0),
                merged_from,
                contradictions,
                metadata,
            ))
            count += 1

        conn.commit()
        logger.info(f"PersistentMemoryStore: {count} entries saved to {self.db_path}")
        return count

    def load_all(self) -> List[Dict[str, Any]]:
        """
        Carga todas las entries desde SQLite.

        Returns:
            Lista de dicts con datos de entries
        """
        conn = self._ensure_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM memory_entries ORDER BY timestamp DESC")
        rows = cursor.fetchall()

        entries = []
        for row in rows:
            entries.append({
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "confidence": row["confidence"],
                "salience": row["salience"],
                "provenance": row["provenance"],
                "timestamp": row["timestamp"],
                "last_access": row["last_access"],
                "access_count": row["access_count"],
                "merged_from": json.loads(row["merged_from"]),
                "contradictions": json.loads(row["contradictions"]),
                "metadata": json.loads(row["metadata"]),
            })

        logger.info(f"PersistentMemoryStore: {len(entries)} entries loaded from {self.db_path}")
        return entries

    def load_by_type(self, mem_type: str) -> List[Dict[str, Any]]:
        """Carga entries de un tipo específico."""
        conn = self._ensure_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM memory_entries WHERE type = ? ORDER BY timestamp DESC",
            (mem_type,)
        )
        rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "type": row["type"],
                "content": row["content"],
                "confidence": row["confidence"],
                "salience": row["salience"],
                "provenance": row["provenance"],
                "timestamp": row["timestamp"],
                "last_access": row["last_access"],
                "access_count": row["access_count"],
                "merged_from": json.loads(row["merged_from"]),
                "contradictions": json.loads(row["contradictions"]),
                "metadata": json.loads(row["metadata"]),
            }
            for row in rows
        ]

    def delete_entry(self, entry_id: str) -> bool:
        """Elimina una entry por ID."""
        conn = self._ensure_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory_entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0

    def clear(self) -> int:
        """Borra todas las entries. Returns count deleted."""
        conn = self._ensure_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM memory_entries")
        count = cursor.fetchone()["c"]
        cursor.execute("DELETE FROM memory_entries")
        conn.commit()
        return count

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Búsqueda simple por texto (LIKE)."""
        conn = self._ensure_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM memory_entries WHERE content LIKE ? ORDER BY salience DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def count(self) -> int:
        """Número total de entries."""
        conn = self._ensure_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c FROM memory_entries")
        return cursor.fetchone()["c"]

    def count_by_type(self) -> Dict[str, int]:
        """Conteo por tipo de memoria."""
        conn = self._ensure_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type, COUNT(*) as c FROM memory_entries GROUP BY type"
        )
        return {row["type"]: row["c"] for row in cursor.fetchall()}

    def _increment_operation(self) -> None:
        """Incrementa contador y auto-save si procede."""
        self._operation_count += 1
        if self.auto_save_interval > 0 and self._operation_count % self.auto_save_interval == 0:
            logger.debug(f"PersistentMemoryStore: auto-save at {self._operation_count} operations")

    def close(self) -> None:
        """Cierra la conexión."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._initialized = False

    def get_stats(self) -> Dict[str, Any]:
        return {
            "db_path": self.db_path,
            "total_entries": self.count(),
            "by_type": self.count_by_type(),
            "operations": self._operation_count,
            "auto_save_interval": self.auto_save_interval,
        }


class PersistentLivingMemory:
    """
    Wrapper de LivingMemory con persistencia automática.

    Extiende LivingMemory con:
    - save_to_disk(): guarda todo a SQLite
    - load_from_disk(): carga todo desde SQLite
    - Auto-save cada N operaciones
    """

    def __init__(self, living_memory: Any, store: PersistentMemoryStore):
        self.memory = living_memory
        self.store = store
        self._auto_save_counter: int = 0
        self._auto_save_threshold: int = store.auto_save_interval

    def save_to_disk(self) -> int:
        """Guarda toda la memoria a disco."""
        return self.store.save_all(self.memory._entries)

    def load_from_disk(self) -> int:
        """Carga memoria desde disco al LivingMemory."""
        from ..core.living_memory import MemoryEntry

        entries_data = self.store.load_all()
        count = 0

        for data in entries_data:
            entry = MemoryEntry(
                id=data["id"],
                type=data["type"],
                content=data["content"],
                confidence=data["confidence"],
                salience=data["salience"],
                provenance=data["provenance"],
                timestamp=data["timestamp"],
                last_access=data["last_access"],
                access_count=data["access_count"],
                merged_from=data["merged_from"],
                contradictions=data["contradictions"],
                metadata=data["metadata"],
            )
            self.memory._entries[entry.id] = entry
            count += 1

        # Actualizar next_id para evitar colisiones
        max_id = 0
        for eid in self.memory._entries:
            parts = eid.split("_")
            if len(parts) >= 2 and parts[-1].isdigit():
                max_id = max(max_id, int(parts[-1]))
        self.memory._next_id = max_id + 1

        logger.info(f"PersistentLivingMemory: {count} entries loaded from disk")
        return count

    def maybe_auto_save(self) -> bool:
        """Auto-save si se ha superado el threshold."""
        self._auto_save_counter += 1
        if self._auto_save_threshold > 0 and self._auto_save_counter >= self._auto_save_threshold:
            self.save_to_disk()
            self._auto_save_counter = 0
            return True
        return False

    def clear_disk(self) -> int:
        """Borra todo del disco."""
        return self.store.clear()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "memory_stats": self.memory.get_stats(),
            "store_stats": self.store.get_stats(),
            "auto_save_counter": self._auto_save_counter,
        }
