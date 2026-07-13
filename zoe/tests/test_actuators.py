"""Tests para actuadores (Fase 1.5)."""

import asyncio
import pytest
import time

from zoe.peripherals.actuators import (
    Actuator,
    LanguageActuator,
    CodeActuator,
    ToolActuator,
    FederationActuator,
    ActuatorManager,
    ActionResult,
)
from zoe.peripherals.llm import MockPeripheral
from zoe.core.cognitive_laws import CognitiveLaws


# ===== ActionResult =====


def test_action_result_initialization():
    """ActionResult se inicializa correctamente."""
    result = ActionResult(success=True, output="test", cost=0.1)
    assert result.success is True
    assert result.output == "test"
    assert result.cost == 0.1
    assert result.timestamp > 0


def test_action_result_to_dict():
    """to_dict serializa."""
    result = ActionResult(success=True, output="test", cost=0.1)
    d = result.to_dict()
    assert d["success"] is True
    assert d["output"] == "test"
    assert d["cost"] == 0.1


# ===== LanguageActuator =====


@pytest.mark.asyncio
async def test_language_actuator_generates_output():
    """LanguageActuator genera output con LLM."""
    llm = MockPeripheral(responses=["Hola, soy Zoe."])
    actuator = LanguageActuator()
    result = await actuator.execute(
        action={"prompt": "Saluda"},
        llm_peripheral=llm,
    )
    assert result.success is True
    assert "Hola" in result.output


@pytest.mark.asyncio
async def test_language_actuator_fails_without_llm():
    """LanguageActuator falla sin LLM."""
    actuator = LanguageActuator()
    result = await actuator.execute(action={"prompt": "test"})
    assert result.success is False
    assert "LLM" in result.error


@pytest.mark.asyncio
async def test_language_actuator_fails_without_prompt():
    """LanguageActuator falla sin prompt."""
    llm = MockPeripheral(responses=["test"])
    actuator = LanguageActuator()
    result = await actuator.execute(action={}, llm_peripheral=llm)
    assert result.success is False


# ===== CodeActuator =====


@pytest.mark.asyncio
async def test_code_actuator_executes_python():
    """CodeActuator ejecuta código Python."""
    actuator = CodeActuator(timeout=5.0)
    result = await actuator.execute(
        action={"code": "print('hello world')", "language": "python"},
    )
    assert result.success is True
    assert "hello world" in result.output


@pytest.mark.asyncio
async def test_code_actuator_executes_shell():
    """CodeActuator ejecuta shell."""
    actuator = CodeActuator(timeout=5.0)
    result = await actuator.execute(
        action={"code": "echo test_output", "language": "bash"},
    )
    assert result.success is True
    assert "test_output" in result.output


@pytest.mark.asyncio
async def test_code_actuator_fails_on_error():
    """CodeActuator captura errores de código."""
    actuator = CodeActuator(timeout=5.0)
    result = await actuator.execute(
        action={"code": "raise ValueError('test error')", "language": "python"},
    )
    assert result.success is False
    assert "test error" in result.error


@pytest.mark.asyncio
async def test_code_actuator_timeout():
    """CodeActuator respeta timeout."""
    actuator = CodeActuator(timeout=0.5)
    result = await actuator.execute(
        action={"code": "import time; time.sleep(2)", "language": "python"},
    )
    assert result.success is False
    assert "timeout" in result.error.lower()


@pytest.mark.asyncio
async def test_code_actuator_rejects_unallowed_language():
    """CodeActuator rechaza lenguajes no permitidos."""
    actuator = CodeActuator(timeout=5.0)
    result = await actuator.execute(
        action={"code": "test", "language": "ruby"},
    )
    assert result.success is False
    assert "not allowed" in result.error.lower()


# ===== ToolActuator =====


@pytest.mark.asyncio
async def test_tool_actuator_calls_sync_function():
    """ToolActuator llama función síncrona."""
    def greet(name: str = "mundo") -> str:
        return f"Hola {name}"

    actuator = ToolActuator(tools={"greet": greet})
    result = await actuator.execute(
        action={"tool": "greet", "args": {"name": "Zoe"}},
    )
    assert result.success is True
    assert "Hola Zoe" in result.output


@pytest.mark.asyncio
async def test_tool_actuator_calls_async_function():
    """ToolActuator llama función asíncrona."""
    async def async_greet(name: str = "mundo") -> str:
        await asyncio.sleep(0.01)
        return f"Async hola {name}"

    actuator = ToolActuator(tools={"async_greet": async_greet})
    result = await actuator.execute(
        action={"tool": "async_greet", "args": {"name": "Zoe"}},
    )
    assert result.success is True
    assert "Async hola Zoe" in result.output


@pytest.mark.asyncio
async def test_tool_actuator_fails_on_missing_tool():
    """ToolActuator falla si tool no existe."""
    actuator = ToolActuator(tools={})
    result = await actuator.execute(action={"tool": "nonexistent"})
    assert result.success is False
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_tool_actuator_handles_exceptions():
    """ToolActuator captura excepciones de tools."""
    def failing_tool() -> str:
        raise RuntimeError("tool error")

    actuator = ToolActuator(tools={"fail": failing_tool})
    result = await actuator.execute(action={"tool": "fail", "args": {}})
    assert result.success is False
    assert "tool error" in result.error


def test_tool_actuator_register_unregister():
    """ToolActuator registra y elimina tools."""
    actuator = ToolActuator()
    actuator.register_tool("test", lambda: "test")
    assert "test" in actuator.list_tools()

    actuator.unregister_tool("test")
    assert "test" not in actuator.list_tools()


# ===== FederationActuator =====


@pytest.mark.asyncio
async def test_federation_actuator_send_message():
    """FederationActuator envía mensaje."""
    actuator = FederationActuator()
    result = await actuator.execute(
        action={
            "federation_type": "send_message",
            "target": "zoe_2",
            "message": "Hola otra Zoe",
        },
    )
    assert result.success is True
    assert len(actuator._messages_sent) == 1


@pytest.mark.asyncio
async def test_federation_actuator_unknown_type():
    """FederationActuator rechaza tipo desconocido."""
    actuator = FederationActuator()
    result = await actuator.execute(
        action={"federation_type": "unknown_type"},
    )
    assert result.success is False


@pytest.mark.asyncio
async def test_federation_actuator_without_motor():
    """FederationActuator sin motor filogenético falla en publish."""
    actuator = FederationActuator(phylogenetic_motor=None)
    result = await actuator.execute(
        action={"federation_type": "publish_improvement"},
    )
    assert result.success is False
    assert "phylogenetic" in result.error.lower()


@pytest.mark.asyncio
async def test_federation_actuator_stats():
    """FederationActuator get_stats funciona."""
    actuator = FederationActuator()
    await actuator.execute(
        action={"federation_type": "send_message", "target": "x", "message": "y"},
    )
    stats = actuator.get_stats()
    assert stats["messages_sent"] == 1
    assert stats["has_phylogenetic"] is False


# ===== ActuatorManager =====


@pytest.mark.asyncio
async def test_manager_executes_language_action():
    """ActuatorManager ejecuta acción de language."""
    manager = ActuatorManager()
    llm = MockPeripheral(responses=["test response"])
    manager.register_actuator(LanguageActuator())

    result = await manager.execute_action(
        action={"actuator": "language", "prompt": "test"},
        llm_peripheral=llm,
    )
    assert result.success is True


@pytest.mark.asyncio
async def test_manager_executes_code_action():
    """ActuatorManager ejecuta acción de code."""
    manager = ActuatorManager()
    manager.register_actuator(CodeActuator(timeout=5.0))

    result = await manager.execute_action(
        action={"actuator": "code", "code": "print('test')", "language": "python"},
    )
    assert result.success is True


@pytest.mark.asyncio
async def test_manager_fails_on_unknown_actuator():
    """ActuatorManager falla si actuador no existe."""
    manager = ActuatorManager()
    result = await manager.execute_action(action={"actuator": "nonexistent"})
    assert result.success is False
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_manager_verifies_laws():
    """ActuatorManager verifica leyes antes de ejecutar."""
    laws = CognitiveLaws()
    manager = ActuatorManager(laws=laws)
    manager.register_actuator(LanguageActuator())
    llm = MockPeripheral(responses=["test"])

    # Acción sin utilidad (violación 1ra ley)
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
async def test_manager_stats():
    """ActuatorManager get_stats funciona."""
    manager = ActuatorManager()
    manager.register_actuator(LanguageActuator())
    llm = MockPeripheral(responses=["test"])

    await manager.execute_action(
        action={"actuator": "language", "prompt": "test"},
        llm_peripheral=llm,
    )

    stats = manager.get_stats()
    assert stats["total_actions"] == 1
    assert stats["successful"] == 1


def test_manager_list_actuators():
    """ActuatorManager lista actuadores."""
    manager = ActuatorManager()
    manager.register_actuator(LanguageActuator())
    manager.register_actuator(CodeActuator())

    actuators = manager.list_actuators()
    assert "language" in actuators
    assert "code" in actuators
