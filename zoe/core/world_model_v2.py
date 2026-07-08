"""
ZOE v1.0 — World Model V2 (Fase 2.1)

World Model mejorado con embeddings más ricos que hash simple.
Intenta usar sentence-transformers si está disponible; si no, usa
un embedding basado en n-gramas de caracteres que captura más
similitud semántica que hash SHA-256.

Mejoras sobre V1:
- Embedding por n-gramas de caracteres (captura raíces de palabras)
- Predictor que aprende patrones (no solo "más de lo mismo")
- Sorpresa más precisa (distingue mejor novedad de rutina)
- Histórico de predicciones para evaluación
"""

from __future__ import annotations

import hashlib
import logging
import time
from collections import deque, Counter
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Intentar importar sentence-transformers (opcional)
try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
    _st_model = None  # lazy load
except ImportError:
    _ST_AVAILABLE = False
    _st_model = None


def _get_st_model():
    """Lazy load sentence-transformers model."""
    global _st_model
    if _st_model is None and _ST_AVAILABLE:
        try:
            _st_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("sentence-transformers model loaded: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers: {e}")
            return None
    return _st_model


def _ngram_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Embedding basado en n-gramas de caracteres.
    Captura más similitud semántica que hash SHA-256 porque
    palabras con raíces similares producen n-gramas similares.
    """
    vec = [0.0] * dim
    text_lower = text.lower().strip()

    # N-gramas de 2, 3 y 4 caracteres
    for n in [2, 3, 4]:
        for i in range(len(text_lower) - n + 1):
            ngram = text_lower[i:i + n]
            # Hash del n-grama a una posición del vector
            h = int(hashlib.md5(ngram.encode()).hexdigest(), 16) % dim
            vec[h] += 1.0

    # L2 normalizar
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _real_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Embedding real: usa sentence-transformers si disponible,
    si no, usa n-gramas.
    """
    if _ST_AVAILABLE:
        model = _get_st_model()
        if model is not None:
            try:
                emb = model.encode(text, normalize_embeddings=True)
                return emb.tolist()
            except Exception as e:
                logger.warning(f"ST embedding failed, using n-gram: {e}")

    return _ngram_embedding(text, dim)


def _cosine_distance(a: List[float], b: List[float]) -> float:
    """Distancia coseno (0 = idénticos, 2 = opuestos)."""
    if not a or not b or len(a) != len(b):
        return 1.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 1.0
    cos_sim = dot / (norm_a * norm_b)
    return max(0.0, 1.0 - cos_sim)


@dataclass
class WorldModelV2:
    """
    World Model V2 con embeddings mejorados y predictor que aprende.

    Mejoras sobre V1:
    - Embeddings por n-gramas (o sentence-transformers si disponible)
    - Predictor que aprende transiciones (no solo "más de lo mismo")
    - Mejor cálculo de sorpresa
    - Histórico de predicciones para evaluación
    """

    history_size: int = 100
    embedding_dim: int = 128
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    novelty_threshold: float = 0.7

    # Predictor de transiciones: qué source sigue a qué
    _transition_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    _source_history: deque = field(default_factory=lambda: deque(maxlen=50))

    # Histórico de sorpresas para calibración
    _surprise_history: deque = field(default_factory=lambda: deque(maxlen=50))
    _avg_surprise: float = 0.5

    # Estadísticas
    _predictions_made: int = 0
    _predictions_correct: int = 0

    def __post_init__(self):
        self.history = deque(self.history, maxlen=self.history_size)
        self._source_history = deque(self._source_history, maxlen=50)
        self._surprise_history = deque(self._surprise_history, maxlen=50)

    async def predict_next(self, recent_observations: List[Any]) -> Dict[str, Any]:
        """
        Predice el próximo estado basado en historial y transiciones aprendidas.
        """
        if not self.history:
            return {
                "predicted_source": "unknown",
                "predicted_embedding": None,
                "confidence": 0.0,
                "strategy": "no_history",
            }

        recent = list(self.history)[-5:]
        last = recent[-1] if recent else None
        if last is None:
            return {
                "predicted_source": "unknown",
                "predicted_embedding": None,
                "confidence": 0.0,
                "strategy": "empty_history",
            }

        # Estrategia 1: predecir basado en transiciones aprendidas
        last_source = last.get("source", "unknown")
        transitions = self._transition_counts.get(last_source, {})
        if transitions:
            # Source más probable después del último
            predicted_source = max(transitions, key=transitions.get)
            transition_confidence = transitions[predicted_source] / sum(transitions.values())
        else:
            predicted_source = last_source
            transition_confidence = 0.3

        # Estrategia 2: si las últimas observaciones son similares, predecir continuación
        if len(recent) >= 2:
            distances = []
            for i in range(1, len(recent)):
                d = _cosine_distance(
                    recent[i - 1].get("embedding", []),
                    recent[i].get("embedding", []),
                )
                distances.append(d)
            avg_distance = sum(distances) / len(distances) if distances else 1.0
            pattern_confidence = max(0.0, 1.0 - avg_distance)
        else:
            pattern_confidence = 0.3

        # Combinar confianzas
        confidence = (transition_confidence * 0.6 + pattern_confidence * 0.4)

        return {
            "predicted_source": predicted_source,
            "predicted_embedding": last.get("embedding"),
            "predicted_content_preview": last.get("content", "")[:80],
            "confidence": confidence,
            "strategy": "learned_transitions",
            "history_size": len(self.history),
            "transition_confidence": transition_confidence,
            "pattern_confidence": pattern_confidence,
        }

    async def compute_surprise(
        self, prediction: Dict[str, Any], actual_observations: List[Any]
    ) -> float:
        """Calcula sorpresa con mejor precisión que V1."""
        if not actual_observations:
            return 0.0

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

        # Generar embedding si no existe
        if actual_embedding is None:
            actual_embedding = _real_embedding(actual_content, self.embedding_dim)

        # Actualizar transiciones aprendidas
        if self._source_history:
            prev_source = self._source_history[-1]
            if prev_source not in self._transition_counts:
                self._transition_counts[prev_source] = {}
            self._transition_counts[prev_source][actual_source] = \
                self._transition_counts[prev_source].get(actual_source, 0) + 1

        self._source_history.append(actual_source)

        # Añadir al historial
        self.history.append({
            "source": actual_source,
            "content": actual_content[:200],
            "embedding": actual_embedding,
            "timestamp": time.time(),
        })

        # Añadir a surprise history
        predicted_embedding = prediction.get("predicted_embedding")
        predicted_source = prediction.get("predicted_source", "unknown")

        if predicted_embedding is None:
            surprise = 0.5
        else:
            # Distancia coseno
            distance = _cosine_distance(predicted_embedding, actual_embedding)
            surprise = min(1.0, distance / 2.0)

            # Bonus de sorpresa si el source predicho era incorrecto
            if predicted_source != actual_source and predicted_source != "unknown":
                surprise = min(1.0, surprise + 0.2)

            # Ajustar por confianza
            confidence = prediction.get("confidence", 0.5)
            surprise = surprise * (0.5 + confidence * 0.5)

        # Actualizar sorpresa promedio
        self._surprise_history.append(surprise)
        if self._surprise_history:
            self._avg_surprise = sum(self._surprise_history) / len(self._surprise_history)

        # Evaluar predicción (si el source predicho coincide)
        self._predictions_made += 1
        if predicted_source == actual_source:
            self._predictions_correct += 1

        return float(min(1.0, surprise))

    def get_prediction_accuracy(self) -> float:
        """Precisión de predicciones de source."""
        if self._predictions_made == 0:
            return 0.0
        return self._predictions_correct / self._predictions_made

    def get_stats(self) -> Dict[str, Any]:
        return {
            "history_size": len(self.history),
            "embedding_dim": self.embedding_dim,
            "embedding_backend": "sentence-transformers" if _ST_AVAILABLE else "n-gram",
            "transitions_learned": sum(len(v) for v in self._transition_counts.values()),
            "sources_tracked": list(self._transition_counts.keys()),
            "predictions_made": self._predictions_made,
            "prediction_accuracy": self.get_prediction_accuracy(),
            "avg_surprise": self._avg_surprise,
            "novelty_threshold": self.novelty_threshold,
        }

    def summary(self) -> str:
        return (
            f"WorldModelV2(history={len(self.history)}, "
            f"backend={'ST' if _ST_AVAILABLE else 'ngram'}, "
            f"accuracy={self.get_prediction_accuracy():.2f}, "
            f"avg_surprise={self._avg_surprise:.3f})"
        )
