"""
Registro de todas las rutas del dashboard.

Cada handler se registra como una lambda que pasa el server
como primer argumento, manteniendo la firma (request) para aiohttp.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import web

if TYPE_CHECKING:
    from .server import DashboardServer


def register_routes(app: web.Application, server: "DashboardServer") -> None:
    """Registra todas las rutas en la aplicacion aiohttp."""

    from .handlers.core import (
        _handle_index, _handle_stats, _handle_memory, _handle_identity,
        _handle_state, _handle_sleep, _handle_wake, _handle_history,
        _handle_federation,
    )
    from .handlers.chat import (
        _handle_websocket, _handle_chat_post, _handle_feed_upload,
    )
    from .handlers.capsules import (
        _handle_capsules_list, _handle_capsules_loaded, _handle_capsule_load,
        _handle_capsule_unload, _handle_capsule_info, _handle_capsule_validate,
        _handle_capsule_create,
    )
    from .handlers.marketplace import (
        _handle_marketplace_list, _handle_marketplace_upload,
        _handle_marketplace_download, _handle_marketplace_use_cases,
        _handle_marketplace_upload_use_case,
    )
    from .handlers.federation import (
        _handle_epistemic_validate, _handle_epistemic_knowledge,
        _handle_epistemic_register, _handle_epistemic_peers,
        _handle_epistemic_stats, _handle_epistemic_request_validation,
    )
    from .handlers.quarantine import (
        _handle_quarantine_list, _handle_quarantine_stats,
        _handle_quarantine_promote, _handle_quarantine_reject,
    )
    from .handlers.mentor import (
        _handle_mentor_get, _handle_mentor_update, _handle_mentor_stats,
    )
    from .handlers.models import (
        _handle_models_system_info, _handle_models_recommend,
        _handle_models_catalog, _handle_models_optimize,
    )
    from .handlers.resources import (
        _handle_resources_graph, _handle_resources_stats, _handle_resources_scan,
        _handle_modelbus_list, _handle_modelbus_stats, _handle_modelbus_select,
        _handle_planner_plan, _handle_planner_stats, _handle_planner_recommend,
    )
    from .handlers.seed import (
        _handle_seed_detect, _handle_seed_inspect, _handle_seed_create,
        _handle_seed_germinate, _handle_seed_stats, _handle_seed_last_report,
    )
    from .handlers.voice import (
        _handle_voice_start, _handle_voice_stop, _handle_voice_status,
    )
    from .handlers.embodiment import (
        _handle_embodiment_compose, _handle_embodiment_bootstrap,
        _handle_embodiment_status, _handle_embodiment_list,
        _handle_embodiment_tear_down, _handle_embodiment_log,
    )
    from .handlers.health import (
        _handle_health, _handle_ready, _handle_live, _handle_metrics,
    )
    from .handlers.llm import _handle_llm_switch
    from .handlers.reflection import (
        _handle_reflections_list, _handle_reflections_metrics, _handle_reflections_config,
    )
    from .handlers.hardware import (
        _handle_hardware_ssds, _handle_hardware_token_rates,
        _handle_hardware_cable_warning, _handle_hardware_system,
        _handle_router_stats, _handle_router_installed, _handle_router_profile,
        _handle_manifest,
    )

    def bind(handler):
        """Bind server as first argument to handler."""
        return lambda request: handler(server, request)

    app.router.add_get("/", bind(_handle_index))
    app.router.add_get("/ws", bind(_handle_websocket))
    app.router.add_post("/chat", bind(_handle_chat_post))
    app.router.add_post("/feed", bind(_handle_feed_upload))
    app.router.add_get("/stats", bind(_handle_stats))
    app.router.add_get("/memory", bind(_handle_memory))
    app.router.add_get("/identity", bind(_handle_identity))
    app.router.add_get("/state", bind(_handle_state))
    app.router.add_post("/sleep", bind(_handle_sleep))
    app.router.add_post("/wake", bind(_handle_wake))
    app.router.add_post("/llm", bind(_handle_llm_switch))
    app.router.add_get("/history", bind(_handle_history))
    app.router.add_get("/federation", bind(_handle_federation))
    # Capsules
    app.router.add_get("/api/capsules", bind(_handle_capsules_list))
    app.router.add_get("/api/capsules/loaded", bind(_handle_capsules_loaded))
    app.router.add_post("/api/capsules/load", bind(_handle_capsule_load))
    app.router.add_post("/api/capsules/unload", bind(_handle_capsule_unload))
    app.router.add_get("/api/capsules/{name}/info", bind(_handle_capsule_info))
    app.router.add_post("/api/capsules/{name}/validate", bind(_handle_capsule_validate))
    app.router.add_post("/api/capsules/create", bind(_handle_capsule_create))
    # Federation
    app.router.add_post("/federation/epistemic/validate", bind(_handle_epistemic_validate))
    app.router.add_get("/federation/epistemic/knowledge/{claim_hash}", bind(_handle_epistemic_knowledge))
    app.router.add_post("/federation/epistemic/register", bind(_handle_epistemic_register))
    app.router.add_get("/federation/epistemic/peers", bind(_handle_epistemic_peers))
    app.router.add_get("/federation/epistemic/stats", bind(_handle_epistemic_stats))
    app.router.add_post("/federation/epistemic/request_validation", bind(_handle_epistemic_request_validation))
    # Quarantine
    app.router.add_get("/api/quarantine", bind(_handle_quarantine_list))
    app.router.add_get("/api/quarantine/stats", bind(_handle_quarantine_stats))
    app.router.add_post("/api/quarantine/{entry_id}/promote", bind(_handle_quarantine_promote))
    app.router.add_post("/api/quarantine/{entry_id}/reject", bind(_handle_quarantine_reject))
    # Marketplace
    app.router.add_get("/api/marketplace/capsules", bind(_handle_marketplace_list))
    app.router.add_post("/api/marketplace/upload", bind(_handle_marketplace_upload))
    app.router.add_post("/api/marketplace/download/{name}", bind(_handle_marketplace_download))
    app.router.add_get("/api/marketplace/use_cases", bind(_handle_marketplace_use_cases))
    app.router.add_post("/api/marketplace/upload_use_case", bind(_handle_marketplace_upload_use_case))
    # Mentor
    app.router.add_get("/api/mentor", bind(_handle_mentor_get))
    app.router.add_post("/api/mentor", bind(_handle_mentor_update))
    app.router.add_get("/api/mentor/stats", bind(_handle_mentor_stats))
    # Models
    app.router.add_get("/api/models/system_info", bind(_handle_models_system_info))
    app.router.add_get("/api/models/recommend", bind(_handle_models_recommend))
    app.router.add_get("/api/models/catalog", bind(_handle_models_catalog))
    app.router.add_post("/api/models/optimize", bind(_handle_models_optimize))
    # Resources
    app.router.add_get("/api/resources", bind(_handle_resources_graph))
    app.router.add_get("/api/resources/stats", bind(_handle_resources_stats))
    app.router.add_post("/api/resources/scan", bind(_handle_resources_scan))
    # ModelBus
    app.router.add_get("/api/modelbus", bind(_handle_modelbus_list))
    app.router.add_get("/api/modelbus/stats", bind(_handle_modelbus_stats))
    app.router.add_post("/api/modelbus/select", bind(_handle_modelbus_select))
    # Planner
    app.router.add_post("/api/planner/plan", bind(_handle_planner_plan))
    app.router.add_get("/api/planner/stats", bind(_handle_planner_stats))
    app.router.add_get("/api/planner/recommend", bind(_handle_planner_recommend))
    # Embodiment
    app.router.add_post("/api/embodiment/compose", bind(_handle_embodiment_compose))
    app.router.add_post("/api/embodiment/bootstrap", bind(_handle_embodiment_bootstrap))
    app.router.add_get("/api/embodiment/status", bind(_handle_embodiment_status))
    app.router.add_get("/api/embodiment/list", bind(_handle_embodiment_list))
    app.router.add_post("/api/embodiment/tear_down", bind(_handle_embodiment_tear_down))
    app.router.add_get("/api/embodiment/log", bind(_handle_embodiment_log))
    # Seed
    app.router.add_get("/api/seed/detect", bind(_handle_seed_detect))
    app.router.add_get("/api/seed/inspect", bind(_handle_seed_inspect))
    app.router.add_post("/api/seed/create", bind(_handle_seed_create))
    app.router.add_post("/api/seed/germinate", bind(_handle_seed_germinate))
    app.router.add_get("/api/seed/stats", bind(_handle_seed_stats))
    app.router.add_get("/api/seed/last_report", bind(_handle_seed_last_report))
    # Voice
    app.router.add_post("/api/voice/start", bind(_handle_voice_start))
    app.router.add_post("/api/voice/stop", bind(_handle_voice_stop))
    app.router.add_get("/api/voice/status", bind(_handle_voice_status))
    # Hardware
    app.router.add_get("/api/hardware/ssds", bind(_handle_hardware_ssds))
    app.router.add_get("/api/hardware/token_rates", bind(_handle_hardware_token_rates))
    app.router.add_get("/api/hardware/cable_warning", bind(_handle_hardware_cable_warning))
    app.router.add_get("/api/hardware/system", bind(_handle_hardware_system))
    # Router
    app.router.add_get("/api/router/stats", bind(_handle_router_stats))
    app.router.add_get("/api/router/installed", bind(_handle_router_installed))
    app.router.add_get("/api/router/profile", bind(_handle_router_profile))
    # PWA + Health
    app.router.add_get("/manifest.json", bind(_handle_manifest))
    app.router.add_get("/health", bind(_handle_health))
    app.router.add_get("/ready", bind(_handle_ready))
    app.router.add_get("/live", bind(_handle_live))
    app.router.add_get("/metrics", bind(_handle_metrics))
    # Reflection (ZOE v2.1 — ReflectionEngine)
    app.router.add_get("/api/reflections", bind(_handle_reflections_list))
    app.router.add_get("/api/reflections/metrics", bind(_handle_reflections_metrics))
    app.router.add_get("/api/reflections/config", bind(_handle_reflections_config))
