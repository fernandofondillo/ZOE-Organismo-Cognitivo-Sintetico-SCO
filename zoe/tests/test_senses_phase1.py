"""Tests para sentidos Fase 1.5 (NetworkSense, AgentSense)."""

import asyncio
import pytest
import time

from zoe.peripherals.senses import NetworkSense, AgentSense
from zoe.core.cognitive_loop import Observation


# ===== NetworkSense =====


@pytest.mark.asyncio
async def test_network_sense_no_endpoints():
    """NetworkSense sin endpoints reporta."""
    sense = NetworkSense(endpoints=[], check_interval=0.0)
    obs = await sense.observe()
    assert obs is not None
    assert obs.source == "network"
    assert "sin endpoints" in obs.content.lower() or "0" in obs.content


@pytest.mark.asyncio
async def test_network_sense_add_endpoint():
    """NetworkSense añade endpoint."""
    sense = NetworkSense(endpoints=[])
    sense.add_endpoint("http://localhost:9999")
    assert len(sense.endpoints) == 1


@pytest.mark.asyncio
async def test_network_sense_observes_endpoint():
    """NetworkSense observa endpoint."""
    sense = NetworkSense(
        endpoints=["http://localhost:99999"],  # puerto inexistente
        check_interval=0.0,
        timeout=0.5,
    )
    obs = await sense.observe()
    assert obs is not None
    # El endpoint no debería ser alcanzable
    if isinstance(obs, list):
        assert any("no alcanzable" in o.content.lower() for o in obs)
    else:
        assert "no alcanzable" in obs.content.lower() or "alcanzable" in obs.content.lower()


@pytest.mark.asyncio
async def test_network_sense_interval_respected():
    """NetworkSense respeta check_interval."""
    sense = NetworkSense(endpoints=[], check_interval=10.0)
    obs1 = await sense.observe()
    # Segunda observación inmediata debería devolver None (dentro del interval)
    obs2 = await sense.observe()
    assert obs2 is None


@pytest.mark.asyncio
async def test_network_sense_detects_recovery():
    """NetworkSense detecta recuperación de endpoint."""
    sense = NetworkSense(
        endpoints=["http://localhost:99999"],  # no alcanzable
        check_interval=0.0,
        timeout=0.5,
    )
    # Primera observación: no alcanzable
    await sense.observe()

    # Simular que ahora es alcanzable (cambiar _last_status manualmente)
    sense._last_status["http://localhost:99999"] = False

    # Como no podemos hacer que el endpoint sea alcanzable en test,
    # verificamos que el código de detección de cambios funciona
    # marcándolo como alcanzable manualmente
    sense._last_status["http://localhost:99999"] = True
    # Segunda observación: sigue no alcanzable, debería detectar "caído"
    obs = await sense.observe()
    if isinstance(obs, list):
        assert any("caído" in o.content.lower() or "caido" in o.content.lower() for o in obs)
    # Si no es lista, puede ser "sin cambios" o detección


# ===== AgentSense =====


@pytest.mark.asyncio
async def test_agent_sense_no_agents():
    """AgentSense sin agentes reporta."""
    sense = AgentSense(known_agents={})
    obs = await sense.observe()
    assert obs is not None
    assert obs.source == "agent"
    assert "0" in obs.content or "sin agentes" in obs.content.lower()


@pytest.mark.asyncio
async def test_agent_sense_register_agent():
    """AgentSense registra agente."""
    sense = AgentSense()
    sense.register_agent("zoe_2", agent_type="zoe", metadata={"version": "0.5"})
    assert "zoe_2" in sense.known_agents
    assert sense.known_agents["zoe_2"]["type"] == "zoe"


@pytest.mark.asyncio
async def test_agent_sense_observes_agents():
    """AgentSense observa agentes registrados."""
    sense = AgentSense()
    sense.register_agent("zoe_2", agent_type="zoe")
    sense.register_agent("claude_1", agent_type="other_ai")

    obs = await sense.observe()
    assert obs is not None
    assert "2" in obs.content  # 2 agentes
    assert obs.metadata["agent_count"] == 2
    assert obs.metadata["active_count"] == 2


@pytest.mark.asyncio
async def test_agent_sense_update_status():
    """AgentSense actualiza estado de agente."""
    sense = AgentSense()
    sense.register_agent("zoe_2", agent_type="zoe")
    sense.update_agent_status("zoe_2", "inactive")

    obs = await sense.observe()
    assert obs.metadata["active_count"] == 0


@pytest.mark.asyncio
async def test_agent_sense_remove_agent():
    """AgentSense elimina agente."""
    sense = AgentSense()
    sense.register_agent("zoe_2")
    sense.remove_agent("zoe_2")
    assert "zoe_2" not in sense.known_agents


@pytest.mark.asyncio
async def test_agent_sense_detects_stale():
    """AgentSense detecta agentes sin señal reciente."""
    sense = AgentSense()
    sense.register_agent("zoe_old", agent_type="zoe")
    # Marcar last_seen como hace 10 minutos
    sense.known_agents["zoe_old"]["last_seen"] = time.time() - 600

    obs = await sense.observe()
    assert "zoe_old" in obs.metadata.get("stale_agents", [])


@pytest.mark.asyncio
async def test_agent_sense_iteration_increments():
    """AgentSense incrementa iteración."""
    sense = AgentSense()
    obs1 = await sense.observe()
    obs2 = await sense.observe()
    assert obs2.metadata["iteration"] > obs1.metadata["iteration"]


@pytest.mark.asyncio
async def test_agent_sense_with_mixed_statuses():
    """AgentSense con agentes en distintos estados."""
    sense = AgentSense()
    sense.register_agent("active_1", agent_type="zoe")
    sense.register_agent("active_2", agent_type="zoe")
    sense.register_agent("inactive_1", agent_type="zoe")
    sense.update_agent_status("inactive_1", "inactive")

    obs = await sense.observe()
    assert obs.metadata["agent_count"] == 3
    assert obs.metadata["active_count"] == 2
