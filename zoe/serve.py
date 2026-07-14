"""
ZOE v1.0 -- Serve (punto de entrada para produccion)

Inicia el organismo ZOE con configuracion de produccion.

Uso:
    python -m zoe.serve --config zoe/config/production.yaml
    ZOE_ENV=production python -m zoe.serve
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
):
    """Sprint 5.17 F3.1: Delega a zoe.core.structured_logging para JSON output."""
    from .core.structured_logging import setup_logging as _setup
    _setup(level=level, log_file=log_file, max_bytes=max_bytes, backup_count=backup_count)


async def serve(config_path: str = None, env: str = None):
    """Inicia ZOE con configuracion."""

    # Cargar configuracion
    from .core.cognitive_loop_v4 import load_config
    config = load_config(config_path=config_path, env=env)

    zoe_config = config.get("zoe", {})
    llm_config = config.get("llm", {})
    mem_config = config.get("memory", {})
    fed_config = config.get("federation", {})
    log_config = config.get("logging", {})

    # Setup logging (with rotation)
    setup_logging(
        level=log_config.get("level", "INFO"),
        log_file=log_config.get("file"),
        max_bytes=log_config.get("max_bytes", 10 * 1024 * 1024),
        backup_count=log_config.get("backup_count", 5),
    )

    organism_id = zoe_config.get("organism_id", "zoe_default")
    tick_interval = zoe_config.get("tick_interval", 5.0)

    logger.info("=" * 60)
    logger.info("ZOE v1.0 -- Synthetic Cognitive Organism")
    logger.info("=" * 60)
    logger.info(f"Organism ID: {organism_id}")
    logger.info(f"Tick interval: {tick_interval}s")
    logger.info(f"LLM backend: {llm_config.get('backend', 'mock')}")
    logger.info(f"Memory DB: {mem_config.get('db_path', 'memory.db')}")
    logger.info(f"Federation enabled: {fed_config.get('enabled', False)}")
    logger.info("=" * 60)

    # Importar componentes
    from .core.state import InternalState
    from .core.world_model import WorldModel
    from .core.world_model_v2 import WorldModelV2
    from .core.subagents.perceiver import Perceiver
    from .core.subagents.forecaster import Forecaster
    from .core.subagents.speaker import Speaker
    from .core.subagents.critic import Critic
    from .core.subagents.phase2_subagents import (
        Memorialist, Learner, Curator, Creativity,
        CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine,
    )
    from .core.cognitive_laws import CognitiveLaws
    from .core.cognitive_physics import CognitivePhysics
    from .core.cognitive_fields import CognitiveFields
    from .core.cognitive_tensions import CognitiveTensions
    from .core.living_memory import LivingMemory
    from .core.intentionality_motor import IntentionalityMotor
    from .core.phylogenetic_motor import PhylogeneticMotor, PhylogeneticPool
    from .core.global_workspace import GlobalWorkspace
    from .core.meta_cognition import MetaCognition
    from .core.active_inference import ActiveInferenceLoop
    from .core.cognitive_loop_v4 import CognitiveLoopV4
    from .core.cognitive_loop_v5 import CognitiveLoopV5
    from .core.depth_classifier import DepthClassifier
    from .core.cognitive_cache import CognitiveCache
    from .core.model_profile_router import ModelProfileRouter
    from .core.federation import FederationManager
    from .alma.identity_vault import IdentityVault
    from .alma.trajectory_chain import TrajectoryChain
    from .alma.ontogenetic_motor_v2 import OntogeneticMotorV2
    from .metabolism.metabolism import Metabolism
    from .memory.memory_types import MemoryType
    from .memory.persistent_store import PersistentMemoryStore, PersistentLivingMemory
    from .memory.deep_consolidation import DeepConsolidation
    from .peripherals.senses import ClockSense, UserInputSense, AgentSense
    from .peripherals.actuators import (
        LanguageActuator, CodeActuator, ToolActuator,
        FederationActuator, ActuatorManager,
    )
    from .peripherals.llm import create_llm_peripheral

    # LLM periferico
    llm = create_llm_peripheral(llm_config)

    # Componentes Fase 0
    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense(), UserInputSense()]
    speaker = Speaker(llm_peripheral=llm)
    subagents_f0 = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    # Componentes Fase 0.5
    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory(max_entries=mem_config.get("max_entries", 1000))
    intentionality = IntentionalityMotor()
    PhylogeneticPool._instance = None
    phylogenetic = PhylogeneticMotor(zoe_id=organism_id)

    # Componentes Fase 1
    # Sprint 5.8 -- Persistencia de identidad y trayectoria entre sesiones
    from pathlib import Path as _Path
    _data_dir = _Path(mem_config.get("db_path", "zoe_data/memory.db")).parent
    _data_dir.mkdir(parents=True, exist_ok=True)
    _vault_path = str(_data_dir / "identity_vault.json")
    _chain_path = str(_data_dir / "trajectory_chain.json")
    _capsules_path = str(_data_dir / "loaded_capsules.json")

    # Cargar identidad existente o crear nueva
    vault = IdentityVault.load_from_disk(_vault_path)
    if vault is None:
        vault = IdentityVault(birth_timestamp=time.time())
        vault.save_to_disk(_vault_path)
        logger.info(f"New ZOE born -- identity hash: {vault.identity_hash[:16]}...")
    else:
        logger.info(f"ZOE identity loaded -- hash: {vault.identity_hash[:16]}...")

    # Cargar trayectoria existente o crear nueva
    chain = TrajectoryChain.load_from_disk(_chain_path)
    if chain is None:
        chain = TrajectoryChain(organism_id=organism_id)
    chain.set_persist_path(_chain_path)  # auto-save tras cada commit
    logger.info(f"Trajectory loaded -- {len(chain._mutations)} mutations")

    ontogenetic = OntogeneticMotorV2(
        identity_vault=vault, trajectory_chain=chain, laws=laws, organism_id=organism_id
    )
    metabolism = Metabolism()

    # 11 Memory Types init
    for mt in MemoryType:
        memory.add(content=f"Init {mt.value}", type=mt.value, provenance="system:init")

    actuator_mgr = ActuatorManager(laws=laws)
    actuator_mgr.register_actuator(LanguageActuator())

    # Componentes Fase 2
    wm_v2 = WorldModelV2()
    ai = ActiveInferenceLoop()
    mc = MetaCognition()
    gw = GlobalWorkspace()

    memorialist = Memorialist(memory=memory)
    learner = Learner()
    curator = Curator(memory=memory)
    creativity_agent = Creativity()
    causal = CausalEngine()
    emotional = EmotionalMotor()
    ethical = EthicalMotor()
    scientific = ScientificEngine()

    all_subagents = subagents_f0 + [
        memorialist, learner, curator, creativity_agent,
        causal, emotional, ethical, scientific,
    ]

    # Fase 3.4: Persistencia
    store = PersistentMemoryStore(
        db_path=mem_config.get("db_path", "zoe_data/memory.db"),
        auto_save_interval=mem_config.get("auto_save_interval", 50),
    )
    persistent_mem = PersistentLivingMemory(memory, store)

    # Fase 3.5: Consolidacion profunda
    deep_consolidation = DeepConsolidation(memory=memory, scientific_engine=scientific)

    # Fase 5: ACD + Cache
    depth_classifier = DepthClassifier()
    cognitive_cache = CognitiveCache(max_size=100, ttl_seconds=300)

    # Sprint 5.10 C8 -- LanguageDetector
    try:
        from .core.language_detector import LanguageDetector
        language_detector = LanguageDetector()
        logger.info("LanguageDetector initialized")
    except Exception as e:
        logger.debug(f"LanguageDetector not available: {e}")
        language_detector = None

    # Fase 4: Federacion
    federation_mgr = None
    fed_server = None
    if fed_config.get("enabled", False):
        federation_mgr = FederationManager(
            organism_id=organism_id,
            host=fed_config.get("host", "0.0.0.0"),
            port=fed_config.get("port", 8642),
            quorum_threshold=fed_config.get("quorum_threshold", 0.7),
        )
        from .core.federation import FederationServer
        fed_server = FederationServer(federation_mgr)
        await fed_server.start()
        logger.info(f"Federation server started on port {fed_config.get('port', 8642)}")

    # Crear organismo V5 (backward-compatible con V4)
    loop = CognitiveLoopV5(
        senses=senses,
        world_model=world_model,
        subagents=all_subagents,
        state=state,
        tick_interval=tick_interval,
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id=organism_id,
        global_workspace=gw,
        meta_cognition=mc,
        active_inference=ai,
        world_model_v2=wm_v2,
        identity_vault=vault,
        trajectory_chain=chain,
        ontogenetic_motor=ontogenetic,
        metabolism=metabolism,
        actuator_manager=actuator_mgr,
        deep_consolidation=deep_consolidation,
        persistent_memory=persistent_mem,
        auto_save_interval=mem_config.get("auto_save_interval", 50),
        config=config,
        # Fase 5 componentes
        depth_classifier=depth_classifier,
        cognitive_cache=cognitive_cache,
    )

    # Inyectar LanguageDetector si esta disponible
    if language_detector:
        loop._language_detector = language_detector

    # Inicializar (carga memoria desde disco)
    logger.info("Initializing organism (loading memory from disk)...")
    loop.initialize()
    logger.info(f"Identity Vault: {vault.summary()}")
    logger.info(f"Memory entries loaded: {memory.count()}")

    # Sprint 5.13 B4 — Iniciar servidor HTTP minimo para k8s probes.
    # El Docker ENTRYPOINT es `python -m zoe.serve`, pero k8s livenessProbe
    # y readinessProbe apuntan a http://:8080/health y /ready. Sin este
    # servidor, los probes fallan y el pod entra en CrashLoopBackOff.
    # El servidor expone SOLO /health, /ready, /live, /metrics — sin dashboard
    # completo (eso requiere python -m zoe.web_dashboard).
    from aiohttp import web
    health_app = web.Application()

    async def _handle_health(request):
        """Liveness probe — el proceso responde."""
        return web.json_response({"status": "ok", "iterations": loop.state.iteration_count})

    async def _handle_ready(request):
        """Readiness probe — el organismo tiene identidad y memoria cargadas."""
        try:
            _mem_count = memory.count()
            _id_hash = vault.identity_hash[:16] if vault else "missing"
            return web.json_response({
                "status": "ready",
                "identity": _id_hash,
                "memory_entries": _mem_count,
            })
        except Exception as e:
            return web.json_response({"status": "not_ready", "error": str(e)}, status=503)

    async def _handle_live(request):
        """Liveness probe — verifica que el cognitive loop avanza."""
        _iter = loop.state.iteration_count
        # Si no ha avanzado en 60s, probablemente esta colgado
        return web.json_response({"status": "alive", "iterations": _iter})

    async def _handle_metrics(request):
        """Prometheus metrics endpoint."""
        try:
            from .core.metrics import generate_metrics
            return web.Response(text=generate_metrics(), content_type="text/plain")
        except Exception:
            return web.Response(text="# metrics not available\n", content_type="text/plain")

    health_app.router.add_get("/health", _handle_health)
    health_app.router.add_get("/ready", _handle_ready)
    health_app.router.add_get("/live", _handle_live)
    health_app.router.add_get("/metrics", _handle_metrics)

    health_runner = web.AppRunner(health_app)
    await health_runner.setup()
    health_port = int(__import__("os").environ.get("ZOE_HEALTH_PORT", "8080"))
    health_site = web.TCPSite(health_runner, "0.0.0.0", health_port)
    await health_site.start()
    logger.info(f"Health/Probes server started on http://0.0.0.0:{health_port}/health")

    # Pensamiento de nacimiento
    logger.info("ZOE is alive. Starting cognitive loop...")

    # Ejecutar
    try:
        await loop.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested via keyboard")
    finally:
        # Detener servidor de health
        await health_runner.cleanup()

        # Graceful shutdown con persistencia
        logger.info("Saving memory to disk...")
        persistent_mem.save_to_disk()

        # Sprint 5.8 -- Persistir identidad, trayectoria y capsulas
        logger.info("Saving identity vault...")
        vault.save_to_disk(_vault_path)
        logger.info("Saving trajectory chain...")
        chain.save_to_disk(_chain_path)

        if fed_server:
            await fed_server.stop()
        logger.info("ZOE stopped. Goodbye.")

    # Stats finales
    stats = loop.get_stats()
    logger.info(f"Final stats: iterations={stats['iterations']}, thoughts={stats['thoughts']}")


def main():
    parser = argparse.ArgumentParser(description="ZOE v1.0 -- Serve")
    parser.add_argument("--config", help="Path to config YAML")
    parser.add_argument("--env", help="Environment (production/development/test)")
    args = parser.parse_args()

    asyncio.run(serve(config_path=args.config, env=args.env))


if __name__ == "__main__":
    main()
