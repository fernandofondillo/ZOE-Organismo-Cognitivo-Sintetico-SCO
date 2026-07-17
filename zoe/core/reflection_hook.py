"""
ZOE v2.1 — ReflectionHook
Integra ReflectionEngine con el ciclo de metabolismo de ZOE.

Se ejecuta durante SLEEPING, utilizando el hook existente del metabolism.
No crea threads independientes — usa asyncio puro.

Uso:
    from zoe.core.reflection_hook import ReflectionHook

    # En metabolism.py, durante transición a SLEEPING:
    reflection_hook = ReflectionHook(reflection_engine)
    results = await reflection_hook.on_sleeping(metabolic_state)
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ReflectionHook:
    """Hook que conecta ReflectionEngine con el metabolismo.

    Principios de integración (vs propuesta L4):
    - NO crea un thread independiente → usa el loop async del metabolism
    - NO usa llama.cpp separado → usa OllamaPeripheral existente
    - NO modifica cognitive_loop_v5.py → solo se conecta al metabolism
    - Respeta compute_budget del metabolism
    """

    def __init__(self, reflection_engine=None):
        self._engine = reflection_engine
        self._sleep_cycle_count: int = 0

    async def on_sleeping(self, metabolic_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Llamado por el metabolism cuando ZOE entra en estado SLEEPING.

        Args:
            metabolic_state: Dict con 'fatigue', 'energy', 'arousal', 'attention',
                           'compute_budget', 'cycle_count'

        Returns:
            Lista de resultados de reflexión (para logging/métricas)
        """
        if self._engine is None:
            logger.debug("ReflectionHook: no engine configured")
            return []

        self._sleep_cycle_count += 1

        # Verificar compute_budget del metabolism
        budget = metabolic_state.get("compute_budget", 1.0)
        if budget < 0.2:
            logger.debug("ReflectionHook: compute_budget too low (%.2f), skipping", budget)
            return []

        try:
            results = await self._engine.run_during_sleeping(metabolic_state)
            if results:
                logger.info(
                    "ReflectionHook: %d insights generated during SLEEPING (cycle %d)",
                    len(results),
                    self._sleep_cycle_count,
                )
            return [r.__dict__ if hasattr(r, '__dict__') else r for r in results]

        except Exception as e:
            logger.error("ReflectionHook: error during reflection: %s", e)
            return []

    async def on_waking(self) -> None:
        """Llamado cuando ZOE despierta.

        Útil para logging y notificaciones.
        """
        if self._engine is None:
            return

        metrics = self._engine.get_metrics()
        logger.info(
            "ReflectionHook: ZOE waking — %d total insights, $%.4f total cost",
            metrics.get("total_insights", 0),
            metrics.get("total_cost_usd", 0.0),
        )
