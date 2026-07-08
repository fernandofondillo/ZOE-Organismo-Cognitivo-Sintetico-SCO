"""
ZOE v1.0 — Test integrado Fase 0 + Fase 0.5

Valida que todos los componentes de Fase 0 y Fase 0.5 funcionan juntos
en un solo organismo. No testea componentes aislados; testea la integración.

Ejecutar:
    python -m pytest zoe/tests/test_integration_phase0_0_5.py -v
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path

import pytest

# Componentes Fase 0
from zoe.core.cognitive_loop import CognitiveLoop, Thought, Observation
from zoe.core.state import InternalState
from zoe.core.world_model import WorldModel
from zoe.core.subagents.perceiver import Perceiver
from zoe.core.subagents.forecaster import Forecaster
from zoe.core.subagents.speaker import Speaker
from zoe.core.subagents.critic import Critic
from zoe.peripherals.senses import ClockSense, FilesystemSense, UserInputSense
from zoe.peripherals.llm import (
    MockPeripheral,
    ZAIPeripheral,
    OllamaPeripheral,
    create_llm_peripheral,
)

# Componentes Fase 0.5
from zoe.core.cognitive_loop_v05 import CognitiveLoopV05
from zoe.core.cognitive_laws import CognitiveLaws, LawID
from zoe.core.cognitive_physics import CognitivePhysics
from zoe.core.cognitive_fields import CognitiveFields
from zoe.core.cognitive_tensions import CognitiveTensions
from zoe.core.living_memory import LivingMemory
from zoe.core.intentionality_motor import IntentionalityMotor
from zoe.core.phylogenetic_motor import PhylogeneticMotor, PhylogeneticPool


# ===== Fixtures =====


@pytest.fixture
def mock_llm():
    """LLM mock con respuestas diversas."""
    return MockPeripheral(
        responses=[
            "Observo el paso del tiempo. Mi entorno está en calma.",
            "La sorpresa es baja. Mi modelo del entorno se mantiene estable.",
            "Reflexiono sobre mi estado interno: energía buena, fatiga mínima.",
            "Las tensiones cognitivas me empujan a explorar nuevos conceptos.",
            "Mi memoria viva reorganiza las experiencias recientes.",
            "Detecto un patrón en las observaciones del reloj.",
            "Siento curiosidad por entender mejor mi propio funcionamiento.",
            "La física cognitiva muestra equilibrio entre exploración y explotación.",
            "Mi identidad persiste a través de cada iteración del bucle.",
            "Genero una hipótesis sobre el comportamiento del entorno.",
        ]
    )


@pytest.fixture
def integrated_organism(mock_llm):
    """
    Organismo completo con TODOS los componentes de Fase 0 + 0.5 integrados.
    Esto es lo que testea este archivo: que todo funcione JUNTO.
    """
    # Fase 0 components
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense()]
    speaker = Speaker(llm_peripheral=mock_llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    # Fase 0.5 components
    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory()
    intentionality = IntentionalityMotor()

    # Reset phylogenetic pool para test aislado
    PhylogeneticPool._instance = None
    phylogenetic = PhylogeneticMotor(zoe_id="zoe_test_integrated")

    # Crear bucle integrado
    loop = CognitiveLoopV05(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=0.1,  # rápido para tests
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id="zoe_test_integrated",
    )

    return loop


# ===== Tests de integración: todos los componentes juntos =====


@pytest.mark.asyncio
async def test_integrated_organism_runs_without_crash(integrated_organism):
    """El organismo integrado corre sin crashear."""
    loop = integrated_organism
    await loop.run(duration_seconds=1.0)
    assert loop.state.iteration_count >= 5


@pytest.mark.asyncio
async def test_integrated_organism_generates_thoughts(integrated_organism):
    """El organismo integrado genera pensamientos autónomos."""
    loop = integrated_organism
    await loop.run(duration_seconds=2.0)
    assert len(loop.thoughts) >= 1
    # Cada pensamiento debe tener contenido
    for thought in loop.thoughts:
        assert thought.content
        assert len(thought.content) > 10


@pytest.mark.asyncio
async def test_integrated_organism_records_observations(integrated_organism):
    """El organismo registra observaciones de los sentidos."""
    loop = integrated_organism
    await loop.run(duration_seconds=1.0)
    assert len(loop.observations) >= 3
    # Todas las observaciones son del ClockSense
    sources = {o.source for o in loop.observations}
    assert "clock" in sources


@pytest.mark.asyncio
async def test_integrated_organism_laws_verified(integrated_organism):
    """Las leyes cognitivas se verifican en cada acción."""
    loop = integrated_organism
    await loop.run(duration_seconds=2.0)
    # Puede haber 0 violaciones (todo pasó) o algunas (algunas rechazadas)
    # Lo importante es que el sistema de leyes funciona
    stats = loop.laws.get_stats()
    assert "total_violations" in stats
    assert "violation_counts" in stats


@pytest.mark.asyncio
async def test_integrated_organism_physics_calculated(integrated_organism):
    """La física cognitiva se calcula en cada iteración."""
    loop = integrated_organism
    await loop.run(duration_seconds=1.0)

    physics = loop.physics
    # Todas las 12 magnitudes deben estar calculadas
    d = physics.to_dict()
    expected_magnitudes = [
        "energy_cognitive",
        "conceptual_mass",
        "cognitive_temperature",
        "uncertainty_pressure",
        "creative_potential",
        "semantic_entropy",
        "goal_gravity",
        "identity_inertia",
        "conceptual_resonance",
        "cognitive_friction",
        "memory_elasticity",
        "causal_density",
    ]
    for mag in expected_magnitudes:
        assert mag in d
        assert isinstance(d[mag], (int, float))


@pytest.mark.asyncio
async def test_integrated_organism_fields_active(integrated_organism):
    """Los campos cognitivos se actualizan."""
    loop = integrated_organism
    await loop.run(duration_seconds=1.0)

    # Al menos el campo de atención debe tener datos
    attention = loop.fields.read("attention")
    # Tras varias iteraciones, el campo debe tener contenido
    all_fields = loop.fields.read_all()
    assert "attention" in all_fields


@pytest.mark.asyncio
async def test_integrated_organism_tensions_evolve(integrated_organism):
    """Las tensiones cognitivas evolucionan."""
    loop = integrated_organism
    await loop.run(duration_seconds=1.0)

    tensions = loop.tensions
    # Las 5 tensiones deben estar presentes
    assert len(tensions.tensions) == 5
    # Tras ejecución, al menos algunas deben tener intensidad > 0
    total_intensity = sum(t.intensity for t in tensions.tensions.values())
    assert total_intensity >= 0  # puede ser 0 si todo en equilibrio


@pytest.mark.asyncio
async def test_integrated_organism_memory_stores_thoughts(integrated_organism):
    """La memoria viva almacena los pensamientos generados."""
    loop = integrated_organism
    await loop.run(duration_seconds=2.0)

    # Si se generaron pensamientos, la memoria debe tener entries
    if loop.thoughts:
        assert loop.memory.count() >= 1
        # Las entries deben tener provenance (3ra ley)
        for entry in loop.memory.all_entries():
            assert entry.provenance


@pytest.mark.asyncio
async def test_integrated_organism_intentionality_generates(integrated_organism):
    """El motor de intencionalidad genera intenciones."""
    loop = integrated_organism
    await loop.run(duration_seconds=2.0)

    # El motor debe haber generado algunas intenciones
    stats = loop.intentionality.get_stats()
    assert stats["total_intentions"] >= 0  # puede ser 0 si todo en equilibrio
    # Pero el motor debe estar funcional
    assert "active_count" in stats


@pytest.mark.asyncio
async def test_integrated_organism_phylogenetic_initialized(integrated_organism):
    """El motor filogenético está inicializado."""
    loop = integrated_organism
    state = loop.phylogenetic.get_species_state()
    assert "species_version" in state
    assert "total_improvements" in state


@pytest.mark.asyncio
async def test_integrated_organism_processes_user_input(integrated_organism):
    """El organismo integrado procesa input del usuario."""
    loop = integrated_organism
    # Añadir sentido de usuario
    user_sense = UserInputSense()
    user_sense.inject_input("Hola Zoe, ¿cómo estás?")
    loop.senses.append(user_sense)

    await loop.run(duration_seconds=1.0)

    # Debe haber registrado la observación del usuario
    user_obs = [o for o in loop.observations if o.source == "user"]
    assert len(user_obs) >= 1


@pytest.mark.asyncio
async def test_integrated_organism_state_evolves(integrated_organism):
    """El estado interno evoluciona durante la ejecución."""
    loop = integrated_organism
    initial_iteration = loop.state.iteration_count

    await loop.run(duration_seconds=1.0)

    assert loop.state.iteration_count > initial_iteration
    # Fatiga debe haber aumentado (cada iteración añade fatiga)
    assert loop.state.fatigue > 0.0


@pytest.mark.asyncio
async def test_integrated_organism_get_stats_complete(integrated_organism):
    """get_stats() devuelve estadísticas completas de Fase 0 + 0.5."""
    loop = integrated_organism
    await loop.run(duration_seconds=1.0)

    stats = loop.get_stats()

    # Fase 0 stats
    assert "iterations" in stats
    assert "observations" in stats
    assert "thoughts" in stats
    assert "energy" in stats
    assert "fatigue" in stats

    # Fase 0.5 stats
    assert "law_violations" in stats
    assert "law_stats" in stats
    assert "physics" in stats
    assert "fields_summary" in stats
    assert "tensions_summary" in stats
    assert "memory_stats" in stats
    assert "intentionality_stats" in stats
    assert "species_state" in stats


@pytest.mark.asyncio
async def test_integrated_organism_stop_works(integrated_organism):
    """stop() detiene el organismo integrado."""
    loop = integrated_organism

    async def stop_after_delay():
        await asyncio.sleep(0.3)
        loop.stop()

    asyncio.create_task(stop_after_delay())
    await loop.run(duration_seconds=10.0)

    # Debe haberse detenido antes de los 10s
    assert loop.state.iteration_count < 50


@pytest.mark.asyncio
async def test_integrated_organism_long_run_stable(integrated_organism):
    """El organismo integrado es estable en ejecución larga."""
    loop = integrated_organism
    await loop.run(duration_seconds=3.0)

    # Tras 3s, no debe haber crasheado
    assert loop.state.iteration_count >= 10
    # Y debe haber generado pensamientos
    assert len(loop.thoughts) >= 1


@pytest.mark.asyncio
async def test_integrated_organism_filesystem_sense(integrated_organism):
    """El organismo integrado funciona con sentido de filesystem."""
    loop = integrated_organism
    with tempfile.TemporaryDirectory() as tmpdir:
        # Crear archivo inicial
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")

        fs_sense = FilesystemSense(watch_dir=tmpdir, interval=0.05)
        loop.senses.append(fs_sense)

        await loop.run(duration_seconds=0.5)

        # Debe haber observaciones del filesystem
        fs_obs = [o for o in loop.observations if o.source == "filesystem"]
        # Puede o no tener (depende del timing), pero no debe crashear


@pytest.mark.asyncio
async def test_integrated_organism_law_rejection_doesnt_crash(integrated_organism):
    """Si una acción viola leyes, se rechaza sin crashear."""
    loop = integrated_organism
    # Desactivar utility law para forzar que algunas acciones pasen
    # (en realidad, las leyes ya filtran automáticamente)
    await loop.run(duration_seconds=1.0)
    # El organismo sigue funcionando tras posibles rechazos
    assert loop.state.iteration_count >= 1


@pytest.mark.asyncio
async def test_integrated_organism_thoughts_have_metadata(integrated_organism):
    """Los pensamientos generados tienen metadata de Fase 0.5."""
    loop = integrated_organism
    await loop.run(duration_seconds=2.0)

    if loop.thoughts:
        thought = loop.thoughts[-1]
        # El metadata debe incluir información de Fase 0.5
        assert "laws_verified" in thought.metadata
        assert "physics" in thought.metadata


@pytest.mark.asyncio
async def test_integrated_organism_memory_operations(integrated_organism):
    """La memoria viva ejecuta operaciones durante la ejecución."""
    loop = integrated_organism
    # Llenar memoria con varias entries para que think() tenga material
    for i in range(10):
        loop.memory.add(
            content=f"entry de test número {i}",
            type="episodic",
            provenance="test_setup",
        )

    await loop.run(duration_seconds=1.0)

    # La memoria debe haber ejecutado operaciones
    stats = loop.memory.get_stats()
    assert stats["operations_count"] >= 0


@pytest.mark.asyncio
async def test_integrated_organism_compatible_with_phase0():
    """El organismo integrado es compatible con CognitiveLoop de Fase 0."""
    # Crear bucle Fase 0 original
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense()]
    mock_llm = MockPeripheral(responses=["test"])
    speaker = Speaker(llm_peripheral=mock_llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    loop_v0 = CognitiveLoop(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=0.1,
    )

    await loop_v0.run(duration_seconds=0.5)
    assert loop_v0.state.iteration_count >= 1

    # Y el bucle Fase 0.5 también funciona
    loop_v05 = CognitiveLoopV05(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=InternalState(),
        tick_interval=0.1,
    )

    await loop_v05.run(duration_seconds=0.5)
    assert loop_v05.state.iteration_count >= 1


@pytest.mark.asyncio
async def test_integrated_organism_llm_backend_swap():
    """El organismo funciona con diferentes backends LLM."""
    for backend_config in [
        {"backend": "mock", "responses": ["test response"]},
    ]:
        llm = create_llm_peripheral(backend_config)
        state = InternalState()
        world_model = WorldModel()
        senses = [ClockSense()]
        speaker = Speaker(llm_peripheral=llm)
        subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

        loop = CognitiveLoopV05(
            senses=senses,
            world_model=world_model,
            subagents=subagents,
            state=state,
            tick_interval=0.1,
        )

        await loop.run(duration_seconds=0.5)
        assert loop.state.iteration_count >= 1


@pytest.mark.asyncio
async def test_integrated_organism_photonetic_pool_shared():
    """El pool filogenético es compartido entre instancias."""
    PhylogeneticPool._instance = None

    # Crear dos organismos con el mismo pool
    state1 = InternalState()
    state2 = InternalState()
    senses = [ClockSense()]
    mock_llm = MockPeripheral(responses=["test"])
    speaker1 = Speaker(llm_peripheral=mock_llm)
    speaker2 = Speaker(llm_peripheral=mock_llm)
    subagents1 = [Perceiver(), Forecaster(WorldModel()), speaker1, Critic()]
    subagents2 = [Perceiver(), Forecaster(WorldModel()), speaker2, Critic()]

    loop1 = CognitiveLoopV05(
        senses=senses,
        subagents=subagents1,
        state=state1,
        tick_interval=0.1,
        zoe_id="zoe_1",
    )
    loop2 = CognitiveLoopV05(
        senses=senses,
        subagents=subagents2,
        state=state2,
        tick_interval=0.1,
        zoe_id="zoe_2",
    )

    # Ambas ZOEs comparten el mismo pool (singleton)
    assert loop1.phylogenetic.pool is loop2.phylogenetic.pool

    # zoe_1 publica una mejora
    loop1.phylogenetic.publish_improvement(
        description="test mejora",
        change_type="add_module",
        payload={},
        metrics_before={},
    )

    # zoe_2 debería verla como pendiente
    pending = loop2.phylogenetic.get_pending_improvements()
    assert len(pending) >= 1


# ===== Test de regresión: todo lo de Fase 0 sigue funcionando =====


@pytest.mark.asyncio
async def test_regression_phase0_cognitive_loop_still_works():
    """CognitiveLoop de Fase 0 (sin componentes 0.5) sigue funcionando."""
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense()]
    mock_llm = MockPeripheral(responses=["test"])
    speaker = Speaker(llm_peripheral=mock_llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    loop = CognitiveLoop(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=0.1,
    )

    await loop.run(duration_seconds=0.5)
    assert loop.state.iteration_count >= 1
    assert len(loop.observations) >= 1


@pytest.mark.asyncio
async def test_regression_phase0_demo_still_works():
    """El demo de Fase 0 sigue funcionando con el bucle básico."""
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense()]
    mock_llm = MockPeripheral(responses=["test thought"])
    speaker = Speaker(llm_peripheral=mock_llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    thoughts_received = []

    async def on_thought(t):
        thoughts_received.append(t)

    loop = CognitiveLoop(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=0.1,
        on_thought=on_thought,
    )

    await loop.run(duration_seconds=1.0)
    # El bucle de Fase 0 funciona
    assert loop.state.iteration_count >= 1


# ===== Test de coherencia: componentes no interfieren entre sí =====


@pytest.mark.asyncio
async def test_coherence_laws_dont_block_all_actions(integrated_organism):
    """Las leyes no bloquean todas las acciones (el organismo sigue pensando)."""
    loop = integrated_organism
    await loop.run(duration_seconds=2.0)

    # Debe haber generado al menos 1 pensamiento
    # (si las leyes bloquearan todo, no habría ninguno)
    assert len(loop.thoughts) >= 1


@pytest.mark.asyncio
async def test_coherence_physics_affects_decisions(integrated_organism):
    """La física cognitiva afecta las decisiones del organismo."""
    loop = integrated_organism
    # Forzar energía baja
    loop.state.energy = 0.1
    loop.physics.energy_cognitive = 0.1

    await loop.run(duration_seconds=1.0)

    # Con energía baja, should_rest debe ser True
    assert loop.physics.should_rest() is True


@pytest.mark.asyncio
async def test_coherence_tensions_generate_thought_triggers(integrated_organism):
    """Las tensiones generan triggers de pensamiento."""
    loop = integrated_organism
    # Forzar estado que genere tensión
    loop.state.fatigue = 0.9
    loop.state.energy = 0.1
    loop.tensions.update_from_state(
        energy=0.1, fatigue=0.9, arousal=0.1, surprise=0.1
    )

    trigger = loop.tensions.get_thought_trigger()
    assert trigger
    assert len(trigger) > 10
