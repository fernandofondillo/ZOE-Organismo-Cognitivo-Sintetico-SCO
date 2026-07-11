"""
ZOE V1.7 — Telegram Bot Bridge (Sprint 1.4)

Puente entre Telegram y ZOE. Permite usar ZOE desde el móvil sin necesidad
de app nativa. Telegram está en todos los móviles y soporta texto, voz
(telegram transcribe) e imágenes.

Sin deconstruir: este módulo es un peripheral adicional. No modifica
el bucle cognitivo ni el CLI ni el Dashboard. Usa la misma API REST
que el Dashboard, o puede conectarse directamente al ZoeChat.

Uso:
    # Requiere python-telegram-bot
    pip install python-telegram-bot

    # Ejecutar
    python -m zoe.peripherals.telegram_bridge --token TU_BOT_TOKEN

    # O con ZOE corriendo en VPS
    python -m zoe.peripherals.telegram_bridge --token TU_BOT_TOKEN --zoe-url http://localhost:8642
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TelegramBridge:
    """
    Puente entre Telegram y ZOE.

    Recibe mensajes de Telegram, los envía a ZOE (vía API REST o directo),
    y responde por Telegram.

    Modos de conexión:
    1. API REST: ZOE corre en un VPS con Dashboard activo. TelegramBridge
       envía peticiones a http://localhost:8642/chat
    2. Directo: TelegramBridge crea un ZoeChat directamente (sin Dashboard)

    El modo API REST es recomendado para producción (ZOE corre como servicio).
    El modo directo es útil para testing y desarrollo.
    """

    def __init__(
        self,
        bot_token: str,
        zoe_url: str = "http://localhost:8642",
        mode: str = "api",
        allowed_user_ids: list = None,
    ):
        """
        Args:
            bot_token: token del bot de Telegram (from @BotFather)
            zoe_url: URL del Dashboard de ZOE (modo api)
            mode: "api" (via REST) o "direct" (ZoeChat directo)
            allowed_user_ids: lista de IDs de usuarios permitidos (None = todos)
        """
        self.bot_token = bot_token
        self.zoe_url = zoe_url.rstrip("/")
        self.mode = mode
        self.allowed_user_ids = allowed_user_ids or []
        self._chat = None  # ZoeChat instance (modo direct)
        self._application = None
        self._user_languages: Dict[int, str] = {}  # user_id → language

    async def initialize(self):
        """Inicializa el bridge."""
        try:
            from telegram import Application
        except ImportError:
            raise ImportError(
                "python-telegram-bot no instalado. Instalar con: pip install python-telegram-bot"
            )

        if self.mode == "direct":
            from ..cli_chat import ZoeChat
            self._chat = ZoeChat(backend="ollama", model="qwen2.5:3b")
            await self._chat.initialize()
            logger.info("TelegramBridge: ZoeChat initialized (direct mode)")

        self._application = (
            Application.builder()
            .token(self.bot_token)
            .build()
        )

        # Registrar handlers
        from telegram import Update
        from telegram.ext import CommandHandler, MessageHandler, filters

        self._application.add_handler(CommandHandler("start", self._handle_start))
        self._application.add_handler(CommandHandler("help", self._handle_help))
        self._application.add_handler(CommandHandler("stats", self._handle_stats))
        self._application.add_handler(CommandHandler("sleep", self._handle_sleep))
        self._application.add_handler(CommandHandler("wake", self._handle_wake))
        self._application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )
        self._application.add_handler(
            MessageHandler(filters.VOICE, self._handle_voice)
        )
        self._application.add_handler(
            MessageHandler(filters.PHOTO, self._handle_photo)
        )

        logger.info("TelegramBridge: initialized")

    async def _handle_start(self, update, context):
        """Comando /start."""
        user_id = update.effective_user.id
        if not self._is_allowed(user_id):
            await update.message.reply_text("No estás autorizado para usar este ZOE.")
            return

        await update.message.reply_text(
            "Hola. Soy ZOE, un organismo cognitivo sintético. "
            "Puedes escribirme directamente. "
            "Comandos: /help, /stats, /sleep, /wake"
        )

    async def _handle_help(self, update, context):
        """Comando /help."""
        help_text = (
            "ZOE — Synthetic Cognitive Organism\n\n"
            "Comandos:\n"
            "/start — Iniciar conversación\n"
            "/help — Esta ayuda\n"
            "/stats — Estadísticas del organismo\n"
            "/sleep — Forzar modo SLEEPING\n"
            "/wake — Forzar modo AWAKE\n\n"
            "Simplemente escribe un mensaje para hablar con ZOE."
        )
        await update.message.reply_text(help_text)

    async def _handle_stats(self, update, context):
        """Comando /stats."""
        user_id = update.effective_user.id
        if not self._is_allowed(user_id):
            return

        if self.mode == "api":
            stats = await self._get_stats_api()
        else:
            stats = self._chat.get_stats()

        if isinstance(stats, dict):
            text = f"ZOE Stats:\n"
            text += f"  Iterations: {stats.get('iteration_count', 'N/A')}\n"
            text += f"  State: {stats.get('metabolic_state', 'N/A')}\n"
            text += f"  Energy: {stats.get('energy', 'N/A')}\n"
            text += f"  Memory entries: {stats.get('memory_count', 'N/A')}\n"
        else:
            text = f"Stats: {stats}"

        await update.message.reply_text(text)

    async def _handle_sleep(self, update, context):
        """Comando /sleep."""
        if self.mode == "api":
            import aiohttp
            async with aiohttp.ClientSession() as session:
                await session.post(f"{self.zoe_url}/sleep")
        else:
            self._chat.metabolism.internal_state.fatigue = 0.9
            self._chat.metabolism.tick(dt=1.0)
        await update.message.reply_text("ZOE is now sleeping. /wake to wake up.")

    async def _handle_wake(self, update, context):
        """Comando /wake."""
        if self.mode == "api":
            import aiohttp
            async with aiohttp.ClientSession() as session:
                await session.post(f"{self.zoe_url}/wake")
        else:
            self._chat.metabolism.internal_state.fatigue = 0.0
            self._chat.metabolism.internal_state.energy = 1.0
            from ..metabolism.metabolism import MetabolicState
            self._chat.metabolism.state = MetabolicState.AWAKE
        await update.message.reply_text("ZOE is awake.")

    async def _handle_message(self, update, context):
        """Maneja mensaje de texto."""
        user_id = update.effective_user.id
        if not self._is_allowed(user_id):
            return

        text = update.message.text
        user_name = update.effective_user.first_name or "Usuario"

        logger.info(f"TelegramBridge: message from {user_name} ({user_id}): {text[:50]}...")

        # Enviar "typing" indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing",
        )

        # Obtener respuesta de ZOE
        if self.mode == "api":
            response = await self._send_to_zoe_api(text)
        else:
            response = await self._send_to_zoe_direct(text)

        # Responder por Telegram
        if response:
            # Telegram tiene límite de 4096 caracteres por mensaje
            if len(response) > 4000:
                # Split en chunks
                for i in range(0, len(response), 4000):
                    await update.message.reply_text(response[i:i+4000])
            else:
                await update.message.reply_text(response)
        else:
            await update.message.reply_text("Lo siento, no pude procesar tu mensaje.")

    async def _handle_voice(self, update, context):
        """Maneja mensaje de voz (Telegram transcribe automáticamente)."""
        user_id = update.effective_user.id
        if not self._is_allowed(user_id):
            return

        # Telegram puede transcribir voz si está habilitado
        # Si no, descargar y transcribir con Whisper (en roadmap Sprint 2)
        await update.message.reply_text(
            "He recibido tu mensaje de voz. "
            "El procesamiento de voz estará disponible pronto."
        )

    async def _handle_photo(self, update, context):
        """Maneja foto (multi-modal en roadmap Sprint 2)."""
        user_id = update.effective_user.id
        if not self._is_allowed(user_id):
            return

        await update.message.reply_text(
            "He recibido tu imagen. "
            "El procesamiento de imágenes estará disponible pronto."
        )

    def _is_allowed(self, user_id: int) -> bool:
        """Verifica si el usuario está autorizado."""
        if not self.allowed_user_ids:
            return True  # sin restricciones
        return user_id in self.allowed_user_ids

    async def _send_to_zoe_api(self, text: str) -> Optional[str]:
        """Envía mensaje a ZOE vía API REST."""
        try:
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
                    else:
                        logger.error(f"API error: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Error sending to ZOE API: {e}")
            return None

    async def _send_to_zoe_direct(self, text: str) -> Optional[str]:
        """Envía mensaje a ZOE directamente (sin API)."""
        try:
            response = await self._chat.send_message_acd(text)
            return response
        except Exception as e:
            logger.error(f"Error in direct chat: {e}")
            return None

    async def _get_stats_api(self) -> dict:
        """Obtiene stats vía API REST."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.zoe_url}/stats") as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
        return {}

    async def run(self):
        """Inicia el bot de Telegram."""
        if not self._application:
            await self.initialize()

        logger.info("TelegramBridge: starting bot...")
        await self._application.initialize()
        await self._application.start()
        await self._application.updater.start_polling()

        # Mantener corriendo
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("TelegramBridge: stopping...")
            await self._application.updater.stop()
            await self._application.stop()
            await self._application.shutdown()

    def get_stats(self) -> Dict[str, Any]:
        """Stats del bridge."""
        return {
            "mode": self.mode,
            "zoe_url": self.zoe_url,
            "allowed_users": len(self.allowed_user_ids),
            "running": self._application is not None,
        }


def main():
    """Entry point para telegram_bridge."""
    parser = argparse.ArgumentParser(description="ZOE Telegram Bot Bridge")
    parser.add_argument("--token", required=True, help="Telegram bot token (from @BotFather)")
    parser.add_argument("--zoe-url", default="http://localhost:8642",
                       help="URL del Dashboard de ZOE (modo api)")
    parser.add_argument("--mode", default="api", choices=["api", "direct"],
                       help="Modo de conexión: api (REST) o direct (ZoeChat)")
    parser.add_argument("--allowed-ids", type=str, default=None,
                       help="IDs de usuarios permitidos (comma-separated)")
    parser.add_argument("--log-level", default="INFO",
                       help="Nivel de logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    allowed_ids = []
    if args.allowed_ids:
        allowed_ids = [int(x.strip()) for x in args.allowed_ids.split(",")]

    bridge = TelegramBridge(
        bot_token=args.token,
        zoe_url=args.zoe_url,
        mode=args.mode,
        allowed_user_ids=allowed_ids,
    )

    asyncio.run(bridge.run())


if __name__ == "__main__":
    main()
