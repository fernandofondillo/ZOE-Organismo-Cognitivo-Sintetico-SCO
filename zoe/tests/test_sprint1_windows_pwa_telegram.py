"""
Tests Sprint 1.2-1.4 — Windows native, PWA, Telegram bridge

Valida detección de Windows, PWA manifest, y estructura del Telegram bridge.
"""

import pytest
import os
import platform
from unittest.mock import patch, MagicMock

from zoe.core.language_detector import LanguageDetector, Language
from zoe.peripherals.telegram_bridge import TelegramBridge


# ============================================================
# 1. Windows detection — ResourceDiscovery
# ============================================================

class TestWindowsResourceDiscovery:

    def test_resource_discovery_imports_on_windows(self):
        """ResourceDiscoverySense se importa sin error (independiente de plataforma)."""
        from zoe.peripherals.resource_discovery import ResourceDiscoverySense
        sense = ResourceDiscoverySense()
        assert sense is not None

    def test_windows_storage_scan_code_exists(self):
        """El código de detección Windows existe en _scan_storage."""
        from zoe.peripherals.resource_discovery import ResourceDiscoverySense
        import inspect
        source = inspect.getsource(ResourceDiscoverySense._scan_storage)
        assert "Windows" in source
        assert "ascii_uppercase" in source

    def test_list_seed_paths_includes_windows(self):
        """list_seed_paths incluye detección Windows."""
        from zoe.core.seed_mode import ZOESeed
        import inspect
        source = inspect.getsource(ZOESeed.list_seed_paths)
        assert "Windows" in source

    def test_detect_seed_volume_includes_windows(self):
        """detect_seed_volume incluye detección Windows."""
        from zoe.core.seed_mode import ZOESeed
        import inspect
        source = inspect.getsource(ZOESeed.detect_seed_volume)
        assert "Windows" in source


# ============================================================
# 2. PWA manifest
# ============================================================

class TestPWAManifest:

    def test_manifest_handler_exists(self):
        """El handler _handle_manifest existe en DashboardServer."""
        from zoe.web_dashboard import DashboardServer
        assert hasattr(DashboardServer, "_handle_manifest")

    def test_manifest_handler_is_coroutine(self):
        """El handler es async."""
        import inspect
        from zoe.web_dashboard import DashboardServer
        assert inspect.iscoroutinefunction(DashboardServer._handle_manifest)

    def test_manifest_route_registered(self):
        """La ruta /manifest.json está registrada."""
        import inspect
        from zoe.web_dashboard import DashboardServer
        source = inspect.getsource(DashboardServer.start)
        assert "/manifest.json" in source

    def test_dashboard_html_has_manifest_link(self):
        """El HTML del dashboard incluye link al manifest."""
        from zoe.web_dashboard import _get_dashboard_html
        html = _get_dashboard_html()
        assert 'manifest.json' in html
        assert 'apple-mobile-web-app-capable' in html
        assert 'theme-color' in html

    def test_dashboard_html_has_responsive_css(self):
        """El HTML del dashboard tiene CSS responsive para móvil."""
        from zoe.web_dashboard import _get_dashboard_html
        html = _get_dashboard_html()
        assert '@media (max-width: 768px)' in html
        assert '@media (max-width: 480px)' in html


# ============================================================
# 3. Telegram bridge
# ============================================================

class TestTelegramBridge:

    def test_telegram_bridge_imports(self):
        """TelegramBridge se importa correctamente."""
        from zoe.peripherals.telegram_bridge import TelegramBridge
        assert TelegramBridge is not None

    def test_telegram_bridge_creation(self):
        """Se puede crear una instancia de TelegramBridge."""
        bridge = TelegramBridge(
            bot_token="test_token",
            zoe_url="http://localhost:8642",
            mode="api",
        )
        assert bridge.bot_token == "test_token"
        assert bridge.mode == "api"
        assert bridge.zoe_url == "http://localhost:8642"

    def test_telegram_bridge_default_mode(self):
        """El modo por defecto es 'api'."""
        bridge = TelegramBridge(bot_token="test")
        assert bridge.mode == "api"

    def test_telegram_bridge_allowed_users(self):
        """Se pueden configurar usuarios permitidos."""
        bridge = TelegramBridge(
            bot_token="test",
            allowed_user_ids=[12345, 67890],
        )
        assert bridge._is_allowed(12345) is True
        assert bridge._is_allowed(99999) is False

    def test_telegram_bridge_no_restriction_by_default(self):
        """Sin restricción por defecto (todos permitidos)."""
        bridge = TelegramBridge(bot_token="test")
        assert bridge._is_allowed(12345) is True
        assert bridge._is_allowed(99999) is True

    def test_telegram_bridge_get_stats(self):
        """get_stats devuelve info del bridge."""
        bridge = TelegramBridge(
            bot_token="test",
            zoe_url="http://localhost:8642",
            mode="api",
        )
        stats = bridge.get_stats()
        assert stats["mode"] == "api"
        assert stats["zoe_url"] == "http://localhost:8642"
        assert stats["running"] is False

    def test_telegram_bridge_zoe_url_trailing_slash(self):
        """zoe_url sin trailing slash."""
        bridge = TelegramBridge(
            bot_token="test",
            zoe_url="http://localhost:8642/",
        )
        assert bridge.zoe_url == "http://localhost:8642"

    def test_telegram_bridge_has_main(self):
        """Tiene función main como entry point."""
        from zoe.peripherals.telegram_bridge import main
        assert callable(main)


# ============================================================
# 4. Language detector — integración con ZOE
# ============================================================

class TestLanguageIntegration:

    def test_language_detector_used_in_seed_manifest(self):
        """El LanguageDetector está disponible para usar en ZOE."""
        detector = LanguageDetector()
        profile = detector.get_profile(Language.ENGLISH)
        assert "You are ZOE" in profile.system_prompt_base

    def test_english_reflex_map_has_greeting(self):
        """El reflex map en inglés tiene saludo."""
        detector = LanguageDetector()
        profile = detector.get_profile(Language.ENGLISH)
        assert "hello" in profile.reflex_map
        assert profile.reflex_map["hello"] == "Hello. I'm here."

    def test_spanish_reflex_map_has_greeting(self):
        """El reflex map en español tiene saludo."""
        detector = LanguageDetector()
        profile = detector.get_profile(Language.SPANISH)
        assert "hola" in profile.reflex_map

    def test_language_profile_has_cultural_notes(self):
        """Cada profile tiene notas culturales."""
        detector = LanguageDetector()
        for lang in Language:
            profile = detector.get_profile(lang)
            assert profile.cultural_notes, f"{lang} has empty cultural_notes"
