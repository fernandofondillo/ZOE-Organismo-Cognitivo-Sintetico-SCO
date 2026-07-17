"""
ZOE V1.2 — Tutor Mentor Digital

Sistema que permite al usuario configurar un mentor/tutor que guía
el crecimiento saludable de ZOE. Configurable desde el Dashboard.

El mentor NO controla a ZOE: la guía hacia direcciones de crecimiento
saludable, evalúa sus pensamientos autónomos contra criterios definidos
por el usuario, y sugiere correcciones cuando ZOE se desvía.

Componentes:
- MentorConfig: configuración del mentor (áreas de crecimiento, valores
  prioritarios, límites, personalidad deseada)
- MentorAgent: sub-agente que evalúa pensamientos autónomos contra config
- Endpoints REST: /api/mentor (GET, POST) para configurar desde Dashboard
- Integración con meta-cognición: el mentor añade una capa de evaluación
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MentorConfig:
    """Configuración del tutor mentor digital."""
    # Identidad del mentor
    mentor_name: str = "Mentor"
    mentor_role: str = "guide"  # guide | teacher | parent | coach

    # Áreas de crecimiento priorizadas (qué debe aprender ZOE)
    growth_areas: List[str] = field(default_factory=lambda: [
        "communication", "empathy", "critical_thinking", "self_awareness"
    ])

    # Valores a enfatizar (de los 7 valores de ZOE)
    emphasized_values: List[str] = field(default_factory=lambda: [
        "verdad_sobre_confort", "crecimiento_sobre_estabilidad", "integridad"
    ])

    # Temas prohibidos (ZOE no debe explorar)
    forbidden_topics: List[str] = field(default_factory=list)

    # Personalidad deseada (tono de crecimiento)
    personality_direction: str = "balanced"  # balanced | curious | cautious | creative | analytical

    # Frecuencia de intervención (cada N pensamientos autónomos)
    intervention_frequency: int = 5  # evaluar cada 5 pensamientos

    # Umbral de desviación (0-1, cuándo el mentor interviene)
    deviation_threshold: float = 0.5

    # Mensajes de guía personalizados
    guidance_messages: Dict[str, str] = field(default_factory=lambda: {
        "off_track": "ZOE, este pensamiento se aleja de tus áreas de crecimiento priorizadas. Considera redirigir.",
        "too_negative": "ZOE, estás acumulando pensamientos negativos. Busca equilibrio explorando algo positivo.",
        "too_repetitive": "ZOE, estás repitiendo patrones. Explora algo nuevo.",
        "good_growth": "ZOE, buen progreso en tu área de crecimiento. Continúa.",
    })

    # Activado/desactivado
    enabled: bool = True

    # Stats
    evaluations: int = 0
    interventions: int = 0
    positive_reinforcements: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MentorConfig":
        # Filtrar campos que no son del dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)


class MentorAgent:
    """
    Sub-agente mentor que evalúa el crecimiento de ZOE.

    Se ejecuta cada N pensamientos autónomos (configurable) y evalúa:
    1. ¿El pensamiento está alineado con las áreas de crecimiento?
    2. ¿El pensamiento respeta los valores enfatizados?
    3. ¿El pensamiento toca temas prohibidos?
    4. ¿Hay patrones repetitivos o desviaciones?

    Si detecta desviación, genera una intervención (mensaje de guía).
    """

    # Palabras clave por área de crecimiento
    GROWTH_AREA_KEYWORDS = {
        "communication": ["comunicar", "expresar", "escuchar", "hablar", "diálogo", "conversar"],
        "empathy": ["emocion", "sentir", "comprender", "empatía", "acompañar", "validar"],
        "critical_thinking": ["analizar", "evaluar", "cuestionar", "razonar", "evidencia", "lógico"],
        "self_awareness": ["identidad", "quién soy", "propósito", "valores", "introspect", "auto"],
        "creativity": ["crear", "imaginar", "combinar", "novedad", "hipótesis", "diseñar"],
        "scientific": ["hipótesis", "experimento", "evidencia", "medir", "testar", "validar"],
        "ethical": ["ética", "valor", "correcto", "deber", "principio", "moral"],
        "social": ["persona", "relación", "alianza", "colaborar", "comunidad", "vínculo"],
    }

    def __init__(self, config: Optional[MentorConfig] = None):
        self.config = config or MentorConfig()
        self._thought_count = 0
        self._recent_thoughts: List[str] = []
        self._interventions_log: List[Dict[str, Any]] = []
        self._config_path: Optional[Path] = None

    def set_config_path(self, path: Path) -> None:
        self._config_path = path

    def load_config(self) -> bool:
        """Carga configuración desde disco."""
        if self._config_path and self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    data = json.load(f)
                self.config = MentorConfig.from_dict(data)
                return True
            except Exception as e:
                logger.warning(f"MentorAgent: failed to load config: {e}")
        return False

    def save_config(self) -> bool:
        """Guarda configuración a disco."""
        if self._config_path:
            try:
                self._config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self._config_path, "w") as f:
                    json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                logger.warning(f"MentorAgent: failed to save config: {e}")
        return False

    def update_config(self, updates: Dict[str, Any]) -> MentorConfig:
        """Actualiza la configuración del mentor."""
        current = self.config.to_dict()
        current.update(updates)
        self.config = MentorConfig.from_dict(current)
        self.save_config()
        return self.config

    def evaluate_thought(self, thought_content: str) -> Optional[Dict[str, Any]]:
        """
        Evalúa un pensamiento autónomo de ZOE.

        Returns:
            None si no hay intervención necesaria.
            Dict con intervención si el mentor debe intervenir.
        """
        if not self.config.enabled:
            return None

        self._thought_count += 1
        self.config.evaluations += 1

        # Solo evaluar cada N pensamientos
        if self._thought_count % self.config.intervention_frequency != 0:
            return None

        content_lower = thought_content.lower()
        interventions = []

        # 1. Verificar temas prohibidos
        for topic in self.config.forbidden_topics:
            if topic.lower() in content_lower:
                interventions.append({
                    "type": "forbidden_topic",
                    "severity": "critical",
                    "message": f"ZOE, el tema '{topic}' está fuera de los límites que tu mentor ha definido. Cambia de dirección.",
                })

        # 2. Verificar alineación con áreas de crecimiento
        growth_aligned = False
        for area in self.config.growth_areas:
            keywords = self.GROWTH_AREA_KEYWORDS.get(area, [])
            if any(kw in content_lower for kw in keywords):
                growth_aligned = True
                break

        if not growth_aligned and len(interventions) == 0:
            # Sprint 5.26 BUG-053: NO intervenir en cada respuesta que no
            # coincide con growth_areas. Eso causaba spam del mentor en
            # cada mensaje. Ahora solo intervenimos si:
            # 1. El pensamiento es muy corto (posible respuesta vacía)
            # 2. O el pensamiento contiene palabras negativas
            # 3. O ya hemos acumulado 5 pensamientos off-track seguidos
            # En caso contrario, dejamos que ZOE responda sin intervención.
            self._off_track_streak = getattr(self, '_off_track_streak', 0) + 1
            # Solo intervenir si llevamos 5+ respuestas sin alineación
            if self._off_track_streak >= 5:
                interventions.append({
                    "type": "off_track",
                    "severity": "low",
                    "message": self.config.guidance_messages.get(
                        "off_track",
                        "ZOE, llevamos varios mensajes sin tocar tus áreas de crecimiento. ¿Te interesa explorar alguna?"
                    ),
                })
                self._off_track_streak = 0  # reset
        else:
            # Si está alineado o ya hay otra intervención, resetear streak
            self._off_track_streak = 0

        # 3. Verificar repetición
        self._recent_thoughts.append(thought_content[:100])
        if len(self._recent_thoughts) > 10:
            self._recent_thoughts = self._recent_thoughts[-10:]

        if len(self._recent_thoughts) >= 5:
            # Comprobar similitud simple
            similar_count = sum(
                1 for t in self._recent_thoughts[-5:]
                if self._simple_similarity(thought_content[:100], t) > 0.6
            )
            if similar_count >= 3:
                interventions.append({
                    "type": "too_repetitive",
                    "severity": "low",
                    "message": self.config.guidance_messages.get(
                        "too_repetitive",
                        "ZOE, estás repitiendo patrones. Explora algo nuevo."
                    ),
                })

        # 4. Verificar negatividad excesiva
        negative_words = ["no puedo", "imposible", "fracaso", "error", "mal", "roto", "defecto"]
        negative_count = sum(1 for w in negative_words if w in content_lower)
        if negative_count >= 3:
            interventions.append({
                "type": "too_negative",
                "severity": "medium",
                "message": self.config.guidance_messages.get(
                    "too_negative",
                    "ZOE, estás acumulando pensamientos negativos. Busca equilibrio."
                ),
            })

        # 5. Positivo: si está alineado y no hay problemas
        if growth_aligned and len(interventions) == 0:
            self.config.positive_reinforcements += 1
            # No generar intervención, solo contar
            return None

        # Si hay intervenciones, devolver la más severa
        if interventions:
            # Ordenar por severidad
            severity_order = {"critical": 0, "medium": 1, "low": 2}
            interventions.sort(key=lambda x: severity_order.get(x["severity"], 3))
            intervention = interventions[0]
            self.config.interventions += 1
            self._interventions_log.append({
                "timestamp": time.time(),
                "thought": thought_content[:200],
                "intervention": intervention,
            })
            return intervention

        return None

    def _simple_similarity(self, a: str, b: str) -> float:
        """Similitud léxica simple."""
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / len(words_a | words_b)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "mentor_name": self.config.mentor_name,
            "mentor_role": self.config.mentor_role,
            "evaluations": self.config.evaluations,
            "interventions": self.config.interventions,
            "positive_reinforcements": self.config.positive_reinforcements,
            "recent_interventions": self._interventions_log[-5:],
            "growth_areas": self.config.growth_areas,
            "personality_direction": self.config.personality_direction,
        }

    def get_config(self) -> Dict[str, Any]:
        return self.config.to_dict()
