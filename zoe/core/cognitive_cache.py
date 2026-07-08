"""
ZOE v1.0 — Cognitive Cache (Fase 5: ACD)

Cache LRU en memoria para respuestas idempotentes.
Clave = hash del input normalizado.

- Tamaño configurable (default 100 entries)
- TTL configurable (default 300s = 5min)
- Invalidación por sesión o por nivel
- Estadísticas de hit/miss

NO persiste a disco: es volátil, solo para reducir latencia en sesión activa.
La persistencia real está en LivingMemory + PersistentMemoryStore.

Implementa la 2da ley (utilidad): no recalcula lo que ya sabe.
"""

from __future__ import annotations

import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada del cache."""
    value: str
    level: str  # CognitiveLevel.value
    timestamp: float = field(default_factory=time.time)
    hits: int = 0


class CognitiveCache:
    """
    Cache LRU con TTL para respuestas cognitivas.

    Uso típico:
        cache = CognitiveCache(max_size=100, ttl_seconds=300)
        cached = cache.get(key)
        if cached:
            return cached
        response = await expensive_pipeline(...)
        cache.put(key, response, level)
        return response
    """

    def __init__(
        self,
        max_size: int = 100,
        ttl_seconds: int = 300,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()

        # Estadísticas
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0

    def get(self, key: str) -> Optional[str]:
        """
        Recupera valor del cache. Devuelve None si miss/expirado.

        LRU: si hit, mueve al final (más reciente).
        """
        if not key:
            self.misses += 1
            return None

        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None

        # Verificar TTL
        if time.time() - entry.timestamp > self.ttl_seconds:
            del self._store[key]
            self.expirations += 1
            self.misses += 1
            return None

        # Hit
        entry.hits += 1
        self.hits += 1
        # Mover al final (LRU)
        self._store.move_to_end(key)
        return entry.value

    def put(self, key: str, value: str, level: str = "L2_STANDARD") -> None:
        """Inserta/actualiza entrada. Eviction LRU si supera max_size."""
        if not key:
            return

        # Si ya existe, actualizar
        if key in self._store:
            self._store[key].value = value
            self._store[key].level = level
            self._store[key].timestamp = time.time()
            self._store.move_to_end(key)
            return

        # Eviction si necesario
        while len(self._store) >= self.max_size:
            self._store.popitem(last=False)  # más viejo
            self.evictions += 1

        self._store[key] = CacheEntry(value=value, level=level)

    def invalidate(self, key: str) -> bool:
        """Invalida entrada específica."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> int:
        """Limpia todo. Devuelve cuántas entries borradas."""
        n = len(self._store)
        self._store.clear()
        return n

    def cleanup_expired(self) -> int:
        """Elimina entries expiradas. Devuelve cuántas borró."""
        now = time.time()
        expired_keys = [
            k for k, e in self._store.items()
            if now - e.timestamp > self.ttl_seconds
        ]
        for k in expired_keys:
            del self._store[k]
        self.expirations += len(expired_keys)
        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del cache."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "size": len(self._store),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "evictions": self.evictions,
            "expirations": self.expirations,
            "ttl_seconds": self.ttl_seconds,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Resumen serializable."""
        return {
            "stats": self.get_stats(),
            "levels": self._level_distribution(),
        }

    def _level_distribution(self) -> Dict[str, int]:
        dist: Dict[str, int] = {}
        for entry in self._store.values():
            dist[entry.level] = dist.get(entry.level, 0) + 1
        return dist
