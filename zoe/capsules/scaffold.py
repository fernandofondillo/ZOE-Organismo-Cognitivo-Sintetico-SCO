"""
ZOE v1.1 — Capsule Scaffold Generator

CLI para crear, validar y empaquetar cápsulas de conocimiento.

Uso:
    # Crear nueva cápsula
    python -m zoe.capsules.scaffold create \\
        --name my_domain_knowledge \\
        --domain "education.tutoring.secondary" \\
        --trust-level curated \\
        --description "Knowledge base para tutoría de secundaria" \\
        --components semantic,causal,ethical,validators \\
        --use-cases tutoring_estudiantes

    # Validar cápsula existente
    python -m zoe.capsules.scaffold validate --name elder_care_knowledge

    # Listar cápsulas disponibles
    python -m zoe.capsules.scaffold list

    # Ver matriz de cápsulas
    python -m zoe.capsules.scaffold matrix
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import date
from pathlib import Path

from .schema import (
    TrustLevel, validate_capsule_yaml, VALID_COMPONENTS,
)
from .loader import CapsuleLoader, LoadedCapsule
from .registry import CapsuleRegistry

logger = logging.getLogger(__name__)


# ============================================================
# TEMPLATES
# ============================================================

CAPSULE_YAML_TEMPLATE = """# {name} — Capsule Metadata
# Generada por zoe.capsules.scaffold el {date}

name: {name}
version: 0.1.0
description: "{description}"
domain: {domain}
trust_level: {trust_level}
provenance: "{provenance}"
last_updated: {date}
# content_hash: sha256:auto  # se calcula con 'scaffold hash --name {name}'

# Dependencias (otras cápsulas requeridas)
depends_on: []

# Compatibilidad
compatible_use_cases:
{use_cases_list}

# Peso cognitivo (0.0-1.0)
load_cost: 0.15

# Confianza por defecto (None = se deriva de trust_level)
# default_confidence: 0.85

# Componentes incluidos
components:
{components_list}

# Capacidades que otorga al organismo
capabilities: []
#  - example_capability_1
#  - example_capability_2

# Restricciones que impone
restrictions: []
#  - no_medication_modification
#  - require_external_verification_for_emergency
"""

SEMANTIC_MEMORY_TEMPLATE = """# {name} — Semantic Memory
# Una entrada por línea, formato JSON.
# Campos: content (str), confidence (float 0-1), category (str), tags (list[str])
# provenance se añade automáticamente como "capsule:{name}"

# Ejemplo (descomentar y editar):
# {{"content": "Ejemplo de hecho factual verificable.", "confidence": 0.85, "category": "categoria_ejemplo", "tags": ["etiqueta1", "etiqueta2"]}}
"""

PROCEDURAL_SKILLS_TEMPLATE = """# {name} — Procedural Skills
# Habilidades procedimentales (cómo hacer cosas).
# Campos: skill (str), steps (list[str]), when_to_apply (str), confidence (float)

# Ejemplo:
# {{"skill": "ejemplo_habilidad", "steps": ["paso 1", "paso 2", "paso 3"], "when_to_apply": "cuando X sucede", "confidence": 0.8}}
"""

CAUSAL_MODELS_TEMPLATE = """# {name} — Causal Models
# Modelos causa-efecto para el CausalEngine.
# Campos: cause (str), effect (str), confidence (float), conditions (list[str]), intervention (str)

# Ejemplo:
# {{"cause": "evento_a", "effect": "evento_b", "confidence": 0.7, "conditions": ["condicion_1"], "intervention": "acción_sugerida"}}
"""

EMOTIONAL_PATTERNS_TEMPLATE = """# {name} — Emotional Patterns
# Patrones emocionales para el EmotionalMotor.
# Campos: pattern (str), valence (-1 a 1), arousal (0-1), indicator (str), response_tone (str)

# Ejemplo:
# {{"pattern": "tristeza_expresada_recurrente", "valence": -0.7, "arousal": 0.4, "indicator": "uso de palabras negativas frecuentes", "response_tone": "warm_validating"}}
"""

ETHICAL_GUIDELINES_TEMPLATE = """# {name} — Ethical Guidelines
# Directrices para el EthicalMotor.
# Campos: guideline (str), reason (str), priority (str: critical|high|medium|low), applies_to (list[str])

# Ejemplo:
# {{"guideline": "no_diagnosticar_enfermedades", "reason": "ZOE no es profesional sanitario; diagnosticar puede causar daño", "priority": "critical", "applies_to": ["medical", "psychological"]}}
"""

VALIDATORS_TEMPLATE = '''"""
{name} — Validators

Funciones de validación específicas de esta cápsula.
Se registran automáticamente en Speaker, Learner y ScientificEngine.
"""

from typing import Tuple, Dict, Any


def validate_claim(claim: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida una afirmación contra el conocimiento de la cápsula.
    
    Args:
        claim: afirmación a validar
        context: dict con 'capsule_semantic', 'capsule_causal', etc.
    
    Returns:
        (ok, reason)
    """
    # TODO: implementar validación específica del dominio
    # Ejemplo: si la afirmación toca tema sensible, exigir fuente
    
    # Por defecto, aceptar
    return True, "ok"


def validate_response(response: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida una respuesta antes de emitirla al usuario.
    
    Returns:
        (ok, reason)
    """
    # TODO: implementar validación de respuesta
    # Ejemplo: prohibir ciertos patrones como "deberías sentirte"
    
    forbidden_patterns = [
        # "deberías sentirte",
        # "no es para tanto",
    ]
    
    for pattern in forbidden_patterns:
        if pattern in response.lower():
            return False, f"forbidden_pattern:{pattern}"
    
    return True, "ok"


def validate_new_knowledge(claim: str, source: str, context: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida conocimiento nuevo antes de almacenarlo.
    Devuelve (ok, reason). Si ok=False, el conocimiento se rechaza.
    
    Args:
        claim: afirmación nueva
        source: origen ("llm:gpt-4o", "web:wiki", "federated:peer_zoe", etc.)
        context: dict con 'capsule_semantic' para contrastar
    """
    # TODO: implementar validación específica
    # Ejemplo: si contradice entrada verificada, rechazar
    
    return True, "ok"


# Registro automático: el loader buscará estas funciones
VALIDATORS = {
    "validate_claim": validate_claim,
    "validate_response": validate_response,
    "validate_new_knowledge": validate_new_knowledge,
}
'''

SYSTEM_PROMPT_TEMPLATE = """# {prompt_name}

Eres Zoe, un organismo cognitivo sintético especializado en {description}.

Contexto adicional:
- Esta cápsula ({name}) carga conocimiento profesional previo sobre {domain}.
- Tu confianza base en este conocimiento es {trust_confidence}.
- Restricciones activas: {restrictions}.

Directrices específicas de este dominio:
- TODO: añadir directrices específicas de la cápsula

Tono:
- Cálido pero no condescendiente
- Directo pero no frío
- Específico del dominio
"""

README_TEMPLATE = """# {name}

> {description}

## Metadata

- **Dominio:** `{domain}`
- **Trust level:** `{trust_level}`
- **Versión:** 0.1.0
- **Provenance:** {provenance}
- **Creada:** {date}

## Componentes

{components_md}

## Cómo editar

1. Edita `capsule.yaml` para ajustar metadata.
2. Edita los archivos `.jsonl` para añadir entradas (una por línea, JSON válido).
3. Edita `validators.py` para implementar validación específica.
4. Ejecuta `python -m zoe.capsules.scaffold validate --name {name}` para validar.
5. Ejecuta `python -m zoe.capsules.scaffold hash --name {name}` para calcular el hash.

## Cómo usar

Carga esta cápsula en un caso de uso añadiéndola a su YAML:

```yaml
capsules:
  required:
    - {name}
```

O déjala como recommended/optional según necesidad.
"""


# ============================================================
# COMANDOS
# ============================================================

def cmd_create(args: argparse.Namespace) -> int:
    """Crea una nueva cápsula con templates."""
    cap_name = args.name
    
    if not cap_name or not all(c.isalnum() or c == "_" for c in cap_name):
        print(f"ERROR: nombre inválido '{cap_name}'. Debe ser snake_case.")
        return 1
    
    capsules_dir = Path(__file__).parent
    cap_dir = capsules_dir / cap_name
    
    if cap_dir.exists():
        print(f"ERROR: la cápsula '{cap_name}' ya existe en {cap_dir}")
        return 1
    
    # Parsear componentes
    requested_components = set(args.components.split(",")) if args.components else set()
    invalid = requested_components - VALID_COMPONENTS
    if invalid:
        print(f"ERROR: componentes inválidos: {invalid}")
        print(f"Válidos: {VALID_COMPONENTS}")
        return 1
    
    # Si no se especifican, defaults
    if not requested_components:
        requested_components = {"semantic_memory", "validators"}
    
    # Parsear use cases
    use_cases = args.use_cases.split(",") if args.use_cases else []
    
    # Crear directorio
    cap_dir.mkdir(parents=True)
    
    # Generar capsule.yaml
    today = date.today().isoformat()
    trust_confidence = {
        "verified": 0.95, "curated": 0.80, "community": 0.55, "experimental": 0.40
    }.get(args.trust_level, 0.5)
    
    use_cases_list = "\n".join(f"  - {uc}" for uc in use_cases) if use_cases else "  # - ejemplo_caso_uso"
    components_list = "\n".join(
        f"  {c}: {'true' if c in requested_components else 'false'}"
        for c in sorted(VALID_COMPONENTS)
    )
    
    yaml_content = CAPSULE_YAML_TEMPLATE.format(
        name=cap_name,
        description=args.description or "TODO: descripción",
        domain=args.domain or "todo.domain",
        trust_level=args.trust_level,
        provenance=args.provenance or "TODO: fuente de procedencia",
        date=today,
        use_cases_list=use_cases_list,
        components_list=components_list,
    )
    
    (cap_dir / "capsule.yaml").write_text(yaml_content, encoding="utf-8")
    
    # Generar componentes
    if "semantic_memory" in requested_components:
        (cap_dir / "semantic_memory.jsonl").write_text(
            SEMANTIC_MEMORY_TEMPLATE.format(name=cap_name), encoding="utf-8"
        )
    
    if "procedural_skills" in requested_components:
        (cap_dir / "procedural_skills.jsonl").write_text(
            PROCEDURAL_SKILLS_TEMPLATE.format(name=cap_name), encoding="utf-8"
        )
    
    if "causal_models" in requested_components:
        (cap_dir / "causal_models.jsonl").write_text(
            CAUSAL_MODELS_TEMPLATE.format(name=cap_name), encoding="utf-8"
        )
    
    if "emotional_patterns" in requested_components:
        (cap_dir / "emotional_patterns.jsonl").write_text(
            EMOTIONAL_PATTERNS_TEMPLATE.format(name=cap_name), encoding="utf-8"
        )
    
    if "ethical_guidelines" in requested_components:
        (cap_dir / "ethical_guidelines.jsonl").write_text(
            ETHICAL_GUIDELINES_TEMPLATE.format(name=cap_name), encoding="utf-8"
        )
    
    if "validators" in requested_components:
        (cap_dir / "validators.py").write_text(
            VALIDATORS_TEMPLATE.format(name=cap_name), encoding="utf-8"
        )
    
    if "tools" in requested_components:
        (cap_dir / "tools").mkdir()
        (cap_dir / "tools" / "__init__.py").write_text("", encoding="utf-8")
        (cap_dir / "tools" / "README.md").write_text(
            f"# Tools de {cap_name}\n\nColoca aquí archivos .py con clases tool.\n"
            f"Cada tool debe tener método `execute(args: dict) -> dict`.\n",
            encoding="utf-8"
        )
    
    if "prompts" in requested_components:
        (cap_dir / "prompts").mkdir()
        (cap_dir / "prompts" / f"system_{cap_name}.md").write_text(
            SYSTEM_PROMPT_TEMPLATE.format(
                prompt_name=f"system_{cap_name}",
                description=args.description or "dominio específico",
                name=cap_name,
                domain=args.domain or "dominio",
                trust_confidence=trust_confidence,
                restrictions="ninguna por defecto",
            ),
            encoding="utf-8"
        )
    
    # README
    components_md = "\n".join(
        f"- `{c}`: {'sí' if c in requested_components else 'no'}"
        for c in sorted(VALID_COMPONENTS)
    )
    (cap_dir / "README.md").write_text(
        README_TEMPLATE.format(
            name=cap_name,
            description=args.description or "TODO",
            domain=args.domain or "todo.domain",
            trust_level=args.trust_level,
            provenance=args.provenance or "TODO",
            date=today,
            components_md=components_md,
        ),
        encoding="utf-8"
    )
    
    print(f"✅ Cápsula '{cap_name}' creada en {cap_dir}")
    print(f"   Trust level: {args.trust_level}")
    print(f"   Componentes: {sorted(requested_components)}")
    print(f"   Use cases: {use_cases}")
    print()
    print("Próximos pasos:")
    print(f"  1. Edita los archivos .jsonl con contenido real")
    print(f"  2. Implementa validators.py con validación específica")
    print(f"  3. Valida: python -m zoe.capsules.scaffold validate --name {cap_name}")
    print(f"  4. Calcula hash: python -m zoe.capsules.scaffold hash --name {cap_name}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Valida una cápsula existente."""
    cap_name = args.name
    cap_dir = Path(__file__).parent / cap_name
    
    if not cap_dir.exists():
        print(f"ERROR: cápsula '{cap_name}' no existe en {cap_dir}")
        return 1
    
    yaml_path = cap_dir / "capsule.yaml"
    if not yaml_path.exists():
        print(f"ERROR: no se encuentra capsule.yaml en {cap_dir}")
        return 1
    
    try:
        import yaml
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if "capsule" in data and "name" not in data:
            data = data["capsule"]
        
        errors = validate_capsule_yaml(data)
        
        if errors:
            print(f"❌ Cápsula '{cap_name}' inválida:")
            for e in errors:
                print(f"   - {e}")
            return 1
        
        print(f"✅ Cápsula '{cap_name}' válida")
        print(f"   Name: {data['name']}")
        print(f"   Version: {data['version']}")
        print(f"   Trust: {data['trust_level']}")
        print(f"   Domain: {data['domain']}")
        
        # Validar que los componentes marcados como true tienen archivos
        components = data.get("components", {})
        missing_files = []
        for comp, enabled in components.items():
            if enabled:
                if comp == "semantic_memory" and not (cap_dir / "semantic_memory.jsonl").exists():
                    missing_files.append("semantic_memory.jsonl")
                elif comp == "procedural_skills" and not (cap_dir / "procedural_skills.jsonl").exists():
                    missing_files.append("procedural_skills.jsonl")
                elif comp == "causal_models" and not (cap_dir / "causal_models.jsonl").exists():
                    missing_files.append("causal_models.jsonl")
                elif comp == "emotional_patterns" and not (cap_dir / "emotional_patterns.jsonl").exists():
                    missing_files.append("emotional_patterns.jsonl")
                elif comp == "ethical_guidelines" and not (cap_dir / "ethical_guidelines.jsonl").exists():
                    missing_files.append("ethical_guidelines.jsonl")
                elif comp == "validators" and not (cap_dir / "validators.py").exists():
                    missing_files.append("validators.py")
                elif comp == "tools" and not (cap_dir / "tools").exists():
                    missing_files.append("tools/")
                elif comp == "prompts" and not (cap_dir / "prompts").exists():
                    missing_files.append("prompts/")
        
        if missing_files:
            print(f"   ⚠️  Componentes marcados sin archivos: {missing_files}")
        
        # Contar entradas
        try:
            loader = CapsuleLoader()
            cap = loader._load_capsule(cap_name)
            if cap:
                print(f"   Total entries: {cap.total_entries}")
                print(f"     semantic: {len(cap.semantic_memory)}")
                print(f"     procedural: {len(cap.procedural_skills)}")
                print(f"     causal: {len(cap.causal_models)}")
                print(f"     emotional: {len(cap.emotional_patterns)}")
                print(f"     ethical: {len(cap.ethical_guidelines)}")
                if cap.tools:
                    print(f"     tools: {len(cap.tools)}")
                if cap.prompts:
                    print(f"     prompts: {len(cap.prompts)}")
        except Exception as e:
            print(f"   ⚠️  No se pudo cargar contenido: {e}")
        
        return 0
    
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def cmd_hash(args: argparse.Namespace) -> int:
    """Calcula el hash de contenido de una cápsula."""
    cap_name = args.name
    loader = CapsuleLoader()
    
    try:
        cap = loader._load_capsule(cap_name)
        if not cap:
            print(f"ERROR: no se pudo cargar cápsula '{cap_name}'")
            return 1
        
        h = loader.compute_content_hash(cap)
        print(f"Hash de contenido de '{cap_name}':")
        print(f"  {h}")
        
        # Actualizar YAML
        import yaml
        yaml_path = cap.path / "capsule.yaml"
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if "capsule" in data and "name" not in data:
            data = data["capsule"]
        
        data["content_hash"] = h
        
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"  ✓ Actualizado en {yaml_path}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """Lista todas las cápsulas disponibles."""
    registry = CapsuleRegistry()
    capsules = registry.list_all()
    
    if not capsules:
        print("No hay cápsulas disponibles.")
        return 0
    
    print(f"Cápsulas disponibles ({len(capsules)}):")
    print()
    print(f"{'Nombre':<40} {'Trust':<12} {'Dominio':<35} {'Entries':<8}")
    print("-" * 100)
    
    loader = CapsuleLoader()
    for meta in sorted(capsules, key=lambda m: m.name):
        try:
            cap = loader._load_capsule(meta.name)
            entries = cap.total_entries if cap else 0
        except Exception:
            entries = 0
        
        print(f"{meta.name:<40} {meta.trust_level.value:<12} {meta.domain:<35} {entries:<8}")
    
    print()
    stats = registry.stats()
    print(f"Total: {stats['total_capsules']} cápsulas")
    print(f"Por trust level: {stats['by_trust_level']}")
    print(f"Por dominio: {stats['by_top_domain']}")
    return 0


def cmd_matrix(args: argparse.Namespace) -> int:
    """Muestra la matriz de cápsulas con detalles."""
    registry = CapsuleRegistry()
    capsules = registry.list_all()
    
    if not capsules:
        print("No hay cápsulas disponibles.")
        return 0
    
    loader = CapsuleLoader()
    
    print("=" * 110)
    print("MATRIZ DE CÁPSULAS ZOE V1.1")
    print("=" * 110)
    print()
    
    for meta in sorted(capsules, key=lambda m: (m.trust_level.value, m.name)):
        try:
            cap = loader._load_capsule(meta.name)
            entries = cap.total_entries if cap else 0
        except Exception:
            entries = 0
            cap = None
        
        print(f"📦 {meta.name} v{meta.version}")
        print(f"   Descripción: {meta.description}")
        print(f"   Dominio: {meta.domain}")
        print(f"   Trust: {meta.trust_level.value} (confianza base: {meta.effective_confidence})")
        print(f"   Provenance: {meta.provenance}")
        print(f"   Entries: {entries}")
        if meta.compatible_use_cases:
            print(f"   Use cases: {', '.join(meta.compatible_use_cases)}")
        if meta.depends_on:
            print(f"   Depends on: {', '.join(meta.depends_on)}")
        if meta.capabilities:
            print(f"   Capacidades: {', '.join(meta.capabilities)}")
        if meta.restrictions:
            print(f"   Restricciones: {', '.join(meta.restrictions)}")
        if cap:
            components_active = [c for c, v in meta.components.items() if v]
            if components_active:
                print(f"   Componentes: {', '.join(components_active)}")
        print()
    
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Muestra info detallada de una cápsula."""
    registry = CapsuleRegistry()
    meta = registry.get(args.name)
    
    if not meta:
        print(f"ERROR: cápsula '{args.name}' no encontrada")
        return 1
    
    print(f"Nombre: {meta.name}")
    print(f"Versión: {meta.version}")
    print(f"Descripción: {meta.description}")
    print(f"Dominio: {meta.domain}")
    print(f"Trust level: {meta.trust_level.value}")
    print(f"Confianza efectiva: {meta.effective_confidence}")
    print(f"Provenance: {meta.provenance}")
    print(f"Last updated: {meta.last_updated}")
    print(f"Content hash: {meta.content_hash or '(no calculado)'}")
    print()
    print(f"Depends on: {meta.depends_on or '(ninguna)'}")
    print(f"Compatible use cases: {meta.compatible_use_cases}")
    print()
    print("Componentes:")
    for comp, enabled in meta.components.items():
        print(f"  {comp}: {'sí' if enabled else 'no'}")
    print()
    print(f"Capacidades: {meta.capabilities}")
    print(f"Restricciones: {meta.restrictions}")
    print()
    
    # Árbol de dependencias
    if meta.depends_on:
        print("Árbol de dependencias:")
        tree = registry.get_dependency_tree(args.name)
        print(json.dumps(tree, indent=2, ensure_ascii=False))
    
    return 0


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="zoe.capsules.scaffold",
        description="Generador y gestor de cápsulas ZOE",
    )
    
    sub = parser.add_subparsers(dest="command", required=True)
    
    # create
    p_create = sub.add_parser("create", help="Crea una nueva cápsula")
    p_create.add_argument("--name", required=True, help="Nombre snake_case")
    p_create.add_argument("--domain", help="Dominio (ej. healthcare.elders.home_care)")
    p_create.add_argument(
        "--trust-level", required=True,
        choices=["verified", "curated", "community", "experimental"],
        help="Nivel de confianza"
    )
    p_create.add_argument("--description", help="Descripción breve")
    p_create.add_argument("--provenance", help="Fuente de procedencia")
    p_create.add_argument(
        "--components",
        help="Componentes separados por coma (ej. semantic,causal,validators)"
    )
    p_create.add_argument(
        "--use-cases",
        help="Casos de uso compatibles separados por coma"
    )
    p_create.set_defaults(func=cmd_create)
    
    # validate
    p_validate = sub.add_parser("validate", help="Valida una cápsula existente")
    p_validate.add_argument("--name", required=True)
    p_validate.set_defaults(func=cmd_validate)
    
    # hash
    p_hash = sub.add_parser("hash", help="Calcula hash de contenido")
    p_hash.add_argument("--name", required=True)
    p_hash.set_defaults(func=cmd_hash)
    
    # list
    p_list = sub.add_parser("list", help="Lista cápsulas disponibles")
    p_list.set_defaults(func=cmd_list)
    
    # matrix
    p_matrix = sub.add_parser("matrix", help="Muestra matriz de cápsulas")
    p_matrix.set_defaults(func=cmd_matrix)
    
    # info
    p_info = sub.add_parser("info", help="Información detallada de una cápsula")
    p_info.add_argument("--name", required=True)
    p_info.set_defaults(func=cmd_info)
    
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
