"""
ZOE v2.1 -- FederationDiscovery

Descubrimiento automatico de peers ZOE.

Modos:
- manual: registro via POST /federation/epistemic/register (default)
- filesystem: peers.json en SSD compartido
- mdns: zeroconf/mDNS en LAN (futuro)
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class FederationDiscovery:
    """
    Descubrimiento de peers ZOE por filesystem o manual.

    Escenario filesystem (SSD compartido):
    - Cada ZOE al arrancar escribe su URL y organism_id en peers.json
    - Al leerlo, descubre a las demas ZOEs
    """

    def __init__(
        self,
        organism_id: str,
        base_url: str,
        discovery_mode: str = "manual",
        peers_file: Optional[str] = None,
    ):
        self.organism_id = organism_id
        self.base_url = base_url
        self.discovery_mode = discovery_mode
        self._peers_file = peers_file
        self._discovered_peers: Dict[str, dict] = {}

    def announce(self) -> bool:
        """
        Anuncia esta ZOE al mecanismo de discovery.
        En modo filesystem: escribe en peers.json.
        """
        if self.discovery_mode == "filesystem" and self._peers_file:
            return self._announce_filesystem()
        elif self.discovery_mode == "manual":
            return True  # Nada que hacer
        return False

    def discover(self) -> List[Dict[str, Any]]:
        """
        Descubre peers disponibles.
        En modo filesystem: lee peers.json.
        En modo manual: devuelve lista vacia.

        Returns:
            Lista de dicts con {organism_id, base_url, last_seen}
        """
        if self.discovery_mode == "filesystem" and self._peers_file:
            return self._discover_filesystem()
        return []

    def _announce_filesystem(self) -> bool:
        """Escribe esta ZOE en peers.json."""
        try:
            peers = {}
            if os.path.exists(self._peers_file):
                with open(self._peers_file, "r", encoding="utf-8") as f:
                    peers = json.load(f)

            peers[self.organism_id] = {
                "organism_id": self.organism_id,
                "base_url": self.base_url,
                "last_seen": time.time(),
            }

            os.makedirs(os.path.dirname(self._peers_file), exist_ok=True)
            tmp = self._peers_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(peers, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self._peers_file)
            return True
        except Exception as e:
            logger.warning(f"FederationDiscovery: announce failed: {e}")
            return False

    def _discover_filesystem(self) -> List[Dict[str, Any]]:
        """Lee peers desde peers.json, filtrando entradas stale (>5 min)."""
        if not os.path.exists(self._peers_file):
            return []
        try:
            with open(self._peers_file, "r", encoding="utf-8") as f:
                peers = json.load(f)

            now = time.time()
            result = []
            for pid, pdata in peers.items():
                if pid == self.organism_id:
                    continue  # Skip self
                last_seen = pdata.get("last_seen", 0)
                if now - last_seen < 300:  # 5 minutos
                    result.append(pdata)
                else:
                    logger.debug(
                        f"FederationDiscovery: peer {pid} stale, skipping"
                    )
            return result
        except Exception as e:
            logger.warning(f"FederationDiscovery: discover failed: {e}")
            return []

    def cleanup_stale(self, max_age_seconds: int = 300) -> int:
        """Elimina peers antiguos de peers.json. Devuelve cantidad eliminada."""
        if not self._peers_file or not os.path.exists(self._peers_file):
            return 0
        try:
            with open(self._peers_file, "r", encoding="utf-8") as f:
                peers = json.load(f)

            now = time.time()
            stale = [
                pid
                for pid, pdata in peers.items()
                if now - pdata.get("last_seen", 0) > max_age_seconds
            ]
            for pid in stale:
                del peers[pid]

            if stale:
                tmp = self._peers_file + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(peers, f, indent=2, ensure_ascii=False)
                os.replace(tmp, self._peers_file)

            return len(stale)
        except Exception as e:
            logger.warning(f"FederationDiscovery: cleanup failed: {e}")
            return 0
