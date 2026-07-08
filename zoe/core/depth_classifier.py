"""
ZOE v1.0 — Depth Classifier (Fase 5: ACD)

Clasificador de profundidad cognitiva. Decide, ANTES de entrar al bucle,
qué nivel de procesamiento necesita un input.

4 niveles (Kahneman-inspired):
- L0_REFLEX:    "hola", "ok", "gracias" → solo Speaker + cache. <1s.
- L1_FAST:      Pregunta factual, confirmación → Perceiver + Memorialist + Speaker. 2-4s.
- L2_STANDARD:  Conversación normal → Fase 0 + 4 sub-agentes principales. 6-10s.
- L3_DEEP:      Análisis causal, ética, creatividad → 12 sub-agentes + meta-cog. 15-30s.

Sin LLM. Heurístico. Objetivo: <50ms por clasificación.

Implementa:
- 2da ley (utilidad): solo gasta cómputo cuando aporta valor
- 4ta ley (coste): nivel → coste registrado
- 5ta ley (confianza): nivel → confianza en la respuesta
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CognitiveLevel(str, Enum):
    """Nivel de profundidad cognitiva."""
    L0_REFLEX = "L0_REFLEX"
    L1_FAST = "L1_FAST"
    L2_STANDARD = "L2_STANDARD"
    L3_DEEP = "L3_DEEP"

    @property
    def numeric(self) -> int:
        return {"L0_REFLEX": 0, "L1_FAST": 1, "L2_STANDARD": 2, "L3_DEEP": 3}[self.value]

    @property
    def cost(self) -> float:
        """Coste cognitivo (4ta ley)."""
        return {0: 0.05, 1: 0.10, 2: 0.30, 3: 0.60}[self.numeric]

    @property
    def default_confidence(self) -> float:
        """Confianza típica del nivel (5ta ley)."""
        return {0: 0.95, 1: 0.80, 2: 0.65, 3: 0.55}[self.numeric]


@dataclass
class ClassificationResult:
    """Resultado de clasificar un input."""
    level: CognitiveLevel
    score: float  # 0.0 - 1.0 (profundidad estimada)
    reasons: List[str]
    normalized_text: str
    cache_key: str
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "score": round(self.score, 4),
            "reasons": self.reasons,
            "cache_key": self.cache_key[:16],
            "timestamp": self.timestamp,
        }


# ---- Heurísticas ----

# L0 — Reflejos. Tokens que NO requieren pensar.
_L0_TOKENS = {
    # Saludos
    "hola", "holaa", "hello", "hi", "hey", "buenas", "buenosdias",
    "buenastardes", "buenasnoches", "quétal", "quetal", "quepasa",
    # Despedidas
    "adios", "adiós", "chao", "bye", "hastaluego", "nosvemos", "agur",
    # Acknowledgements
    "ok", "okay", "vale", "venga", "bien", "genial", "perfecto",
    "entendido", "claro", "sip", "sí", "si", "no", "nop", "nose",
    "gracias", "thanks", "thankyou", "muchasgracias", "denada",
    "nada", "nade", "de", "nada2",
    # Siglas / abreviaciones
    "k", "kk", "jeje", "jaja", "lol", "xD", "xd",
}

# L3 — Indicadores de profundidad. Palabras que piden análisis.
_L3_KEYWORDS = {
    # Análisis causal
    "analiza", "analizar", "analisis", "análisis", "causas", "consecuencias",
    "porque", "por qué", "porque", "porq", "razones", "fundamento",
    "explica", "explicar", "explicación", "justifica", "justificar",
    # Comparación / evaluación
    "compara", "comparar", "comparación", "diferencias", "similitudes",
    "evalúa", "evalua", "evaluar", "evaluación", "valora", "valora",
    "critica", "criticar", "crítica", "revisa", "revisar",
    # Dilemas / ética
    "dilema", "ético", "ética", "moral", "deberia", "debería", "correcto",
    "incorrecto", "responsabilidad", "principios", "valores",
    # Creatividad / diseño
    "diseña", "diseñar", "propón", "propon", "propone", "idear",
    "crea", "crear", "inventa", "brainstorm", "lluvia", "ideas",
    # Investigación
    "investiga", "investigar", "investigación", "estudia", "estudiar",
    "sintetiza", "sintetizar", "síntesis", "sintesis", "resume", "resumir",
    "comprende", "comprender", "profundiza", "profundizar",
    # Hipótesis / prospectiva
    "hipótesis", "hipotesis", "predice", "predecir", "predicción",
    "proyecta", "proyectar", "escenarios", "futuro", "tendencias",
    # Crítica metodológica
    "metodología", "metodologia", "rigor", "sesgo", "validez",
    "fiabilidad", "evidencia", "pruebas",
}

# L1 — Indicadores de consulta factual (rápida)
_L1_KEYWORDS = {
    "qué", "que", "quién", "quien", "cuál", "cual", "cuándo", "cuando",
    "dónde", "donde", "cuánto", "cuanto", "cuántos", "cuantos",
    "recuerda", "recordar", "recuerdas", "tienes", "tienes",
    "dime", "muéstrame", "muestrame", "lista", "muestra",
    "cómo", "como", "estado", "estás", "estas",
}

# L3 — Patrones estructurales (regex)
_L3_PATTERNS = [
    re.compile(r"\b(si|si no|en caso de)\b.+\b(entonces|debería|podría)\b", re.I),
    re.compile(r"\b(ventajas|desventajas|pros|contras|contras)\b", re.I),
    re.compile(r"\b(primero|segundo|tercero|finalmente)\b.*\b(primero|segundo|tercero|finalmente)\b", re.I),
    re.compile(r"\b(por un lado|por otro lado|sin embargo|no obstante|aunque)\b", re.I),
    re.compile(r"\d+\.\s.+\n\d+\.\s", re.I | re.S),  # lista numerada con 2+ items
]

# L1 — Patrones estructurales
_L1_PATTERNS = [
    re.compile(r"^(qué|quién|cuál|cuándo|dónde|cómo|cuánto)\s", re.I),
    re.compile(r"\b(recuerdas|tienes|sabes)\b", re.I),
]


class DepthClassifier:
    """
    Clasificador heurístico de profundidad cognitiva.

    Sin LLM. Combina 4 señales:
    1. Token exacto (L0) — match directo
    2. Keywords L3 → sube score
    3. Longitud → más texto suele implicar más profundidad
    4. Patrones estructurales → condicional/listas = L3

    Tiempo objetivo: <50ms.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        # Umbrales configurables
        self.l0_max_length = self.config.get("l0_max_length", 25)
        self.l1_max_length = self.config.get("l1_max_length", 80)
        self.l3_keyword_threshold = self.config.get("l3_keyword_threshold", 1)
        self.l2_default_length = self.config.get("l2_default_length", 150)

        # Estadísticas
        self.classifications = 0
        self.level_distribution: Dict[str, int] = {
            "L0_REFLEX": 0, "L1_FAST": 0, "L2_STANDARD": 0, "L3_DEEP": 0
        }

    def classify(self, text: str) -> ClassificationResult:
        """
        Clasifica un texto en un CognitiveLevel.

        Args:
            text: input del usuario (string crudo)

        Returns:
            ClassificationResult con nivel, score, razones y cache_key
        """
        if not text or not text.strip():
            # Empty → L0
            return self._make_result(
                CognitiveLevel.L0_REFLEX, 0.0,
                ["empty_input"], ""
            )

        normalized = self._normalize(text)
        reasons: List[str] = []
        score = 0.0

        # 1. Token exacto L0
        token_check = normalized.lower().rstrip(".!? ")
        if token_check in _L0_TOKENS:
            reasons.append(f"l0_token_match:{token_check}")
            return self._make_result(
                CognitiveLevel.L0_REFLEX, 0.05,
                reasons, normalized
            )

        # 2. Tokens L0 al inicio + poca longitud
        first_word = normalized.lower().split()[0] if normalized.split() else ""
        if first_word in _L0_TOKENS and len(normalized) <= self.l0_max_length:
            reasons.append(f"l0_short_with_token:{first_word}")
            return self._make_result(
                CognitiveLevel.L0_REFLEX, 0.10,
                reasons, normalized
            )

        # 3. Detectar keywords L3
        text_lower = normalized.lower()
        l3_hits = [kw for kw in _L3_KEYWORDS if kw in text_lower]
        if l3_hits:
            score += min(0.4, 0.15 * len(l3_hits))
            reasons.append(f"l3_keywords:{l3_hits[:3]}")

        # 4. Patrones L3
        for pattern in _L3_PATTERNS:
            if pattern.search(text):
                score += 0.2
                reasons.append(f"l3_pattern:{pattern.pattern[:30]}")
                break

        # 5. Longitud
        length = len(normalized)
        if length > 200:
            score += 0.2
            reasons.append(f"length_long:{length}")
        elif length > 100:
            score += 0.1
            reasons.append(f"length_medium:{length}")
        elif length <= self.l1_max_length:
            score += 0.05
            reasons.append(f"length_short:{length}")

        # 6. Puntuación compleja
        if text.count("?") >= 2:
            score += 0.1
            reasons.append("multi_question")
        if ";" in text:
            score += 0.05
            reasons.append("semicolon")
        if text.count("\n") >= 2:
            score += 0.1
            reasons.append("multiline")

        # 7. Tokens L1 (pregunta factual corta)
        l1_hits = [kw for kw in _L1_KEYWORDS if kw in text_lower]
        if l1_hits and score < 0.3:
            score += 0.05
            reasons.append(f"l1_keywords:{l1_hits[:3]}")

        # ---- Decidir nivel ----
        # Safety override: si contiene keyword L3 explícito, mínimo L3
        force_l3 = bool(l3_hits)
        # Si texto largo + L3 keyword, forzar L3
        if force_l3 and length > 80:
            level = CognitiveLevel.L3_DEEP
            score = max(score, 0.7)
            reasons.append("forced_l3:keyword+length")
        elif force_l3:
            level = CognitiveLevel.L3_DEEP
            score = max(score, 0.5)
            reasons.append("forced_l3:keyword")
        elif score >= 0.5:
            level = CognitiveLevel.L3_DEEP
        elif score >= 0.25:
            level = CognitiveLevel.L2_STANDARD
        elif score >= 0.10:
            level = CognitiveLevel.L1_FAST
        else:
            # Default: si muy corto y sin señales, L1 (porque ya pasó el filtro L0)
            level = CognitiveLevel.L1_FAST if length <= self.l1_max_length else CognitiveLevel.L2_STANDARD
            reasons.append(f"default_fallback:{level.value}")

        return self._make_result(level, score, reasons, normalized)

    def _make_result(
        self, level: CognitiveLevel, score: float,
        reasons: List[str], normalized: str
    ) -> ClassificationResult:
        self.classifications += 1
        self.level_distribution[level.value] += 1
        return ClassificationResult(
            level=level,
            score=min(1.0, max(0.0, score)),
            reasons=reasons,
            normalized_text=normalized,
            cache_key=self._cache_key(normalized),
            timestamp=time.time(),
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """Normaliza para cache key y comparación."""
        # Lowercase + collapse whitespace + strip
        t = text.strip().lower()
        t = re.sub(r"\s+", " ", t)
        # Quitar acentos para matching de keywords (preserva texto original)
        return t

    @staticmethod
    def _cache_key(normalized: str) -> str:
        """Hash SHA-256 del texto normalizado."""
        if not normalized:
            return "empty"
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del clasificador."""
        total = max(1, self.classifications)
        return {
            "total_classifications": self.classifications,
            "level_distribution": dict(self.level_distribution),
            "level_percentages": {
                k: round(v / total * 100, 1)
                for k, v in self.level_distribution.items()
            },
        }
