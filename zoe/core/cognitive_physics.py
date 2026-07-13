"""
ZOE v1.0 — Cognitive Physics

12 magnitudes medibles que gobiernan el organismo.
Convierten ZOE de "colección de módulos" a "sistema dinámico gobernado por leyes cuantificables".

Magnitudes:
1. Energía cognitiva (eCog) — presupuesto de cómputo disponible
2. Masa conceptual (mCon) — conexiones de un concepto en memoria
3. Temperatura cognitiva (tCog) — actividad del bucle (iteraciones/s)
4. Presión de incertidumbre (pUnc) — sorpresa acumulada no resuelta
5. Potencial creativo (pCre) — diversidad de hipótesis generadas
6. Entropía semántica (hSem) — diversidad de conceptos activos
7. Gravedad de objetivos (gObj) — atracción de intenciones sobre atención
8. Inercia de identidad (iIden) — resistencia al cambio de valores
9. Resonancia conceptual (rCon) — similitud entre conceptos activos
10. Fricción cognitiva (fCog) — coste de cambiar de contexto
11. Elasticidad de memoria (eMem) — capacidad de reorganización
12. Densidad causal (dCau) — concentración de relaciones causales
"""

from __future__ import annotations

import math
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CognitivePhysics:
    """
    Calcula y mantiene las 12 magnitudes de física cognitiva.

    Las magnitudes se calculan en cada iteración del bucle cognitivo
    y afectan las decisiones del organismo.
    """

    # Estado medible (12 magnitudes)
    energy_cognitive: float = 1.0  # eCog: 0-1
    conceptual_mass: float = 0.0  # mCon: cuenta
    cognitive_temperature: float = 0.0  # tCog: iter/s
    uncertainty_pressure: float = 0.0  # pUnc: 0-1 (acumulada)
    creative_potential: float = 0.0  # pCre: 0-1
    semantic_entropy: float = 0.0  # hSem: 0-1
    goal_gravity: float = 0.0  # gObj: 0-1
    identity_inertia: float = 1.0  # iIden: 0-1 (1 = máxima inercia)
    conceptual_resonance: float = 0.0  # rCon: 0-1
    cognitive_friction: float = 0.0  # fCog: 0-1
    memory_elasticity: float = 1.0  # eMem: 0-1
    causal_density: float = 0.0  # dCau: 0-1

    # Histórico para cálculos derivados
    _iteration_history: List[float] = field(default_factory=list)
    _surprise_history: List[float] = field(default_factory=list)
    _concept_history: List[List[str]] = field(default_factory=list)
    _last_context: str = ""
    _context_changes: int = 0
    _last_update: float = field(default_factory=time.time)

    def update(
        self,
        state: Any,
        observations: List[Any],
        thoughts: List[Any],
        intentions: List[Any] = None,
        memory_concepts: List[str] = None,
        causal_relations: int = 0,
        current_context: str = "",
    ) -> Dict[str, float]:
        """
        Actualiza las 12 magnitudes dado el estado actual del organismo.

        Returns:
            dict con todas las magnitudes calculadas
        """
        now = time.time()
        dt = max(0.001, now - self._last_update)
        self._last_update = now

        # 1. Energía cognitiva (del estado interno)
        self.energy_cognitive = getattr(state, "energy", 1.0)

        # 2. Masa conceptual (número de conceptos en memoria)
        if memory_concepts:
            self.conceptual_mass = float(len(memory_concepts))
        else:
            self.conceptual_mass = 0.0

        # 3. Temperatura cognitiva (iteraciones por segundo)
        iteration = getattr(state, "iteration_count", 0)
        self._iteration_history.append(now)
        # Mantener solo últimos 60s
        cutoff = now - 60.0
        self._iteration_history = [t for t in self._iteration_history if t > cutoff]
        if len(self._iteration_history) > 1:
            time_window = self._iteration_history[-1] - self._iteration_history[0]
            if time_window > 0:
                self.cognitive_temperature = (len(self._iteration_history) - 1) / time_window
            else:
                self.cognitive_temperature = 0.0
        else:
            self.cognitive_temperature = 0.0

        # 4. Presión de incertidumbre (sorpresa acumulada no resuelta)
        # Sorpresa reciente promedio, ajustada por pensamientos generados (resolución)
        recent_surprises = [getattr(t, "surprise", 0.0) for t in thoughts[-10:]] if thoughts else []
        if recent_surprises:
            avg_surprise = sum(recent_surprises) / len(recent_surprises)
            # Cada pensamiento reduce presión (resolución de incertidumbre)
            resolution_factor = min(1.0, len(thoughts[-10:]) / 10.0) if thoughts else 0.0
            self.uncertainty_pressure = avg_surprise * (1.0 - resolution_factor * 0.5)
        else:
            self.uncertainty_pressure = 0.0

        # 5. Potencial creativo (diversidad de hipótesis/pensamientos recientes)
        if thoughts and len(thoughts) >= 2:
            # Diversidad = 1 - similitud media
            recent_thoughts = thoughts[-10:]
            contents = [getattr(t, "content", "") for t in recent_thoughts]
            similarities = []
            for i in range(len(contents)):
                for j in range(i + 1, len(contents)):
                    sim = self._jaccard(contents[i], contents[j])
                    similarities.append(sim)
            if similarities:
                avg_sim = sum(similarities) / len(similarities)
                self.creative_potential = 1.0 - avg_sim
            else:
                self.creative_potential = 0.5
        else:
            self.creative_potential = 0.0

        # 6. Entropía semántica (diversidad de conceptos activos)
        if memory_concepts and len(memory_concepts) > 1:
            # Shannon entropy sobre frecuencia de conceptos
            # (simplificado: contar conceptos únicos vs totales)
            unique = len(set(memory_concepts))
            total = len(memory_concepts)
            if total > 0:
                ratio = unique / total
                self.semantic_entropy = -ratio * math.log(ratio + 1e-10) if ratio > 0 else 0.0
                # Normalizar a 0-1 (máximo de -x*log(x) en [0,1] es 1/e ≈ 0.368)
                self.semantic_entropy = min(1.0, self.semantic_entropy / 0.368)
            else:
                self.semantic_entropy = 0.0
        else:
            self.semantic_entropy = 0.0

        # 7. Gravedad de objetivos (cuántas intenciones activas)
        if intentions:
            self.goal_gravity = min(1.0, len(intentions) / 10.0)
        else:
            self.goal_gravity = 0.0

        # 8. Inercia de identidad (resistencia al cambio)
        # Alta cuando hay poca sorpresa acumulada, baja cuando mucha
        self.identity_inertia = max(0.1, 1.0 - self.uncertainty_pressure)

        # 9. Resonancia conceptual (similitud entre conceptos activos)
        if memory_concepts and len(memory_concepts) >= 2:
            # Similitud media entre conceptos (simplificado: palabras compartidas)
            concepts = list(set(memory_concepts))[:20]  # muestra
            if len(concepts) >= 2:
                similarities = []
                for i in range(min(len(concepts), 10)):
                    for j in range(i + 1, min(len(concepts), 10)):
                        sim = self._jaccard(concepts[i], concepts[j])
                        similarities.append(sim)
                if similarities:
                    self.conceptual_resonance = sum(similarities) / len(similarities)
                else:
                    self.conceptual_resonance = 0.0
            else:
                self.conceptual_resonance = 0.0
        else:
            self.conceptual_resonance = 0.0

        # 10. Fricción cognitiva (coste de cambiar de contexto)
        if current_context != self._last_context:
            self._context_changes += 1
            self._last_context = current_context
            # Fricción aumenta con cambios recientes, decae con tiempo
            self.cognitive_friction = min(1.0, self.cognitive_friction + 0.2)
        else:
            # Decae
            self.cognitive_friction = max(0.0, self.cognitive_friction - 0.05)

        # 11. Elasticidad de memoria (capacidad de reorganización)
        # Alta cuando hay energía y poca fatiga
        energy = getattr(state, "energy", 1.0)
        fatigue = getattr(state, "fatigue", 0.0)
        self.memory_elasticity = energy * (1.0 - fatigue)

        # 12. Densidad causal (concentración de relaciones causales)
        # Simplificado: ratio de relaciones causales vs conceptos
        if memory_concepts and len(memory_concepts) > 0:
            self.causal_density = min(1.0, causal_relations / (len(memory_concepts) * 2.0))
        else:
            self.causal_density = 0.0

        return self.to_dict()

    def _jaccard(self, a: str, b: str) -> float:
        """Similitud de Jaccard entre dos strings."""
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)

    def to_dict(self) -> Dict[str, float]:
        """Todas las magnitudes como dict."""
        return {
            "energy_cognitive": self.energy_cognitive,
            "conceptual_mass": self.conceptual_mass,
            "cognitive_temperature": self.cognitive_temperature,
            "uncertainty_pressure": self.uncertainty_pressure,
            "creative_potential": self.creative_potential,
            "semantic_entropy": self.semantic_entropy,
            "goal_gravity": self.goal_gravity,
            "identity_inertia": self.identity_inertia,
            "conceptual_resonance": self.conceptual_resonance,
            "cognitive_friction": self.cognitive_friction,
            "memory_elasticity": self.memory_elasticity,
            "causal_density": self.causal_density,
        }

    def should_rest(self) -> bool:
        """Decisión basada en física: ¿debe descansar el organismo?"""
        return (
            self.energy_cognitive < 0.2
            or self.uncertainty_pressure > 0.8
            or self.cognitive_friction > 0.7
        )

    def should_consolidate(self) -> bool:
        """Decisión basada en física: ¿debe consolidar memoria?"""
        return (
            self.memory_elasticity > 0.6
            and self.conceptual_mass > 10
            and self.cognitive_temperature < 0.5  # poca actividad
        )

    def should_explore(self) -> bool:
        """Decisión basada en física: ¿debe explorar?"""
        return (
            self.creative_potential > 0.5
            and self.energy_cognitive > 0.5
            and self.uncertainty_pressure < 0.5
        )

    def summary(self) -> str:
        """Resumen legible del estado físico cognitivo."""
        return (
            f"eCog={self.energy_cognitive:.2f} "
            f"tCog={self.cognitive_temperature:.2f} "
            f"pUnc={self.uncertainty_pressure:.2f} "
            f"pCre={self.creative_potential:.2f} "
            f"hSem={self.semantic_entropy:.2f} "
            f"iIden={self.identity_inertia:.2f}"
        )
