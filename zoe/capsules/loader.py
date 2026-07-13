"""
ZOE v1.1 — Capsule Loader

Carga cápsulas de conocimiento al inicializar ZOE y las inyecta en
los componentes correspondientes (memoria, CausalEngine, EmotionalMotor, etc.).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

import yaml

from .schema import (
    CapsuleMeta, TrustLevel, parse_capsule_yaml, validate_capsule_yaml,
    TRUST_TO_CONFIDENCE,
)

logger = logging.getLogger(__name__)


@dataclass
class LoadedCapsule:
    """Una cápsula cargada en memoria, lista para inyectar."""
    meta: CapsuleMeta
    path: Path
    
    # Contenido cargado (puede estar vacío si el componente no aplica)
    semantic_memory: List[Dict[str, Any]] = field(default_factory=list)
    procedural_skills: List[Dict[str, Any]] = field(default_factory=list)
    causal_models: List[Dict[str, Any]] = field(default_factory=list)
    emotional_patterns: List[Dict[str, Any]] = field(default_factory=list)
    ethical_guidelines: List[Dict[str, Any]] = field(default_factory=list)
    validators: Optional[Any] = None  # módulo Python cargado dinámicamente
    tools: List[Any] = field(default_factory=list)  # instancias de tools
    prompts: Dict[str, str] = field(default_factory=dict)
    
    @property
    def name(self) -> str:
        return self.meta.name
    
    @property
    def total_entries(self) -> int:
        return (
            len(self.semantic_memory) +
            len(self.procedural_skills) +
            len(self.causal_models) +
            len(self.emotional_patterns) +
            len(self.ethical_guidelines)
        )


class CapsuleLoadError(Exception):
    """Error al cargar una cápsula."""


class CapsuleLoader:
    """Carga cápsulas al inicializar ZOE."""
    
    def __init__(self, capsules_dir: Optional[Path] = None):
        if capsules_dir is None:
            capsules_dir = Path(__file__).parent
        self.capsules_dir = capsules_dir
    
    def list_available(self) -> List[str]:
        """Lista las cápsulas disponibles en el directorio."""
        if not self.capsules_dir.exists():
            return []
        return [
            d.name for d in self.capsules_dir.iterdir()
            if d.is_dir() and (d / "capsule.yaml").exists()
        ]
    
    def load_for_use_case(
        self, use_case_name: str, config: Dict[str, Any]
    ) -> List[LoadedCapsule]:
        """
        Carga todas las cápsulas compatibles con un caso de uso.
        
        Args:
            use_case_name: nombre del caso de uso
            config: dict con keys 'required', 'recommended', 'optional'
        
        Returns:
            Lista de LoadedCapsule listas para inyectar
        """
        capsule_config = config.get("capsules", {})
        if isinstance(capsule_config, dict):
            required = capsule_config.get("required", [])
            recommended = capsule_config.get("recommended", [])
            optional = capsule_config.get("optional", [])
        else:
            # Compatibilidad: si es lista, todas required
            required = list(capsule_config)
            recommended = []
            optional = []
        
        capsules: List[LoadedCapsule] = []
        loaded_names: Set[str] = set()
        
        # 1. Required: deben cargarse o fallar
        for name in required:
            if name in loaded_names:
                continue
            cap = self._load_capsule(name)
            if not cap:
                raise CapsuleLoadError(f"Required capsule not found: {name}")
            capsules.append(cap)
            loaded_names.add(name)
            logger.info(f"Loaded required capsule: {name} ({cap.total_entries} entries)")
        
        # 2. Recommended: cargar si existen
        for name in recommended:
            if name in loaded_names:
                continue
            try:
                cap = self._load_capsule(name)
                if cap:
                    capsules.append(cap)
                    loaded_names.add(name)
                    logger.info(f"Loaded recommended capsule: {name} ({cap.total_entries} entries)")
            except CapsuleLoadError as e:
                logger.warning(f"Could not load recommended capsule {name}: {e}")
        
        # 3. Optional: cargar si existen y no hay conflicto
        for name in optional:
            if name in loaded_names:
                continue
            try:
                cap = self._load_capsule(name)
                if cap:
                    capsules.append(cap)
                    loaded_names.add(name)
                    logger.info(f"Loaded optional capsule: {name} ({cap.total_entries} entries)")
            except CapsuleLoadError as e:
                logger.warning(f"Could not load optional capsule {name}: {e}")
        
        # 4. Resolver dependencias recursivas
        capsules = self._resolve_dependencies(capsules, loaded_names)
        
        return capsules
    
    def _load_capsule(self, name: str) -> Optional[LoadedCapsule]:
        """Carga una cápsula individual desde disco."""
        cap_dir = self.capsules_dir / name
        yaml_path = cap_dir / "capsule.yaml"
        
        if not yaml_path.exists():
            return None
        
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            # El YAML puede estar anidado bajo 'capsule:' key
            if "capsule" in data and "name" not in data:
                data = data["capsule"]
            
            meta = parse_capsule_yaml(data)
            
            cap = LoadedCapsule(meta=meta, path=cap_dir)
            
            # Cargar componentes según meta.components
            components = meta.components
            
            if components.get("semantic_memory"):
                cap.semantic_memory = self._load_jsonl(cap_dir / "semantic_memory.jsonl")
            
            if components.get("procedural_skills"):
                cap.procedural_skills = self._load_jsonl(cap_dir / "procedural_skills.jsonl")
            
            if components.get("causal_models"):
                cap.causal_models = self._load_jsonl(cap_dir / "causal_models.jsonl")
            
            if components.get("emotional_patterns"):
                cap.emotional_patterns = self._load_jsonl(cap_dir / "emotional_patterns.jsonl")
            
            if components.get("ethical_guidelines"):
                cap.ethical_guidelines = self._load_jsonl(cap_dir / "ethical_guidelines.jsonl")
            
            if components.get("validators"):
                cap.validators = self._load_python_module(
                    cap_dir / "validators.py", module_name=f"capsule_{name}_validators"
                )
            
            if components.get("tools"):
                cap.tools = self._load_tools(cap_dir / "tools")
            
            if components.get("prompts"):
                cap.prompts = self._load_prompts(cap_dir / "prompts")
            
            return cap
            
        except Exception as e:
            logger.error(f"Failed to load capsule {name}: {e}")
            raise CapsuleLoadError(f"Failed to load capsule {name}: {e}")
    
    def _load_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        """Carga un archivo JSON Lines."""
        if not path.exists():
            return []
        entries = []
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON in {path}:{line_num}: {e}")
        return entries
    
    def _load_python_module(self, path: Path, module_name: str):
        """Carga dinámicamente un módulo Python."""
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def _load_tools(self, tools_dir: Path) -> List[Any]:
        """Carga todas las tools de un directorio."""
        if not tools_dir.exists():
            return []
        tools = []
        for py_file in sorted(tools_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            try:
                module = self._load_python_module(
                    py_file, module_name=f"capsule_tool_{py_file.stem}"
                )
                # Convención: cada tool define una clase con su nombre
                # Buscar clases con método 'execute' o 'run'
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        hasattr(attr, "execute") or hasattr(attr, "run")):
                        try:
                            instance = attr()
                            tools.append(instance)
                            break
                        except Exception as e:
                            logger.warning(f"Could not instantiate tool {attr_name}: {e}")
            except Exception as e:
                logger.warning(f"Could not load tool {py_file}: {e}")
        return tools
    
    def _load_prompts(self, prompts_dir: Path) -> Dict[str, str]:
        """Carga todos los prompts .md de un directorio."""
        if not prompts_dir.exists():
            return {}
        prompts = {}
        for md_file in sorted(prompts_dir.glob("*.md")):
            with open(md_file, "r", encoding="utf-8") as f:
                prompts[md_file.stem] = f.read()
        return prompts
    
    def _resolve_dependencies(
        self, capsules: List[LoadedCapsule], loaded_names: Set[str]
    ) -> List[LoadedCapsule]:
        """Resuelve dependencias recursivas cargando cápsulas faltantes."""
        changed = True
        while changed:
            changed = False
            for cap in list(capsules):
                for dep in cap.meta.depends_on:
                    if dep not in loaded_names:
                        try:
                            dep_cap = self._load_capsule(dep)
                            if dep_cap:
                                capsules.append(dep_cap)
                                loaded_names.add(dep)
                                changed = True
                                logger.info(f"Loaded dependency: {dep} (required by {cap.name})")
                        except CapsuleLoadError as e:
                            logger.warning(f"Could not load dependency {dep}: {e}")
        
        # Verificar dependencias circulares
        self._check_circular_deps(capsules)
        
        # Ordenar: dependencias primero
        return self._topological_sort(capsules)
    
    def _check_circular_deps(self, capsules: List[LoadedCapsule]) -> None:
        """Detecta dependencias circulares."""
        cap_by_name = {c.name: c for c in capsules}
        visited = set()
        rec_stack = set()
        
        def visit(name: str, path: List[str]) -> None:
            if name in rec_stack:
                cycle = path + [name]
                raise CapsuleLoadError(f"Circular dependency detected: {' -> '.join(cycle)}")
            if name in visited:
                return
            visited.add(name)
            rec_stack.add(name)
            cap = cap_by_name.get(name)
            if cap:
                for dep in cap.meta.depends_on:
                    visit(dep, path + [name])
            rec_stack.discard(name)
        
        for cap in capsules:
            visit(cap.name, [])
    
    def _topological_sort(self, capsules: List[LoadedCapsule]) -> List[LoadedCapsule]:
        """Ordena para que las dependencias se carguen primero."""
        cap_by_name = {c.name: c for c in capsules}
        visited = set()
        result: List[LoadedCapsule] = []
        
        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            cap = cap_by_name.get(name)
            if cap:
                for dep in cap.meta.depends_on:
                    if dep in cap_by_name:
                        visit(dep)
                result.append(cap)
        
        for cap in capsules:
            visit(cap.name)
        
        return result
    
    def compute_content_hash(self, cap: LoadedCapsule) -> str:
        """Calcula hash SHA-256 del contenido de la cápsula."""
        h = hashlib.sha256()
        h.update(cap.meta.name.encode())
        h.update(cap.meta.version.encode())
        for entry in cap.semantic_memory:
            h.update(json.dumps(entry, sort_keys=True).encode())
        for entry in cap.causal_models:
            h.update(json.dumps(entry, sort_keys=True).encode())
        for entry in cap.emotional_patterns:
            h.update(json.dumps(entry, sort_keys=True).encode())
        for entry in cap.ethical_guidelines:
            h.update(json.dumps(entry, sort_keys=True).encode())
        return f"sha256:{h.hexdigest()}"
