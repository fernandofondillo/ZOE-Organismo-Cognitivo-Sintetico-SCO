"""
ZOE v2.1 — SemanticSearch (embeddings opcionales)

Capa de busqueda semantica que convive con Jaccard.
Usa sentence-transformers si esta disponible; si no, fallback a Jaccard.
Los embeddings se cachean por entry_id para evitar recalcular.
"""

from __future__ import annotations

import logging
import math
import os
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SemanticSearch:
    """
    Busqueda semantica basada en embeddings.

    - Genera embeddings del query y de las entries
    - Compara por similitud coseno
    - Cachea embeddings por entry_id
    - Fallback a Jaccard si sentence-transformers no esta instalado
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model = None
        self._model_name = model_name
        self._cache: Dict[str, list] = {}  # entry_id -> embedding vector
        self._available = False
        self._initialize()

    def _initialize(self) -> None:
        """Intenta cargar sentence-transformers. Si falla, desactiva."""
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            self._available = True
            logger.info(f"SemanticSearch: model '{self._model_name}' loaded")
        except ImportError:
            logger.info(
                "SemanticSearch: sentence-transformers not installed. "
                "Install with: pip install sentence-transformers. "
                "Falling back to Jaccard."
            )
            self._available = False
        except Exception as e:
            logger.warning(f"SemanticSearch: model load failed: {e}. Using Jaccard.")
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def compute_embedding(self, text: str) -> Optional[list]:
        """Computa embedding de un texto. Returns None si no disponible."""
        if not self._available or self._model is None:
            return None
        try:
            import numpy as np

            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.debug(f"SemanticSearch: embedding computation failed: {e}")
            return None

    def _cosine_similarity(self, a: list, b: list) -> float:
        """Similitud coseno entre dos vectores."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(
        self,
        query: str,
        entries: Dict[str, Any],
        n: int = 5,
        jaccard_fallback: bool = True,
    ) -> List[Tuple[float, Any]]:
        """
        Busca entries por similitud semantica (coseno) o Jaccard.

        Args:
            query: texto de busqueda
            entries: dict {entry_id: MemoryEntry}
            n: numero de resultados
            jaccard_fallback: si True, mezcla resultados semanticos con Jaccard

        Returns:
            Lista de (score, entry) ordenados por score descendente
        """
        if not self._available:
            # Fallback: devolver vacio para que el llamante use Jaccard
            return []

        query_embedding = self.compute_embedding(query)
        if query_embedding is None:
            return []

        scored = []
        for entry_id, entry in entries.items():
            # Verificar cache
            cached = self._cache.get(entry_id)
            if cached is None:
                entry_embedding = self.compute_embedding(entry.content)
                if entry_embedding is None:
                    continue
                self._cache[entry_id] = entry_embedding
                cached = entry_embedding

            score = self._cosine_similarity(query_embedding, cached)
            scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:n]

    def invalidate_cache(self, entry_id: str) -> None:
        """Invalida el embedding cacheado de una entry."""
        self._cache.pop(entry_id, None)

    def clear_cache(self) -> None:
        """Limpia toda la cache de embeddings."""
        self._cache.clear()

    def get_stats(self) -> dict:
        return {
            "available": self._available,
            "model": self._model_name if self._available else None,
            "cached_embeddings": len(self._cache),
        }
