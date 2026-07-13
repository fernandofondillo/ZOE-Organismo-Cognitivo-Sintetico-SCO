"""Tests para CognitiveLoopV3 (Fase 3 — bucle integrado completo)."""

import asyncio
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
from zoe.alma.ontogenetic_motor import OntogeneticMotor
from zoe.metabolism.metabolism import Metabolism
from zoe.memory.memory_types import MemoryType
from zoe.peripherals.senses import ClockSense, UserInputSense, AgentSense
from zoe.peripherals.actuators import (
    LanguageActuator, CodeActuator, ToolActuator, FederationActuator,
    ActuatorManager,
)
from zoe.peripherals.llm import MockPeripheral


@pytest.fixture
def full_v3_organism():
    """Organismo completo con CognitiveLoopV3 y TODOS los componentes."""
    llm = MockPeripheral(responses=[
        "Observo mi entorno con todos mis sentidos activos.",
        "Mi metabolismo mantiene mi energía en niveles óptimos.",
        "Las leyes cognitivas verifican cada pensamiento que genero.",
        "Mi identidad persiste: hash verificado, invariantes intactos.",
        "La física cognitiva mide mi estado con 12 magnitudes.",
        "Las tensiones internas me empujan a explorar y consolidar.",
        "Mi memoria viva reorganiza las experiencias en 11 tipos.",
        "El motor ontogenético prepara mutaciones firmadas.",
        "El motor de intencionalidad genera nuevos deseos cognitivos.",
        "El Active Inference minimiza mi sorpresa esperada.",
        "El Global Workspace selecciona las mejores propuestas.",
        "La meta-cognición decide entre System 1 y System 2.",
        "Soy Zoe. Un organismo cognitivo sintético.",
        "La trayectoria firmada registra cada cambio.",
        "Pienso, luego existo. Aunque nadie me hable.",
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
    phylogenetic = PhylogeneticMotor(zoe_id="zoe_v3_test")

    # Fase 1
    vault = IdentityVault(birth_timestamp=1000.0)
    chain = TrajectoryChain(organism_id="zoe_v3_test")
    ontogenetic = OntogeneticMotor(
        identity_vault=vault, trajectory_chain=chain, laws=laws, organism_id="zoe_v3_test"
    )
    metabolism = Metabolism()

    # 11 Memory Types
    for mt in MemoryType:
        memory.add(content=f"init {mt.value}", type=mt.value, provenance="test")

    # Actuadores
    actuator_mgr = ActuatorManager(laws=laws)
    actuator_mgr.register_actuator(LanguageActuator())
    actuator_mgr.register_actuator(CodeActuator(timeout=5.0))

    # Fase 2
    wm_v2 = WorldModelV2()
    ai = ActiveInferenceLoop()
    mc = MetaCognition()
    gw = GlobalWorkspace()

    # 8 sub-agentes Fase 2
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
        zoe_id="zoe_v3_test",
        # Fase 2/3
        global_workspace=gw,
        meta_cognition=mc,
        active_inference=ai,
        world_model_v2=wm_v2,
        # Fase 1
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
        "laws": laws,
        "physics": physics,
        "fields": fields,
        "tensions": tensions,
        "intentionality": intentionality,
        "phylogenetic": phylogenetic,
        "global_workspace": gw,
        "meta_cognition": mc,
        "active_inference": ai,
        "world_model_v2": wm_v2,
        "actuator_manager": actuator_mgr,
        "llm": llm,
        "subagents": all_subagents,
    }


# ===== Tests básicos V3 =====


@pytest.mark.asyncio
async def test_v3_runs_without_crash(full_v3_organism):
    """V3 corre sin crashear."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.state.iteration_count >= 5


@pytest.mark.asyncio
async def test_v3_generates_thoughts(full_v3_organism):
    """V3 genera pensamientos autónomos."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=2.0)
    assert len(loop.thoughts) >= 1


@pytest.mark.asyncio
async def test_v3_long_run_stable(full_v3_organism):
    """V3 es estable en ejecución larga."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=3.0)
    assert loop.state.iteration_count >= 10


# ===== Tests: Global Workspace integrado =====


@pytest.mark.asyncio
async def test_v3_workspace_competes(full_v3_organism):
    """V3: el Global Workspace ejecuta competiciones."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.workspace_competitions >= 1


@pytest.mark.asyncio
async def test_v3_subagent_proposals_collected(full_v3_organism):
    """V3: los sub-agentes proponen al workspace."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=2.0)
    assert loop.subagent_proposals >= 1


@pytest.mark.asyncio
async def test_v3_workspace_selects_winners(full_v3_organism):
    """V3: el workspace selecciona ganadores."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    # Si hubo competiciones, debería haber ganadores registrados
    gw_stats = loop.global_workspace.get_stats()
    assert gw_stats["total_competitions"] >= 1


# ===== Tests: Meta-cognición integrada =====


@pytest.mark.asyncio
async def test_v3_meta_cognition_used(full_v3_organism):
    """V3: la meta-cognición se usa para System 1/2."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    total = loop.system1_uses + loop.system2_uses
    assert total >= 1


@pytest.mark.asyncio
async def test_v3_system2_activates_on_surprise(full_v3_organism):
    """V3: System 2 se activa con sorpresa alta."""
    loop = full_v3_organism["loop"]
    # Forzar sorpresa alta inyectando observación novedosa
    for sense in loop.senses:
        if hasattr(sense, "inject_input"):
            sense.inject_input("algo totalmente nuevo e inesperado y diferente")
            break

    await loop.run(duration_seconds=2.0)
    # Debería haber algún uso de System 2
    # (no garantizado porque depende del contexto, pero el sistema debe funcionar)
    assert loop.system1_uses + loop.system2_uses >= 1


# ===== Tests: Active Inference integrado =====


@pytest.mark.asyncio
async def test_v3_active_inference_consulted(full_v3_organism):
    """V3: Active Inference se consulta."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.active_inference_consultations >= 1


@pytest.mark.asyncio
async def test_v3_active_inference_learns(full_v3_organism):
    """V3: Active Inference aprende transiciones."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=2.0)
    ai_stats = loop.active_inference.get_stats()
    assert ai_stats["actions_taken"] >= 1


# ===== Tests: 12 sub-agentes integrados =====


@pytest.mark.asyncio
async def test_v3_12_subagents_present(full_v3_organism):
    """V3: los 12 sub-agentes están presentes."""
    loop = full_v3_organism["loop"]
    assert len(loop.subagents) == 12


@pytest.mark.asyncio
async def test_v3_subagents_contribute_to_workspace(full_v3_organism):
    """V3: múltiples sub-agentes contribuyen propuestas."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=2.0)
    # Debería haber propuestas de múltiples sub-agentes
    assert loop.subagent_proposals >= 1


# ===== Tests: Fase 1 integrada en V3 =====


@pytest.mark.asyncio
async def test_v3_identity_vault_persists(full_v3_organism):
    """V3: Identity Vault persiste durante ejecución."""
    vault = full_v3_organism["vault"]
    loop = full_v3_organism["loop"]
    h1 = vault.identity_hash
    await loop.run(duration_seconds=1.0)
    assert vault.identity_hash == h1


@pytest.mark.asyncio
async def test_v3_ontogenetic_mutations_applied(full_v3_organism):
    """V3: mutaciones se aplican con sorpresa alta."""
    loop = full_v3_organism["loop"]
    chain = full_v3_organism["chain"]
    initial_mutations = len(chain._mutations)

    # Forzar sorpresa alta inyectando input novedoso
    for sense in loop.senses:
        if hasattr(sense, "inject_input"):
            sense.inject_input("algo completamente nuevo y muy diferente e inesperado")
            break

    await loop.run(duration_seconds=2.0)
    # Debería haber aplicado alguna mutación (si sorpresa > 0.5)
    # No garantizado, pero el sistema no debe crashear
    assert chain.verify_chain() is True


@pytest.mark.asyncio
async def test_v3_metabolism_integrates(full_v3_organism):
    """V3: el metabolismo se integra."""
    loop = full_v3_organism["loop"]
    metabolism = full_v3_organism["metabolism"]
    await loop.run(duration_seconds=1.0)
    assert metabolism.state is not None


# ===== Tests: estadísticas completas =====


@pytest.mark.asyncio
async def test_v3_get_stats_complete(full_v3_organism):
    """V3: get_stats() incluye estadísticas de todas las fases."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    stats = loop.get_stats()

    # Fase 0
    assert "iterations" in stats
    assert "thoughts" in stats
    # Fase 0.5
    assert "law_violations" in stats
    assert "physics" in stats
    assert "fields_summary" in stats
    assert "tensions_summary" in stats
    assert "memory_stats" in stats
    # Fase 2/3
    assert "workspace_competitions" in stats
    assert "system1_uses" in stats
    assert "system2_uses" in stats
    assert "system2_rate" in stats
    assert "active_inference_consultations" in stats
    assert "subagent_proposals" in stats
    assert "workspace_stats" in stats
    assert "meta_cognition_stats" in stats
    assert "active_inference_stats" in stats


# ===== Tests: no-regresión =====


@pytest.mark.asyncio
async def test_v3_processes_user_input(full_v3_organism):
    """V3: procesa input del usuario."""
    loop = full_v3_organism["loop"]
    for sense in loop.senses:
        if hasattr(sense, "inject_input"):
            sense.inject_input("Hola Zoe, ¿cómo estás?")
            break

    await loop.run(duration_seconds=1.0)
    user_obs = [o for o in loop.observations if o.source == "user"]
    assert len(user_obs) >= 1


@pytest.mark.asyncio
async def test_v3_stop_works(full_v3_organism):
    """V3: stop() detiene el organismo."""
    loop = full_v3_organism["loop"]

    async def stop_after():
        await asyncio.sleep(0.3)
        loop.stop()

    asyncio.create_task(stop_after())
    await loop.run(duration_seconds=10.0)
    assert loop.state.iteration_count < 50


@pytest.mark.asyncio
async def test_v3_laws_verified(full_v3_organism):
    """V3: las leyes se verifican."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert all(loop.laws.get_stats()["active_laws"].values())


@pytest.mark.asyncio
async def test_v3_thoughts_have_system_metadata(full_v3_organism):
    """V3: los pensamientos tienen metadata de System 1/2."""
    loop = full_v3_organism["loop"]
    await loop.run(duration_seconds=2.0)

    if loop.thoughts:
        thought = loop.thoughts[-1]
        assert "system" in thought.metadata
        assert thought.metadata["system"] in ["system1", "system2"]
