"""
ZOE v1.0 — Cognitive Loop V4 (Fase 4)

Extiende CognitiveLoopV3 con:
- DeepConsolidation integrada durante SLEEPING
- Auto-carga de memoria al iniciar
- Auto-guardado al detener + periódico
- Configuración desde YAML
- Recovery tras crash

Mantiene compatibilidad: si los componentes Fase 4 no se proporcionan,
funciona como CognitiveLoopV3.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import time
from typing import Optional, List, Dict, Any, Callable, Awaitable

from .cognitive_loop_v3 import CognitiveLoopV3
from .cognitive_loop import Thought, Observation

logger = logging.getLogger(__name__)


class CognitiveLoopV4(CognitiveLoopV3):
    """
    Bucle cognitivo Fase 4.

    Añade sobre V3:
    - DeepConsolidation durante SLEEPING
    - Auto-carga/guardado de memoria persistente
    - Auto-save periódico
    - Graceful shutdown (guarda antes de cerrar)
    - Recovery (carga último estado al iniciar)
    """

    def __init__(
        self,
        *args,
        # Fase 4 componentes
        deep_consolidation: Any = None,
        persistent_memory: Any = None,
        auto_save_interval: int = 50,  # cada N iteraciones
        config: Dict[str, Any] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Fase 4
        self.deep_consolidation = deep_consolidation
        self.persistent_memory = persistent_memory
        self.auto_save_interval = auto_save_interval
        self.config = config or {}

        # Estado de shutdown
        self._shutdown_requested = False
        self._signal_handlers_installed = False

        # Estadísticas Fase 4
        self.consolidation_cycles: int = 0
        self.auto_saves: int = 0
        self.memory_loads: int = 0

    def initialize(self) -> None:
        """
        Inicializa el organismo: carga memoria desde disco si existe.
        Llamar antes de run().
        """
        if self.persistent_memory:
            try:
                loaded = self.persistent_memory.load_from_disk()
                if loaded > 0:
                    self.memory_loads += 1
                    logger.info(f"V4: loaded {loaded} memory entries from disk")
            except Exception as e:
                logger.warning(f"V4: failed to load memory from disk: {e}")

        # Instalar signal handlers para graceful shutdown
        self._install_signal_handlers()

    def _install_signal_handlers(self) -> None:
        """Instala handlers para SIGTERM/SIGINT (graceful shutdown)."""
        if self._signal_handlers_installed:
            return

        try:
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, self._handle_shutdown_signal)
            self._signal_handlers_installed = True
            logger.debug("V4: signal handlers installed")
        except (NotImplementedError, RuntimeError):
            # Signal handlers no disponibles en algunos entornos (tests)
            pass

    def _handle_shutdown_signal(self) -> None:
        """Maneja SIGTERM/SIGINT: guarda memoria y detiene."""
        logger.info("V4: shutdown signal received, saving memory...")
        self._shutdown_requested = True
        self.stop()
        self._graceful_shutdown()

    def _graceful_shutdown(self) -> None:
        """Guarda memoria antes de cerrar."""
        if self.persistent_memory:
            try:
                saved = self.persistent_memory.save_to_disk()
                logger.info(f"V4: saved {saved} entries to disk on shutdown")
            except Exception as e:
                logger.error(f"V4: failed to save on shutdown: {e}")

    async def _tick(self) -> None:
        """Ejecuta una iteración del bucle cognitivo Fase 4."""
        # Ejecutar tick de V3
        await super()._tick()

        # Fase 4: DeepConsolidation durante SLEEPING
        if self.metabolism and self.deep_consolidation:
            if self.metabolism.state.value == "sleeping":
                # Solo consolidar cada N iteraciones durante sueño
                if self.state.iteration_count % 3 == 0:
                    try:
                        result = self.deep_consolidation.consolidate()
                        self.consolidation_cycles += 1
                        logger.info(
                            f"V4: deep consolidation #{self.consolidation_cycles} "
                            f"completed: {result.get('total_operations', 0)} operations"
                        )
                        # Guardar después de consolidación
                        if self.persistent_memory:
                            self.persistent_memory.save_to_disk()
                            self.auto_saves += 1
                    except Exception as e:
                        logger.warning(f"V4: deep consolidation failed: {e}")

        # Fase 4: Auto-save periódico
        if (
            self.persistent_memory
            and self.auto_save_interval > 0
            and self.state.iteration_count % self.auto_save_interval == 0
            and self.state.iteration_count > 0
        ):
            try:
                self.persistent_memory.save_to_disk()
                self.auto_saves += 1
                logger.debug(f"V4: auto-save #{self.auto_saves} at iteration {self.state.iteration_count}")
            except Exception as e:
                logger.warning(f"V4: auto-save failed: {e}")

        # Fase 4: Shutdown check
        if self._shutdown_requested:
            self.stop()

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas completas incluyendo Fase 4."""
        stats = super().get_stats()

        # Fase 4 stats
        stats["consolidation_cycles"] = self.consolidation_cycles
        stats["auto_saves"] = self.auto_saves
        stats["memory_loads"] = self.memory_loads
        stats["shutdown_requested"] = self._shutdown_requested

        if self.deep_consolidation:
            stats["deep_consolidation_stats"] = self.deep_consolidation.get_stats()

        if self.persistent_memory:
            stats["persistent_memory_stats"] = self.persistent_memory.get_stats()

        return stats


def load_config(config_path: str = None, env: str = None) -> Dict[str, Any]:
    """
    Carga configuración desde YAML.

    Args:
        config_path: ruta al archivo YAML. Si None, busca default.
        env: entorno ('production', 'development', 'test'). Si None, usa ZOE_ENV.

    Returns:
        Dict con configuración
    """
    if env is None:
        env = os.environ.get("ZOE_ENV", "development")

    if config_path is None:
        # Buscar en ubicaciones estándar
        candidates = [
            f"zoe/config/{env}.yaml",
            f"zoe/config/{env}.yml",
            f"config/{env}.yaml",
            f"/etc/zoe/{env}.yaml",
        ]
        for path in candidates:
            if os.path.exists(path):
                config_path = path
                break

    if config_path is None or not os.path.exists(config_path):
        logger.warning(f"No config file found for env '{env}', using defaults")
        return _default_config()

    try:
        import yaml
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Config loaded from {config_path} (env={env})")
        return config
    except ImportError:
        logger.warning("PyYAML not available, using defaults")
        return _default_config()
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
        return _default_config()


def _default_config() -> Dict[str, Any]:
    """Configuración por defecto."""
    return {
        "zoe": {
            "organism_id": "zoe_default",
            "tick_interval": 5.0,
            "environment": "development",
        },
        "llm": {
            "backend": "mock",
            "model": None,
        },
        "metabolism": {
            "drowsy_threshold": 0.6,
            "sleep_threshold": 0.8,
            "wake_threshold": 0.3,
        },
        "memory": {
            "db_path": "zoe_data/memory.db",
            "auto_save_interval": 50,
            "max_entries": 1000,
        },
        "federation": {
            "enabled": False,
            "port": 8642,
            "peers": [],
        },
        "logging": {
            "level": "INFO",
            "file": None,
        },
    }
