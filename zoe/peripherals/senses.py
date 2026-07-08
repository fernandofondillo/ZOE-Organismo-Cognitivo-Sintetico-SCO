"""
ZOE v1.0 — Senses (sentidos digitales)

Cada sentido es una fuente de observaciones del entorno.

Sentidos implementados:
- Fase 0: ClockSense, FilesystemSense, UserInputSense
- Fase 1.5: NetworkSense, AgentSense

Cada sentido implementa la interfaz Sense (6ta ley: modularidad).
Los sentidos escriben en CognitiveFields cuando están conectados al bucle.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from ..core.cognitive_loop import Observation

logger = logging.getLogger(__name__)


class Sense(ABC):
    """Clase base para todos los sentidos de ZOE."""

    @abstractmethod
    async def observe(self) -> Optional[Observation | List[Observation]]:
        """Recoge observaciones del entorno."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class ClockSense(Sense):
    """
    Sentido del reloj interno.

    Observa el paso del tiempo, la hora del día, y detecta patrones temporales.
    Es el sentido más básico: siempre está activo, siempre produce observaciones.
    """

    def __init__(self, pattern_interval: float = 60.0):
        """
        Args:
            pattern_interval: cada cuántos segundos reportar patrón temporal (default 60s)
        """
        self.pattern_interval = pattern_interval
        self._last_observation_time = time.time()
        self._last_pattern_report = 0.0
        self._iteration = 0

    @property
    def name(self) -> str:
        return "clock"

    async def observe(self) -> Optional[Observation]:
        """Produce una observación del tiempo."""
        now = time.time()
        dt = now - self._last_observation_time
        self._last_observation_time = now
        self._iteration += 1

        # Hora del día
        local_time = time.localtime(now)
        hour = local_time.tm_hour
        minute = local_time.tm_min

        # Determinar franja
        if 6 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 18:
            period = "afternoon"
        elif 18 <= hour < 22:
            period = "evening"
        else:
            period = "night"

        # Contenido de la observación
        content = f"Tick {self._iteration}: han pasado {dt:.1f}s. Hora local: {hour:02d}:{minute:02d} ({period})."

        # Cada pattern_interval, generar observación más rica
        if now - self._last_pattern_report > self.pattern_interval:
            self._last_pattern_report = now
            content += f" Reporte periódico: {self._iteration} ticks desde inicio."

        return Observation(
            timestamp=now,
            source=self.name,
            content=content,
            metadata={
                "hour": hour,
                "minute": minute,
                "period": period,
                "dt_since_last": dt,
                "iteration": self._iteration,
            },
        )


class FilesystemSense(Sense):
    """
    Sentido del filesystem.

    Observa cambios en un directorio: archivos nuevos, modificados, eliminados.
    Útil para detectar actividad del entorno digital.
    """

    def __init__(self, watch_dir: str, interval: float = 30.0):
        """
        Args:
            watch_dir: directorio a observar
            interval: cada cuántos segundos observar (default 30s)
        """
        self.watch_dir = watch_dir
        self.interval = interval
        self._last_check = 0.0
        self._last_state: Dict[str, float] = {}  # path -> mtime

    @property
    def name(self) -> str:
        return "filesystem"

    async def observe(self) -> Optional[Observation | List[Observation]]:
        """Observa cambios en el directorio."""
        now = time.time()
        if now - self._last_check < self.interval:
            return None
        self._last_check = now

        if not os.path.isdir(self.watch_dir):
            return None

        observations: List[Observation] = []
        current_state: Dict[str, float] = {}

        try:
            for entry in os.listdir(self.watch_dir):
                full_path = os.path.join(self.watch_dir, entry)
                if os.path.isfile(full_path):
                    mtime = os.path.getmtime(full_path)
                    current_state[entry] = mtime

                    # Archivo nuevo
                    if entry not in self._last_state:
                        observations.append(
                            Observation(
                                timestamp=now,
                                source=self.name,
                                content=f"Nuevo archivo detectado: {entry}",
                                metadata={"event": "new_file", "path": entry, "mtime": mtime},
                            )
                        )
                    # Archivo modificado
                    elif mtime > self._last_state[entry]:
                        observations.append(
                            Observation(
                                timestamp=now,
                                source=self.name,
                                content=f"Archivo modificado: {entry}",
                                metadata={
                                    "event": "modified_file",
                                    "path": entry,
                                    "mtime": mtime,
                                    "prev_mtime": self._last_state[entry],
                                },
                            )
                        )

            # Archivos eliminados
            for old_entry in self._last_state:
                if old_entry not in current_state:
                    observations.append(
                        Observation(
                            timestamp=now,
                            source=self.name,
                            content=f"Archivo eliminado: {old_entry}",
                            metadata={"event": "deleted_file", "path": old_entry},
                        )
                    )

            self._last_state = current_state
        except Exception as e:
            logger.warning(f"FilesystemSense error: {e}")
            return None

        if not observations:
            # Sin cambios: observación de "quietud"
            return Observation(
                timestamp=now,
                source=self.name,
                content=f"Sin cambios en {self.watch_dir} ({len(current_state)} archivos monitoreados)",
                metadata={"event": "no_change", "file_count": len(current_state)},
            )

        return observations


class UserInputSense(Sense):
    """
    Sentido de input del usuario.

    Permite inyectar inputs manualmente para testing o interacción.
    """

    def __init__(self):
        self._pending_inputs: List[str] = []
        self._iteration = 0

    @property
    def name(self) -> str:
        return "user"

    def inject_input(self, content: str) -> None:
        """Inyecta un input del usuario (para testing o interacción)."""
        self._pending_inputs.append(content)

    async def observe(self) -> Optional[Observation]:
        self._iteration += 1
        if not self._pending_inputs:
            return None
        content = self._pending_inputs.pop(0)
        return Observation(
            timestamp=time.time(),
            source=self.name,
            content=f"Usuario dice: {content}",
            metadata={"raw_input": content, "iteration": self._iteration},
        )


class NetworkSense(Sense):
    """
    Sentido de red.

    Observa conectividad: endpoints HTTP alcanzables, latencia, cambios.
    Útil para detectar si el entorno digital cambia (servicios caen, aparecen).
    """

    def __init__(
        self,
        endpoints: List[str] = None,
        check_interval: float = 60.0,
        timeout: float = 5.0,
    ):
        """
        Args:
            endpoints: lista de URLs a monitorear (ej: ["http://localhost:11434"])
            check_interval: cada cuántos segundos verificar (default 60s)
            timeout: timeout por request en segundos
        """
        self.endpoints = endpoints or []
        self.check_interval = check_interval
        self.timeout = timeout
        self._last_check = 0.0
        self._last_status: Dict[str, bool] = {}
        self._iteration = 0

    @property
    def name(self) -> str:
        return "network"

    def add_endpoint(self, url: str) -> None:
        """Añade un endpoint a monitorear."""
        if url not in self.endpoints:
            self.endpoints.append(url)

    async def observe(self) -> Optional[Observation | List[Observation]]:
        """Observa estado de la red."""
        now = time.time()
        if now - self._last_check < self.check_interval:
            return None
        self._last_check = now
        self._iteration += 1

        if not self.endpoints:
            return Observation(
                timestamp=now,
                source=self.name,
                content=f"Sin endpoints configurados para monitorear (iteración {self._iteration}).",
                metadata={"endpoints": 0, "iteration": self._iteration},
            )

        observations: List[Observation] = []
        current_status: Dict[str, bool] = {}

        for url in self.endpoints:
            reachable = await self._check_endpoint(url)
            current_status[url] = reachable

            # Detectar cambios
            prev = self._last_status.get(url)
            if prev is None:
                # Primera verificación
                status_text = "alcanzable" if reachable else "no alcanzable"
                observations.append(
                    Observation(
                        timestamp=now,
                        source=self.name,
                        content=f"Endpoint {url}: {status_text} (primera verificación).",
                        metadata={
                            "endpoint": url,
                            "reachable": reachable,
                            "event": "initial_check",
                            "iteration": self._iteration,
                        },
                    )
                )
            elif prev != reachable:
                # Cambio de estado
                if reachable:
                    observations.append(
                        Observation(
                            timestamp=now,
                            source=self.name,
                            content=f"Endpoint {url} ahora alcanzable (antes caído).",
                            metadata={
                                "endpoint": url,
                                "reachable": True,
                                "event": "recovered",
                                "iteration": self._iteration,
                            },
                        )
                    )
                else:
                    observations.append(
                        Observation(
                            timestamp=now,
                            source=self.name,
                            content=f"Endpoint {url} caído (antes alcanzable).",
                            metadata={
                                "endpoint": url,
                                "reachable": False,
                                "event": "down",
                                "iteration": self._iteration,
                            },
                        )
                    )

        self._last_status = current_status

        if not observations:
            # Sin cambios
            reachable_count = sum(1 for v in current_status.values() if v)
            return Observation(
                timestamp=now,
                source=self.name,
                content=f"Red estable: {reachable_count}/{len(self.endpoints)} endpoints alcanzables.",
                metadata={
                    "endpoints": len(self.endpoints),
                    "reachable": reachable_count,
                    "event": "no_change",
                    "iteration": self._iteration,
                },
            )

        return observations

    async def _check_endpoint(self, url: str) -> bool:
        """Verifica si un endpoint es alcanzable."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    return resp.status < 500
        except Exception:
            return False


class AgentSense(Sense):
    """
    Sentido de otros agentes.

    Detecta presencia y estado de otros agentes/ZOEs en el entorno.
    Útil para federación y modelo social.
    """

    def __init__(self, known_agents: Dict[str, Dict[str, Any]] = None):
        """
        Args:
            known_agents: dict de {agent_id: {type, status, last_seen, ...}}
        """
        self.known_agents = known_agents or {}
        self._last_check = 0.0
        self._iteration = 0

    @property
    def name(self) -> str:
        return "agent"

    def register_agent(
        self,
        agent_id: str,
        agent_type: str = "unknown",
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Registra un agente conocido."""
        self.known_agents[agent_id] = {
            "type": agent_type,
            "status": "active",
            "last_seen": time.time(),
            "metadata": metadata or {},
        }

    def update_agent_status(self, agent_id: str, status: str) -> None:
        """Actualiza estado de un agente."""
        if agent_id in self.known_agents:
            self.known_agents[agent_id]["status"] = status
            self.known_agents[agent_id]["last_seen"] = time.time()

    def remove_agent(self, agent_id: str) -> None:
        """Elimina un agente conocido."""
        self.known_agents.pop(agent_id, None)

    async def observe(self) -> Optional[Observation]:
        """Observa estado de agentes conocidos."""
        self._iteration += 1
        now = time.time()

        if not self.known_agents:
            return Observation(
                timestamp=now,
                source=self.name,
                content=f"Sin agentes conocidos en el entorno (iteración {self._iteration}).",
                metadata={"agent_count": 0, "iteration": self._iteration},
            )

        # Contar agentes activos
        active_count = sum(
            1 for a in self.known_agents.values() if a.get("status") == "active"
        )

        # Detectar agentes no vistos recientemente
        stale_agents = []
        for agent_id, info in self.known_agents.items():
            last_seen = info.get("last_seen", 0)
            if now - last_seen > 300:  # 5 min sin señal
                stale_agents.append(agent_id)

        content_parts = [
            f"{active_count}/{len(self.known_agents)} agentes activos.",
        ]
        if stale_agents:
            content_parts.append(
                f"Agentes sin señal reciente: {', '.join(stale_agents[:3])}."
            )

        return Observation(
            timestamp=now,
            source=self.name,
            content=" ".join(content_parts),
            metadata={
                "agent_count": len(self.known_agents),
                "active_count": active_count,
                "stale_agents": stale_agents,
                "iteration": self._iteration,
            },
        )
