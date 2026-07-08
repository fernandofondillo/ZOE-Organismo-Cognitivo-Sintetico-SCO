"""
ZOE v1.0 — World Model (mínimo, Fase 0)

Predice el próximo input basado en historial.
En Fase 0 es un predictor simple basado en embeddings + memoria.

En fases posteriores evoluciona a JEPA-style neural predictor.
"""

from __future__ import annotations

import hashlib
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def _simple_hash_embedding(text: str, dim: int = 64) -> List[float]:
    """Embedding determinístico simple basado en hash (para Fase 0).

    En Fase 2 se reemplaza por sentence-transformers real.
    """
    vec = [0.0] * dim
    h = hashlib.sha256(text.encode()).digest()
    for i in range(dim):
        # Usar bytes del hash para generar valores
        byte_idx = (i * 4) % len(h)
        chunk = h[byte_idx : byte_idx + 4]
        val = int.from_bytes(chunk, "big") / 0xFFFFFFFF
        vec[i] = (val * 2) - 1.0  # normalizar a [-1, 1]
    # L2 normalize
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine_distance(a: List[float], b: List[float]) -> float:
    """Distancia coseno entre dos vectores (0 = idénticos, 2 = opuestos)."""
    if not a or not b or len(a) != len(b):
        return 1.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 1.0
    cos_sim = dot / (norm_a * norm_b)
    return 1.0 - cos_sim  # 0 = idéntico, 2 = opuesto


@dataclass
class WorldModel:
    """
    World Model mínimo: predice próximo input basado en historial.

    Estrategia Fase 0:
    - Mantiene historial de observaciones recientes (con embeddings)
    - Predice que el próximo input será similar al último visto
    - Surprise = distancia entre predicción y observación real
    - Si input es muy novedoso (poca similitud con historial), surprise alta
    """

    history_size: int = 50
    history: deque = field(default_factory=lambda: deque(maxlen=50))
    embedding_dim: int = 64
    novelty_threshold: float = 0.7  # distancia coseno sobre la cual es "novedoso"

    def __post_init__(self):
        if len(self.history) > self.history_size:
            self.history = deque(self.history, maxlen=self.history_size)
        else:
            self.history = deque(self.history, maxlen=self.history_size)

    async def predict_next(
        self, recent_observations: List[Any]
    ) -> Dict[str, Any]:
        """
        Predice el próximo estado basado en historial.

        En Fase 0: predice "más de lo mismo" (estabilidad).
        Surprise aparecerá cuando la realidad rompa el patrón.
        """
        # Si no hay historial, predicción nula con baja confianza
        if not self.history:
            return {
                "predicted_source": "unknown",
                "predicted_embedding": None,
                "confidence": 0.0,
                "strategy": "no_history",
            }

        # Tomar últimas observaciones del historial
        recent = list(self.history)[-5:] if self.history else []

        # Estrategia simple: predecir que la próxima observación será similar a la última
        last = recent[-1] if recent else None
        if last is None:
            return {
                "predicted_source": "unknown",
                "predicted_embedding": None,
                "confidence": 0.0,
                "strategy": "empty_history",
            }

        # Si las últimas observaciones son similares entre sí (patrón estable),
        # predecir más de lo mismo con alta confianza
        if len(recent) >= 2:
            distances = []
            for i in range(1, len(recent)):
                d = _cosine_distance(
                    recent[i - 1].get("embedding", []),
                    recent[i].get("embedding", []),
                )
                distances.append(d)
            avg_distance = sum(distances) / len(distances) if distances else 1.0
            confidence = max(0.0, 1.0 - avg_distance)
        else:
            confidence = 0.3

        return {
            "predicted_source": last.get("source", "unknown"),
            "predicted_embedding": last.get("embedding"),
            "predicted_content_preview": last.get("content", "")[:80],
            "confidence": confidence,
            "strategy": "pattern_continuation",
            "history_size": len(self.history),
        }

    async def compute_surprise(
        self, prediction: Dict[str, Any], actual_observations: List[Any]
    ) -> float:
        """
        Calcula sorpresa: diferencia entre predicción y realidad.

        Returns:
            surprise (0-1): 0 = nada de sorpresa, 1 = sorpresa máxima
        """
        if not actual_observations:
            return 0.0

        # Tomar la última observación real
        actual = actual_observations[-1]
        actual_embedding = None
        actual_source = "unknown"
        actual_content = ""

        if hasattr(actual, "embedding"):
            actual_embedding = actual.embedding
        if hasattr(actual, "source"):
            actual_source = actual.source
        if hasattr(actual, "content"):
            actual_content = actual.content
        elif isinstance(actual, dict):
            actual_embedding = actual_embedding or actual.get("embedding")
            actual_source = actual.get("source", "unknown")
            actual_content = actual.get("content", "")

        # Si no hay embedding real, calcularlo del contenido
        if actual_embedding is None:
            actual_embedding = _simple_hash_embedding(actual_content, self.embedding_dim)

        predicted_embedding = prediction.get("predicted_embedding")

        # Añadir SIEMPRE al historial (incluso si no hay predicción previa)
        self._add_to_history(
            source=actual_source,
            content=actual_content,
            embedding=actual_embedding,
        )

        # Si no hay predicción, sorpresa = 0.5 (neutral)
        if predicted_embedding is None:
            return 0.5

        # Calcular distancia coseno
        distance = _cosine_distance(predicted_embedding, actual_embedding)

        # Convertir distancia a sorpresa (0-1)
        # distance=0 → surprise=0, distance=2 → surprise=1
        surprise = min(1.0, distance / 2.0)

        # Ajustar por confianza de la predicción
        confidence = prediction.get("confidence", 0.5)
        # Si la confianza era alta y la distancia también, más sorpresa
        adjusted_surprise = surprise * (0.5 + confidence * 0.5)

        return float(min(1.0, adjusted_surprise))

    def _add_to_history(
        self,
        source: str,
        content: str,
        embedding: Optional[List[float]] = None,
    ) -> None:
        """Añade observación al historial."""
        self.history.append(
            {
                "source": source,
                "content": content[:200],  # acotar
                "embedding": embedding or [],
                "timestamp": time.time(),
            }
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            "history_size": len(self.history),
            "embedding_dim": self.embedding_dim,
            "novelty_threshold": self.novelty_threshold,
        }
