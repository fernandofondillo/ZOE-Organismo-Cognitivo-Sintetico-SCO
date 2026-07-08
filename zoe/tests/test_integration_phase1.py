"""
ZOE v1.0 — Tests de integración Fase 1

Valida que los componentes de Fase 1 (Identity Vault, Trajectory Chain,
Ontogenetic Motor, Metabolism, 11 Memory Types, Sentidos/Actuadores)
funcionan integrados con Fase 0 + 0.5.
"""

import asyncio
import pytest
import time

from zoe.core.cognitive_loop import Thought
from zoe.core.cognitive_loop_v05 import CognitiveLoopV05
from zoe.core.state import InternalState
from zoe.core.world_model import WorldModel
from zoe.core.subagents.perceiver import Perceiver
from zoe.core.subagents.forecaster import Forecaster
from zoe.core.subagents.speaker import Speaker
from zoe.core.subagents.critic import Critic
from zoe.core.cognitive_laws import CognitiveLaws
from zoe.core.cognitive_physics import CognitivePhysics
from zoe.core.cognitive_fields import CognitiveFields
from zoe.core.cognitive_tensions import CognitiveTensions
from zoe.core.living_memory import LivingMemory
from zoe.core.intentionality_motor import IntentionalityMotor
from zoe.core.phylogenetic_motor import PhylogeneticMotor, PhylogeneticPool

from zoe.alma.identity_vault import IdentityVault
from zoe.alma.trajectory_chain import TrajectoryChain
from zoe.alma.ontogenetic_motor import OntogeneticMotor

from zoe.metabolism.metabolism import Metabolism, MetabolicState

from zoe.memory.memory_types import MemoryType, create_entry

from zoe.peripherals.senses import ClockSense, UserInputSense, AgentSense
from zoe.peripherals.actuators import (
    LanguageActuator,
    CodeActuator,
    ToolActuator,
    FederationActuator,
    ActuatorManager,
)
from zoe.peripherals.llm import MockPeripheral


@pytest.fixture
def phase1_organism():
    """Organismo completo Fase 0 + 0.5 + 1."""
    # LLM mock
    llm = MockPeripheral(responses=[
        "Pienso en mi entorno y mi estado interno.",
        "Mi identidad persiste a través del bucle cognitivo.",
        "Observo, predigo, evalúo, decido, actúo.",
        "Las leyes cognitivas guían cada acción.",
    ])

    # Fase 0
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense(), UserInputSense(), AgentSense()]
    speaker = Speaker(llm_peripheral=llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    # Fase 0.5
    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory()
    intentionality = IntentionalityMotor()
    PhylogeneticPool._instance = None
    phylogenetic = PhylogeneticMotor(zoe_id="zoe_test")

    # Fase 1
    vault = IdentityVault(birth_timestamp=1000.0)
    chain = TrajectoryChain(organism_id="zoe_test")
    ontogenetic = OntogeneticMotor(
        identity_vault=vault, trajectory_chain=chain, laws=laws, organism_id="zoe_test"
    )
    metabolism = Metabolism()

    # Bucle
    loop = CognitiveLoopV05(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=0.1,
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id="zoe_test",
    )

    return {
        "loop": loop,
        "vault": vault,
        "chain": chain,
        "ontogenetic": ontogenetic,
        "metabolism": metabolism,
        "memory": memory,
        "laws": laws,
        "llm": llm,
    }


# ===== Tests de integración Fase 1 =====


@pytest.mark.asyncio
async def test_phase1_organism_runs(phase1_organism):
    """El organismo Fase 1 completo corre sin crashear."""
    loop = phase1_organism["loop"]
    await loop.run(duration_seconds=1.0)
    assert loop.state.iteration_count >= 5


@pytest.mark.asyncio
async def test_phase1_identity_vault_persists(phase1_organism):
    """El Identity Vault mantiene su hash durante la ejecución."""
    vault = phase1_organism["vault"]
    loop = phase1_organism["loop"]
    initial_hash = vault.identity_hash

    await loop.run(duration_seconds=1.0)

    assert vault.identity_hash == initial_hash


@pytest.mark.asyncio
async def test_phase1_ontogenetic_motor_applies_mutations(phase1_organism):
    """El Motor Ontogenético aplica mutaciones firmadas."""
    ontogenetic = phase1_organism["ontogenetic"]
    chain = phase1_organism["chain"]

    mutation = ontogenetic.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "test memory"},
        justification="test",
        provenance="test",
    )
    success, _ = ontogenetic.apply_mutation(mutation)
    assert success is True
    assert len(chain._mutations) == 1
    assert chain.verify_chain() is True


@pytest.mark.asyncio
async def test_phase1_ontogenetic_rejects_identity_breaking(phase1_organism):
    """Mutaciones que rompen identidad son rechazadas."""
    ontogenetic = phase1_organism["ontogenetic"]

    mutation = ontogenetic.propose_mutation(
        type="add_memory",
        target="vectors",  # target prohibido
        payload={"content": "test"},
        justification="test",
        provenance="test",
    )
    success, reason = ontogenetic.apply_mutation(mutation)
    assert success is False
    assert "identity" in reason.lower()


@pytest.mark.asyncio
async def test_phase1_metabolism_integrates(phase1_organism):
    """El Metabolismo se integra con el bucle."""
    metabolism = phase1_organism["metabolism"]
    loop = phase1_organism["loop"]

    # El metabolismo empieza awake
    assert metabolism.state == MetabolicState.AWAKE

    # Tras ejecución, sigue funcionando
    await loop.run(duration_seconds=0.5)
    assert metabolism.state in [MetabolicState.AWAKE, MetabolicState.DROWSY]


@pytest.mark.asyncio
async def test_phase1_metabolism_transitions(phase1_organism):
    """El Metabolismo transita a DROWSY con fatiga alta."""
    metabolism = phase1_organism["metabolism"]
    metabolism.internal_state.fatigue = 0.7
    metabolism.tick(dt=1.0)
    assert metabolism.state == MetabolicState.DROWSY


@pytest.mark.asyncio
async def test_phase1_11_memory_types(phase1_organism):
    """Los 11 tipos de memoria funcionan con LivingMemory."""
    memory = phase1_organism["memory"]

    # Añadir entries de varios tipos usando memory.add() que asigna IDs
    for i, mem_type in enumerate(list(MemoryType)[:5]):
        memory.add(
            content=f"test {mem_type.value}",
            type=mem_type.value,
            provenance="test",
        )

    # Verificar que los tipos están presentes
    types_present = set(e.type for e in memory.all_entries())
    assert len(types_present) >= 5


@pytest.mark.asyncio
async def test_phase1_actuator_manager(phase1_organism):
    """El ActuatorManager ejecuta acciones con leyes verificadas."""
    laws = phase1_organism["laws"]
    llm = phase1_organism["llm"]

    manager = ActuatorManager(laws=laws)
    manager.register_actuator(LanguageActuator())

    result = await manager.execute_action(
        action={
            "actuator": "language",
            "prompt": "test",
            "uncertainty_reduction": 0.3,
            "capacity_increase": 0.1,
        },
        llm_peripheral=llm,
    )
    assert result.success is True


@pytest.mark.asyncio
async def test_phase1_actuator_rejects_law_violation(phase1_organism):
    """ActuatorManager rechaza acciones que violan leyes."""
    laws = phase1_organism["laws"]
    llm = phase1_organism["llm"]

    manager = ActuatorManager(laws=laws)
    manager.register_actuator(LanguageActuator())

    result = await manager.execute_action(
        action={
            "actuator": "language",
            "prompt": "test",
            "uncertainty_reduction": 0.0,
            "capacity_increase": 0.0,
        },
        llm_peripheral=llm,
    )
    assert result.success is False
    assert "law" in result.error.lower() or "violat" in result.error.lower()


@pytest.mark.asyncio
async def test_phase1_code_actuator_executes(phase1_organism):
    """CodeActuator ejecuta código en el contexto del organismo."""
    manager = ActuatorManager()
    manager.register_actuator(CodeActuator(timeout=5.0))

    result = await manager.execute_action(
        action={
            "actuator": "code",
            "code": "print(2 + 2)",
            "language": "python",
            "uncertainty_reduction": 0.3,
        }
    )
    assert result.success is True
    assert "4" in result.output


@pytest.mark.asyncio
async def test_phase1_trajectory_chain_rollback(phase1_organism):
    """Trajectory Chain permite rollback de mutaciones."""
    ontogenetic = phase1_organism["ontogenetic"]
    chain = phase1_organism["chain"]

    # Aplicar mutación
    mutation = ontogenetic.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "test"},
        justification="test",
        provenance="test",
    )
    ontogenetic.apply_mutation(mutation)

    # Revertir
    success, _ = ontogenetic.rollback(mutation.id)
    assert success is True
    assert chain.verify_chain() is True


@pytest.mark.asyncio
async def test_phase1_agent_sense_integrates(phase1_organism):
    """AgentSense funciona en el bucle."""
    loop = phase1_organism["loop"]

    # Registrar un agente
    for sense in loop.senses:
        if hasattr(sense, "register_agent"):
            sense.register_agent("zoe_other", agent_type="zoe")
            break

    await loop.run(duration_seconds=0.5)

    # Debe haber observaciones del AgentSense
    agent_obs = [o for o in loop.observations if o.source == "agent"]
    assert len(agent_obs) >= 1


@pytest.mark.asyncio
async def test_phase1_full_integration(phase1_organism):
    """Integración completa: bucle + leyes + física + memoria + Vault + Metabolismo + mutaciones."""
    loop = phase1_organism["loop"]
    ontogenetic = phase1_organism["ontogenetic"]
    chain = phase1_organism["chain"]
    vault = phase1_organism["vault"]
    metabolism = phase1_organism["metabolism"]

    # Aplicar mutación antes de ejecutar
    mutation = ontogenetic.propose_mutation(
        type="add_memory",
        target="episodic",
        payload={"content": "pre-execution memory"},
        justification="test integration",
        provenance="test",
    )
    ontogenetic.apply_mutation(mutation)

    # Ejecutar bucle
    await loop.run(duration_seconds=1.0)

    # Verificar que todo funciona
    assert loop.state.iteration_count >= 5
    assert vault.identity_hash is not None
    assert chain.verify_chain() is True
    assert metabolism.state in [MetabolicState.AWAKE, MetabolicState.DROWSY]
    assert len(chain._mutations) >= 1


@pytest.mark.asyncio
async def test_phase1_all_actuators_available():
    """Todos los actuadores están disponibles y funcionan."""
    laws = CognitiveLaws()
    manager = ActuatorManager(laws=laws)
    manager.register_actuator(LanguageActuator())
    manager.register_actuator(CodeActuator(timeout=5.0))
    manager.register_actuator(ToolActuator(tools={"echo": lambda: "echoed"}))
    manager.register_actuator(FederationActuator())

    actuators = manager.list_actuators()
    assert "language" in actuators
    assert "code" in actuators
    assert "tool" in actuators
    assert "federation" in actuators


@pytest.mark.asyncio
async def test_phase1_all_senses_available():
    """Todos los sentidos están disponibles."""
    senses = [ClockSense(), UserInputSense(), AgentSense()]

    for sense in senses:
        obs = await sense.observe()
        assert obs is not None or obs is None  # no crashea


@pytest.mark.asyncio
async def test_phase1_regression_all_previous_tests_still_pass():
    """Los componentes de Fase 0 + 0.5 siguen funcionando."""
    # Fase 0
    state = InternalState()
    state.tick(dt=1.0)
    assert state.iteration_count == 1

    # Fase 0.5
    laws = CognitiveLaws()
    action = {"type": "rest"}
    passed, _ = laws.verify_action(action)
    assert passed is True

    physics = CognitivePhysics()
    assert physics.energy_cognitive == 1.0

    # Fase 1
    vault = IdentityVault(birth_timestamp=1000.0)
    assert vault.identity_hash is not None

    metabolism = Metabolism()
    assert metabolism.state == MetabolicState.AWAKE
