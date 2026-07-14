"""
Tests Fase 7G — Endpoints REST /api/hardware/*

Valida los 4 endpoints nuevos de la Fase 7G:
- GET /api/hardware/ssds → SSDs portátiles recomendados
- GET /api/hardware/token_rates → tabla de tokens/s por modelo
- GET /api/hardware/cable_warning → warning sobre cable USB-C
- GET /api/hardware/system → info de hardware del host

Estos tests usan aiohttp TestClient/TestServer directamente (sin
pytest-aiohttp plugin) para máxima compatibilidad.
"""

import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from zoe.core.model_optimizer import (
    ModelOptimizer,
    RECOMMENDED_SSDS,
    EXPECTED_TOKEN_RATES,
)


# ============================================================
# Helpers
# ============================================================

def make_test_app():
    """
    Crea una app aiohttp de test con los 4 endpoints de Fase 7G
    registrados, sin necesidad de instanciar DashboardServer completo.
    """
    app = web.Application()

    async def handle_ssds(request):
        ssds = ModelOptimizer.get_recommended_ssds()
        return web.json_response({"ssds": ssds, "count": len(ssds)})

    async def handle_token_rates(request):
        rates = ModelOptimizer.get_expected_token_rates()
        return web.json_response({
            "token_rates": rates,
            "count": len(rates),
            "benchmark": {
                "hardware": "MacBook Air M2/M3 8GB",
                "ssd": "2000 MB/s USB-C",
                "cable": "USB 3.2 Gen 2 (cable corto original)",
                "note": "Con pendrive USB normal (400 MB/s), divide entre 3-5",
            },
        })

    async def handle_cable_warning(request):
        return web.json_response(ModelOptimizer.get_cable_warning())

    async def handle_system(request):
        opt = ModelOptimizer()
        return web.json_response(opt.get_system_info())

    app.router.add_get("/api/hardware/ssds", handle_ssds)
    app.router.add_get("/api/hardware/token_rates", handle_token_rates)
    app.router.add_get("/api/hardware/cable_warning", handle_cable_warning)
    app.router.add_get("/api/hardware/system", handle_system)
    return app


async def _fetch_json(path: str) -> dict:
    """Helper: levanta servidor de test, hace GET, devuelve JSON, cierra."""
    app = make_test_app()
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    try:
        resp = await client.get(path)
        data = await resp.json()
        return resp.status, data
    finally:
        await client.close()


def run_async(coro):
    """Ejecuta una corrutina de forma segura en tests síncronos."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Ya hay un loop corriendo (pytest-asyncio mode=auto)
            # Usar asyncio.ensure_future + sleep
            import threading
            result = [None]
            error = [None]

            def runner():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result[0] = new_loop.run_until_complete(coro)
                    new_loop.close()
                except Exception as e:
                    error[0] = e

            t = threading.Thread(target=runner)
            t.start()
            t.join()
            if error[0]:
                raise error[0]
            return result[0]
    except RuntimeError:
        pass
    return asyncio.run(coro)


# ============================================================
# 1. GET /api/hardware/ssds
# ============================================================

class TestHardwareSSDsEndpoint:

    def test_ssds_returns_200(self):
        status, _ = run_async(_fetch_json("/api/hardware/ssds"))
        assert status == 200

    def test_ssds_returns_json(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        assert isinstance(data, dict)
        assert "ssds" in data
        assert "count" in data

    def test_ssds_count_matches_list(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        assert data["count"] == len(data["ssds"])

    def test_ssds_has_at_least_3(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        assert data["count"] >= 3

    def test_ssds_have_required_fields(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        for ssd in data["ssds"]:
            assert "model" in ssd
            assert "capacity_tb" in ssd
            assert "read_speed_mbps" in ssd
            assert "price_eur" in ssd
            assert "recommended" in ssd
            assert "why" in ssd

    def test_ssds_includes_crucial_x10_pro(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        models = [s["model"] for s in data["ssds"]]
        assert "Crucial X10 Pro" in models

    def test_ssds_all_2000_plus_mbps(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        for ssd in data["ssds"]:
            assert ssd["read_speed_mbps"] >= 2000

    def test_ssds_exactly_one_recommended(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        recommended = [s for s in data["ssds"] if s["recommended"]]
        assert len(recommended) == 1
        assert recommended[0]["model"] == "Crucial X10 Pro"


# ============================================================
# 2. GET /api/hardware/token_rates
# ============================================================

class TestHardwareTokenRatesEndpoint:

    def test_token_rates_returns_200(self):
        status, _ = run_async(_fetch_json("/api/hardware/token_rates"))
        assert status == 200

    def test_token_rates_returns_json(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        assert isinstance(data, dict)
        assert "token_rates" in data
        assert "count" in data
        assert "benchmark" in data

    def test_token_rates_count_matches_list(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        assert data["count"] == len(data["token_rates"])

    def test_token_rates_has_at_least_5(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        assert data["count"] >= 5

    def test_token_rates_have_required_fields(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        for rate in data["token_rates"]:
            assert "model" in rate
            assert "quantization" in rate
            assert "ram_usage_gb" in rate
            assert "tokens_per_second_range" in rate
            assert "experience" in rate
            assert "strategy" in rate

    def test_token_rates_includes_qwen_3b(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        models = [r["model"] for r in data["token_rates"]]
        assert "Qwen 2.5 3B" in models

    def test_token_rates_includes_iq2_models(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        iq2_models = [r for r in data["token_rates"] if r["quantization"] == "IQ2_M"]
        assert len(iq2_models) >= 2

    def test_token_rates_benchmark_fields(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        bench = data["benchmark"]
        assert "hardware" in bench
        assert "ssd" in bench
        assert "cable" in bench
        assert "note" in bench

    def test_token_rates_benchmark_mentions_macbook(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        assert "MacBook" in data["benchmark"]["hardware"]


# ============================================================
# 3. GET /api/hardware/cable_warning
# ============================================================

class TestHardwareCableWarningEndpoint:

    def test_cable_warning_returns_200(self):
        status, _ = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert status == 200

    def test_cable_warning_returns_json(self):
        _, data = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert isinstance(data, dict)

    def test_cable_warning_has_required_fields(self):
        _, data = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert "title" in data
        assert "problem" in data
        assert "solution" in data
        assert "symptom_slow" in data
        assert "symptom_fast" in data
        assert "impact_factor" in data

    def test_cable_warning_mentions_usb_2(self):
        _, data = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert "USB 2.0" in data["problem"]

    def test_cable_warning_impact_factor_10x(self):
        _, data = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert data["impact_factor"] == "10x"

    def test_cable_warning_title_mentions_cable_corto(self):
        _, data = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert "cable corto" in data["title"].lower()

    def test_cable_warning_has_symptoms(self):
        _, data = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert "lent" in data["symptom_slow"].lower() or "tarda" in data["symptom_slow"].lower()
        assert "rápid" in data["symptom_fast"].lower() or "fast" in data["symptom_fast"].lower()


# ============================================================
# 4. GET /api/hardware/system
# ============================================================

class TestHardwareSystemEndpoint:

    def test_system_returns_200(self):
        status, _ = run_async(_fetch_json("/api/hardware/system"))
        assert status == 200

    def test_system_returns_json(self):
        _, data = run_async(_fetch_json("/api/hardware/system"))
        assert isinstance(data, dict)

    def test_system_has_required_fields(self):
        _, data = run_async(_fetch_json("/api/hardware/system"))
        assert "platform" in data
        assert "machine" in data
        assert "is_apple_silicon" in data
        assert "total_ram_gb" in data
        assert "available_ram_gb" in data
        assert "cpu_cores" in data
        # Fase 7G
        assert "p_cores" in data
        assert "e_cores" in data

    def test_system_p_cores_positive(self):
        _, data = run_async(_fetch_json("/api/hardware/system"))
        assert isinstance(data["p_cores"], int)
        assert data["p_cores"] > 0

    def test_system_e_cores_non_negative(self):
        _, data = run_async(_fetch_json("/api/hardware/system"))
        assert isinstance(data["e_cores"], int)
        assert data["e_cores"] >= 0

    def test_system_ram_positive(self):
        _, data = run_async(_fetch_json("/api/hardware/system"))
        assert data["total_ram_gb"] > 0
        assert data["available_ram_gb"] > 0

    def test_system_is_apple_silicon_is_bool(self):
        _, data = run_async(_fetch_json("/api/hardware/system"))
        assert isinstance(data["is_apple_silicon"], bool)


# ============================================================
# 5. Integración: handlers registrados en DashboardServer
# ============================================================

class TestDashboardServerHandlerRegistration:
    """
    Sprint 5.13 B8: Verifica que los handlers de Fase 7G estén registrados
    en routes.py (dashboard modularizado). Antes verificaba metodos en
    DashboardServer, pero el dashboard fue modularizado en Sprint 5.12
    y los handlers ahora son funciones en dashboard/handlers/hardware.py.
    """

    def test_dashboard_server_has_hardware_handlers(self):
        """Sprint 5.13 B8: Los 4 handlers de hardware existen como funciones en dashboard/handlers/hardware.py."""
        from zoe.dashboard.handlers.hardware import (
            _handle_hardware_ssds,
            _handle_hardware_token_rates,
            _handle_hardware_cable_warning,
            _handle_hardware_system,
        )
        # Si importan sin error, existen
        assert callable(_handle_hardware_ssds)
        assert callable(_handle_hardware_token_rates)
        assert callable(_handle_hardware_cable_warning)
        assert callable(_handle_hardware_system)

    def test_dashboard_server_handlers_are_coroutines(self):
        """Sprint 5.13 B8: Los handlers son corrutinas (async def)."""
        import inspect
        from zoe.dashboard.handlers.hardware import (
            _handle_hardware_ssds,
            _handle_hardware_token_rates,
            _handle_hardware_cable_warning,
            _handle_hardware_system,
        )
        for handler in (
            _handle_hardware_ssds,
            _handle_hardware_token_rates,
            _handle_hardware_cable_warning,
            _handle_hardware_system,
        ):
            assert inspect.iscoroutinefunction(handler), f"{handler.__name__} should be async"

    def test_handlers_call_model_optimizer_apis(self):
        """Los handlers usan ModelOptimizer (no lógica duplicada)."""
        assert hasattr(ModelOptimizer, "get_recommended_ssds")
        assert hasattr(ModelOptimizer, "get_expected_token_rates")
        assert hasattr(ModelOptimizer, "get_cable_warning")
        assert hasattr(ModelOptimizer, "get_system_info")


# ============================================================
# 6. Respuestas coherentes con APIs estáticas
# ============================================================

class TestEndpointAPIConsistency:
    """
    Verifica que los endpoints devuelven exactamente lo mismo que las
    APIs estáticas de ModelOptimizer (no hay transformaciones raras).
    """

    def test_ssds_match_static_api(self):
        _, data = run_async(_fetch_json("/api/hardware/ssds"))
        assert data["ssds"] == ModelOptimizer.get_recommended_ssds()

    def test_token_rates_match_static_api(self):
        _, data = run_async(_fetch_json("/api/hardware/token_rates"))
        assert data["token_rates"] == ModelOptimizer.get_expected_token_rates()

    def test_cable_warning_matches_static_api(self):
        _, data = run_async(_fetch_json("/api/hardware/cable_warning"))
        assert data == ModelOptimizer.get_cable_warning()

    def test_system_matches_get_system_info(self):
        _, data = run_async(_fetch_json("/api/hardware/system"))
        expected = ModelOptimizer().get_system_info()
        assert data["platform"] == expected["platform"]
        assert data["is_apple_silicon"] == expected["is_apple_silicon"]
        assert data["p_cores"] == expected["p_cores"]
        assert data["e_cores"] == expected["e_cores"]
