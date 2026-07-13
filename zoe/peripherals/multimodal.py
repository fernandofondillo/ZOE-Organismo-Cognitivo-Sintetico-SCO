"""
ZOE V1.7 — Multi-modal Peripherals (Sprint 2)

Visión (VLM) y Voz (STT + TTS) como nuevos sentidos y actuadores.

Sin deconstruir: estos son peripherals NUEVOS. No modifican el bucle
cognitivo, ni el CLI, ni el Dashboard existente. El bucle cognitivo
solo ve Observation objects — no sabe ni le importa si el input viene
de texto, voz, o imagen.

Componentes:
1. VLMPeripheral — LLM con capacidad de visión (GPT-4o, Claude, LLaVA)
2. VisionSense — sentido que procesa imágenes
3. VoiceInputSense — sentido que captura y transcribe audio (Whisper STT)
4. VoiceActuator — actuador que genera voz (Piper TTS)

Dependencias opcionales (no rompen nada si no están instaladas):
- Para visión: API cloud (GPT-4o/Claude) o Ollama con LLaVA
- Para STT: whisper o whisper.cpp
- Para TTS: piper-tts
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, AsyncIterator
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================
# 1. VLMPeripheral — LLM con capacidad de visión
# ============================================================

class VLMPeripheral:
    """
    LLM con capacidad de visión (Vision Language Model).

    Usa el mismo backend que LLMPeripheral pero añade soporte para imágenes.
    Soporta:
    - GPT-4o (OpenAI) — visión nativa
    - Claude (Anthropic) — visión nativa
    - LLaVA (Ollama) — visión local gratis

    Si no hay VLM disponible, hace fallback a descripción de texto simple.

    Este NO es un LLMPeripheral (no hereda) porque la interfaz es diferente:
    generate() acepta imágenes además de texto. Pero el Speaker puede usarlo
    cuando detecte que hay imágenes en el contexto.
    """

    def __init__(self, backend: str = "openai_compatible", model: str = "gpt-4o",
                 api_key: str = None, base_url: str = None):
        self.backend = backend
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or "https://api.openai.com/v1"

    @property
    def name(self) -> str:
        return f"vlm_{self.backend}"

    async def generate(self, prompt: str, images: List[bytes] = None,
                       system: str = None, max_tokens: int = 500,
                       temperature: float = 0.7) -> str:
        """
        Genera respuesta desde prompt + imágenes.

        Args:
            prompt: texto del usuario
            images: lista de imágenes en bytes (PNG, JPEG)
            system: system prompt
            max_tokens: máximo tokens de respuesta
            temperature: temperatura de generación

        Returns:
            Descripción o respuesta sobre las imágenes
        """
        if not images:
            # Sin imágenes, usar como LLM normal
            return await self._generate_text_only(prompt, system, max_tokens, temperature)

        if self.backend == "openai_compatible":
            return await self._generate_openai_vision(prompt, images, system, max_tokens, temperature)
        elif self.backend == "anthropic":
            return await self._generate_anthropic_vision(prompt, images, system, max_tokens, temperature)
        elif self.backend == "ollama":
            return await self._generate_ollama_vision(prompt, images, system, max_tokens, temperature)
        else:
            return "[VLM no disponible. Backend no soportado para visión.]"

    async def _generate_text_only(self, prompt, system, max_tokens, temperature) -> str:
        """Fallback: sin imágenes, respuesta simple."""
        return f"[VLM sin imágenes. Prompt: {prompt[:100]}]"

    async def _generate_openai_vision(self, prompt, images, system, max_tokens, temperature) -> str:
        """Genera con GPT-4o vision API."""
        try:
            import aiohttp

            messages = []
            if system:
                messages.append({"role": "system", "content": system})

            # Construir contenido multimodal
            content = [{"type": "text", "text": prompt}]
            for img_bytes in images:
                b64 = base64.b64encode(img_bytes).decode()
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                })

            messages.append({"role": "user", "content": content})

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error = await resp.text()
                        logger.error(f"OpenAI VLM error: {resp.status} - {error}")
                        return f"[Error VLM: {resp.status}]"
        except Exception as e:
            logger.error(f"OpenAI VLM error: {e}")
            return f"[Error VLM: {e}]"

    async def _generate_anthropic_vision(self, prompt, images, system, max_tokens, temperature) -> str:
        """Genera con Claude vision API."""
        try:
            import aiohttp

            content = [{"type": "text", "text": prompt}]
            for img_bytes in images:
                b64 = base64.b64encode(img_bytes).decode()
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}
                })

            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": content}],
            }
            if system:
                payload["system"] = system

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["content"][0]["text"]
                    else:
                        error = await resp.text()
                        logger.error(f"Anthropic VLM error: {resp.status} - {error}")
                        return f"[Error VLM: {resp.status}]"
        except Exception as e:
            logger.error(f"Anthropic VLM error: {e}")
            return f"[Error VLM: {e}]"

    async def _generate_ollama_vision(self, prompt, images, system, max_tokens, temperature) -> str:
        """Genera con LLaVA vía Ollama (local, gratis)."""
        try:
            import aiohttp

            # Ollama soporta imágenes en base64
            images_b64 = [base64.b64encode(img).decode() for img in images]

            payload = {
                "model": self.model or "llava:7b",
                "prompt": prompt,
                "images": images_b64,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            if system:
                payload["system"] = system

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "")
                    else:
                        return f"[Error Ollama VLM: {resp.status}]"
        except Exception as e:
            logger.error(f"Ollama VLM error: {e}")
            return f"[Error Ollama VLM: {e}. ¿Está LLaVA instalado? ollama pull llava:7b]"

    async def health_check(self) -> bool:
        """Verifica si el VLM está disponible."""
        try:
            response = await self.generate("test", images=None, max_tokens=5)
            return not response.startswith("[Error")
        except Exception:
            return False


# ============================================================
# 2. VisionSense — sentido que procesa imágenes
# ============================================================

from .senses import Sense
from ..core.cognitive_loop import Observation


class VisionSense(Sense):
    """
    Sentido que procesa imágenes recibidas del usuario.

    Cuando el usuario envía una imagen (vía Dashboard, Telegram, o API),
    VisionSense la procesa con el VLM y genera una Observation con la
    descripción de lo que ve.

    El bucle cognitivo no sabe que es una imagen — solo ve una Observation
    con texto descriptivo. El Speaker puede entonces responder sobre la
    imagen como si fuera una observación textual.

    Uso:
        sense = VisionSense(vlm=VLMPeripheral(backend="openai_compatible"))
        # Cuando llega una imagen:
        sense.inject_image(image_bytes, user_prompt="¿Qué ves en esta imagen?")
        # En el siguiente tick, el bucle la procesará
    """

    def __init__(self, vlm: VLMPeripheral = None):
        self._vlm = vlm
        self._pending_images: List[Dict[str, Any]] = []
        self._observations_generated = 0

    @property
    def name(self) -> str:
        return "vision"

    def inject_image(self, image_bytes: bytes, user_prompt: str = "Describe esta imagen"):
        """Inyecta una imagen para procesar en el próximo tick."""
        self._pending_images.append({
            "image": image_bytes,
            "prompt": user_prompt,
            "timestamp": time.time(),
        })

    async def observe(self) -> List[Observation]:
        """Procesa imágenes pendientes y genera observaciones."""
        if not self._pending_images or not self._vlm:
            return []

        observations = []
        while self._pending_images:
            item = self._pending_images.pop(0)
            try:
                description = await self._vlm.generate(
                    prompt=item["prompt"],
                    images=[item["image"]],
                    max_tokens=300,
                )
                observations.append(Observation(
                    timestamp=item["timestamp"],
                    source="vision",
                    content=description,
                    metadata={
                        "image_size_bytes": len(item["image"]),
                        "user_prompt": item["prompt"],
                    }
                ))
                self._observations_generated += 1
            except Exception as e:
                logger.error(f"VisionSense error: {e}")
                observations.append(Observation(
                    timestamp=time.time(),
                    source="vision",
                    content=f"[Error procesando imagen: {e}]",
                    metadata={"error": str(e)},
                ))

        return observations

    def get_stats(self) -> Dict[str, Any]:
        return {
            "observations_generated": self._observations_generated,
            "pending_images": len(self._pending_images),
            "vlm_available": self._vlm is not None,
        }


# ============================================================
# 3. VoiceInputSense — sentido que transcribe audio (STT)
# ============================================================

class VoiceInputSense(Sense):
    """
    Sentido que captura audio del micrófono y lo transcribe a texto.

    Usa Whisper (openai/whisper o whisper.cpp) para Speech-to-Text.
    Whisper es local, gratis, y soporta 99 idiomas.

    Si whisper no está instalado, el sentido no falla — simplemente no
    genera observaciones. Esto mantiene backward compatibility.

    Uso:
        sense = VoiceInputSense(engine="whisper", model="base")
        # Capturar audio del micrófono
        await sense.start_listening(duration=5.0)
        # O inyectar audio manualmente
        sense.inject_audio(audio_bytes, format="wav")
    """

    def __init__(self, engine: str = "whisper", model: str = "base"):
        self._engine = engine
        self._model = model
        self._whisper = None
        self._pending_audio: List[Dict[str, Any]] = []
        self._transcriptions_generated = 0
        self._listening = False

    @property
    def name(self) -> str:
        return "voice_input"

    def _load_whisper(self):
        """Carga Whisper perezosamente (solo cuando se necesita)."""
        if self._whisper is not None:
            return self._whisper

        try:
            import whisper
            self._whisper = whisper.load_model(self._model)
            logger.info(f"VoiceInputSense: Whisper model '{self._model}' loaded")
            return self._whisper
        except ImportError:
            logger.warning(
                "VoiceInputSense: whisper no instalado. "
                "Instalar con: pip install openai-whisper"
            )
            return None
        except Exception as e:
            logger.error(f"VoiceInputSense: error loading whisper: {e}")
            return None

    def inject_audio(self, audio_bytes: bytes, format: str = "wav",
                     language: str = None):
        """Inyecta audio para transcribir en el próximo tick."""
        self._pending_audio.append({
            "audio": audio_bytes,
            "format": format,
            "language": language,
            "timestamp": time.time(),
        })

    async def start_listening(self, duration: float = 5.0, sample_rate: int = 16000):
        """Captura audio del micrófono durante N segundos."""
        try:
            import numpy as np
            import sounddevice as sd

            self._listening = True
            logger.info(f"VoiceInputSense: listening for {duration}s...")

            # Capturar en hilo separado para no bloquear el bucle
            recording = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sd.rec(int(duration * sample_rate), 
                              samplerate=sample_rate, channels=1, dtype='float32')
            )
            await asyncio.sleep(duration)
            self._listening = False

            # Convertir a bytes WAV
            import io
            import wave
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes((recording * 32767).astype(np.int16).tobytes())

            self.inject_audio(wav_buffer.getvalue(), format="wav")
            logger.info("VoiceInputSense: audio captured")

        except ImportError:
            logger.warning(
                "VoiceInputSense: sounddevice/numpy no instalado. "
                "Instalar con: pip install sounddevice numpy"
            )
        except Exception as e:
            logger.error(f"VoiceInputSense: recording error: {e}")

    async def observe(self) -> List[Observation]:
        """Transcribe audio pendiente y genera observaciones."""
        if not self._pending_audio:
            return []

        whisper = self._load_whisper()
        if whisper is None:
            # Whisper no disponible, limpiar cola
            self._pending_audio.clear()
            return []

        observations = []
        while self._pending_audio:
            item = self._pending_audio.pop(0)
            try:
                # Transcribir con Whisper
                import io
                import tempfile

                # Whisper necesita un archivo, no bytes
                with tempfile.NamedTemporaryFile(suffix=f".{item['format']}", delete=False) as f:
                    f.write(item["audio"])
                    temp_path = f.name

                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: whisper.transcribe(temp_path, language=item.get("language"))
                )

                os.unlink(temp_path)  # limpiar temp

                text = result.get("text", "").strip()
                if text:
                    observations.append(Observation(
                        timestamp=item["timestamp"],
                        source="voice_input",
                        content=text,
                        metadata={
                            "language": result.get("language", "unknown"),
                            "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0,
                            "transcription_engine": "whisper",
                        }
                    ))
                    self._transcriptions_generated += 1

            except Exception as e:
                logger.error(f"VoiceInputSense: transcription error: {e}")

        return observations

    def get_stats(self) -> Dict[str, Any]:
        return {
            "transcriptions_generated": self._transcriptions_generated,
            "pending_audio": len(self._pending_audio),
            "listening": self._listening,
            "whisper_available": self._whisper is not None,
            "engine": self._engine,
            "model": self._model,
        }


# ============================================================
# 4. VoiceActuator — actuador que genera voz (TTS)
# ============================================================

from .actuators import Actuator, ActionResult


class VoiceActuator(Actuator):
    """
    Actuador que genera voz desde texto (Text-to-Speech).

    Usa Piper TTS (local, gratis, natural, multilingüe).
    Si piper no está instalado, no falla — simplemente no reproduce audio.

    Uso:
        actuator = VoiceActuator(engine="piper", voice="es_ES-davefx-medium")
        await actuator.execute(Action(type="voice", payload="Hola, soy ZOE"))
    """

    def __init__(self, engine: str = "piper", voice: str = "es_ES-davefx-medium",
                 models_dir: str = None):
        self._engine = engine
        self._voice = voice
        self._models_dir = models_dir or os.path.expanduser("~/.local/share/piper")
        self._piper = None
        self._utterances_generated = 0

    @property
    def name(self) -> str:
        return "voice"

    def _load_piper(self):
        """Carga Piper perezosamente."""
        if self._piper is not None:
            return self._piper

        try:
            # Piper se ejecuta como comando externo
            import shutil
            if shutil.which("piper"):
                self._piper = True
                return self._piper
            else:
                logger.warning(
                    "VoiceActuator: piper no instalado. "
                    "Instalar desde https://github.com/rhasspy/piper"
                )
                return None
        except Exception as e:
            logger.error(f"VoiceActuator: error loading piper: {e}")
            return None

    async def execute(self, action: Dict[str, Any], 
                      llm_peripheral: Any = None,
                      context: Dict[str, Any] = None) -> ActionResult:
        """Genera voz desde texto."""
        text = action.get("payload", action.get("text", ""))
        if isinstance(text, dict):
            text = str(text)

        if not text:
            return ActionResult(success=False, error="Empty text")

        piper = self._load_piper()
        if piper is None:
            # Piper no disponible — no fallar, solo log
            logger.info(f"VoiceActuator: [piper no disponible] Texto: {text[:50]}...")
            return ActionResult(success=True, output={"text": text, "audio": None})

        try:
            import subprocess
            import tempfile

            # Generar audio con piper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_path = f.name

            process = await asyncio.create_subprocess_exec(
                "piper",
                "--model", self._voice,
                "--output_file", output_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate(text.encode())

            if process.returncode == 0:
                # Leer audio generado
                with open(output_path, 'rb') as f:
                    audio_bytes = f.read()
                os.unlink(output_path)

                self._utterances_generated += 1

                # Reproducir (en hilo separado para no bloquear)
                await self._play_audio(audio_bytes)

                return ActionResult(
                    success=True,
                    output={"text": text, "audio_size": len(audio_bytes)}
                )
            else:
                logger.error(f"VoiceActuator: piper error: {stderr.decode()}")
                return ActionResult(success=False, error=stderr.decode())

        except Exception as e:
            logger.error(f"VoiceActuator: error: {e}")
            return ActionResult(success=False, error=str(e))

    async def _play_audio(self, audio_bytes: bytes):
        """Reproduce audio (no bloqueante)."""
        try:
            import tempfile
            import subprocess

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name

            # Reproducir con ffplay (parte de ffmpeg, disponible en la mayoría de sistemas)
            process = await asyncio.create_subprocess_exec(
                "ffplay", "-nodisp", "-autoexit", temp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.wait()
            os.unlink(temp_path)

        except FileNotFoundError:
            # ffplay no disponible, intentar afplay (macOS) o aplay (Linux)
            try:
                player = "afplay" if os.uname().sysname == "Darwin" else "aplay"
                process = await asyncio.create_subprocess_exec(
                    player, temp_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await process.wait()
                os.unlink(temp_path)
            except (OSError, subprocess.SubprocessError):
                logger.warning("VoiceActuator: no audio player available")
        except Exception as e:
            logger.warning(f"VoiceActuator: playback error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "utterances_generated": self._utterances_generated,
            "engine": self._engine,
            "voice": self._voice,
            "piper_available": self._piper is not None,
        }
