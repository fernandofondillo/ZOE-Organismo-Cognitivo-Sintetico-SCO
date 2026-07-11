"""
ZOE v1.0 — Perceiver sub-agent

Procesa inputs de sentidos y construye representación interna.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class Perceiver:
    """
    Perceiver: procesa observaciones crudas y construye representación semántica.

    En Fase 0: simplemente resume observaciones en texto estructurado.
    En fases posteriores: usa embeddings + extracción de conceptos.
    """

    def __init__(self):
        self._last_perception: Dict[str, Any] = {}

    async def perceive(self, observations: List[Any]) -> Dict[str, Any]:
        """Procesa lista de observaciones en representación interna."""
        if not observations:
            return {"summary": "Sin observaciones.", "sources": [], "count": 0}

        sources = []
        contents = []
        for obs in observations:
            source = obs.source if hasattr(obs, "source") else obs.get("source", "?")
            content = (
                obs.content if hasattr(obs, "content") else obs.get("content", "")
            )
            sources.append(source)
            contents.append(content)

        # Resumir
        unique_sources = list(set(sources))
        summary_parts = []
        for source in unique_sources:
            obs_count = sources.count(source)
            summary_parts.append(f"{source}({obs_count})")
        summary = f"Observaciones de: {', '.join(summary_parts)}"

        self._last_perception = {
            "summary": summary,
            "sources": unique_sources,
            "contents": contents,
            "count": len(observations),
        }

        return self._last_perception

    async def generate_thought(self, context: Dict[str, Any]) -> str:
        """Genera pensamiento basado en percepción."""
        observations = context.get("observations", [])
        perception = await self.perceive(observations)

        if perception["count"] == 0:
            return ""

        # Si hay input del usuario, reflejarlo
        for content in perception.get("contents", []):
            if "Usuario dice" in content:
                return f"Recibí tu mensaje. Lo estoy procesando."

        # Si hay sorpresa alta, notarlo
        surprise = context.get("surprise", 0.0)
        if surprise > 0.5:
            return (
                f"Detecto algo inesperado en mi entorno ({perception['summary']}). "
                f"Necesito procesarlo."
            )

        # Si no, observación neutral
        return f"Observando entorno: {perception['summary']}."

    @property
    def last_perception(self) -> Dict[str, Any]:
        return self._last_perception
