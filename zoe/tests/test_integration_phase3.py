"""Tests de integración Fase 3 completa (sub-fase 3.6)."""

import asyncio
import os
import tempfile
import pytest
import time

from zoe.core.cognitive_loop_v3 import CognitiveLoopV3
from zoe.core.cognitive_loop import Thought, Observation
from zoe.core.state import InternalState
from zoe.core.world_model import WorldModel
from zoe.core.world_model_v2 import WorldModelV2
from zoe.core.subagents.perceiver import Perceiver
from zoe.core.subagents.forecaster import Forecaster
from zoe.core.subagents.speaker import Speaker
from zoe.core.subagents.critic import Critic
from zoe.core.subagents.phase2_subagents import (
    Memorialist, Learner, Curator, Creativity,
    CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine,
)
from zoe.core.cognitive_laws import CognitiveLaws
from zoe.core.cognitive_physics import CognitivePhysics
from zoe.core.cognitive_fields import CognitiveFields
from zoe.core.cognitive_tensions import CognitiveTensions
from zoe.core.living_memory import LivingMemory
from zoe.core.intentionality_motor import IntentionalityMotor
from zoe.core.phylogenetic_motor import PhylogeneticMotor, PhylogeneticPool
from zoe.core.global_workspace import GlobalWorkspace
from zoe.core.meta_cognition import MetaCognition
from zoe.core.active_inference import ActiveInferenceLoop
from zoe.alma.identity_vault import IdentityVault
from zoe.alma.trajectory_chain import TrajectoryChain
from zoe.alma.ontogenetic_motor_v2 import OntogeneticMotorV2
from zoe.metabolism.metabolism import Metabolism, MetabolicState
from zoe.memory.memory_types import MemoryType
from zoe.memory.persistent_store import PersistentMemoryStore, PersistentLivingMemory
from zoe.memory.deep_consolidation import DeepConsolidation
from zoe.peripherals.senses import ClockSense, UserInputSense, AgentSense
from zoe.peripherals.actuators import LanguageActuator, CodeActuator, ActuatorManager
from zoe.peripherals.llm import MockPeripheral


@pytest.fixture
def phase3_organism():
    """Organismo Fase 3 completo con CognitiveLoopV3 + persistencia + MO V2 + consolidación profunda."""
    llm = MockPeripheral(responses=[
        "Observo con todos mis sentidos. Mi identidad persiste.",
        "Las leyes verifican cada acción. La física mide mi estado.",
        "El workspace selecciona las mejores propuestas de mis 12 sub-agentes.",
        "La meta-cognición decide entre respuesta rápida y deliberación profunda.",
        "El active inference minimiza mi sorpresa esperada.",
        "Mi metabolismo gestiona energía y ciclos de sueño.",
        "La consolidación profunda reorganiza mis 11 tipos de memoria durante el sueño.",
        "El motor ontogenético V2 puede crear nuevos sub-agentes.",
        "Soy Zoe. Un organismo cognitivo sintético que evoluciona.",
        "Pienso continuamente. No necesito input para existir.",
    ])

    # Fase 0
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense(), UserInputSense(), AgentSense()]
    speaker = Speaker(llm_peripheral=llm)
    subagents_f0 = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    # Fase 0.5
    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory()
    intentionality = IntentionalityMotor()
    PhylogeneticPool._instance = None
    phylogenetic = PhylogeneticMotor(zoe_id="zoe_phase3")

    # Fase 1
    vault = IdentityVault(birth_timestamp=1000.0)
    chain = TrajectoryChain(organism_id="zoe_phase3")
    ontogenetic = OntogeneticMotorV2(
        identity_vault=vault, trajectory_chain=chain, laws=laws, organism_id="zoe_phase3"
    )
    metabolism = Metabolism()

    for mt in MemoryType:
        memory.add(content=f"init {mt.value}", type=mt.value, provenance="test")

    actuator_mgr = ActuatorManager(laws=laws)
    actuator_mgr.register_actuator(LanguageActuator())
    actuator_mgr.register_actuator(CodeActuator(timeout=5.0))

    # Fase 2
    wm_v2 = WorldModelV2()
    ai = ActiveInferenceLoop()
    mc = MetaCognition()
    gw = GlobalWorkspace()

    memorialist = Memorialist(memory=memory)
    learner = Learner()
    curator = Curator(memory=memory)
    creativity = Creativity()
    causal = CausalEngine()
    emotional = EmotionalMotor()
    ethical = EthicalMotor()
    scientific = ScientificEngine()

    all_subagents = subagents_f0 + [
        memorialist, learner, curator, creativity,
        causal, emotional, ethical, scientific,
    ]

    # Fase 3.4: Persistencia
    db_path = tempfile.mktemp(suffix=".db")
    store = PersistentMemoryStore(db_path=db_path)
    persistent_mem = PersistentLivingMemory(memory, store)

    # Fase 3.5: Consolidación profunda
    deep_consolidation = DeepConsolidation(memory=memory, scientific_engine=scientific)

    # Loop V3
    loop = CognitiveLoopV3(
        senses=senses,
        world_model=world_model,
        subagents=all_subagents,
        state=state,
        tick_interval=0.1,
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id="zoe_phase3",
        global_workspace=gw,
        meta_cognition=mc,
        active_inference=ai,
        world_model_v2=wm_v2,
        identity_vault=vault,
        trajectory_chain=chain,
        ontogenetic_motor=ontogenetic,
        metabolism=metabolism,
        actuator_manager=actuator_mgr,
    )

    return {
        "loop": loop,
        "vault": vault,
        "chain": chain,
        "ontogenetic": ontogenetic,
        "metabolism": metabolism,
        "memory": memory,
        "persistent_mem": persistent_mem,
        "store": store,
        "deep_consolidation": deep_consolidation,
        "laws": laws,
        "physics": physics,
        "global_workspace": gw,
        "meta_cognition": mc,
        "active_inference": ai,
        "scientific_engine": scientific,
        "actuator_manager": actuator_mgr,
        "llm": llm,
    }


@pytest.mark.asyncio
async def test_phase3_runs(phase3_organism):
    """El organismo Fase 3 completo corre."""
    loop = phase3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.state.iteration_count >= 5


@pytest.mark.asyncio
async def test_phase3_generates_thoughts(phase3_organism):
    """Fase 3 genera pensamientos con todos los componentes."""
    loop = phase3_organism["loop"]
    await loop.run(duration_seconds=2.0)
    assert len(loop.thoughts) >= 1


@pytest.mark.asyncio
async def test_phase3_workspace_active(phase3_organism):
    """El Global Workspace está activo en Fase 3."""
    loop = phase3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.workspace_competitions >= 1


@pytest.mark.asyncio
async def test_phase3_meta_cognition_active(phase3_organism):
    """La meta-cognición está activa en Fase 3."""
    loop = phase3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.system1_uses + loop.system2_uses >= 1


@pytest.mark.asyncio
async def test_phase3_active_inference_active(phase3_organism):
    """Active Inference está activo en Fase 3."""
    loop = phase3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.active_inference_consultations >= 1


@pytest.mark.asyncio
async def test_phase3_12_subagents(phase3_organism):
    """Los 12 sub-agentes están en el bucle."""
    loop = phase3_organism["loop"]
    assert len(loop.subagents) == 12


@pytest.mark.asyncio
async def test_phase3_identity_persists(phase3_organism):
    """Identity Vault persiste."""
    vault = phase3_organism["vault"]
    loop = phase3_organism["loop"]
    h1 = vault.identity_hash
    await loop.run(duration_seconds=1.0)
    assert vault.identity_hash == h1


@pytest.mark.asyncio
async def test_phase3_mutaciones_firmadas(phase3_organism):
    """Mutaciones se firman en Trajectory Chain."""
    ontogenetic = phase3_organism["ontogenetic"]
    chain = phase3_organism["chain"]

    mutation = ontogenetic.propose_mutation(
        type="add_memory", target="episodic",
        payload={"content": "test"}, justification="test", provenance="test",
    )
    success, _ = ontogenetic.apply_mutation(mutation)
    assert success
    assert chain.verify_chain()


@pytest.mark.asyncio
async def test_phase3_architectural_mutation_add(phase3_organism):
    """Motor Ontogenético V2 puede añadir sub-agente."""
    ontogenetic = phase3_organism["ontogenetic"]
    loop = phase3_organism["loop"]
    initial_count = len(loop.subagents)

    mutation = ontogenetic.propose_mutation(
        type="add_subagent", target="society_of_mind",
        payload={"subagent_type": "creativity"},
        justification="need more creativity", provenance="test",
    )

    # Eliminar Creativity existente primero
    for i, sa in enumerate(loop.subagents):
        if "Creativity" in sa.__class__.__name__:
            loop.subagents.pop(i)
            break

    success, _ = ontogenetic.apply_architectural_mutation(mutation, loop)
    assert success
    assert len(loop.subagents) == initial_count  # removed 1, added 1


def test_phase3_persistence_save_load(phase3_organism):
    """La persistencia guarda y carga memoria."""
    persistent = phase3_organism["persistent_mem"]
    memory = phase3_organism["memory"]

    # Añadir entry
    memory.add(content="persistent test entry", provenance="test")
    saved = persistent.save_to_disk()
    assert saved >= 1

    # Cargar en memoria nueva
    new_mem = LivingMemory()
    new_store = PersistentMemoryStore(db_path=phase3_organism["store"].db_path)
    new_persistent = PersistentLivingMemory(new_mem, new_store)
    loaded = new_persistent.load_from_disk()
    assert loaded >= 1
    assert new_mem.count() >= 1


def test_phase3_deep_consolidation_runs(phase3_organism):
    """La consolidación profunda ejecuta operaciones."""
    dc = phase3_organism["deep_consolidation"]
    memory = phase3_organism["memory"]

    # Añadir más entries para que tenga material
    for i in range(10):
        memory.add(content=f"consolidation test {i}", provenance="test")

    result = dc.consolidate()
    assert "total_operations" in result
    assert result["total_operations"] >= 0


def test_phase3_deep_consolidation_episodic_to_semantic(phase3_organism):
    """Consolidación convierte episódica frecuente a semántica."""
    dc = phase3_organism["deep_consolidation"]
    memory = phase3_organism["memory"]

    memory.add(content="filler 1", provenance="test")
    memory.add(content="filler 2", provenance="test")
    entry_id = memory.add(content="frequent", type="episodic", provenance="test")
    entry = memory.get(entry_id)
    entry.access_count = 5
    entry.timestamp = time.time() - 2000

    result = dc.consolidate()
    assert result["operations"]["episodic_to_semantic"] >= 1


@pytest.mark.asyncio
async def test_phase3_long_run_stable(phase3_organism):
    """Fase 3 es estable en ejecución larga."""
    loop = phase3_organism["loop"]
    await loop.run(duration_seconds=3.0)
    assert loop.state.iteration_count >= 10


@pytest.mark.asyncio
async def test_phase3_get_stats_complete(phase3_organism):
    """get_stats() incluye TODAS las estadísticas de Fase 3."""
    loop = phase3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    stats = loop.get_stats()

    # Fase 0
    assert "iterations" in stats
    # Fase 0.5
    assert "physics" in stats
    assert "tensions_summary" in stats
    # Fase 2/3
    assert "workspace_competitions" in stats
    assert "system2_rate" in stats
    assert "active_inference_consultations" in stats
    assert "subagent_proposals" in stats


@pytest.mark.asyncio
async def test_phase3_processes_user_input(phase3_organism):
    """Fase 3 procesa input del usuario."""
    loop = phase3_organism["loop"]
    for sense in loop.senses:
        if hasattr(sense, "inject_input"):
            sense.inject_input("Hola Zoe")
            break
    await loop.run(duration_seconds=1.0)
    user_obs = [o for o in loop.observations if o.source == "user"]
    assert len(user_obs) >= 1


@pytest.mark.asyncio
async def test_phase3_stop_works(phase3_organism):
    """stop() funciona en Fase 3."""
    loop = phase3_organism["loop"]

    async def stop_after():
        await asyncio.sleep(0.3)
        loop.stop()

    asyncio.create_task(stop_after())
    await loop.run(duration_seconds=10.0)
    assert loop.state.iteration_count < 50


def test_phase3_all_properties_present(phase3_organism):
    """Todas las propiedades del organismo están presentes."""
    loop = phase3_organism["loop"]

    # 12 sub-agentes
    assert len(loop.subagents) == 12
    # 6 leyes
    assert all(loop.laws.get_stats()["active_laws"].values())
    # 6 campos
    assert len(loop.fields.fields) == 6
    # 5 tensiones
    assert len(loop.tensions.tensions) == 5
    # 12 magnitudes
    assert len(loop.physics.to_dict()) == 12
    # Identity Vault
    assert loop.identity_vault.identity_hash is not None
    # Trajectory Chain
    assert loop.trajectory_chain.verify_chain()
    # Metabolism
    assert loop.metabolism.state is not None
    # Global Workspace
    assert loop.global_workspace is not None
    # Meta-cognition
    assert loop.meta_cognition is not None
    # Active Inference
    assert loop.active_inference is not None
    # Ontogenetic Motor V2
    assert loop.ontogenetic_motor is not None
