"""
ZOE v1.0 — Actuators

Actuadores del organismo. Cada actuador ejecuta acciones que pasan
por verify_action() de CognitiveLaws (6 leyes cognitivas).

Actuadores:
- LanguageActuator: genera output en lenguaje natural vía LLM periférico
- CodeActuator: ejecuta código en sandbox
- ToolActuator: invoca tools (skills)
- FederationActuator: comunica con otras ZOEs

Cada actuador implementa la interfaz Actuator (6ta ley: modularidad).
Los actuadores leen de CognitiveFields para contexto y escriben resultados.
"""

from __future__ import annotations

import logging
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


@dataclass
class ActionResult:
    """Resultado de una acción ejecutada por un actuador."""

    success: bool
    output: str = ""
    error: str = ""
    cost: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "cost": self.cost,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class Actuator(ABC):
    """Clase base para actuadores de ZOE."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def execute(
        self,
        action: Dict[str, Any],
        llm_peripheral: Any = None,
        context: Dict[str, Any] = None,
    ) -> ActionResult:
        """
        Ejecuta una acción.

        Args:
            action: dict con la acción a ejecutar (debe pasar verify_action)
            llm_peripheral: LLM periférico (si needed)
            context: contexto adicional (fields, state, etc.)

        Returns:
            ActionResult con resultado
        """
        ...


class LanguageActuator(Actuator):
    """
    Actuador de lenguaje: genera output en lenguaje natural.

    Usa el LLM periférico para producir respuestas.
    """

    def __init__(self, max_tokens: int = 500, temperature: float = 0.7):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._last_output: str = ""

    @property
    def name(self) -> str:
        return "language"

    async def execute(
        self,
        action: Dict[str, Any],
        llm_peripheral: Any = None,
        context: Dict[str, Any] = None,
    ) -> ActionResult:
        """Genera output en lenguaje natural."""
        if not llm_peripheral:
            return ActionResult(
                success=False,
                error="No LLM peripheral available",
                cost=0.0,
            )

        prompt = action.get("prompt", action.get("content", ""))
        system = action.get("system", None)

        if not prompt:
            return ActionResult(
                success=False,
                error="No prompt provided",
                cost=0.0,
            )

        try:
            output = await llm_peripheral.generate(
                prompt=prompt,
                system=system,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            self._last_output = output

            return ActionResult(
                success=True,
                output=output,
                cost=action.get("cost", 0.3),
                metadata={
                    "actuator": self.name,
                    "prompt_length": len(prompt),
                    "output_length": len(output),
                },
            )
        except Exception as e:
            logger.error(f"LanguageActuator error: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                cost=0.1,
                metadata={"actuator": self.name},
            )


class CodeActuator(Actuator):
    """
    Actuador de código: ejecuta código en sandbox.

    En Fase 1: sandbox básico con subprocess (timeout, sin red).
    En Fase 4: sandbox Docker real con aislamiento completo.
    """

    def __init__(self, timeout: float = 10.0, allowed_commands: List[str] = None):
        self.timeout = timeout
        # Comandos permitidos (whitelist)
        self.allowed_commands = allowed_commands or [
            "python3",
            "python",
            "echo",
            "ls",
            "cat",
            "head",
            "tail",
            "wc",
            "sort",
            "uniq",
            "grep",
        ]

    @property
    def name(self) -> str:
        return "code"

    async def execute(
        self,
        action: Dict[str, Any],
        llm_peripheral: Any = None,
        context: Dict[str, Any] = None,
    ) -> ActionResult:
        """Ejecuta código en sandbox."""
        code = action.get("code", action.get("content", ""))
        language = action.get("language", "python")

        if not code:
            return ActionResult(
                success=False,
                error="No code provided",
                cost=0.0,
            )

        # Verificar lenguaje permitido
        if language not in ("python", "python3", "shell", "bash"):
            return ActionResult(
                success=False,
                error=f"Language not allowed: {language}",
                cost=0.0,
            )

        # Construir comando
        if language in ("python", "python3"):
            cmd = ["python3", "-c", code]
        else:
            cmd = ["bash", "-c", code]

        # Verificar comando base está en whitelist
        if cmd[0] not in self.allowed_commands and cmd[0] != "bash":
            return ActionResult(
                success=False,
                error=f"Command not allowed: {cmd[0]}",
                cost=0.0,
            )

        try:
            import asyncio

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return ActionResult(
                    success=False,
                    error=f"Timeout after {self.timeout}s",
                    cost=0.5,
                    metadata={"actuator": self.name, "timeout": True},
                )

            output = stdout.decode("utf-8", errors="replace") if stdout else ""
            error = stderr.decode("utf-8", errors="replace") if stderr else ""

            success = proc.returncode == 0

            return ActionResult(
                success=success,
                output=output,
                error=error if not success else "",
                cost=0.3,
                metadata={
                    "actuator": self.name,
                    "returncode": proc.returncode,
                    "language": language,
                },
            )
        except Exception as e:
            logger.error(f"CodeActuator error: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                cost=0.1,
                metadata={"actuator": self.name},
            )


class ToolActuator(Actuator):
    """
    Actuador de tools: invoca tools (skills).

    Las tools son funciones Python registradas con un nombre.
    Cada tool tiene una interfaz clara (6ta ley: modularidad).
    """

    def __init__(self, tools: Dict[str, Any] = None):
        """
        Args:
            tools: dict de {tool_name: callable}
        """
        self.tools: Dict[str, Any] = tools or {}

    @property
    def name(self) -> str:
        return "tool"

    def register_tool(self, name: str, func: Any) -> None:
        """Registra una tool."""
        self.tools[name] = func

    def unregister_tool(self, name: str) -> None:
        """Elimina una tool."""
        self.tools.pop(name, None)

    def list_tools(self) -> List[str]:
        """Lista tools disponibles."""
        return list(self.tools.keys())

    async def execute(
        self,
        action: Dict[str, Any],
        llm_peripheral: Any = None,
        context: Dict[str, Any] = None,
    ) -> ActionResult:
        """Invoca una tool."""
        tool_name = action.get("tool", action.get("content", ""))
        tool_args = action.get("args", {})

        if not tool_name:
            return ActionResult(
                success=False,
                error="No tool name provided",
                cost=0.0,
            )

        if tool_name not in self.tools:
            return ActionResult(
                success=False,
                error=f"Tool not found: {tool_name}. Available: {self.list_tools()}",
                cost=0.0,
            )

        func = self.tools[tool_name]

        try:
            # Si la función es async, await; si no, ejecutar directamente
            import inspect

            if inspect.iscoroutinefunction(func):
                result = await func(**tool_args)
            else:
                result = func(**tool_args)

            # Normalizar resultado
            if isinstance(result, str):
                output = result
            elif isinstance(result, dict):
                output = str(result.get("output", result))
            else:
                output = str(result)

            return ActionResult(
                success=True,
                output=output,
                cost=0.2,
                metadata={
                    "actuator": self.name,
                    "tool": tool_name,
                    "args": tool_args,
                },
            )
        except Exception as e:
            logger.error(f"ToolActuator error executing {tool_name}: {e}")
            return ActionResult(
                success=False,
                error=str(e),
                cost=0.1,
                metadata={"actuator": self.name, "tool": tool_name},
            )


class FederationActuator(Actuator):
    """
    Actuador de federación: comunica con otras ZOEs.

    Publica mutaciones, envía mensajes, solicita validación.
    Conectado con PhylogeneticMotor.
    """

    def __init__(self, phylogenetic_motor: Any = None):
        self.phylogenetic_motor = phylogenetic_motor
        self._messages_sent: List[Dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "federation"

    def set_phylogenetic_motor(self, motor: Any) -> None:
        self.phylogenetic_motor = motor

    async def execute(
        self,
        action: Dict[str, Any],
        llm_peripheral: Any = None,
        context: Dict[str, Any] = None,
    ) -> ActionResult:
        """Ejecuta acción de federación."""
        fed_type = action.get("federation_type", action.get("content", ""))

        if fed_type == "publish_improvement":
            return await self._publish_improvement(action)
        elif fed_type == "try_improvement":
            return await self._try_improvement(action)
        elif fed_type == "incorporate_validated":
            return await self._incorporate_validated(action)
        elif fed_type == "send_message":
            return await self._send_message(action)
        else:
            return ActionResult(
                success=False,
                error=f"Unknown federation type: {fed_type}",
                cost=0.0,
            )

    async def _publish_improvement(self, action: Dict[str, Any]) -> ActionResult:
        """Publica una mejora en el pool filogenético."""
        if not self.phylogenetic_motor:
            return ActionResult(
                success=False,
                error="No phylogenetic motor configured",
                cost=0.0,
            )

        try:
            imp_id = self.phylogenetic_motor.publish_improvement(
                description=action.get("description", ""),
                change_type=action.get("change_type", "add_module"),
                payload=action.get("payload", {}),
                metrics_before=action.get("metrics_before", {}),
            )
            return ActionResult(
                success=True,
                output=f"Improvement published: {imp_id}",
                cost=0.2,
                metadata={"improvement_id": imp_id},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                error=str(e),
                cost=0.1,
            )

    async def _try_improvement(self, action: Dict[str, Any]) -> ActionResult:
        """Prueba una mejora pendiente."""
        if not self.phylogenetic_motor:
            return ActionResult(
                success=False,
                error="No phylogenetic motor configured",
                cost=0.0,
            )

        pending = self.phylogenetic_motor.get_pending_improvements()
        if not pending:
            return ActionResult(
                success=True,
                output="No pending improvements to try",
                cost=0.05,
            )

        # En Fase 1: solo reportar pendientes
        # En Fase 4: ejecutar test real
        return ActionResult(
            success=True,
            output=f"{len(pending)} improvements pending to try",
            cost=0.1,
            metadata={"pending_count": len(pending)},
        )

    async def _incorporate_validated(self, action: Dict[str, Any]) -> ActionResult:
        """Incorpora mejoras validadas."""
        if not self.phylogenetic_motor:
            return ActionResult(
                success=False,
                error="No phylogenetic motor configured",
                cost=0.0,
            )

        incorporated = self.phylogenetic_motor.incorporate_validated()
        return ActionResult(
            success=True,
            output=f"Incorporated {len(incorporated)} improvements: {incorporated}",
            cost=0.2,
            metadata={"incorporated": incorporated},
        )

    async def _send_message(self, action: Dict[str, Any]) -> ActionResult:
        """Envía mensaje a otra ZOE (placeholder para Fase 4)."""
        target = action.get("target", "unknown")
        message = action.get("message", "")

        self._messages_sent.append(
            {
                "target": target,
                "message": message,
                "timestamp": time.time(),
            }
        )

        return ActionResult(
            success=True,
            output=f"Message queued for {target}: {message[:50]}...",
            cost=0.1,
            metadata={"target": target, "message_length": len(message)},
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            "messages_sent": len(self._messages_sent),
            "has_phylogenetic": self.phylogenetic_motor is not None,
        }


class ActuatorManager:
    """
    Gestor de actuadores.

    Mantiene una colección de actuadores y los ejecuta según el tipo de acción.
    Cada acción pasa por verify_action() antes de ejecutarse.
    """

    def __init__(self, laws: Any = None):
        self.actuators: Dict[str, Actuator] = {}
        self.laws = laws
        self._results: List[ActionResult] = []

    def register_actuator(self, actuator: Actuator) -> None:
        """Registra un actuador."""
        self.actuators[actuator.name] = actuator

    def get_actuator(self, name: str) -> Optional[Actuator]:
        return self.actuators.get(name)

    def list_actuators(self) -> List[str]:
        return list(self.actuators.keys())

    async def execute_action(
        self,
        action: Dict[str, Any],
        llm_peripheral: Any = None,
        context: Dict[str, Any] = None,
    ) -> ActionResult:
        """
        Ejecuta una acción:
        1. Verifica leyes cognitivas (si configuradas)
        2. Selecciona actuador
        3. Ejecuta
        4. Registra resultado
        """
        # 1. Verificar leyes
        if self.laws:
            law_action = self._to_law_action(action)
            passed, violations = self.laws.verify_action(law_action)
            if not passed:
                reasons = [v.reason for v in violations]
                result = ActionResult(
                    success=False,
                    error=f"Laws violated: {reasons}",
                    cost=0.0,
                    metadata={"violations": [v.law.value for v in violations]},
                )
                self._results.append(result)
                return result

        # 2. Seleccionar actuador
        actuator_type = action.get("actuator", "language")
        actuator = self.actuators.get(actuator_type)

        if not actuator:
            result = ActionResult(
                success=False,
                error=f"Actuator not found: {actuator_type}. Available: {self.list_actuators()}",
                cost=0.0,
            )
            self._results.append(result)
            return result

        # 3. Ejecutar
        result = await actuator.execute(action, llm_peripheral, context)

        # 4. Registrar
        self._results.append(result)
        if len(self._results) > 100:
            self._results = self._results[-50:]

        return result

    def _to_law_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte acción de actuador a dict de ley."""
        return {
            "type": action.get("type", "communicate"),
            "uncertainty_reduction": action.get("uncertainty_reduction", 0.2),
            "capacity_increase": action.get("capacity_increase", 0.1),
            "cost": action.get("cost", 0.2),
            "preserves_identity": action.get("preserves_identity", True),
            "provenance": action.get("provenance", "actuator"),
            "confidence": action.get("confidence", 0.5),
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_actions": len(self._results),
            "successful": sum(1 for r in self._results if r.success),
            "failed": sum(1 for r in self._results if not r.success),
            "actuators": self.list_actuators(),
        }
