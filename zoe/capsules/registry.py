"""
ZOE v1.1 — Capsule Registry

Registro de cápsulas disponibles, con metadata para búsqueda y compatibilidad.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .loader import CapsuleLoader, LoadedCapsule
from .schema import CapsuleMeta, TrustLevel, parse_capsule_yaml

logger = logging.getLogger(__name__)


class CapsuleRegistry:
    """
    Registro de cápsulas disponibles en el sistema.
    
    Mantiene un índice de metadata para que ZOE pueda:
    - Listar cápsulas disponibles
    - Buscar cápsulas por dominio
    - Buscar cápsulas compatibles con un caso de uso
    - Verificar dependencias antes de cargar
    """
    
    def __init__(self, capsules_dir: Optional[Path] = None):
        self.loader = CapsuleLoader(capsules_dir)
        self._index: Dict[str, CapsuleMeta] = {}
        self._refresh_index()
    
    def _refresh_index(self) -> None:
        """Refresca el índice leyendo todos los capsule.yaml."""
        self._index.clear()
        for name in self.loader.list_available():
            try:
                yaml_path = self.loader.capsules_dir / name / "capsule.yaml"
                with open(yaml_path, "r", encoding="utf-8") as f:
                    import yaml
                    data = yaml.safe_load(f)
                if "capsule" in data and "name" not in data:
                    data = data["capsule"]
                meta = parse_capsule_yaml(data)
                self._index[name] = meta
            except Exception as e:
                logger.warning(f"Could not index capsule {name}: {e}")
    
    def list_all(self) -> List[CapsuleMeta]:
        """Lista metadata de todas las cápsulas disponibles."""
        return list(self._index.values())
    
    def get(self, name: str) -> Optional[CapsuleMeta]:
        """Obtiene metadata de una cápsula por nombre."""
        return self._index.get(name)
    
    def by_domain(self, domain_prefix: str) -> List[CapsuleMeta]:
        """Busca cápsulas cuyo dominio empieza con el prefijo."""
        return [
            m for m in self._index.values()
            if m.domain.startswith(domain_prefix)
        ]
    
    def by_use_case(self, use_case: str) -> List[CapsuleMeta]:
        """Busca cápsulas compatibles con un caso de uso."""
        return [
            m for m in self._index.values()
            if use_case in m.compatible_use_cases
        ]
    
    def by_trust_level(self, level: TrustLevel) -> List[CapsuleMeta]:
        """Busca cápsulas por nivel de confianza."""
        return [m for m in self._index.values() if m.trust_level == level]
    
    def capabilities_for(self, capsule_name: str) -> List[str]:
        """Devuelve las capacidades que otorga una cápsula."""
        meta = self._index.get(capsule_name)
        return meta.capabilities if meta else []
    
    def check_compatibility(
        self, capsule_name: str, use_case: str
    ) -> tuple[bool, str]:
        """
        Verifica si una cápsula es compatible con un caso de uso.
        
        Returns:
            (ok, reason)
        """
        meta = self._index.get(capsule_name)
        if not meta:
            return False, f"capsule_not_found:{capsule_name}"
        
        if use_case not in meta.compatible_use_cases:
            return False, f"not_compatible_with_use_case:{use_case}"
        
        return True, "ok"
    
    def get_dependency_tree(self, capsule_name: str) -> Dict[str, Any]:
        """
        Devuelve el árbol de dependencias de una cápsula.
        
        Returns:
            Dict anidado con la estructura de dependencias.
        """
        meta = self._index.get(capsule_name)
        if not meta:
            return {"error": f"capsule_not_found:{capsule_name}"}
        
        tree = {
            "name": capsule_name,
            "trust_level": meta.trust_level.value,
            "dependencies": [],
        }
        
        for dep in meta.depends_on:
            dep_tree = self.get_dependency_tree(dep)
            tree["dependencies"].append(dep_tree)
        
        return tree
    
    def stats(self) -> Dict[str, Any]:
        """Estadísticas del registro."""
        total = len(self._index)
        by_trust = {}
        for meta in self._index.values():
            level = meta.trust_level.value
            by_trust[level] = by_trust.get(level, 0) + 1
        
        by_domain = {}
        for meta in self._index.values():
            top_domain = meta.domain.split(".")[0]
            by_domain[top_domain] = by_domain.get(top_domain, 0) + 1
        
        return {
            "total_capsules": total,
            "by_trust_level": by_trust,
            "by_top_domain": by_domain,
            "capsules_dir": str(self.loader.capsules_dir),
        }
