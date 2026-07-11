"""
Tests Fase 5 — ACD (Adaptive Cognitive Depth) + Streaming

Cubre:
- DepthClassifier: clasificación L0/L1/L2/L3
- CognitiveCache: hit/miss/eviction/TTL
- CognitiveLoopV5: pipeline ramificado + backward compat
- Streaming: Mock/Ollama/OpenAI streaming
- Trayectoria: marca nivel ACD
- Latencia: umbrales por nivel
"""

import asyncio
import time
import pytest
from unittest.mock import MagicMock, AsyncMock

from zoe.core.depth_classifier import (
    DepthClassifier, CognitiveLevel, ClassificationResult,
)
from zoe.core.cognitive_cache import CognitiveCache
from zoe.core.cognitive_loop_v5 import CognitiveLoopV5
from zoe.core.cognitive_loop import Thought, Observation
from zoe.core.state import InternalState
from zoe.core.cognitive_laws import CognitiveLaws
from zoe.core.cognitive_physics import CognitivePhysics
from zoe.core.cognitive_fields import CognitiveFields
from zoe.core.cognitive_tensions import CognitiveTensions
from zoe.core.living_memory import LivingMemory
from zoe.core.intentionality_motor import IntentionalityMotor
from zoe.core.phylogenetic_motor import PhylogeneticMotor, PhylogeneticPool
from zoe.core.world_model import WorldModel
from zoe.core.world_model_v2 import WorldModelV2
from zoe.core.subagents.perceiver import Perceiver
from zoe.core.subagents.forecaster import Forecaster
from zoe.core.subagents.speaker import Speaker
from zoe.core.subagents.critic import Critic
from zoe.alma.identity_vault import IdentityVault
from zoe.alma.trajectory_chain import TrajectoryChain
from zoe.alma.ontogenetic_motor_v2 import OntogeneticMotorV2
from zoe.metabolism.metabolism import Metabolism
from zoe.peripherals.llm import MockPeripheral
from zoe.peripherals.senses import ClockSense, UserInputSense


# =====================================================
# 1. DepthClassifier
# =====================================================

class TestDepthClassifier:
    """Tests del clasificador de profundidad cognitiva."""

    def setup_method(self):
        self.clf = DepthClassifier()

    def test_l0_simple_greeting(self):
        """'hola' debe clasificarse como L0_REFLEX."""
        result = self.clf.classify("hola")
        assert result.level == CognitiveLevel.L0_REFLEX
        assert result.score < 0.2

    def test_l0_ok(self):
        result = self.clf.classify("ok")
        assert result.level == CognitiveLevel.L0_REFLEX

    def test_l0_gracias(self):
        result = self.clf.classify("gracias")
        assert result.level == CognitiveLevel.L0_REFLEX

    def test_l0_bye(self):
        result = self.clf.classify("bye")
        assert result.level == CognitiveLevel.L0_REFLEX

    def test_l0_capitalized(self):
        """'Hola' con mayúscula también L0."""
        result = self.clf.classify("Hola")
        assert result.level == CognitiveLevel.L0_REFLEX

    def test_l0_with_punctuation(self):
        """'hola!' también L0."""
        result = self.clf.classify("hola!")
        assert result.level == CognitiveLevel.L0_REFLEX

    def test_l3_causal_analysis(self):
        """'analiza las causas...' debe ser L3_DEEP."""
        result = self.clf.classify("analiza las causas de la inflación en Europa")
        assert result.level == CognitiveLevel.L3_DEEP
        assert "forced_l3:keyword" in " ".join(result.reasons) or "l3_keywords" in " ".join(result.reasons)

    def test_l3_ethical_dilemma(self):
        result = self.clf.classify("plantea un dilema ético sobre la eutanasia")
        assert result.level == CognitiveLevel.L3_DEEP

    def test_l3_compare(self):
        result = self.clf.classify("compara las ventajas y desventajas de Python vs Rust")
        assert result.level == CognitiveLevel.L3_DEEP

    def test_l3_long_question(self):
        """Pregunta larga y compleja sin keyword L3 explícito debe ser al menos L2."""
        result = self.clf.classify(
            "Me gustaría saber tu opinión detallada sobre el estado actual "
            "de la inteligencia artificial, considerando los avances recientes "
            "en modelos generativos, los riesgos potenciales para la sociedad, "
            "y qué papel deberían jugar los gobiernos en su regulación."
        )
        assert result.level in (CognitiveLevel.L2_STANDARD, CognitiveLevel.L3_DEEP)

    def test_l1_simple_question(self):
        """'¿cómo te llamas?' debe ser L1_FAST."""
        result = self.clf.classify("cómo te llamas?")
        # Puede ser L1 o L2, pero NO L0 ni L3
        assert result.level in (CognitiveLevel.L1_FAST, CognitiveLevel.L2_STANDARD)

    def test_l1_remember(self):
        result = self.clf.classify("recuerdas mi nombre?")
        assert result.level in (CognitiveLevel.L1_FAST, CognitiveLevel.L2_STANDARD)

    def test_empty_input(self):
        """Empty input → L0."""
        result = self.clf.classify("")
        assert result.level == CognitiveLevel.L0_REFLEX

    def test_cache_key_stable(self):
        """Mismo input → mismo cache_key."""
        r1 = self.clf.classify("Hola")
        r2 = self.clf.classify("hola")
        r3 = self.clf.classify("HOLA ")
        assert r1.cache_key == r2.cache_key == r3.cache_key

    def test_cache_key_different(self):
        """Inputs diferentes → cache_keys diferentes."""
        r1 = self.clf.classify("hola")
        r2 = self.clf.classify("adiós")
        assert r1.cache_key != r2.cache_key

    def test_stats_increment(self):
        """Cada classify() incrementa stats."""
        initial = self.clf.classifications
        self.clf.classify("hola")
        self.clf.classify("adiós")
        assert self.clf.classifications == initial + 2
        assert self.clf.level_distribution["L0_REFLEX"] >= 2

    def test_get_stats_format(self):
        self.clf.classify("hola")
        self.clf.classify("analiza esto en profundidad")
        stats = self.clf.get_stats()
        assert "total_classifications" in stats
        assert "level_distribution" in stats
        assert "level_percentages" in stats
        assert stats["total_classifications"] >= 2

    def test_latency_under_50ms(self):
        """Clasificación debe ser <50ms."""
        inputs = ["hola", "¿cómo estás?", "analiza las causas profundas de la guerra"]
        for inp in inputs:
            start = time.time()
            self.clf.classify(inp)
            elapsed_ms = (time.time() - start) * 1000
            assert elapsed_ms < 50, f"Clasificación de '{inp}' tardó {elapsed_ms:.1f}ms"


# =====================================================
# 2. CognitiveCache
# =====================================================

class TestCognitiveCache:

    def test_put_and_get(self):
        cache = CognitiveCache(max_size=10, ttl_seconds=60)
        cache.put("key1", "value1", "L0_REFLEX")
        assert cache.get("key1") == "value1"
        assert cache.hits == 1
        assert cache.misses == 0

    def test_miss(self):
        cache = CognitiveCache()
        assert cache.get("nonexistent") is None
        assert cache.misses == 1
        assert cache.hits == 0

    def test_eviction_lru(self):
        cache = CognitiveCache(max_size=3, ttl_seconds=60)
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        cache.put("k3", "v3")
        # k1 es el más viejo, debería evictarse
        cache.put("k4", "v4")
        assert cache.get("k1") is None  # evicted
        assert cache.get("k4") == "v4"
        assert cache.evictions >= 1

    def test_lru_order_on_get(self):
        """Get debe mover entry al final (más reciente)."""
        cache = CognitiveCache(max_size=2, ttl_seconds=60)
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        # Get k1 → ahora k1 es más reciente
        cache.get("k1")
        # Put k3 → k2 (más viejo) debería evictarse
        cache.put("k3", "v3")
        assert cache.get("k1") == "v1"  # sigue
        assert cache.get("k2") is None  # evicted
        assert cache.get("k3") == "v3"

    def test_ttl_expiration(self):
        """Entradas con TTL expirado no se devuelven."""
        cache = CognitiveCache(max_size=10, ttl_seconds=0)  # TTL 0 = expira inmediatamente
        cache.put("k1", "v1")
        time.sleep(0.01)
        assert cache.get("k1") is None
        assert cache.expirations >= 1

    def test_clear(self):
        cache = CognitiveCache()
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        n = cache.clear()
        assert n == 2
        assert cache.get("k1") is None

    def test_invalidate(self):
        cache = CognitiveCache()
        cache.put("k1", "v1")
        assert cache.invalidate("k1") is True
        assert cache.get("k1") is None
        assert cache.invalidate("nonexistent") is False

    def test_get_stats(self):
        cache = CognitiveCache(max_size=5, ttl_seconds=30)
        cache.put("k1", "v1")
        cache.get("k1")  # hit
        cache.get("k2")  # miss
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
        assert stats["max_size"] == 5
        assert "hit_rate" in stats

    def test_level_distribution(self):
        cache = CognitiveCache()
        cache.put("k1", "v1", "L0_REFLEX")
        cache.put("k2", "v2", "L1_FAST")
        cache.put("k3", "v3", "L0_REFLEX")
        dist = cache._level_distribution()
        assert dist["L0_REFLEX"] == 2
        assert dist["L1_FAST"] == 1


# =====================================================
# 3. CognitiveLoopV5 con ACD
# =====================================================

@pytest.fixture
def zoe_v5_loop():
    """Loop V5 completo con ACD activo y mock LLM."""
    # Reset singleton
    PhylogeneticPool._instance = None

    llm = MockPeripheral(responses=[
        "Respuesta de test.",
        "Otra respuesta.",
        "Pensamiento autónomo.",
    ])

    state = InternalState()
    world_model = WorldModel()
    senses = [ClockSense(), UserInputSense()]
    speaker = Speaker(llm_peripheral=llm)
    subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

    laws = CognitiveLaws()
    physics = CognitivePhysics()
    fields = CognitiveFields()
    tensions = CognitiveTensions()
    memory = LivingMemory()
    intentionality = IntentionalityMotor()
    phylogenetic = PhylogeneticMotor(zoe_id="test_v5")

    vault = IdentityVault(birth_timestamp=time.time())
    chain = TrajectoryChain(organism_id="test_v5")
    ontogenetic = OntogeneticMotorV2(
        identity_vault=vault, trajectory_chain=chain,
        laws=laws, organism_id="test_v5"
    )

    depth_classifier = DepthClassifier()
    cognitive_cache = CognitiveCache(max_size=50, ttl_seconds=60)

    loop = CognitiveLoopV5(
        senses=senses,
        world_model=world_model,
        subagents=subagents,
        state=state,
        tick_interval=0.1,
        laws=laws,
        physics=physics,
        fields=fields,
        tensions=tensions,
        memory=memory,
        intentionality=intentionality,
        phylogenetic=phylogenetic,
        zoe_id="test_v5",
        identity_vault=vault,
        trajectory_chain=chain,
        ontogenetic_motor=ontogenetic,
        metabolism=Metabolism(),
        depth_classifier=depth_classifier,
        cognitive_cache=cognitive_cache,
    )

    return loop


class TestCognitiveLoopV5ACD:

    @pytest.mark.asyncio
    async def test_l0_response_no_llm(self, zoe_v5_loop):
        """L0_REFLEX debe responder sin llamar al LLM."""
        result = await zoe_v5_loop.process_user_input_acd("hola")
        assert result["level"] == "L0_REFLEX"
        assert result["response"]  # no vacía
        assert result["latency_ms"] < 500  # <500ms con mock
        assert result["cache_hit"] is False  # primera vez

    @pytest.mark.asyncio
    async def test_l0_cache_hit(self, zoe_v5_loop):
        """Segunda vez misma entrada L0 → cache hit."""
        await zoe_v5_loop.process_user_input_acd("hola")
        result = await zoe_v5_loop.process_user_input_acd("hola")
        assert result["level"] == "L0_REFLEX"
        assert result["cache_hit"] is True
        # Cache hit debe ser más rápido
        assert result["latency_ms"] < 100

    @pytest.mark.asyncio
    async def test_l1_fast_response(self, zoe_v5_loop):
        """L1_FAST usa Speaker pero no todo el pipeline."""
        result = await zoe_v5_loop.process_user_input_acd("cómo te llamas?")
        assert result["level"] in ("L1_FAST", "L2_STANDARD")
        assert result["response"]

    @pytest.mark.asyncio
    async def test_l3_deep_response(self, zoe_v5_loop):
        """L3_DEEP ejecuta pipeline completo."""
        result = await zoe_v5_loop.process_user_input_acd(
            "analiza en profundidad las causas económicas de la Primera Guerra Mundial"
        )
        assert result["level"] == "L3_DEEP"
        assert result["response"]
        assert result["cost"] == CognitiveLevel.L3_DEEP.cost

    @pytest.mark.asyncio
    async def test_trajectory_marks_acd_level(self, zoe_v5_loop):
        """Cada respuesta registra mutación con acd_level en payload."""
        await zoe_v5_loop.process_user_input_acd("hola")
        await zoe_v5_loop.process_user_input_acd("analiza este tema en profundidad")

        # Verificar cadena
        assert zoe_v5_loop.trajectory_chain.verify_chain()
        mutations = zoe_v5_loop.trajectory_chain.get_active_mutations()
        # Al menos 2 mutaciones registradas
        acd_mutations = [m for m in mutations if m.type == "respond_to_user"]
        assert len(acd_mutations) >= 2

        # Verificar que el payload contiene acd_level
        levels = [m.payload.get("acd_level") for m in acd_mutations]
        assert "L0_REFLEX" in levels
        assert "L3_DEEP" in levels

    @pytest.mark.asyncio
    async def test_stats_include_acd(self, zoe_v5_loop):
        """get_stats() incluye métricas ACD."""
        await zoe_v5_loop.process_user_input_acd("hola")
        await zoe_v5_loop.process_user_input_acd("ok")
        await zoe_v5_loop.process_user_input_acd("analiza esto en profundidad")

        stats = zoe_v5_loop.get_stats()
        assert "acd_classifications" in stats
        assert stats["acd_classifications"] == 3
        assert "acd_level_counts" in stats
        assert "acd_latency_by_level" in stats
        assert "L0_REFLEX" in stats["acd_latency_by_level"]

    @pytest.mark.asyncio
    async def test_backward_compat_no_acd(self):
        """V5 sin depth_classifier debe comportarse como V4 (legacy)."""
        PhylogeneticPool._instance = None
        llm = MockPeripheral(responses=["Legacy response."])
        state = InternalState()
        world_model = WorldModel()
        senses = [ClockSense(), UserInputSense()]
        speaker = Speaker(llm_peripheral=llm)
        subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

        loop = CognitiveLoopV5(
            senses=senses,
            world_model=world_model,
            subagents=subagents,
            state=state,
            tick_interval=0.1,
            laws=CognitiveLaws(),
            physics=CognitivePhysics(),
            fields=CognitiveFields(),
            tensions=CognitiveTensions(),
            memory=LivingMemory(),
            intentionality=IntentionalityMotor(),
            phylogenetic=PhylogeneticMotor(zoe_id="test_compat"),
            zoe_id="test_compat",
            identity_vault=IdentityVault(birth_timestamp=time.time()),
            trajectory_chain=TrajectoryChain(organism_id="test_compat"),
            ontogenetic_motor=OntogeneticMotorV2(
                identity_vault=IdentityVault(birth_timestamp=time.time()),
                trajectory_chain=TrajectoryChain(organism_id="test_compat"),
                laws=CognitiveLaws(),
                organism_id="test_compat",
            ),
            # NO depth_classifier, NO cognitive_cache
        )

        result = await loop.process_user_input_acd("hola")
        assert result["level"] == "LEGACY"  # sin ACD
        assert result["response"]

    @pytest.mark.asyncio
    async def test_l0_latency_under_500ms(self, zoe_v5_loop):
        """L0 con mock debe ser <500ms."""
        for _ in range(5):
            result = await zoe_v5_loop.process_user_input_acd("hola")
            assert result["latency_ms"] < 500, f"L0 tardó {result['latency_ms']}ms"

    @pytest.mark.asyncio
    async def test_l3_latency_can_be_longer(self, zoe_v5_loop):
        """L3 puede tardar más, pero con mock sigue siendo <2s."""
        result = await zoe_v5_loop.process_user_input_acd(
            "diseña un sistema ético completo para gobernar IA"
        )
        assert result["level"] == "L3_DEEP"
        # Mock es rápido, pero permitimos hasta 3s para L3
        assert result["latency_ms"] < 3000


# =====================================================
# 4. Streaming
# =====================================================

class TestStreaming:

    @pytest.mark.asyncio
    async def test_mock_streaming_yields_chunks(self):
        """MockPeripheral.generate_streaming debe yield múltiples chunks."""
        llm = MockPeripheral(responses=["Hola mundo esto es una prueba"])
        chunks = []
        async for chunk in llm.generate_streaming("test"):
            chunks.append(chunk)
        assert len(chunks) > 1  # múltiples palabras
        full = "".join(chunks)
        assert "Hola" in full

    @pytest.mark.asyncio
    async def test_speaker_streaming(self):
        """Speaker.generate_streaming delega al LLM."""
        llm = MockPeripheral(responses=["Respuesta en streaming de prueba"])
        speaker = Speaker(llm_peripheral=llm)

        chunks = []
        async for chunk in speaker.generate_streaming(
            "test prompt", system="test system"
        ):
            chunks.append(chunk)

        assert len(chunks) > 0
        full = "".join(chunks)
        assert "Respuesta" in full or "streaming" in full.lower()

    @pytest.mark.asyncio
    async def test_streaming_no_llm(self):
        """Speaker sin LLM yields mensaje default."""
        speaker = Speaker(llm_peripheral=None)
        chunks = []
        async for chunk in speaker.generate_streaming("test"):
            chunks.append(chunk)
        assert len(chunks) >= 1

    @pytest.mark.asyncio
    async def test_supports_streaming_property(self):
        """Cada backend declara si soporta streaming real."""
        mock = MockPeripheral()
        assert mock.supports_streaming is False  # mock simula

        from zoe.peripherals.llm import OllamaPeripheral, OpenAICompatiblePeripheral
        ollama = OllamaPeripheral()
        assert ollama.supports_streaming is True

        openai_p = OpenAICompatiblePeripheral(api_key="test")
        assert openai_p.supports_streaming is True


# =====================================================
# 5. Integración CLI Chat
# =====================================================

class TestCLIChatACDIntegration:

    @pytest.mark.asyncio
    async def test_zoe_chat_uses_v5(self):
        """ZoeChat debe instanciar V5 con ACD."""
        from zoe.cli_chat import ZoeChat
        chat = ZoeChat(backend="mock", db_path="/tmp/zoe_test_v5.db")
        await chat.initialize()
        try:
            # Verificar que es V5 con ACD
            from zoe.core.cognitive_loop_v5 import CognitiveLoopV5
            assert isinstance(chat.loop, CognitiveLoopV5)
            assert chat.loop.depth_classifier is not None
            assert chat.loop.cognitive_cache is not None

            # Enviar mensaje L0
            result = await chat.send_message_acd("hola")
            assert result["level"] == "L0_REFLEX"
            assert result["response"]

            # Enviar mensaje L3
            result = await chat.send_message_acd(
                "analiza las causas profundas de la desigualdad económica"
            )
            assert result["level"] == "L3_DEEP"
        finally:
            await chat.shutdown()
            # cleanup
            import os
            if os.path.exists("/tmp/zoe_test_v5.db"):
                os.remove("/tmp/zoe_test_v5.db")

    @pytest.mark.asyncio
    async def test_zoe_chat_streaming(self):
        """ZoeChat.send_message_streaming debe yield metadata + chunks + done."""
        from zoe.cli_chat import ZoeChat
        chat = ZoeChat(backend="mock", db_path="/tmp/zoe_test_v5_stream.db")
        await chat.initialize()
        try:
            events = []
            async for event in chat.send_message_streaming("¿cómo estás?"):
                events.append(event)

            # Debe haber al menos: 1 metadata + N chunks + 1 done
            types = [e["type"] for e in events]
            assert "metadata" in types
            assert "done" in types
            # El done debe tener la respuesta completa
            done_event = next(e for e in events if e["type"] == "done")
            assert done_event["content"]
        finally:
            await chat.shutdown()
            import os
            if os.path.exists("/tmp/zoe_test_v5_stream.db"):
                os.remove("/tmp/zoe_test_v5_stream.db")


# =====================================================
# 6. Tests de regresión: V4 sigue funcionando
# =====================================================

class TestV4BackwardCompat:

    @pytest.mark.asyncio
    async def test_v4_still_works_without_acd(self):
        """CognitiveLoopV4 (sin V5) debe seguir funcionando igual."""
        from zoe.core.cognitive_loop_v4 import CognitiveLoopV4
        PhylogeneticPool._instance = None

        llm = MockPeripheral(responses=["Test V4"])
        state = InternalState()
        world_model = WorldModel()
        senses = [ClockSense(), UserInputSense()]
        speaker = Speaker(llm_peripheral=llm)
        subagents = [Perceiver(), Forecaster(world_model), speaker, Critic()]

        loop = CognitiveLoopV4(
            senses=senses,
            world_model=world_model,
            subagents=subagents,
            state=state,
            tick_interval=0.1,
            laws=CognitiveLaws(),
            physics=CognitivePhysics(),
            fields=CognitiveFields(),
            tensions=CognitiveTensions(),
            memory=LivingMemory(),
            intentionality=IntentionalityMotor(),
            phylogenetic=PhylogeneticMotor(zoe_id="test_v4"),
            zoe_id="test_v4",
        )

        # Ejecutar algunos ticks
        await loop._tick()
        await loop._tick()
        assert loop.state.iteration_count >= 2
        assert len(loop.observations) >= 2

    def test_v5_is_subclass_of_v4(self):
        """V5 debe heredar de V4 (sin desconstruir)."""
        from zoe.core.cognitive_loop_v4 import CognitiveLoopV4
        assert issubclass(CognitiveLoopV5, CognitiveLoopV4)
