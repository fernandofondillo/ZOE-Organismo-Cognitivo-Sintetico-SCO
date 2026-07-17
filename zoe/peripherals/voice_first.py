"""
ZOE V1.7 — Voice-First Mode (Sprint 4)

Conversación natural por voz, tipo "Her". ZOE escucha continuamente,
responde por voz, puede ser interrumpida, y mantiene el flujo conversacional.

Componentes:
1. VoiceFirstMode — orquesta el bucle continuo de voz
2. WakeWordDetector — detecta "Hey ZOE" para activar (openWakeWord)
3. VoiceActivityDetector — detecta cuando el usuario habla/termina (VAD)
4. InterruptionHandler — maneja interrupciones durante la respuesta

Sin deconstruir: VoiceFirstMode usa VoiceInputSense (STT) y VoiceActuator (TTS)
del Sprint 2. No modifica el bucle cognitivo, ni el CLI, ni el Dashboard.

Dependencias opcionales:
- Whisper STT (pip install openai-whisper) — transcripción
- Piper TTS (https://github.com/rhasspy/piper) — síntesis de voz
- openWakeWord (pip install openwakeword) — detección de wake word
- sounddevice + numpy (pip install sounddevice numpy) — captura de audio
- webrtcvad (pip install webrtcvad) — Voice Activity Detection

Si alguna no está instalada, VoiceFirstMode no falla — informa al usuario
qué falta y cómo instalarlo.

Uso:
    from zoe.peripherals.voice_first import VoiceFirstMode
    
    mode = VoiceFirstMode(
        zoe_chat=chat,
        wake_word="hey zoe",
        stt_engine="whisper",
        tts_engine="piper",
        voice="es_ES-davefx-medium",
    )
    await mode.run()
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import wave
import io
import tempfile
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, AsyncIterator

logger = logging.getLogger(__name__)


class VoiceState(str, Enum):
    """Estados del Voice-first mode."""
    IDLE = "idle"                    # Esperando wake word
    LISTENING = "listening"          # Usuario está hablando
    PROCESSING = "processing"        # ZOE está pensando
    SPEAKING = "speaking"            # ZOE está hablando
    INTERRUPTED = "interrupted"      # Usuario interrumpió a ZOE


@dataclass
class VoiceConfig:
    """Configuración del Voice-first mode."""
    wake_word: str = "hey zoe"
    wake_word_sensitivity: float = 0.5  # 0-1, menor = más sensible
    vad_aggressiveness: int = 3  # 0-3, mayor = más agresivo
    silence_duration: float = 1.5  # segundos de silencio para terminar
    max_recording_duration: float = 30.0  # máximo por turno
    sample_rate: int = 16000
    stt_model: str = "base"  # whisper model: tiny, base, small, medium, large
    tts_voice: str = "es_ES-davefx-medium"
    tts_speed: float = 1.0
    enable_interruption: bool = True
    min_response_delay: float = 0.3  # delay antes de empezar a hablar
    cooldown_after_speaking: float = 0.5  # no escuchar durante X seg después de hablar


class WakeWordDetector:
    """
    Detecta la wake word "Hey ZOE" para activar la escucha.
    
    Usa openWakeWord si está instalado. Si no, usa un detector simple
    basado en energía + silencio (cualquier sonido fuerte activa).
    """

    def __init__(self, wake_word: str = "hey zoe", sensitivity: float = 0.5):
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self._model = None
        self._available = False

    def initialize(self) -> bool:
        """Inicializa el detector. Returns True si está disponible."""
        try:
            import openwakeword
            openwakeword.download_models()
            self._model = openwakeword.Model()
            self._available = True
            logger.info(f"WakeWordDetector: openWakeWord initialized (wake word: '{self.wake_word}')")
            return True
        except ImportError:
            logger.warning(
                "WakeWordDetector: openwakeword no instalado. "
                "Instalar con: pip install openwakeword. "
                "Fallback: detección por energía."
            )
            self._available = False
            return False
        except Exception as e:
            logger.error(f"WakeWordDetector: init error: {e}")
            self._available = False
            return False

    def detect(self, audio_frames: bytes) -> bool:
        """
        Detecta wake word en audio frames.
        
        Args:
            audio_frames: 16-bit PCM audio at 16kHz
            
        Returns:
            True si se detectó la wake word
        """
        if self._available and self._model:
            try:
                import numpy as np
                audio = np.frombuffer(audio_frames, dtype=np.int16)
                predictions = self._model.predict(audio)
                
                # Buscar wake word en predicciones
                for name, score in predictions.items():
                    if self.wake_word in name.lower() or "hey_zoe" in name.lower():
                        if score >= self.sensitivity:
                            return True
                return False
            except Exception as e:
                logger.debug(f"Wake word detection error: {e}")
                return False
        else:
            # Fallback: detección por energía
            import numpy as np
            audio = np.frombuffer(audio_frames, dtype=np.int16)
            energy = np.abs(audio).mean()
            # Umbral: si energía > 1000, considerar como activación
            return bool(energy > 1000)

    @property
    def available(self) -> bool:
        return self._available


class VoiceActivityDetector:
    """
    Detecta Voice Activity (cuándo el usuario está hablando y cuándo para).
    
    Usa webrtcvad si está instalado. Si no, usa detección por energía simple.
    """

    def __init__(self, aggressiveness: int = 3, silence_duration: float = 1.5):
        self.aggressiveness = aggressiveness
        self.silence_duration = silence_duration
        self._vad = None
        self._available = False

    def initialize(self) -> bool:
        """Inicializa VAD."""
        try:
            import webrtcvad
            self._vad = webrtcvad.Vad(self.aggressiveness)
            self._available = True
            logger.info(f"VoiceActivityDetector: webrtcvad initialized (aggressiveness: {self.aggressiveness})")
            return True
        except ImportError:
            logger.warning(
                "VoiceActivityDetector: webrtcvad no instalado. "
                "Instalar con: pip install webrtcvad. "
                "Fallback: detección por energía."
            )
            self._available = False
            return False
        except Exception as e:
            logger.error(f"VoiceActivityDetector: init error: {e}")
            self._available = False
            return False

    def is_speech(self, audio_frame: bytes, sample_rate: int = 16000) -> bool:
        """Detecta si un frame de audio contiene voz."""
        if self._available and self._vad:
            try:
                return bool(self._vad.is_speech(audio_frame, sample_rate))
            except Exception:
                return False
        else:
            # Fallback: energía
            import numpy as np
            audio = np.frombuffer(audio_frame, dtype=np.int16)
            energy = np.abs(audio).mean()
            return bool(energy > 500)

    @property
    def available(self) -> bool:
        return self._available


class InterruptionHandler:
    """
    Maneja interrupciones del usuario durante la respuesta de ZOE.
    
    Si ZOE está hablando y el usuario empieza a hablar, detecta la
    interrupción y detiene la respuesta de ZOE.
    """

    def __init__(self, vad: VoiceActivityDetector, enabled: bool = True):
        self.vad = vad
        self.enabled = enabled
        self._monitoring = False
        self._interrupted = False

    def start_monitoring(self):
        """Empieza a monitorear interrupciones."""
        self._monitoring = True
        self._interrupted = False

    def stop_monitoring(self):
        """Detiene el monitoreo."""
        self._monitoring = False

    def check_interruption(self, audio_frame: bytes) -> bool:
        """Verifica si hay interrupción. Returns True si el usuario interrumpió."""
        if not self.enabled or not self._monitoring:
            return False
        
        if self.vad.is_speech(audio_frame):
            self._interrupted = True
            return True
        return False

    @property
    def was_interrupted(self) -> bool:
        return self._interrupted

    def reset(self):
        self._interrupted = False


class VoiceFirstMode:
    """
    Modo conversación natural por voz.
    
    Bucle continuo:
    1. Escuchar wake word ("Hey ZOE")
    2. Cuando se detecta, empezar a grabar
    3. Detectar silencio (fin del habla del usuario)
    4. Transcribir con Whisper STT
    5. Procesar con ZOE (bucle cognitivo normal)
    6. Sintetizar respuesta con Piper TTS
    7. Reproducir respuesta (con detección de interrupción)
    8. Volver al paso 1
    
    Si no hay wake word detector, funciona en modo "push to talk":
    el usuario pulsa Enter para hablar.
    
    Sin deconstruir: usa VoiceInputSense y VoiceActuator del Sprint 2.
    No modifica el bucle cognitivo.
    """

    def __init__(
        self,
        zoe_chat=None,
        zoe_url: str = "http://localhost:8642",
        config: VoiceConfig = None,
        mode: str = "auto",  # "auto", "wake_word", "push_to_talk"
    ):
        self.zoe_chat = zoe_chat
        self.zoe_url = zoe_url.rstrip("/")
        self.config = config or VoiceConfig()
        self.mode = mode
        
        self.state = VoiceState.IDLE
        self._wake_detector = WakeWordDetector(
            wake_word=self.config.wake_word,
            sensitivity=self.config.wake_word_sensitivity,
        )
        self._vad = VoiceActivityDetector(
            aggressiveness=self.config.vad_aggressiveness,
            silence_duration=self.config.silence_duration,
        )
        self._interruption = InterruptionHandler(
            vad=self._vad,
            enabled=self.config.enable_interruption,
        )
        
        self._whisper = None
        self._running = False
        self._turns = 0
        self._total_audio_recorded = 0.0  # seconds
        self._total_processing_time = 0.0  # seconds

    async def initialize(self) -> Dict[str, bool]:
        """Inicializa todos los componentes. Returns dict de disponibilidad."""
        availability = {
            "wake_word": self._wake_detector.initialize(),
            "vad": self._vad.initialize(),
            "whisper": await self._init_whisper(),
            "piper": self._check_piper(),
        }

        # Decidir modo
        if self.mode == "auto":
            if availability["wake_word"]:
                self.mode = "wake_word"
            else:
                self.mode = "push_to_talk"

        logger.info(f"VoiceFirstMode: initialized (mode: {self.mode})")
        logger.info(f"  wake_word: {availability['wake_word']}")
        logger.info(f"  vad: {availability['vad']}")
        logger.info(f"  whisper: {availability['whisper']}")
        logger.info(f"  piper: {availability['piper']}")

        return availability

    async def _init_whisper(self) -> bool:
        """Inicializa Whisper STT."""
        try:
            import whisper
            self._whisper = whisper.load_model(self.config.stt_model)
            logger.info(f"VoiceFirstMode: Whisper '{self.config.stt_model}' loaded")
            return True
        except ImportError:
            logger.warning("VoiceFirstMode: whisper no instalado. pip install openai-whisper")
            return False
        except Exception as e:
            logger.error(f"VoiceFirstMode: Whisper init error: {e}")
            return False

    def _check_piper(self) -> bool:
        """Verifica si Piper TTS está disponible."""
        import shutil
        return shutil.which("piper") is not None

    async def run(self):
        """Ejecuta el bucle de voice-first mode."""
        if not self._whisper:
            print("❌ Whisper STT no disponible. Instalar con: pip install openai-whisper")
            return

        self._running = True
        print(self._get_banner())

        try:
            if self.mode == "wake_word":
                await self._run_wake_word_loop()
            else:
                await self._run_push_to_talk_loop()
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n\nVoice-first mode stopped.")
        finally:
            self._running = False

    async def _run_wake_word_loop(self):
        """Bucle con detección de wake word continuo."""
        import sounddevice as sd
        import numpy as np

        print(f"👂 Listening for '{self.config.wake_word}'... (Ctrl+C to stop)")

        frame_duration = 30  # ms per frame
        frame_size = int(self.config.sample_rate * frame_duration / 1000)

        while self._running:
            self.state = VoiceState.IDLE

            # Capturar frames y detectar wake word
            recording = await self._capture_audio(frame_size, detect_wake=True)

            if recording is None:
                continue  # no wake word detected in this cycle

            # Wake word detectada! Grabar utterance
            print("🎤 ZOE is listening...")
            self.state = VoiceState.LISTENING

            audio_data = await self._record_until_silence()

            if audio_data is None or len(audio_data) == 0:
                print("  (no speech detected)")
                continue

            # Transcribir
            print("📝 Transcribing...")
            self.state = VoiceState.PROCESSING
            text = await self._transcribe(audio_data)

            if not text or len(text.strip()) < 2:
                print("  (couldn't understand)")
                continue

            print(f"  User: {text}")

            # Procesar con ZOE
            processing_start = time.time()
            response = await self._process_with_zoe(text)
            self._total_processing_time += time.time() - processing_start

            if not response:
                continue

            print(f"  ZOE: {response[:100]}...")

            # Sintetizar y reproducir
            self.state = VoiceState.SPEAKING
            await self._speak(response)

            # Cooldown
            await asyncio.sleep(self.config.cooldown_after_speaking)
            self._turns += 1

    async def _run_push_to_talk_loop(self):
        """Bucle push-to-talk (sin wake word)."""
        print("🔊 Push-to-talk mode. Press Enter to speak, Ctrl+C to stop.")

        while self._running:
            self.state = VoiceState.IDLE
            
            # Esperar Enter
            await asyncio.get_event_loop().run_in_executor(None, input)

            # Grabar
            print("🎤 Listening... (speak now)")
            self.state = VoiceState.LISTENING

            audio_data = await self._record_until_silence()

            if audio_data is None or len(audio_data) == 0:
                print("  (no speech detected)")
                continue

            # Transcribir
            print("📝 Transcribing...")
            self.state = VoiceState.PROCESSING
            text = await self._transcribe(audio_data)

            if not text or len(text.strip()) < 2:
                print("  (couldn't understand)")
                continue

            print(f"  User: {text}")

            # Procesar con ZOE
            response = await self._process_with_zoe(text)

            if not response:
                continue

            print(f"  ZOE: {response[:100]}...")

            # Sintetizar y reproducir
            self.state = VoiceState.SPEAKING
            await self._speak(response)

            self._turns += 1
            print("\n🔊 Press Enter to speak again...")

    async def _capture_audio(self, frame_size: int, detect_wake: bool = False) -> Optional[bytes]:
        """Captura audio para detección de wake word."""
        try:
            import sounddevice as sd
            import numpy as np

            audio = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sd.rec(frame_size, samplerate=self.config.sample_rate,
                              channels=1, dtype='int16')
            )
            await asyncio.sleep(frame_size / 1000.0)  # frame_duration

            audio_bytes = audio.tobytes()

            if detect_wake:
                if self._wake_detector.detect(audio_bytes):
                    return audio_bytes
                return None

            return audio_bytes
        except ImportError:
            logger.error("sounddevice not installed. pip install sounddevice")
            return None
        except Exception as e:
            logger.error(f"Audio capture error: {e}")
            return None

    async def _record_until_silence(self) -> Optional[bytes]:
        """Graba audio hasta detectar silencio."""
        try:
            import sounddevice as sd
            import numpy as np

            frame_duration = 30  # ms
            frame_size = int(self.config.sample_rate * frame_duration / 1000)
            
            recording = []
            silence_start = None
            recording_start = time.time()

            while self._running:
                # Capturar frame
                frame = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: sd.rec(frame_size, samplerate=self.config.sample_rate,
                                  channels=1, dtype='int16')
                )
                await asyncio.sleep(frame_duration / 1000.0)
                
                frame_bytes = frame.tobytes()
                recording.append(frame)

                # Detectar silencio
                is_speech = self._vad.is_speech(frame_bytes, self.config.sample_rate)
                
                if is_speech:
                    silence_start = None
                else:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= self.config.silence_duration:
                        # Silencio suficiente, terminar grabación
                        break

                # Timeout
                if time.time() - recording_start > self.config.max_recording_duration:
                    break

            if not recording:
                return None

            audio_data = np.concatenate(recording)
            self._total_audio_recorded += len(audio_data) / self.config.sample_rate
            return audio_data.tobytes()

        except ImportError:
            logger.error("sounddevice not installed")
            return None
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return None

    async def _transcribe(self, audio_bytes: bytes) -> Optional[str]:
        """Transcribe audio con Whisper."""
        if not self._whisper:
            return None

        try:
            # Whisper necesita un archivo
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            # Escribir WAV
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.config.sample_rate)
                wf.writeframes(audio_bytes)

            # Transcribir
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._whisper.transcribe(temp_path)
            )

            os.unlink(temp_path)
            return result.get("text", "").strip()

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    async def _process_with_zoe(self, text: str) -> Optional[str]:
        """Procesa texto con ZOE y devuelve respuesta."""
        try:
            if self.zoe_chat:
                # Modo directo
                response = await self.zoe_chat.send_message_acd(text)
                return response
            else:
                # Modo API REST
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.zoe_url}/chat",
                        json={"message": text},
                        timeout=aiohttp.ClientTimeout(total=120),
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("response", "")
                        return None
        except Exception as e:
            logger.error(f"ZOE processing error: {e}")
            return None

    async def _speak(self, text: str):
        """Sintetiza voz y reproduce, con detección de interrupción."""
        if not self._check_piper():
            # Sin Piper, solo imprimir texto
            print(f"  (TTS not available) {text[:200]}")
            return

        try:
            import subprocess
            import tempfile

            # Generar audio con Piper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                output_path = f.name

            process = await asyncio.create_subprocess_exec(
                "piper",
                "--model", self.config.tts_voice,
                "--output_file", output_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            await process.communicate(text.encode())

            if process.returncode != 0:
                logger.error("Piper TTS failed")
                return

            # Leer audio
            with open(output_path, 'rb') as f:
                audio_bytes = f.read()
            os.unlink(output_path)

            # Reproducir (con interrupción)
            await self._play_with_interruption(audio_bytes)

        except FileNotFoundError:
            logger.warning("piper not found")
        except Exception as e:
            logger.error(f"TTS error: {e}")

    async def _play_with_interruption(self, audio_bytes: bytes):
        """Reproduce audio con detección de interrupción."""
        try:
            import tempfile
            import subprocess

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name

            # Determinar player según plataforma
            import platform
            if platform.system() == "Darwin":
                player = "afplay"
            elif platform.system() == "Linux":
                player = "aplay"
            else:
                player = "ffplay"

            process = await asyncio.create_subprocess_exec(
                player, "-q" if player == "ffplay" else "", temp_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            # Monitorear interrupción mientras reproduce
            # Sprint 5.23 F0-6 (BUG-007 fix): corregido typo ``enable_interrupción``
            # (con acento) → ``enable_interruption``. El typo causaba AttributeError
            # silenciada por ``except Exception`` en L694, dejando la feature
            # de interrumpir a ZOE mientras habla completamente muerta.
            if self.config.enable_interruption:
                self._interruption.start_monitoring()
                # Monitorear en paralelo
                monitor_task = asyncio.create_task(self._monitor_during_playback())
                try:
                    await process.wait()
                finally:
                    monitor_task.cancel()
                    self._interruption.stop_monitoring()
                    
                    if self._interruption.was_interrupted:
                        process.kill()
                        await process.wait()
                        self.state = VoiceState.INTERRUPTED
                        print("  (interrupted)")
            else:
                await process.wait()

            os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Playback error: {e}")

    async def _monitor_during_playback(self):
        """Monitorea interrupciones durante la reproducción."""
        try:
            import sounddevice as sd
            frame_size = int(self.config.sample_rate * 0.03)
            
            while self._interruption._monitoring:
                frame = sd.rec(frame_size, samplerate=self.config.sample_rate,
                             channels=1, dtype='int16')
                await asyncio.sleep(0.03)
                
                if self._interruption.check_interruption(frame.tobytes()):
                    break
        except OSError as e:
            logger.debug(f"Sounddevice interruption monitoring error: {e}")

    def _get_banner(self) -> str:
        """Banner de inicio."""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║  ZOE Voice-First Mode                                        ║
╠══════════════════════════════════════════════════════════════╣
║  Mode:       {self.mode:<47}║
║  Wake word:  '{self.config.wake_word}'{" " * (45 - len(self.config.wake_word))}║
║  STT:        Whisper ({self.config.stt_model}){" " * (35 - len(self.config.stt_model))}║
║  TTS:        Piper ({self.config.tts_voice[:20]}){" " * (35 - len(self.config.tts_voice[:20]))}║
║  VAD:        {'webrtcvad' if self._vad.available else 'energy-based'}{" " * (40 if self._vad.available else 34)}║
║  Interrupt:  {'enabled' if self.config.enable_interruption else 'disabled'}{" " * (41 if self.config.enable_interruption else 40)}║
╠══════════════════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                                        ║
╚══════════════════════════════════════════════════════════════╝
"""

    def get_stats(self) -> Dict[str, Any]:
        """Stats del Voice-first mode."""
        return {
            "mode": self.mode,
            "state": self.state.value,
            "turns": self._turns,
            "total_audio_recorded_s": round(self._total_audio_recorded, 1),
            "total_processing_time_s": round(self._total_processing_time, 1),
            "wake_word_available": self._wake_detector.available,
            "vad_available": self._vad.available,
            "whisper_available": self._whisper is not None,
            "piper_available": self._check_piper(),
            "config": {
                "wake_word": self.config.wake_word,
                "stt_model": self.config.stt_model,
                "tts_voice": self.config.tts_voice,
                "enable_interruption": self.config.enable_interruption,
            },
        }

    def stop(self):
        """Detiene el Voice-first mode."""
        self._running = False


def main():
    """Entry point para voice-first mode."""
    import argparse

    parser = argparse.ArgumentParser(description="ZOE Voice-First Mode")
    parser.add_argument("--zoe-url", default="http://localhost:8642",
                       help="URL del Dashboard de ZOE")
    parser.add_argument("--wake-word", default="hey zoe",
                       help="Wake word (default: 'hey zoe')")
    parser.add_argument("--stt-model", default="base",
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size")
    parser.add_argument("--tts-voice", default="es_ES-davefx-medium",
                       help="Piper TTS voice")
    parser.add_argument("--mode", default="auto",
                       choices=["auto", "wake_word", "push_to_talk"],
                       help="Mode: auto, wake_word, or push_to_talk")
    parser.add_argument("--no-interruption", action="store_true",
                       help="Disable interruption during ZOE's response")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                       format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    config = VoiceConfig(
        wake_word=args.wake_word,
        stt_model=args.stt_model,
        tts_voice=args.tts_voice,
        enable_interruption=not args.no_interruption,
    )

    mode = VoiceFirstMode(
        zoe_url=args.zoe_url,
        config=config,
        mode=args.mode,
    )

    asyncio.run(mode.initialize())
    asyncio.run(mode.run())


if __name__ == "__main__":
    main()
