"""
ZOE v1.2 — Circuit Breaker para LLM

Protege las llamadas a LLM contra fallos en cascada.
Estados:
- CLOSED: funcionamiento normal, las llamadas pasan directamente
- OPEN: demasiados fallos consecutivos, se usa fallback
- HALF_OPEN: después de timeout, se prueba una llamada real

Umbral: 5 fallos consecutivos → OPEN
Timeout: 30 segundos en OPEN → HALF_OPEN
Fallback: PatternSpeaker como respaldo

Thread-safe con asyncio locks.
"""

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Estados del circuit breaker."""

    CLOSED = "closed"       # Normal: las llamadas pasan
    OPEN = "open"           # Fallando: usa fallback
    HALF_OPEN = "half_open"  # Recuperando: prueba una llamada


class CircuitBreakerError(Exception):
    """Excepción lanzada cuando el circuit breaker está OPEN."""

    def __init__(self, message: str, fallback_result: Optional[Any] = None):
        super().__init__(message)
        self.fallback_result = fallback_result


class CircuitBreaker:
    """
    Circuit breaker para llamadas a LLM.

    Protege contra fallos en cascada detectando fallos consecutivos
    y cambiando a un modo de fallback cuando se supera el umbral.

    Args:
        name: identificador del circuit breaker
        failure_threshold: número de fallos consecutivos para abrir
        recovery_timeout: segundos en OPEN antes de pasar a HALF_OPEN
        expected_exception: excepción(es) que cuentan como fallo
        fallback_factory: factory opcional para crear fallback
    """

    def __init__(
        self,
        name: str = "llm_circuit",
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exception: tuple = (Exception,),
        fallback_factory: Optional[Callable[[], Any]] = None,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.fallback_factory = fallback_factory

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._last_success_time: Optional[float] = None
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0
        self._total_fallbacks = 0

        # Thread-safe lock
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Estado actual del circuit breaker."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Fallos consecutivos actuales."""
        return self._failure_count

    @property
    def is_closed(self) -> bool:
        """True si el circuito está cerrado (funcionando)."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """True si el circuito está abierto (fallback)."""
        return self._state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """True si el circuito está en recuperación."""
        return self._state == CircuitState.HALF_OPEN

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del circuit breaker."""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
            "total_fallbacks": self._total_fallbacks,
            "last_failure_time": self._last_failure_time,
            "last_success_time": self._last_success_time,
        }

    def summary(self) -> str:
        """Resumen legible del estado."""
        return (
            f"CircuitBreaker({self.name}, state={self._state.value}, "
            f"failures={self._failure_count}/{self.failure_threshold}, "
            f"calls={self._total_calls}, fallbacks={self._total_fallbacks})"
        )

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Ejecuta una función con protección del circuit breaker.

        Si el circuito está CLOSED: ejecuta normalmente.
        Si el circuito está OPEN: usa fallback si está disponible.
        Si el circuito está HALF_OPEN: prueba una llamada real.

        Args:
            func: función asíncrona a ejecutar
            *args, **kwargs: argumentos para func

        Returns:
            resultado de func o del fallback

        Raises:
            CircuitBreakerError: si el circuito está OPEN y no hay fallback
            Exception: si la llamada falla en HALF_OPEN
        """
        async with self._lock:
            self._total_calls += 1

            # Verificar si debemos cambiar de OPEN a HALF_OPEN
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(
                        "Circuit %s: timeout reached, transitioning OPEN → HALF_OPEN",
                        self.name,
                    )
                    self._state = CircuitState.HALF_OPEN
                else:
                    # Usar fallback
                    self._total_fallbacks += 1
                    fallback_result = await self._execute_fallback(*args, **kwargs)
                    logger.debug(
                        "Circuit %s: OPEN, using fallback", self.name
                    )
                    return fallback_result

        # Ejecutar la llamada real
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            # Si estábamos en HALF_OPEN, volver a OPEN y usar fallback
            if self._state == CircuitState.HALF_OPEN:
                fallback_result = await self._execute_fallback(*args, **kwargs)
                return fallback_result
            # En CLOSED, re-lanzar la excepción
            raise

    async def _on_success(self) -> None:
        """Maneja una llamada exitosa."""
        async with self._lock:
            self._success_count += 1
            self._total_successes += 1
            self._last_success_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                # Recuperación exitosa: volver a CLOSED
                logger.info(
                    "Circuit %s: recovery successful, HALF_OPEN → CLOSED",
                    self.name,
                )
                self._state = CircuitState.CLOSED
                self._failure_count = 0
            elif self._state == CircuitState.CLOSED:
                # Resetear contador de fallos en éxito
                if self._failure_count > 0:
                    self._failure_count = 0

    async def _on_failure(self) -> None:
        """Maneja una llamada fallida."""
        async with self._lock:
            self._failure_count += 1
            self._total_failures += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                # Fallo en recuperación: volver a OPEN
                logger.warning(
                    "Circuit %s: recovery failed, HALF_OPEN → OPEN",
                    self.name,
                )
                self._state = CircuitState.OPEN
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    # Umbral superado: abrir circuito
                    logger.warning(
                        "Circuit %s: threshold reached (%d/%d), CLOSED → OPEN",
                        self.name,
                        self._failure_count,
                        self.failure_threshold,
                    )
                    self._state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Verifica si ha pasado el tiempo de recuperación."""
        if self._last_failure_time is None:
            return True
        elapsed = time.monotonic() - self._last_failure_time
        return elapsed >= self.recovery_timeout

    async def _execute_fallback(self, *args, **kwargs) -> Any:
        """
        Ejecuta el fallback cuando el circuito está OPEN.

        Intenta usar PatternSpeaker si está disponible,
        de lo contrario devuelve una respuesta genérica.
        """
        try:
            if self.fallback_factory:
                fallback = self.fallback_factory()
                if hasattr(fallback, "generate"):
                    # Es un LLMPeripheral-like
                    prompt = kwargs.get("prompt") or (args[0] if args else "")
                    system = kwargs.get("system")
                    max_tokens = kwargs.get("max_tokens", 300)
                    temperature = kwargs.get("temperature", 0.7)
                    return await fallback.generate(
                        prompt=prompt,
                        system=system,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                elif callable(fallback):
                    return await fallback(*args, **kwargs)
        except Exception as e:
            logger.warning("Circuit %s: fallback failed: %s", self.name, e)

        # Fallback por defecto: respuesta genérica
        prompt = kwargs.get("prompt") or (args[0] if args else "")
        return (
            f"[Servicio temporalmente no disponible. "
            f"Circuit breaker {self.name} está OPEN. "
            f"Intente más tarde.]"
        )

    def force_open(self) -> None:
        """Fuerza el circuito a estado OPEN (para tests)."""
        self._state = CircuitState.OPEN
        self._failure_count = self.failure_threshold
        self._last_failure_time = time.monotonic()
        logger.warning("Circuit %s: forced OPEN", self.name)

    def force_closed(self) -> None:
        """Fuerza el circuito a estado CLOSED (para tests)."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        logger.warning("Circuit %s: forced CLOSED", self.name)

    def force_half_open(self) -> None:
        """Fuerza el circuito a estado HALF_OPEN (para tests)."""
        self._state = CircuitState.HALF_OPEN
        logger.warning("Circuit %s: forced HALF_OPEN", self.name)


class LLMCircuitBreaker:
    """
    Wrapper especializado para proteger un LLMPeripheral.

    Envuelve un LLMPeripheral y añade protección de circuit breaker
    a todas sus llamadas generate().
    """

    def __init__(
        self,
        llm_peripheral: Any,
        name: str = "llm_circuit",
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ):
        self._llm = llm_peripheral
        self._circuit = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=(Exception,),
            fallback_factory=self._create_fallback,
        )

    @property
    def name(self) -> str:
        """Nombre del LLM envuelto."""
        return getattr(self._llm, "name", "unknown")

    @property
    def circuit_state(self) -> CircuitState:
        """Estado actual del circuit breaker."""
        return self._circuit.state

    @property
    def supports_streaming(self) -> bool:
        """Delega al LLM subyacente."""
        return getattr(self._llm, "supports_streaming", False)

    def _create_fallback(self) -> Any:
        """Crea un PatternPeripheral como fallback."""
        try:
            from zoe.core.subagents.speaker import PatternSpeaker
            return PatternSpeaker()
        except ImportError:
            try:
                from zoe.peripherals.llm import MockPeripheral
                return MockPeripheral(responses=[
                    "El servicio de lenguaje no está disponible en este momento.",
                    "Estoy teniendo dificultades técnicas. Inténtalo más tarde.",
                    "No puedo procesar tu mensaje ahora. Estoy en modo recuperación.",
                ])
            except ImportError:
                return None

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> str:
        """
        Genera texto con protección de circuit breaker.

        Si el circuito está OPEN, usa PatternSpeaker como fallback.
        """
        return await self._circuit.call(
            self._llm.generate,
            prompt,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    async def generate_streaming(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ):
        """
        Genera texto en streaming con protección de circuit breaker.

        Si el circuito está OPEN, genera el fallback de una vez.
        """
        if self._circuit.is_open and not self._circuit._should_attempt_reset():
            # Usar fallback directamente
            fallback_text = await self._circuit.call(
                self._llm.generate,
                prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            for word in fallback_text.split(" "):
                yield word + " "
            return

        # Intentar streaming real
        try:
            async for chunk in self._llm.generate_streaming(
                prompt, system, max_tokens, temperature
            ):
                yield chunk
            await self._circuit._on_success()
        except Exception as e:
            await self._circuit._on_failure()
            # Fallback: generar texto completo y dividirlo
            fallback_text = await self._circuit._execute_fallback(
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            for word in fallback_text.split(" "):
                yield word + " "

    async def health_check(self) -> bool:
        """Verifica salud del LLM a través del circuit breaker."""
        try:
            result = await self._circuit.call(
                self._llm.generate, "Responde: OK", max_tokens=10
            )
            return bool(result)
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas combinadas del LLM y circuit breaker."""
        stats = self._circuit.get_stats()
        stats["llm_name"] = self.name
        stats["llm_supports_streaming"] = self.supports_streaming
        return stats
