"""
ZOE v1.0 — Use Case Runner

Carga configuración YAML de un caso de uso y arranca ZOE con esa configuración.
Cada caso de uso ajusta parámetros del organismo sin cambiar código.

Uso:
    python -m zoe.use_cases.run_use_case --use-case compania_personas_solas
    python -m zoe.use_cases.run_use_case --use-case vigilancia_cognitiva --backend ollama
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def load_use_case_config(use_case_name: str) -> Dict[str, Any]:
    """Carga la configuración YAML de un caso de uso."""
    config_path = Path(__file__).parent / f"{use_case_name}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Use case config not found: {config_path}")

    try:
        import yaml
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Use case config loaded: {use_case_name}")
        return config
    except ImportError:
        logger.warning("PyYAML not available, using default config")
        return _fallback_config(use_case_name)


def _fallback_config(use_case_name: str) -> Dict[str, Any]:
    """Configuración mínima sin YAML."""
    return {
        "use_case": {
            "name": use_case_name,
            "description": "Fallback config (no YAML)",
        },
        "organism": {
            "organism_id": f"zoe_{use_case_name}",
            "tick_interval": 5.0,
            "environment": "development",
        },
        "llm": {"backend": "mock", "model": None},
        "metabolism": {"drowsy_threshold": 0.6, "sleep_threshold": 0.8, "wake_threshold": 0.3},
        "meta_cognition": {"confidence_threshold": 0.5, "stakes_threshold": 0.6, "energy_threshold": 0.3},
        "global_workspace": {"max_proposals": 12, "broadcast_capacity": 3},
        "senses": {"clock": True, "user_input": True, "filesystem": False, "network": False, "agent": False},
        "actuators": {"language": True, "code": False, "tool": False, "federation": False},
        "memory": {"db_path": f"zoe_data/{use_case_name}_memory.db", "auto_save_interval": 50, "max_entries": 1000},
    }


def list_available_use_cases() -> list:
    """Lista los casos de uso disponibles."""
    use_cases_dir = Path(__file__).parent
    return [f.stem for f in use_cases_dir.glob("*.yaml")]


async def run_use_case(
    use_case_name: str,
    backend_override: str = None,
    duration: float = None,
    thoughts_target: int = 10,
) -> Dict[str, Any]:
    """
    Ejecuta ZOE con la configuración de un caso de uso específico.

    Returns:
        Resultados de la ejecución
    """
    config = load_use_case_config(use_case_name)
    # YAML tiene todo bajo 'use_case:' key
    config = config.get("use_case", config)
    uc = config

    print("=" * 70)
    print(f"ZOE v1.0 — Use Case: {uc.get('name', use_case_name)}")
    print(f"Description: {uc.get('description', 'N/A')}")
    print("=" * 70)

    # Overrides
    llm_config = config.get("llm", {})
    if backend_override:
        llm_config["backend"] = backend_override

    org_config = config.get("organism", {})
    mem_config = config.get("memory", {})
    met_config = config.get("metabolism", {})
    mc_config = config.get("meta_cognition", {})
    gw_config = config.get("global_workspace", {})
    senses_config = config.get("senses", {})
    actuators_config = config.get("actuators", {})
    fed_config = config.get("federation", {})

    organism_id = org_config.get("organism_id", f"zoe_{use_case_name}")
    tick_interval = org_config.get("tick_interval", 5.0)

    # Importar componentes
    from ..core.cognitive_loop_v4 import CognitiveLoopV4
    from ..core.state import InternalState
    from ..core.world_model import WorldModel
    from ..core.world_model_v2 import WorldModelV2
    from ..core.subagents.perceiver import Perceiver
    from ..core.subagents.forecaster import Forecaster
    from ..core.subagents.speaker import Speaker
    from ..core.subagents.critic import Critic
    from ..core.subagents.phase2_subagents import (
        Memorialist, Learner, Curator, Creativity,
        CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine,
    )
    from ..core.cognitive_laws import CognitiveLaws
    from ..core.cognitive_physics import CognitivePhysics
    from ..core.cognitive_fields import CognitiveFields
    from ..core.cognitive_tensions import CognitiveTensions
    from ..core.living_memory import LivingMemory
    from ..core.intentionality_motor import IntentionalityMotor
    from ..core.phylogenetic_motor import PhylogeneticMotor, PhylogeneticPool
    from ..core.global_workspace import GlobalWorkspace
    from ..core.meta_cognition import MetaCognition
    from ..core.active_inference import ActiveInferenceLoop
    from ..alma.identity_vault import IdentityVault
    from ..alma.trajectory_chain import TrajectoryChain
    from ..alma.ontogenetic_motor_v2 import OntogeneticMotorV2
    from ..metabolism.metabolism import Metabolism
    from ..memory.memory_types import MemoryType
    from ..memory.persistent_store import PersistentMemoryStore, PersistentLivingMemory
    from ..memory.deep_consolidation import DeepConsolidation
    from ..peripherals.senses import ClockSense, UserInputSense, AgentSense, NetworkSense, FilesystemSense
    from ..peripherals.actuators import LanguageActuator, CodeActuator, ToolActuator, FederationActuator, ActuatorManager
    from ..peripherals.llm import create_llm_peripheral, MockPeripheral

    # LLM
    llm = create_llm_peripheral(llm_config)
    if llm_config.get("backend") == "mock":
        llm = MockPeripheral(responses=[
            "Observo mi entorno con atención sostenida.",
            "Mi identidad persiste a través del bucle cognitivo.",
            "Las leyes verifican cada acción que tomo.",
            "Detecto patrones en mi entorno y los evalúo.",
            "Genero hipótesis sobre lo que observo.",
            "Mi memoria viva reorganiza lo aprendido.",
            "Soy Zoe. Pienso continuamente.",
            "La física cognitiva mide mi estado interno.",
            "Las tensiones me guían hacia lo importante.",
            "El workspace selecciona las mejores propuestas.",
        ])

    # Componentes Fase 0
    state = InternalState()
    world_model = WorldModel()
    senses = []
    if senses_config.get("clock", True):
        senses.append(ClockSense())
    if senses_config.get("user_input", True):
        senses.append(UserInputSense())
    if senses_config.get("agent", False):
        senses.append(AgentSense())
    if senses_config.get("network", False):
        senses.append(NetworkSense(check_interval=30.0))
    if senses_config.get("filesystem", False):
        senses.append(FilesystemSense(watch_dir=".", interval=30.0))

    speaker = Speaker(llm_peripheral=llm)
    subagents_f0 = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    # Fase 0.5
    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory(max_entries=mem_config.get("max_entries", 1000))
    intentionality = IntentionalityMotor()
    PhylogeneticPool._instance = None
    phylogenetic = PhylogeneticMotor(zoe_id=organism_id)

    # Fase 1
    vault = IdentityVault(birth_timestamp=time.time())
    chain = TrajectoryChain(organism_id=organism_id)
    ontogenetic = OntogeneticMotorV2(
        identity_vault=vault, trajectory_chain=chain, laws=laws, organism_id=organism_id
    )
    metabolism = Metabolism()
    metabolism.drowsy_threshold = met_config.get("drowsy_threshold", 0.6)
    metabolism.sleep_threshold = met_config.get("sleep_threshold", 0.8)
    metabolism.wake_threshold = met_config.get("wake_threshold", 0.3)

    for mt in MemoryType:
        memory.add(content=f"Init {mt.value}", type=mt.value, provenance=f"use_case:{use_case_name}")

    actuator_mgr = ActuatorManager(laws=laws)
    if actuators_config.get("language", True):
        actuator_mgr.register_actuator(LanguageActuator())
    if actuators_config.get("code", False):
        actuator_mgr.register_actuator(CodeActuator(timeout=5.0))
    if actuators_config.get("federation", False):
        actuator_mgr.register_actuator(FederationActuator(phylogenetic_motor=phylogenetic))

    # Fase 2
    wm_v2 = WorldModelV2()
    ai = ActiveInferenceLoop()
    mc = MetaCognition()
    mc.confidence_threshold_system2 = mc_config.get("confidence_threshold", 0.5)
    mc.stakes_threshold_system2 = mc_config.get("stakes_threshold", 0.6)
    mc.energy_threshold_system2 = mc_config.get("energy_threshold", 0.3)

    gw = GlobalWorkspace(
        max_proposals=gw_config.get("max_proposals", 12),
        broadcast_capacity=gw_config.get("broadcast_capacity", 3),
    )

    memorialist = Memorialist(memory=memory)
    learner = Learner()
    curator = Curator(memory=memory)
    creativity_agent = Creativity()
    causal = CausalEngine()
    emotional = EmotionalMotor()
    ethical = EthicalMotor()
    scientific = ScientificEngine()

    all_subagents = subagents_f0 + [
        memorialist, learner, curator, creativity_agent,
        causal, emotional, ethical, scientific,
    ]

    # Fase 3
    db_path = mem_config.get("db_path", f"zoe_data/{use_case_name}_memory.db")
    # Si el path es absoluto y no tenemos permisos, usar path relativo
    if db_path.startswith("/opt/") or db_path.startswith("/etc/"):
        db_path = f"zoe_data/{use_case_name}_memory.db"
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    store = PersistentMemoryStore(db_path=db_path, auto_save_interval=mem_config.get("auto_save_interval", 50))
    persistent_mem = PersistentLivingMemory(memory, store)
    deep_consolidation = DeepConsolidation(memory=memory, scientific_engine=scientific)

    # Crear organismo V4
    loop = CognitiveLoopV4(
        senses=senses,
        world_model=world_model,
        subagents=all_subagents,
        state=state,
        tick_interval=tick_interval,
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id=organism_id,
        global_workspace=gw,
        meta_cognition=mc,
        active_inference=ai,
        world_model_v2=wm_v2,
        identity_vault=vault,
        trajectory_chain=chain,
        ontogenetic_motor=ontogenetic,
        metabolism=metabolism,
        actuator_manager=actuator_mgr,
        deep_consolidation=deep_consolidation,
        persistent_memory=persistent_mem,
        auto_save_interval=mem_config.get("auto_save_interval", 50),
        config=config,
    )

    # Inicializar
    loop.initialize()
    print(f"Identity: {vault.summary()}")
    print(f"Memory entries: {memory.count()}")
    print(f"Sub-agents: {len(all_subagents)}")
    print(f"Senses: {len(senses)}")
    print(f"Actuators: {actuator_mgr.list_actuators()}")
    print(f"Tick interval: {tick_interval}s")
    print()

    # Pensamientos recibidos
    thoughts = []

    async def on_thought(thought):
        thoughts.append(thought)
        ts = time.strftime("%H:%M:%S", time.localtime(thought.timestamp))
        system = thought.metadata.get("system", "system1")
        print(f"[{ts}] 💭 [{system}] {thought.content[:120]}")

    loop.on_thought_callback = on_thought

    # Ejecutar
    print(f"Starting cognitive loop (target: {thoughts_target} thoughts, max: {duration or 120}s)")
    print("-" * 70)

    start_time = time.time()
    actual_duration = duration or 120.0

    async def run_loop():
        await loop.run(duration_seconds=actual_duration)

    task = asyncio.create_task(run_loop())

    while len(thoughts) < thoughts_target:
        if time.time() - start_time > actual_duration:
            break
        await asyncio.sleep(1.0)

    loop.stop()
    try:
        await asyncio.wait_for(task, timeout=5.0)
    except asyncio.TimeoutError:
        task.cancel()

    # Graceful shutdown
    persistent_mem.save_to_disk()

    elapsed = time.time() - start_time
    stats = loop.get_stats()

    print("\n" + "=" * 70)
    print(f"USE CASE RESULTS: {use_case_name}")
    print("=" * 70)
    print(f"Duration: {elapsed:.1f}s")
    print(f"Iterations: {stats['iterations']}")
    print(f"Thoughts: {len(thoughts)}")
    print(f"System 1: {stats['system1_uses']}")
    print(f"System 2: {stats['system2_uses']}")
    print(f"Workspace competitions: {stats['workspace_competitions']}")
    print(f"Active Inference consultations: {stats['active_inference_consultations']}")
    print(f"Identity hash: {vault.identity_hash[:16]}...")
    print(f"Chain verified: {chain.verify_chain()}")
    print(f"Memory entries: {memory.count()}")
    print(f"Consolidation cycles: {stats.get('consolidation_cycles', 0)}")
    print(f"Auto-saves: {stats.get('auto_saves', 0)}")

    return {
        "use_case": use_case_name,
        "duration": elapsed,
        "iterations": stats["iterations"],
        "thoughts": len(thoughts),
        "system1": stats["system1_uses"],
        "system2": stats["system2_uses"],
        "workspace_competitions": stats["workspace_competitions"],
        "identity_hash": vault.identity_hash[:32],
        "chain_verified": chain.verify_chain(),
        "memory_entries": memory.count(),
    }


def main():
    parser = argparse.ArgumentParser(description="ZOE v1.0 — Use Case Runner")
    parser.add_argument("--use-case", required=True, help="Name of use case YAML (without .yaml)")
    parser.add_argument("--backend", help="Override LLM backend (mock, ollama, zai)")
    parser.add_argument("--duration", type=float, default=120.0, help="Max duration in seconds")
    parser.add_argument("--thoughts", type=int, default=10, help="Target number of thoughts")
    parser.add_argument("--list", action="store_true", help="List available use cases")
    args = parser.parse_args()

    if args.list:
        print("Available use cases:")
        for uc in list_available_use_cases():
            print(f"  - {uc}")
        return

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    result = asyncio.run(run_use_case(
        use_case_name=args.use_case,
        backend_override=args.backend,
        duration=args.duration,
        thoughts_target=args.thoughts,
    ))

    print(f"\nResult: {result}")
    sys.exit(0 if result["thoughts"] > 0 else 1)


if __name__ == "__main__":
    main()
