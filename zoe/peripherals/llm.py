"""
ZOE v1.0 — LLM Peripheral

Abstracción de LLM periférico con múltiples backends.
ZOE es agnóstica al LLM. Cualquiera sirve como "sentido de lenguaje".

Backends:
- OllamaPeripheral: Ollama local (default para producción)
- OpenAICompatiblePeripheral: cualquier API OpenAI-compatible
- ZAIPeripheral: z-ai CLI (para desarrollo en este entorno)
- MockPeripheral: respuestas determinísticas para tests
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, AsyncIterator

logger = logging.getLogger(__name__)


class LLMPeripheral(ABC):
    """Clase base para LLM periféricos."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> str:
        """Genera texto a partir de un prompt."""
        ...

    async def generate_streaming(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Genera texto token a token (Fase 5).

        Implementación por defecto: llama a generate() y divide el resultado
        en chunks de palabras. Los backends reales (Ollama, OpenAI) hacen streaming real.

        Yields:
            chunks de texto (palabras o tokens)
        """
        # Default: simular streaming dividiendo la respuesta completa
        full = await self.generate(prompt, system, max_tokens, temperature)
        # Yield por palabras (más natural que por caracteres)
        for word in full.split(" "):
            yield word + " "

    @property
    def supports_streaming(self) -> bool:
        """Indica si el backend soporta streaming real (token a token)."""
        return False

    async def health_check(self) -> bool:
        """Verifica que el backend esté disponible."""
        try:
            response = await self.generate("Responde: OK", max_tokens=10)
            return bool(response)
        except Exception as e:
            logger.warning(f"LLM health check failed: {e}")
            return False


class MockPeripheral(LLMPeripheral):
    """LLM periférico mock para tests determinísticos."""

    def __init__(self, responses: Optional[List[str]] = None):
        self._responses = responses or [
            "Observando el entorno.",
            "He notado un patrón.",
            "Reflexionando sobre lo ocurrido.",
            "Generando hipótesis.",
            "Consolidando aprendizaje.",
        ]
        self._idx = 0

    @property
    def name(self) -> str:
        return "mock"

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> str:
        # Determinístico basado en hash del prompt (para tests reproducibles)
        if self._responses:
            response = self._responses[self._idx % len(self._responses)]
            self._idx += 1
            return response
        return ""

    async def generate_streaming(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Streaming mock: yield por palabras."""
        full = await self.generate(prompt, system, max_tokens, temperature)
        for word in full.split(" "):
            yield word + " "


class OllamaPeripheral(LLMPeripheral):
    """LLM periférico vía Ollama (local)."""

    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "ollama"

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> str:
        import aiohttp

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        if system:
            payload["system"] = system

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate", json=payload, timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Ollama error {resp.status}: {await resp.text()}")
                data = await resp.json()
                return data.get("response", "").strip()

    @property
    def supports_streaming(self) -> bool:
        return True

    async def generate_streaming(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Streaming real con Ollama (NDJSON)."""
        import aiohttp

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        if system:
            payload["system"] = system

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate", json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Ollama error {resp.status}: {await resp.text()}")
                async for line in resp.content:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

    async def health_check(self) -> bool:
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False


class OpenAICompatiblePeripheral(LLMPeripheral):
    """LLM periférico vía API OpenAI-compatible."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url.rstrip("/")

        if not self.api_key:
            logger.warning("OpenAICompatiblePeripheral: sin API key")

    @property
    def name(self) -> str:
        return "openai_compatible"

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> str:
        import aiohttp

        if not self.api_key:
            raise RuntimeError("OpenAI API key no configurada")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"OpenAI error {resp.status}: {await resp.text()}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()

    @property
    def supports_streaming(self) -> bool:
        return True

    async def generate_streaming(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Streaming real con API OpenAI-compatible (SSE)."""
        import aiohttp

        if not self.api_key:
            raise RuntimeError("OpenAI API key no configurada")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"OpenAI error {resp.status}: {await resp.text()}")
                async for line in resp.content:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(b"data: "):
                        line = line[6:]
                    if line == b"[DONE]":
                        break
                    try:
                        chunk = json.loads(line)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        token = delta.get("content", "")
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        continue


class ZAIPeripheral(LLMPeripheral):
    """
    LLM periférico vía z-ai CLI.

    Útil para desarrollo y tests en este entorno.
    """

    def __init__(self, model: str = "glm-4.6"):
        self.model = model
        self._zai_available: Optional[bool] = None

    @property
    def name(self) -> str:
        return "zai"

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> str:
        # z-ai CLI es síncrono, ejecutar en thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._generate_sync, prompt, system, max_tokens
        )

    def _generate_sync(
        self, prompt: str, system: Optional[str], max_tokens: int
    ) -> str:
        # Construir prompt combinado
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n---\n\n{prompt}"

        # Usar z-ai CLI directamente
        cmd = ["z-ai", "chat", "--prompt", full_prompt, "--model", self.model]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            if result.returncode != 0:
                logger.warning(f"z-ai CLI error: {result.stderr[:200]}")
                return f"[z-ai error: {result.returncode}]"

            output = result.stdout.strip()
            if not output:
                return ""

            # z-ai CLI devuelve JSON con la respuesta.
            # Extraer solo el content del message.
            return self._extract_content(output)

        except subprocess.TimeoutExpired:
            logger.warning("z-ai CLI timeout")
            return "[z-ai timeout]"
        except FileNotFoundError:
            logger.warning("z-ai CLI no disponible")
            return "[z-ai not found]"
        except Exception as e:
            logger.warning(f"z-ai CLI exception: {e}")
            return f"[z-ai error: {e}]"

    def _extract_content(self, output: str) -> str:
        """Extrae el contenido del mensaje de la salida de z-ai CLI."""
        # z-ai CLI devuelve texto con prefijo "🚀 Initializing..." y luego JSON
        # Buscar el JSON en la salida

        # Intentar parsear como JSON directamente
        try:
            data = json.loads(output)
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

        # Buscar JSON dentro del texto (puede haber texto antes/después)
        import re

        # Buscar el primer { que inicie un JSON válido
        json_match = re.search(r'\{[\s\S]*\}', output)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

        # Si no se pudo parsear, devolver el output tal cual
        # (puede ser texto plano en algunas versiones del CLI)
        # Pero filtrar líneas de log de z-ai
        lines = output.split("\n")
        filtered = [l for l in lines if not l.startswith("🚀") and not l.startswith("✅") and not l.startswith("🎉")]
        return "\n".join(filtered).strip()

    async def health_check(self) -> bool:
        if self._zai_available is not None:
            return self._zai_available
        # Verificar que z-ai está en PATH
        loop = asyncio.get_event_loop()
        self._zai_available = await loop.run_in_executor(
            None, lambda: shutil.which("z-ai") is not None
        )
        return self._zai_available


def create_llm_peripheral(config: Dict[str, Any]) -> LLMPeripheral:
    """
    Factory para crear LLM periférico desde configuración.

    Args:
        config: dict con keys 'backend' y dependencias del backend

    Example:
        >>> config = {"backend": "ollama", "model": "qwen2.5:3b"}
        >>> llm = create_llm_peripheral(config)
    """
    backend = config.get("backend", "mock").lower()

    if backend == "ollama":
        return OllamaPeripheral(
            model=config.get("model", "qwen2.5:3b"),
            base_url=config.get("base_url", "http://localhost:11434"),
        )
    elif backend in ("openai", "openai_compatible"):
        return OpenAICompatiblePeripheral(
            model=config.get("model", "gpt-4o-mini"),
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.openai.com/v1"),
        )
    elif backend == "zai":
        return ZAIPeripheral(model=config.get("model", "glm-4.6"))
    elif backend == "mock":
        return MockPeripheral(responses=config.get("responses"))
    else:
        raise ValueError(f"Backend LLM desconocido: {backend}")
