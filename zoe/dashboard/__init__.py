"""
ZOE Dashboard -- Paquete de modulos del dashboard web.

Backward compatibility: DashboardServer se exporta desde aqui.
"""

from __future__ import annotations

from .server import DashboardServer

__all__ = ["DashboardServer"]
