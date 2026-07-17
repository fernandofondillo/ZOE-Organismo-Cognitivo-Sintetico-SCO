"""
Utilidades compartidas del dashboard.

Funciones sanitización de nombres, construcción de rutas seguras,
y helpers usados por handlers y middleware.
"""

from __future__ import annotations

import re
from pathlib import Path


def _sanitize_name(name: str) -> str:
    """Sanitiza un nombre de cápsula/archivo: solo permite [a-zA-Z0-9_-]."""
    return re.sub(r"[^a-zA-Z0-9_-]", "", name)


def _safe_path(base: Path, name: str) -> Path:
    """Construye una ruta segura dentro de *base* sanitizando *name*.

    Raises:
        ValueError: si la ruta resuelta escapa de *base*.

    Sprint 5.24 F3v2-7 (BUG-033 fix): usar ``relative_to`` en vez de
    ``str.startswith`` para evitar falsos positivos cuando ``base`` es
    un prefijo string de otra carpeta (p.ej. ``/data/zoe`` vs
    ``/data/zoe-evil``).
    """
    safe = _sanitize_name(name)
    if not safe:
        raise ValueError(f"Invalid name after sanitization: {name!r}")
    result = (base / safe).resolve()
    base_resolved = base.resolve()
    # Sprint 5.24: usar relative_to que es estrictamente más seguro que startswith
    try:
        result.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"Invalid path: {safe} (escapes base {base_resolved})")
    return result
