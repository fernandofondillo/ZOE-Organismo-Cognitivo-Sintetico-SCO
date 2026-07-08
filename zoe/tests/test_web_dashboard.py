"""Tests para Web Dashboard."""

import asyncio
import pytest
import tempfile

from zoe.web_dashboard import DashboardServer, _get_dashboard_html


def test_dashboard_html_not_empty():
    """El HTML del dashboard no está vacío."""
    html = _get_dashboard_html()
    assert len(html) > 1000
    assert "<html" in html
    assert "ZOE" in html
    assert "WebSocket" in html or "ws" in html.lower()


def test_dashboard_html_has_panels():
    """El HTML tiene los 3 paneles."""
    html = _get_dashboard_html()
    assert "panel-left" in html
    assert "panel-center" in html
    assert "panel-right" in html


def test_dashboard_html_has_chat():
    """El HTML tiene chat."""
    html = _get_dashboard_html()
    assert "chatInput" in html
    assert "sendMessage" in html
    assert "chatMessages" in html


def test_dashboard_html_has_state():
    """El HTML tiene indicadores de estado."""
    html = _get_dashboard_html()
    assert "barEnergy" in html
    assert "barFatigue" in html
    assert "barArousal" in html


def test_dashboard_html_has_llm_selector():
    """El HTML tiene selector de LLM."""
    html = _get_dashboard_html()
    assert "llmSelect" in html
    assert "switchLLM" in html
    assert "ollama" in html
    assert "zai" in html


def test_dashboard_html_has_feed():
    """El HTML tiene función de alimentar."""
    html = _get_dashboard_html()
    assert "feedFile" in html
    assert "uploadFile" in html
    assert "fileInput" in html


def test_dashboard_html_has_history():
    """El HTML tiene historial."""
    html = _get_dashboard_html()
    assert "showHistory" in html


def test_dashboard_html_has_sleep_wake():
    """El HTML tiene sleep/wake."""
    html = _get_dashboard_html()
    assert "toggleSleep" in html


def test_dashboard_html_has_federation():
    """El HTML tiene sección de federación."""
    html = _get_dashboard_html()
    assert "federation" in html.lower() or "fed-section" in html


def test_dashboard_html_has_thoughts():
    """El HTML tiene panel de pensamientos autónomos."""
    html = _get_dashboard_html()
    assert "thoughts" in html
    assert "addThought" in html


def test_dashboard_server_initialization():
    """DashboardServer se inicializa correctamente."""
    db = tempfile.mktemp(suffix=".db")
    server = DashboardServer(backend="mock", port=18642, db_path=db)
    assert server.port == 18642
    assert server.backend == "mock"


@pytest.mark.asyncio
async def test_dashboard_server_initialize_zoe():
    """DashboardServer inicializa ZOE."""
    db = tempfile.mktemp(suffix=".db")
    server = DashboardServer(backend="mock", port=18643, db_path=db)
    await server.initialize()
    assert server.chat is not None
    assert server.chat.vault is not None
    assert server.chat.memory is not None
    await server.chat.shutdown()
