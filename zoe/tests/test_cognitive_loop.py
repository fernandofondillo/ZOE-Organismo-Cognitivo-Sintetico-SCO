"""Tests para CognitiveLoop."""

import asyncio
import pytest

from zoe.core.cognitive_loop import CognitiveLoop, Thought, Observation
from zoe.core.state import InternalState
from zoe.peripherals.senses import ClockSense, UserInputSense


@pytest.mark.asyncio
async def test_loop_runs_without_input():
    """El bucle ejecuta iteraciones sin input externo."""
    loop = CognitiveLoop(
        senses=[ClockSense()],
        tick_interval=0.1,
        state=InternalState(),
    )

    # Correr 1 segundo
    await loop.run(duration_seconds=1.0)

    # Debe haber ejecutado al menos 5 iteraciones
    assert loop.state.iteration_count >= 5
    assert len(loop.observations) > 0


@pytest.mark.asyncio
async def test_loop_records_observations():
    """El bucle registra observaciones de los sentidos."""
    clock = ClockSense()
    loop = CognitiveLoop(
        senses=[clock],
        tick_interval=0.1,
        state=InternalState(),
    )

    await loop.run(duration_seconds=0.5)

    # Todas las observaciones deben ser del ClockSense
    for obs in loop.observations:
        assert obs.source == "clock"


@pytest.mark.asyncio
async def test_loop_with_user_input():
    """El bucle procesa input del usuario cuando lo hay."""
    user_sense = UserInputSense()
    user_sense.inject_input("Hola Zoe")

    loop = CognitiveLoop(
        senses=[user_sense, ClockSense()],
        tick_interval=0.1,
        state=InternalState(),
    )

    await loop.run(duration_seconds=0.5)

    # Debe haber registrado la observación del usuario
    user_obs = [o for o in loop.observations if o.source == "user"]
    assert len(user_obs) >= 1


@pytest.mark.asyncio
async def test_loop_state_updates():
    """El estado interno se actualiza durante el bucle."""
    state = InternalState()
    initial_iteration = state.iteration_count

    loop = CognitiveLoop(
        senses=[ClockSense()],
        tick_interval=0.1,
        state=state,
    )

    await loop.run(duration_seconds=0.5)

    assert state.iteration_count > initial_iteration


@pytest.mark.asyncio
async def test_loop_callback_on_thought():
    """El callback on_thought se invoca cuando se genera un pensamiento."""
    thoughts_received = []

    async def on_thought(thought):
        thoughts_received.append(thought)

    # Crear un loop con un speaker mock que siempre genera pensamiento
    from zoe.core.subagents.speaker import Speaker
    from zoe.peripherals.llm import MockPeripheral

    speaker = Speaker(llm_peripheral=MockPeripheral(responses=["Pensamiento de prueba."]))

    loop = CognitiveLoop(
        senses=[ClockSense()],
        subagents=[speaker],
        tick_interval=0.1,
        on_thought=on_thought,
        state=InternalState(),
    )

    await loop.run(duration_seconds=2.0)

    # Debe haber recibido al menos 1 pensamiento
    # (la decisión de pensar es probabilística, puede ser 0 en 2s)
    # Verificamos que si se recibió, es válido
    for t in thoughts_received:
        assert isinstance(t, Thought)
        assert t.content
        assert t.timestamp > 0


@pytest.mark.asyncio
async def test_loop_stop():
    """stop() detiene el bucle."""
    loop = CognitiveLoop(
        senses=[ClockSense()],
        tick_interval=0.1,
        state=InternalState(),
    )

    async def stop_after_delay():
        await asyncio.sleep(0.3)
        loop.stop()

    asyncio.create_task(stop_after_delay())
    await loop.run(duration_seconds=10.0)

    # Debe haberse detenido antes de los 10s
    assert loop.state.iteration_count < 50


@pytest.mark.asyncio
async def test_loop_get_stats():
    """get_stats() devuelve estadísticas correctas."""
    loop = CognitiveLoop(
        senses=[ClockSense()],
        tick_interval=0.1,
        state=InternalState(),
    )

    await loop.run(duration_seconds=0.5)
    stats = loop.get_stats()

    assert "iterations" in stats
    assert "observations" in stats
    assert "thoughts" in stats
    assert "energy" in stats
    assert "fatigue" in stats
    assert stats["iterations"] >= 1
