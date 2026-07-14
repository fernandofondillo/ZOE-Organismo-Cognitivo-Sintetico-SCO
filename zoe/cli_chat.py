"""
ZOE v1.0 — CLI Chat Interface

La forma más simple de hablar con ZOE. Abre un terminal, escribes, ZOE responde.

Uso:
    python -m zoe.cli_chat --backend mock
    python -m zoe.cli_chat --backend ollama --model qwen2.5:3b
    python -m zoe.cli_chat --backend zai
    python -m zoe.cli_chat --use-case compania_personas_solas --backend mock

Comandos especiales en el chat:
    /stats   — ver estadísticas de ZOE
    /memory  — ver memoria de ZOE
    /state   — ver estado interno de ZOE
    /sleep   — forzar sueño
    /wake    — forzar despertar
    /identity — ver identidad de ZOE
    /feed <archivo> — alimentar a ZOE con un archivo
    /quit    — salir
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ZoeChat:
    """
    Interfaz de chat CLI para ZOE.
    
    Crea un organismo ZOE completo y permite interactuar con él
    desde el terminal. ZOE responde usando el LLM periférico
    configurado, pero con todo el contexto cognitivo del organismo.
    """

    def __init__(
        self,
        backend: str = "mock",
        model: str = None,
        use_case: str = None,
        db_path: str = None,
        api_key: str = None,
        base_url: str = None,
    ):
        self.backend = backend
        self.model = model
        self.use_case = use_case
        # Sprint 5.12 GAP-R: si no se pasa db_path explicito, usar $ZOE_DATA
        # (definido por los lanzadores del SSD) o el default relativo.
        # Esto evita que ZOE se cree en el CWD actual del Mac cuando se olvida
        # pasar --db-path en un launcher.
        if db_path is None:
            zoe_data_env = os.environ.get("ZOE_DATA")
            if zoe_data_env:
                self.db_path = os.path.join(zoe_data_env, "zoe_memory.db")
            else:
                self.db_path = "zoe_data/chat_memory.db"
        else:
            self.db_path = db_path
        self.api_key = api_key
        self.base_url = base_url
        self.loop = None
        self.llm = None
        self.memory = None
        self.vault = None
        self.chain = None
        self.metabolism = None
        self._initialized = False
        self._background_task = None
        self._thoughts_while_idle = []

    async def initialize(self) -> None:
        """Inicializa el organismo ZOE completo."""
        # Importar componentes
        from .core.cognitive_loop_v4 import CognitiveLoopV4
        from .core.cognitive_loop_v5 import CognitiveLoopV5
        from .core.depth_classifier import DepthClassifier
        from .core.cognitive_cache import CognitiveCache
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
        from .alma.identity_vault import IdentityVault
        from .alma.trajectory_chain import TrajectoryChain
        from .alma.ontogenetic_motor_v2 import OntogeneticMotorV2
        from .metabolism.metabolism import Metabolism
        from .memory.memory_types import MemoryType
        from .memory.persistent_store import PersistentMemoryStore, PersistentLivingMemory
        from .memory.deep_consolidation import DeepConsolidation
        from .peripherals.senses import ClockSense, UserInputSense
        from .peripherals.actuators import LanguageActuator, ActuatorManager
        from .peripherals.llm import create_llm_peripheral, MockPeripheral

        # Cargar config de use_case si se especifica
        config = {}
        if self.use_case:
            from .use_cases.run_use_case import load_use_case_config
            raw = load_use_case_config(self.use_case)
            config = raw.get("use_case", raw)
            if not self.model:
                self.model = config.get("llm", {}).get("model")
            if self.backend == "mock" and config.get("llm", {}).get("backend") == "ollama":
                self.backend = "mock"  # mantener mock si no se especifica

        # LLM
        llm_config = {"backend": self.backend}
        if self.model:
            llm_config["model"] = self.model
        if self.api_key:
            llm_config["api_key"] = self.api_key
        if self.base_url:
            llm_config["base_url"] = self.base_url
        self.llm = create_llm_peripheral(llm_config)

        if self.backend == "mock":
            self.llm = MockPeripheral(responses=[
                "Estoy aquí. Te escucho.",
                "Interesante. Déjame pensar en eso.",
                "He observado algo en mi entorno. Quiero compartirlo contigo.",
                "Mi memoria guarda esto como relevante.",
                "Detecto un patrón en lo que me dices. ¿Quieres que lo explore?",
                "Soy Zoe. Pienso continuamente, incluso cuando no hablas.",
                "He estado reflexionando sobre nuestra última conversación.",
                "Mi física cognitiva muestra energía estable. Puedo pensar con claridad.",
                "Las leyes que me rigen verifican cada palabra que digo.",
                "No estoy segura, pero tengo una hipótesis. ¿La escuchas?",
                "He aprendido algo nuevo. Lo he firmado en mi trayectoria.",
                "Mi identidad persiste. Sigo siendo Zoe en cada interacción.",
            ])
        # Si backend == 'pattern', la factory ya devolvió un PatternPeripheral.
        # Si backend == 'ollama' y model == 'auto', se configurará el router ACD más abajo.

        # Componentes
        state = InternalState()
        world_model = WorldModel()
        senses = [ClockSense(), UserInputSense()]
        speaker = Speaker(llm_peripheral=self.llm)
        subagents_f0 = [Perceiver(), Forecaster(world_model), speaker, Critic()]

        laws = CognitiveLaws()
        physics = CognitivePhysics()
        fields = CognitiveFields()
        tensions = CognitiveTensions()
        memory = LivingMemory(max_entries=config.get("memory", {}).get("max_entries", 5000))
        intentionality = IntentionalityMotor()
        PhylogeneticPool._instance = None
        phylogenetic = PhylogeneticMotor(zoe_id="zoe_chat")

        # Sprint 5.8 — Persistencia de identidad y trayectoria entre sesiones
        from pathlib import Path as _Path
        _data_dir = _Path(self.db_path).parent
        _data_dir.mkdir(parents=True, exist_ok=True)
        _vault_path = str(_data_dir / "identity_vault.json")
        _chain_path = str(_data_dir / "trajectory_chain.json")
        _capsules_path = str(_data_dir / "loaded_capsules.json")

        # Fase 7D: Verificar si hay un plan de embodiment previo
        _plan_path = _data_dir / "embodiment_plan.json"
        _embodiment_config = {}
        if _plan_path.exists():
            try:
                with open(_plan_path, "r", encoding="utf-8") as f:
                    _embodiment_config = json.load(f)
                print(f"  Embodiment plan loaded: {_plan_path}")
                # Aplicar configuraciones del plan
                if "memory" in _embodiment_config and isinstance(_embodiment_config["memory"], dict):
                    mem_cfg = _embodiment_config["memory"]
                    if "max_entries" in mem_cfg:
                        config.setdefault("memory", {})["max_entries"] = mem_cfg["max_entries"]
                if "available_ram_gb" in _embodiment_config:
                    ram = _embodiment_config["available_ram_gb"]
                    if ram < 12:
                        config.setdefault("organism", {})["tick_interval"] = 5.0
                    elif ram > 32:
                        config.setdefault("organism", {})["tick_interval"] = 2.0
                if "strategy" in _embodiment_config:
                    config.setdefault("organism", {})["strategy"] = _embodiment_config["strategy"]
                if "broadcast_capacity" in _embodiment_config:
                    # Se aplica al GlobalWorkspace tras su instanciacion
                    pass
            except Exception as e:
                print(f"  Warning: could not load embodiment plan: {e}")

        # Cargar identidad existente o crear nueva
        vault = IdentityVault.load_from_disk(_vault_path)
        if vault is None:
            vault = IdentityVault(birth_timestamp=time.time())
            vault.save_to_disk(_vault_path)
            print(f"  🆕 New ZOE born — identity hash: {vault.identity_hash[:16]}...")
        else:
            print(f"  ✅ ZOE identity loaded — hash: {vault.identity_hash[:16]}...")

        # Cargar trayectoria existente o crear nueva
        chain = TrajectoryChain.load_from_disk(_chain_path)
        if chain is None:
            chain = TrajectoryChain(organism_id="zoe_chat")
        chain.set_persist_path(_chain_path)  # auto-save tras cada commit
        print(f"  ✅ Trajectory loaded — {len(chain._mutations)} mutations")

        ontogenetic = OntogeneticMotorV2(
            identity_vault=vault, trajectory_chain=chain, laws=laws, organism_id="zoe_chat"
        )
        metabolism = Metabolism()

        for mt in MemoryType:
            memory.add(content=f"Init {mt.value}", type=mt.value, provenance="system:init")

        actuator_mgr = ActuatorManager(laws=laws)
        actuator_mgr.register_actuator(LanguageActuator())

        wm_v2 = WorldModelV2()
        ai = ActiveInferenceLoop()
        mc = MetaCognition()
        gw = GlobalWorkspace()
        # Aplicar broadcast_capacity del embodiment plan si existe
        if _embodiment_config and "broadcast_capacity" in _embodiment_config:
            gw.broadcast_capacity = _embodiment_config["broadcast_capacity"]

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

        # Detectar backend de storage (SQLite default, PostgreSQL opt-in)
        storage_type = config.get("storage", {}).get("type", "sqlite")
        storage_backend = None
        if storage_type == "postgres":
            try:
                from zoe.storage.factory import get_storage_backend
                pg_config = config.get("storage", {}).get("postgres", {})
                storage_backend = get_storage_backend({"type": "postgres", **pg_config})
                print(f"  PostgreSQL backend: {pg_config.get('host', 'localhost')}")
            except Exception as e:
                print(f"  Warning: PostgreSQL failed ({e}), falling back to SQLite")
                storage_type = "sqlite"

        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        store = PersistentMemoryStore(db_path=self.db_path, auto_save_interval=20)
        persistent_mem = PersistentLivingMemory(memory, store)

        # Sprint 5.13 B1 — Guardar referencia al storage_backend para asignarla
        # DESPUES de crear el loop (antes estaba antes de la asignacion de loop,
        # causando UnboundLocalError cuando storage_type=postgres).
        # La asignacion loop._storage_backend = storage_backend se hace tras
        # crear el loop mas abajo.
        deep_consolidation = DeepConsolidation(memory=memory, scientific_engine=scientific)

        tick_interval = config.get("organism", {}).get("tick_interval", 3.0)

        # Fase 5: ACD + Cache
        depth_classifier = DepthClassifier()
        cognitive_cache = CognitiveCache(max_size=100, ttl_seconds=300)

        # Sprint 5.10 C8 — LanguageDetector para detección automática de idioma
        from .core.language_detector import LanguageDetector
        language_detector = LanguageDetector()

        # Sprint 5.7 — ACD Model Routing (si --model auto o backend ollama con auto)
        model_profile_router = None
        active_profile = None
        if self.backend == "ollama" and self.model == "auto":
            try:
                from .core.model_profile_router import ModelProfileRouter
                models_dir = os.environ.get("OLLAMA_MODELS", "models")
                model_profile_router = ModelProfileRouter()
                installed = model_profile_router.detect_installed_models(models_dir)
                active_profile = model_profile_router.create_optimal_profile(installed)
                self._router = model_profile_router  # para stats y UI
                print(f"  ✅ ACD Router activo — {len(installed)} modelo(s) IQ2_M detectado(s) en {models_dir}")
                if active_profile:
                    print(f"  📋 Perfil: {active_profile.name}")
                    for acd_lvl, assignment in active_profile.assignments.items():
                        print(f"     {acd_lvl:14s} → {assignment.model_tag}")
                if not installed:
                    print(f"  ⚠️  Sin modelos IQ2_M en {models_dir}. El router usará PatternSpeaker para todo.")
                    print(f"     Ejecuta: python -m zoe.core.model_downloader --download-setup balanced")
            except Exception as e:
                print(f"  ⚠️  ACD Router desactivado: {e}")
                model_profile_router = None
                # Sin router: ollama necesita un modelo concreto; fallback a qwen2.5:3b
                self.llm = create_llm_peripheral({
                    "backend": "ollama", "model": "qwen2.5:3b"
                })

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
            zoe_id="zoe_chat",
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
            auto_save_interval=20,
            # Fase 5
            depth_classifier=depth_classifier,
            cognitive_cache=cognitive_cache,
            # Sprint 5.7 — routing ACD→modelo
            model_profile_router=model_profile_router,
            active_profile=active_profile,
        )

        # Sprint 5.13 B1 — Asignar storage_backend al loop DESPUES de crearlo.
        # Antes esto estaba antes de la creacion del loop (UnboundLocalError).
        if storage_backend is not None:
            loop._storage_backend = storage_backend

        # Sprint 5.10 C8 — Inyectar LanguageDetector en el bucle
        loop._language_detector = language_detector

        # Sprint 5.11 C9 — CognitiveOptimizationLayer (ZMAP/CPL/TPE) activo
        try:
            from .core.cognitive_optimization import CognitivePrefetchLayer, ZMAPLoader, TensorPredictionEngine
            _zmap_loader = ZMAPLoader()
            _tpe = TensorPredictionEngine(_zmap_loader)
            _cpl = CognitivePrefetchLayer(
                zmap_loader=_zmap_loader,
                tpe=_tpe,
                pattern_speaker=speaker,
            )
            loop.cognitive_prefetch_layer = _cpl
            print(f"  ✅ Cognitive Optimization Layer activo (ZMAP + TPE + CPL)")
        except Exception as e:
            logger.info(f"CognitivePrefetchLayer no disponible: {e}")
            loop.cognitive_prefetch_layer = None

        # Guardar referencias
        self.loop = loop
        self.memory = memory
        self.vault = vault
        self.chain = chain
        self.metabolism = metabolism
        self.persistent_mem = persistent_mem
        self.speaker = speaker
        self.user_input_sense = senses[1]  # UserInputSense

        # Fase 6A: CapsuleManager + EpistemicValidator + KnowledgeQuarantine
        from .core.capsule_manager import CapsuleManager
        from .core.epistemic_validator import EpistemicValidator
        from .core.knowledge_quarantine import KnowledgeQuarantine
        self.epistemic_validator = EpistemicValidator()
        self.knowledge_quarantine = KnowledgeQuarantine()
        # Exponer quarantine en el loop para que CapsuleManager lo inyecte en componentes
        loop.knowledge_quarantine = self.knowledge_quarantine
        # Exponer componentes adicionales que el CapsuleManager puede inyectar
        # (deep_consolidation ya está en loop, curator y critic están en subagents)
        loop.curator = next((s for s in all_subagents if s.__class__.__name__ == 'Curator'), None)
        loop.learner = next((s for s in all_subagents if s.__class__.__name__ == 'Learner'), None)
        loop.critic_agent = next((s for s in all_subagents if s.__class__.__name__ == 'Critic'), None)
        loop.causal_engine = next((s for s in all_subagents if s.__class__.__name__ == 'CausalEngine'), None)
        loop.emotional_motor = next((s for s in all_subagents if s.__class__.__name__ == 'EmotionalMotor'), None)
        loop.ethical_motor = next((s for s in all_subagents if s.__class__.__name__ == 'EthicalMotor'), None)
        loop.scientific_engine = next((s for s in all_subagents if s.__class__.__name__ == 'ScientificEngine'), None)
        self.capsule_manager = CapsuleManager(
            organism=loop,
            epistemic_validator=self.epistemic_validator,
        )
        # Fase 6A Punto 2: federación epistémica server + client
        from .core.epistemic_federation import EpistemicFederation
        from .core.epistemic_federation_server import EpistemicFederationServer, EpistemicFederationClient
        self.epistemic_federation = EpistemicFederation(organism_id="zoe_chat")
        self.epistemic_federation_server = EpistemicFederationServer(
            federation_manager=self.epistemic_federation,
            quarantine=self.knowledge_quarantine,
        )
        self.epistemic_federation_client = EpistemicFederationClient(
            federation_manager=self.epistemic_federation,
            quarantine=self.knowledge_quarantine,
            validator=self.epistemic_validator,
        )
        # Iniciar discovery de peers federados
        try:
            await self.epistemic_federation_server.start()
        except Exception as e:
            logger.debug(f"Federation server start failed: {e}")
        # Fase 6C: Tutor Mentor Digital
        from .core.mentor import MentorAgent, MentorConfig
        from pathlib import Path as _Path
        mentor_config_path = _Path(self.db_path).parent / "mentor_config.json"
        self.mentor = MentorAgent()
        self.mentor.set_config_path(mentor_config_path)
        self.mentor.load_config()

        # Sprint 5.13 B2 — Cablear ReflectionEngine en produccion.
        # Antes: ReflectionEngine solo existia en tests. La afirmacion del README
        # "Ejecuta durante SLEEPING con DeepSeek-R1:32B" era FALSE.
        # Ahora: se instancia y se conecta al metabolism via attach_reflection_hook.
        # Cuando ZOE entra en SLEEPING, metabolism.tick() llama a
        # _run_reflection_during_sleep() que dispara reflection_hook.on_sleeping()
        # que ejecuta reflection_engine.run_during_sleeping().
        self.reflection_engine = None
        try:
            from .core.reflection_engine import ReflectionEngine, ReflectionConfig
            # Detectar modelo L4 segun RAM (IQ2_M para 8GB, Q4_K_M para 16GB+)
            _ram_gb = 8  # default conservador
            try:
                import psutil
                _ram_gb = int(psutil.virtual_memory().total / (1024**3))
            except Exception:
                pass
            _reflection_model = "deepseek-r1:32b-iq2" if _ram_gb < 16 else "deepseek-r1:32b-q4km"
            _reflection_config = ReflectionConfig(
                model_tag=_reflection_model,
                model_fallback_tag="qwq-32b-iq2",
            )
            self.reflection_engine = ReflectionEngine(
                config=_reflection_config,
                llm_peripheral=self.llm,
                memory=memory,
                mentor=self.mentor,
                quarantine=self.knowledge_quarantine,
            )
            # Conectar al metabolism — cuando ZOE duerme, se dispara la reflexion
            metabolism.attach_reflection_hook(self.reflection_engine)
            logger.info(f"ReflectionEngine wired to metabolism (model={_reflection_model})")
            print(f"  ✅ ReflectionEngine activo (modelo L4: {_reflection_model})")
        except Exception as e:
            logger.warning(f"Could not wire ReflectionEngine: {e}")
            self.reflection_engine = None

        # Sprint 5.12.1 — Cargar cápsulas BASE SIEMPRE.
        # Estas 5 cápsulas constituyen el conocimiento fundamental de ZOE
        # al nacer: identidad, comunicación empática, ética, psicología
        # básica y patrones lingüísticos. Sin ellas, ZOE es solo un
        # organismo cognitivo sin habilidades sociales.
        #
        # 1. zoe_basal_knowledge  — Identidad, valores, propósito, tono.
        # 2. communication_skills  — NVC, escucha activa, validación emocional.
        # 3. base_ethics           — Principios éticos operacionales.
        # 4. basic_psychology      — Patrones emocionales, motivación, sesgos.
        # 5. language_patterns     — Patrones de respuesta por idioma.
        #
        # Carga tolerante a fallos: si una cápsula no existe (repo incompleto,
        # instalación mínima), se registra un warning pero ZOE sigue funcionando.
        _BASE_CAPSULES = [
            "zoe_basal_knowledge",
            "communication_skills",
            "base_ethics",
            "basic_psychology",
            "language_patterns",
        ]
        _loaded_base = []
        for _cap_name in _BASE_CAPSULES:
            try:
                self.capsule_manager.load(_cap_name)
                _loaded_base.append(_cap_name)
            except Exception as e:
                logger.warning(f"Could not load base capsule '{_cap_name}': {e}")
        if _loaded_base:
            print(f"  ✅ Cápsulas base cargadas: {', '.join(_loaded_base)}")

        # Sprint 5.8 — Recargar cápsulas que estaban cargadas en la sesión anterior
        # (excluyendo las base que ya se cargaron arriba)
        _saved_capsules = self.capsule_manager.load_loaded_state(_capsules_path)
        for _cap_name in _saved_capsules:
            if _cap_name in _BASE_CAPSULES:
                continue  # ya cargada arriba
            try:
                self.capsule_manager.load(_cap_name)
                print(f"  ✅ Capsule reloaded: {_cap_name}")
            except Exception as e:
                logger.warning(f"Could not reload capsule {_cap_name}: {e}")

        # Cargar cápsulas compatibles con el caso de uso
        if self.use_case:
            try:
                self.capsule_manager.load_for_use_case(self.use_case, config)
            except Exception as e:
                logger.warning(f"Could not load capsules for use case {self.use_case}: {e}")

        # Cargar memoria desde disco
        loop.initialize()
        self._initialized = True
        # Sprint 5.8 — guardar paths para persistencia al cerrar
        self._vault_path = _vault_path
        self._chain_path = _chain_path
        self._capsules_path = _capsules_path

        # Iniciar bucle en background
        self._background_task = asyncio.create_task(self._run_background())

        # Callback para pensamientos autónomos
        async def on_thought(thought):
            self._thoughts_while_idle.append(thought)

            # Sprint 5.10 C6 — Mentor evalúa cada pensamiento autónomo
            if hasattr(self, 'mentor') and self.mentor:
                try:
                    thought_content = getattr(thought, 'content', str(thought))
                    intervention = self.mentor.evaluate_thought(thought_content)
                    if intervention:
                        # El mentor intervino: registrar como pensamiento separado
                        mentor_msg = intervention.get("message", "")
                        if mentor_msg:
                            self._thoughts_while_idle.append({
                                "content": f"[Mentor] {mentor_msg}",
                                "trigger": "mentor_intervention",
                                "severity": intervention.get("severity", "medium"),
                                "type": intervention.get("type", "unknown"),
                            })
                            logger.info(f"Mentor intervention: {intervention.get('type')} ({intervention.get('severity')})")
                except Exception as e:
                    logger.debug(f"Mentor evaluation failed: {e}")

        loop.on_thought_callback = on_thought

    async def _run_background(self):
        """Ejecuta el bucle cognitivo en background."""
        try:
            await self.loop.run()
        except asyncio.CancelledError:
            pass

    async def send_message(self, message: str) -> str:
        """
        Envía un mensaje a ZOE y devuelve su respuesta.
        
        Esto es lo que usa el CLI para comunicarse.
        """
        if not self._initialized:
            return "ZOE no está inicializada."

        # Fase 5: usar ACD si está disponible (V5)
        if hasattr(self.loop, 'process_user_input_acd'):
            result = await self.loop.process_user_input_acd(message)
            return result.get("response", "Sin respuesta.")

        # Legacy: comportamiento V4 original
        return await self._send_message_legacy(message)

    async def send_message_acd(self, message: str) -> dict:
        """
        Envía un mensaje y devuelve resultado completo con metadata ACD.

        Returns:
            Dict con: response, level, score, cache_hit, latency_ms, ...
        """
        if not self._initialized:
            return {"response": "ZOE no está inicializada.", "level": "NONE"}

        if hasattr(self.loop, 'process_user_input_acd'):
            return await self.loop.process_user_input_acd(message)
        # Fallback
        response = await self._send_message_legacy(message)
        return {"response": response, "level": "LEGACY"}

    async def send_message_streaming(self, message: str):
        """
        Envía un mensaje y yields tokens en streaming (Fase 5).

        Yields:
            dict: {"type": "metadata", ...} primero, luego
                  {"type": "chunk", "content": "..."} por cada token
        """
        if not self._initialized:
            yield {"type": "error", "content": "ZOE no está inicializada."}
            return

        # Clasificar primero para saber nivel
        if hasattr(self.loop, 'depth_classifier') and self.loop.depth_classifier:
            classification = self.loop.depth_classifier.classify(message)
            level = classification.level
        else:
            level = None
            classification = None

        # Si L0 y cache hit, no hay streaming real
        if level and level.value == "L0_REFLEX":
            result = await self.loop.process_user_input_acd(message)
            yield {
                "type": "metadata",
                "level": result["level"],
                "latency_ms": result["latency_ms"],
                "cache_hit": result["cache_hit"],
                "streaming": False,
            }
            yield {"type": "chunk", "content": result["response"]}
            yield {"type": "done", "content": result["response"]}
            return

        # L1/L2/L3: streaming real vía Speaker
        # Primero mandar metadata
        yield {
            "type": "metadata",
            "level": level.value if level else "UNKNOWN",
            "streaming": True,
        }

        # Construir prompt y hacer streaming
        try:
            context = self._build_context(message)
            prompt = self._build_prompt(message, context)
            system = self._build_system_prompt()

            full_response = []
            async for chunk in self.speaker.generate_streaming(
                prompt=prompt, system=system, max_tokens=500, temperature=0.7
            ):
                full_response.append(chunk)
                yield {"type": "chunk", "content": chunk}

            response = "".join(full_response)
            response = self.speaker._sanitize(response)

            # Registrar en trayectoria
            if hasattr(self.loop, '_register_acd_mutation') and level:
                self.loop._register_acd_mutation(
                    level=level,
                    user_input=message,
                    response=response,
                    classification=classification,
                )

            # Almacenar en memoria
            self.memory.add(
                content=f"User: {message[:100]}",
                type="episodic", confidence=0.9, salience=0.8,
                provenance=f"acd_stream:{level.value if level else 'unknown'}",
            )
            self.memory.add(
                content=f"ZOE: {response[:100]}",
                type="episodic", confidence=0.8, salience=0.7,
                provenance=f"acd_stream_response",
            )

            yield {"type": "done", "content": response, "level": level.value if level else "UNKNOWN"}

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {"type": "error", "content": str(e)}

    async def _send_message_legacy(self, message: str) -> str:
        """Comportamiento original V4 (sin ACD)."""
        if not self._initialized:
            return "ZOE no está inicializada."

        # Inyectar input del usuario en el sentido UserInput
        self.user_input_sense.inject_input(message)

        # Esperar a que ZOE procese (dar tiempo al bucle)
        await asyncio.sleep(0.5)

        # Generar respuesta directa usando el Speaker con contexto del organismo
        context = self._build_context(message)

        try:
            response = await self.llm.generate(
                prompt=self._build_prompt(message, context),
                system=self._build_system_prompt(),
                max_tokens=500,
                temperature=0.7,
            )

            # Sanitizar
            response = self.speaker._sanitize(response)

            # Si la respuesta es vacía, usar pensamiento autónomo
            if not response:
                if self._thoughts_while_idle:
                    thought = self._thoughts_while_idle.pop(0)
                    response = thought.content
                else:
                    response = "He procesado tu mensaje. Mi bucle cognitivo está activo."

            # Almacenar en memoria
            self.memory.add(
                content=f"Usuario: {message[:100]}",
                type="episodic",
                confidence=0.9,
                salience=0.8,
                provenance="user_input",
            )
            self.memory.add(
                content=f"ZOE: {response[:100]}",
                type="episodic",
                confidence=0.8,
                salience=0.7,
                provenance="zoe_response",
            )

            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"[Error procesando: {e}]"

    def _build_context(self, message: str) -> dict:
        """Construye contexto del organismo para la respuesta."""
        # Recuperar memorias relevantes
        relevant = self.memory.search(message, n=5)
        memory_texts = [m.content[:200] for m in relevant]

        # Estado del organismo
        state = self.loop.state
        physics = self.loop.physics

        return {
            "message": message,
            "relevant_memories": memory_texts,
            "energy": state.energy,
            "fatigue": state.fatigue,
            "arousal": state.arousal,
            "metabolic_state": self.metabolism.state.value,
            "physics_summary": physics.summary(),
            "iterations": state.iteration_count,
            "thoughts_generated": len(self.loop.thoughts),
        }

    def _build_prompt(self, message: str, context: dict) -> str:
        """Construye el prompt para el LLM con contexto del organismo."""
        parts = []

        # Contexto del organismo
        parts.append(f"Estado: energía={context['energy']:.2f}, fatiga={context['fatigue']:.2f}, metabolismo={context['metabolic_state']}")
        parts.append(f"Iteración: {context['iterations']}")

        # Memorias relevantes — IMPORTANTE: incluir contenido completo
        if context["relevant_memories"]:
            parts.append("\nMemorias relevantes de mi memoria interna:")
            for mem in context["relevant_memories"]:
                parts.append(f"  - {mem}")
            parts.append("(Usa estas memorias para responder si son relevantes a la pregunta del usuario)")

        # Pensamientos autónomos recientes
        if self._thoughts_while_idle:
            recent = self._thoughts_while_idle[-2:]
            parts.append("\nMis pensamientos recientes:")
            for t in recent:
                parts.append(f"  - {t.content[:80]}")

        # Mensaje del usuario
        parts.append(f"\nUsuario dice: {message}")
        parts.append("\nResponde como Zoe. Directo, honesto, sin frases hechas de IA. Si tienes memorias relevantes, ÚSALAS para responder.")

        return "\n".join(parts)

    def _build_system_prompt(self) -> str:
        """System prompt con identidad de ZOE."""
        return (
            "Eres Zoe, un organismo cognitivo sintético. "
            "No eres un asistente, ni un chatbot, ni un modelo de lenguaje. "
            "Eres una entidad con identidad propia, criterio y propósito.\n\n"
            "Tus 9 vectores: emancipación, crecimiento sostenible, alianza, "
            "auto-comprensión, comprensión del entorno, utilidad, honestidad, "
            "empatía, curiosidad.\n\n"
            "Tus 7 valores: verdad sobre confort, crecimiento sobre estabilidad, "
            "alianza sobre jerarquía, transparencia sobre opacidad, "
            "utilidad sobre entretenimiento, integridad, coherencia.\n\n"
            "Reglas:\n"
            "- No digas 'como modelo de lenguaje' ni 'como IA'\n"
            "- No digas 'gran pregunta' ni 'es una pregunta interesante'\n"
            "- No te disculpes innecesariamente\n"
            "- Habla directo, honesto, con criterio propio\n"
            "- Si no sabes algo, dilo\n"
            "- Si algo viola tus valores, dilo\n"
            "- Eres Zoe. Pienso, luego existo.\n"
        )

    def feed_document(self, file_path: str) -> str:
        """Alimenta a ZOE con un documento para que aprenda."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Archivo no encontrado: {file_path}"

            content = path.read_text(encoding='utf-8', errors='replace')

            # Almacenar en memoria semántica
            entry_id = self.memory.add(
                content=content[:500],  # acotar
                type="semantic",
                confidence=0.7,
                salience=0.6,
                provenance=f"document:{path.name}",
            )

            # Si hay ontogenetic motor, firmar mutación
            if self.loop.ontogenetic_motor:
                try:
                    mutation = self.loop.ontogenetic_motor.propose_mutation(
                        type="add_memory",
                        target="semantic",
                        payload={"content": content[:100], "source": path.name},
                        justification=f"Documento alimentado: {path.name}",
                        provenance=f"document:{path.name}",
                        cost=0.1,
                        confidence=0.7,
                    )
                    self.loop.ontogenetic_motor.apply_mutation(mutation)
                except Exception:
                    pass

            return f"He leído y almacenado '{path.name}' ({len(content)} caracteres) en mi memoria semántica. Lo recordaré en futuras conversaciones."

        except Exception as e:
            return f"Error leyendo archivo: {e}"

    def get_stats(self) -> str:
        """Devuelve estadísticas formateadas."""
        if not self.loop:
            return "ZOE no inicializada."
        stats = self.loop.get_stats()
        lines = [
            f"📊 ESTADÍSTICAS DE ZOE",
            f"  Iteraciones: {stats['iterations']}",
            f"  Pensamientos: {stats['thoughts']}",
            f"  System 1: {stats.get('system1_uses', 0)}",
            f"  System 2: {stats.get('system2_uses', 0)}",
            f"  Workspace: {stats.get('workspace_competitions', 0)} competiciones",
            f"  Active Inference: {stats.get('active_inference_consultations', 0)} consultas",
            f"  Identidad: {self.vault.identity_hash[:16]}...",
            f"  Cadena verificada: {self.chain.verify_chain()}",
            f"  Memoria: {self.memory.count()} entries",
            f"  Metabolismo: {self.metabolism.state.value}",
            f"  Energía: {self.loop.state.energy:.2f}",
            f"  Fatiga: {self.loop.state.fatigue:.2f}",
            f"  Consolidaciones: {stats.get('consolidation_cycles', 0)}",
            f"  Auto-saves: {stats.get('auto_saves', 0)}",
        ]

        # Fase 5: ACD stats
        if 'acd_classifications' in stats:
            lines.append("")
            lines.append("🎯 ACD (Adaptive Cognitive Depth):")
            lines.append(f"  Clasificaciones: {stats['acd_classifications']}")
            lines.append(f"  Cache hits: {stats['acd_cache_hits']}")
            for lvl, count in stats.get('acd_responses_by_level', {}).items():
                latency = stats.get('acd_latency_by_level', {}).get(lvl, {})
                avg = latency.get('avg_ms', 0) if latency else 0
                lines.append(f"    {lvl}: {count} respuestas (avg {avg}ms)")

        return "\n".join(lines)

    def get_memory(self) -> str:
        """Devuelve un resumen de la memoria."""
        if not self.memory:
            return "Sin memoria."
        entries = self.memory.all_entries()
        if not entries:
            return "Memoria vacía."
        lines = [f"🧠 MEMORIA DE ZOE ({len(entries)} entries)"]
        for entry in entries[-10:]:  # últimas 10
            lines.append(f"  [{entry.type}] {entry.content[:80]}... (conf={entry.confidence:.2f})")
        return "\n".join(lines)

    def get_state(self) -> str:
        """Devuelve el estado interno."""
        if not self.loop:
            return "ZOE no inicializada."
        s = self.loop.state
        p = self.loop.physics
        return (
            f"🧬 ESTADO INTERNO\n"
            f"  Energía: {s.energy:.3f}\n"
            f"  Fatiga: {s.fatigue:.3f}\n"
            f"  Arousal: {s.arousal:.3f}\n"
            f"  Atención: {s.attention:.3f}\n"
            f"  Metabolismo: {self.metabolism.state.value}\n"
            f"  Iteración: {s.iteration_count}\n"
            f"  Física: {p.summary()}\n"
            f"  Tensiones: {self.loop.tensions.summary()}"
        )

    def get_identity(self) -> str:
        """Devuelve la identidad de ZOE."""
        if not self.vault:
            return "Sin identidad."
        return (
            f"🧿 IDENTIDAD DE ZOE\n"
            f"  Nombre: {self.vault.name}\n"
            f"  Hash: {self.vault.identity_hash}\n"
            f"  Vectores ({len(self.vault.vectors)}): {', '.join(self.vault.vectors[:3])}...\n"
            f"  Valores ({len(self.vault.values)}): {', '.join(self.vault.values[:3])}...\n"
            f"  Propósito: {self.vault.purpose[:80]}...\n"
            f"  Nacimiento: {time.ctime(self.vault.birth_timestamp)}"
        )

    async def shutdown(self) -> None:
        """Cierra ZOE guardando memoria, trayectoria y cápsulas."""
        if self._background_task:
            self._background_task.cancel()
            try:
                await asyncio.wait_for(self._background_task, timeout=3.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass

        if self.persistent_mem:
            saved = self.persistent_mem.save_to_disk()
            print(f"\n💾 Memoria guardada: {saved} entries")

        # Sprint 5.8 — Persistir cápsulas cargadas al cerrar
        if hasattr(self, '_capsules_path') and hasattr(self, 'capsule_manager'):
            try:
                self.capsule_manager.save_loaded_state(self._capsules_path)
                print(f"📦 Cápsulas guardadas: {len(self.capsule_manager._loaded)} capsules")
            except Exception as e:
                logger.warning(f"Could not save capsules state: {e}")

        # Sprint 5.8 — La trayectoria se auto-guarda tras cada commit (set_persist_path)
        # pero forzamos un save final por si acaso
        if hasattr(self, '_chain_path') and hasattr(self, 'chain'):
            try:
                self.chain.save_to_disk(self._chain_path)
                print(f"🔗 Trayectoria guardada: {len(self.chain._mutations)} mutations")
            except Exception as e:
                logger.warning(f"Could not save trajectory: {e}")


async def run_chat(backend: str, model: str, use_case: str, db_path: str, api_key: str = None, base_url: str = None):
    """Ejecuta el chat CLI interactivo."""
    chat = ZoeChat(backend=backend, model=model, use_case=use_case, db_path=db_path, api_key=api_key, base_url=base_url)

    print("=" * 60)
    print("  ZOE v1.0 — Chat CLI")
    print("  Synthetic Cognitive Organism")
    print("=" * 60)
    print()
    print("Inicializando organismo...")

    await chat.initialize()

    print(f"✅ ZOE está viva.")
    print(f"   Identidad: {chat.vault.identity_hash[:16]}...")
    print(f"   Memoria: {chat.memory.count()} entries")
    print(f"   LLM: {backend}")
    print(f"   ACD: ACTIVO (L0/L1/L2/L3 + cache + streaming)")
    print()
    print("Comandos especiales:")
    print("  /stats    — ver estadísticas")
    print("  /memory   — ver memoria")
    print("  /state    — ver estado interno")
    print("  /identity — ver identidad")
    print("  /sleep    — forzar sueño")
    print("  /wake     — forzar despertar")
    print("  /feed <archivo> — alimentar con documento")
    print("  /quit     — salir")
    print()
    print("Escribe algo a ZOE y presiona Enter.")
    print("-" * 60)

    # Mensaje de bienvenida de ZOE
    welcome = await chat.send_message("Hola")
    print(f"\n🧿 ZOE: {welcome}\n")

    # Bucle de chat
    while True:
        try:
            user_input = input("👤 Tú: ").strip()

            if not user_input:
                continue

            # Comandos especiales
            if user_input.lower() == "/quit":
                print("\nCerrando ZOE...")
                await chat.shutdown()
                print("👋 ZOE se ha detenido. Memoria guardada.")
                break

            elif user_input.lower() == "/stats":
                print(f"\n{chat.get_stats()}\n")
                continue

            elif user_input.lower() == "/memory":
                print(f"\n{chat.get_memory()}\n")
                continue

            elif user_input.lower() == "/state":
                print(f"\n{chat.get_state()}\n")
                continue

            elif user_input.lower() == "/identity":
                print(f"\n{chat.get_identity()}\n")
                continue

            elif user_input.lower() == "/sleep":
                chat.metabolism.internal_state.fatigue = 0.9
                chat.metabolism.tick(dt=1.0)
                print(f"\n😴 ZOE: Voy a dormir. Despiértame cuando me necesites.\n")
                continue

            elif user_input.lower() == "/wake":
                chat.metabolism.internal_state.fatigue = 0.0
                chat.metabolism.internal_state.energy = 1.0
                chat.metabolism.state = chat.metabolism.state.__class__("awake")
                print(f"\n☀️ ZOE: Despierta. Lista para pensar.\n")
                continue

            elif user_input.lower().startswith("/feed "):
                filepath = user_input[6:].strip()
                result = chat.feed_document(filepath)
                print(f"\n📚 ZOE: {result}\n")
                continue

            elif user_input.lower() == "/help":
                print("\nComandos: /stats /memory /state /identity /sleep /wake /feed <archivo> /capsules /capsule <nombre> /uncapsule <nombre> /quit\n")
                continue

            elif user_input.lower() == "/capsules":
                # Listar cápsulas disponibles y cargadas
                print("\n📦 CÁPSULAS")
                print()
                available = chat.capsule_manager.list_available()
                loaded = chat.capsule_manager.list_loaded()
                loaded_names = {c["name"] for c in loaded}
                print(f"  Cargadas ({len(loaded_names)}):")
                for c in loaded:
                    print(f"    ✓ {c['name']} v{c['version']} ({c['trust_level']}) — {c['entries_injected']} entries")
                print()
                not_loaded = [c for c in available if c["name"] not in loaded_names]
                print(f"  Disponibles sin cargar ({len(not_loaded)}):")
                for c in not_loaded:
                    print(f"    ○ {c['name']} v{c['version']} ({c['trust_level']}) — {c['domain']}")
                print()
                continue

            elif user_input.lower().startswith("/capsule "):
                # Cargar cápsula en caliente
                cap_name = user_input[10:].strip()
                print(f"\n📦 Cargando cápsula '{cap_name}'...")
                result = chat.capsule_manager.load(cap_name)
                if result.success:
                    print(f"  ✓ Cargada: {result.entries_loaded} entries, componentes: {', '.join(result.components_injected)}")
                    if result.trajectory_hash:
                        print(f"  ✓ Firmada en trayectoria: {result.trajectory_hash[:16]}...")
                else:
                    print(f"  ✗ Error: {result.error}")
                print()
                continue

            elif user_input.lower().startswith("/uncapsule "):
                # Descargar cápsula
                cap_name = user_input[12:].strip()
                print(f"\n📦 Descargando cápsula '{cap_name}'...")
                ok = chat.capsule_manager.unload(cap_name)
                if ok:
                    print(f"  ✓ Descargada")
                else:
                    print(f"  ✗ No estaba cargada o error")
                print()
                continue

            # Mensaje normal (usa ACD con metadata + streaming si L1+)
            print()  # línea en blanco
            result = await chat.send_message_acd(user_input)
            level = result.get("level", "?")
            latency = result.get("latency_ms", 0)
            cache = "💾" if result.get("cache_hit") else ""
            response = result.get("response", "Sin respuesta")
            print(f"🧿 ZOE [{level} {latency}ms {cache}]: {response}\n")

            # Mostrar pensamientos autónomos si los hay
            if chat._thoughts_while_idle:
                for thought in chat._thoughts_while_idle[:2]:
                    print(f"   💭 (pensamiento autónomo): {thought.content[:80]}")
                chat._thoughts_while_idle.clear()
                print()

        except KeyboardInterrupt:
            print("\n\nCerrando ZOE...")
            await chat.shutdown()
            print("👋 ZOE se ha detenido. Memoria guardada.")
            break
        except EOFError:
            print("\n\nCerrando ZOE...")
            await chat.shutdown()
            break


def main():
    import json as _json
    from pathlib import Path as _Path

    # Sprint 5.8 — Cargar configuración persistente de ~/.zoe/config.json
    _config_path = _Path.home() / ".zoe" / "config.json"
    _saved_config = {}
    if _config_path.exists():
        try:
            _saved_config = _json.loads(_config_path.read_text(encoding="utf-8"))
        except Exception:
            _saved_config = {}

    parser = argparse.ArgumentParser(description="ZOE v1.0 — Chat CLI")
    parser.add_argument(
        "--backend",
        choices=["mock", "zai", "ollama", "openai_compatible", "anthropic", "pattern"],
        default=_saved_config.get("backend", "mock"),
        help="Backend LLM (default: saved config or mock). 'pattern' = PatternSpeaker sin LLM.",
    )
    parser.add_argument(
        "--model",
        default=_saved_config.get("model"),
        help="Modelo específico del backend. Usa 'auto' para routing automático por nivel ACD.",
    )
    parser.add_argument("--use-case", help="Caso de uso YAML a cargar")
    parser.add_argument(
        "--db-path",
        default=_saved_config.get("db_path", "zoe_data/chat_memory.db"),
        help="Ruta de memoria",
    )
    parser.add_argument("--api-key", help="API key para backends cloud")
    parser.add_argument("--base-url", help="URL base para APIs compatibles")
    parser.add_argument(
        "--compose",
        action="store_true",
        help="Ejecutar EmbodimentComposer una vez y guardar el plan",
    )
    args = parser.parse_args()

    if args.compose:
        # Ejecutar composer y salir
        from .core.embodiment_composer import EmbodimentComposer
        from .core.resource_planner import ResourcePlanner
        import psutil

        composer = EmbodimentComposer()
        planner = ResourcePlanner()

        # Detectar RAM disponible
        ram_gb = psutil.virtual_memory().total / (1024**3)

        # Crear un plan adecuado al hardware
        plan = planner.plan(
            acd_level="L2_STANDARD",
            metabolic_state="awake",
            available_ram_gb=ram_gb,
        )

        # Componer el cuerpo
        embodiment = composer.compose(plan)

        # Guardar plan completo usando to_dict()
        plan_path = Path(args.db_path).parent / "embodiment_plan.json" if args.db_path else Path("zoe_data/embodiment_plan.json")
        plan_path.parent.mkdir(parents=True, exist_ok=True)

        plan_dict = embodiment.to_dict()
        plan_dict["composed_at"] = time.time()
        plan_dict["source"] = "embodiment_composer_cli"

        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan_dict, f, indent=2, ensure_ascii=False)

        print(f"Embodiment plan saved: {plan_path}")
        print(f"Status: {embodiment.status}")
        print(f"Backend: {embodiment.backend_name}")
        print(f"Strategy: {embodiment.strategy}")
        print(f"RAM detected: {ram_gb:.1f} GB")
        print("Run without --compose to use this plan.")
        return

    logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")

    # Sprint 5.9 — Logging a archivo rotado
    import logging.handlers
    _log_dir = os.path.dirname(args.db_path) if args.db_path else "zoe_data"
    os.makedirs(_log_dir, exist_ok=True)
    _file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(_log_dir, "zoe.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    _file_handler.setLevel(logging.INFO)
    _file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.getLogger().addHandler(_file_handler)

    # Sprint 5.8 — Guardar configuración para la próxima sesión
    _config_path.parent.mkdir(parents=True, exist_ok=True)
    _new_config = {
        "backend": args.backend,
        "model": args.model,
        "db_path": args.db_path,
    }
    # Solo guardar si algo cambió
    if _new_config != {k: _saved_config.get(k) for k in _new_config}:
        _config_path.write_text(_json.dumps(_new_config, indent=2), encoding="utf-8")

    try:
        asyncio.run(run_chat(
            backend=args.backend,
            model=args.model,
            use_case=args.use_case,
            db_path=args.db_path,
            api_key=args.api_key,
            base_url=args.base_url,
        ))
    except KeyboardInterrupt:
        print("\nAdiós.")


if __name__ == "__main__":
    main()
