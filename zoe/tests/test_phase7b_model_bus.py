"""
Tests Fase 7B — Universal Model Bus (UMB)
"""

import asyncio
import pytest
import time

from zoe.peripherals.model_bus import (
    ModelBus, BackendEntry, SelectionStrategy,
)
from zoe.peripherals.llm import (
    MockPeripheral, LLMPeripheral,
)
from zoe.peripherals.resource_discovery import (
    ResourceGraph, ResourceNode, ResourceType,
)


# ============================================================
# Helpers
# ============================================================

class FakeLLM(LLMPeripheral):
    """LLM fake para tests del bus."""
    def __init__(self, name: str, response: str = "ok", fail: bool = False):
        self._name = name
        self._response = response
        self._fail = fail
        self._call_count = 0

    @property
    def name(self) -> str:
        return self._name

    async def generate(self, prompt, system=None, max_tokens=300, temperature=0.7):
        self._call_count += 1
        if self._fail:
            raise RuntimeError(f"{self._name} failed")
        return self._response

    async def generate_streaming(self, prompt, system=None, max_tokens=300, temperature=0.7):
        if self._fail:
            raise RuntimeError(f"{self._name} failed")
        for word in self._response.split():
            yield word + " "


# ============================================================
# 1. BackendEntry
# ============================================================

class TestBackendEntry:

    def test_to_dict(self):
        entry = BackendEntry(
            peripheral=MockPeripheral(),
            name="test",
            priority=7,
            cost_per_1k=0.02,
            tags=["local", "fast"],
        )
        d = entry.to_dict()
        assert d["name"] == "test"
        assert d["priority"] == 7
        assert d["available"] is True
        assert "local" in d["tags"]


# ============================================================
# 2. ModelBus — registro y gestión
# ============================================================

class TestModelBusRegistration:

    def test_add_backend(self):
        bus = ModelBus()
        bus.add_backend(MockPeripheral(), name="mock1", priority=5)
        assert len(bus.list_backends()) == 1

    def test_add_multiple_backends(self):
        bus = ModelBus()
        bus.add_backend(MockPeripheral(), name="mock1", priority=5)
        bus.add_backend(MockPeripheral(), name="mock2", priority=8)
        assert len(bus.list_backends()) == 2

    def test_remove_backend(self):
        bus = ModelBus()
        bus.add_backend(MockPeripheral(), name="mock1")
        assert bus.remove_backend("mock1") is True
        assert len(bus.list_backends()) == 0

    def test_remove_nonexistent(self):
        bus = ModelBus()
        assert bus.remove_backend("nope") is False

    def test_mark_unavailable(self):
        bus = ModelBus()
        bus.add_backend(MockPeripheral(), name="mock1")
        bus.mark_unavailable("mock1")
        assert bus.get_available_backends() == []

    def test_mark_available(self):
        bus = ModelBus()
        bus.add_backend(MockPeripheral(), name="mock1")
        bus.mark_unavailable("mock1")
        bus.mark_available("mock1")
        assert len(bus.get_available_backends()) == 1

    def test_list_backends(self):
        bus = ModelBus()
        bus.add_backend(MockPeripheral(), name="mock1", priority=3, cost_per_1k=0.01)
        bus.add_backend(MockPeripheral(), name="mock2", priority=8, cost_per_1k=0.05)
        backends = bus.list_backends()
        assert len(backends) == 2
        names = [b["name"] for b in backends]
        assert "mock1" in names
        assert "mock2" in names


# ============================================================
# 3. ModelBus — selección de backend
# ============================================================

class TestModelBusSelection:

    def test_select_by_priority(self):
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        bus.add_backend(FakeLLM("low"), name="low", priority=3)
        bus.add_backend(FakeLLM("high"), name="high", priority=9)
        selected = bus.select_backend()
        assert selected.name == "high"

    def test_select_cheapest(self):
        bus = ModelBus(strategy=SelectionStrategy.CHEAPEST)
        bus.add_backend(FakeLLM("expensive"), name="exp", cost_per_1k=0.05)
        bus.add_backend(FakeLLM("cheap"), name="cheap", cost_per_1k=0.0)
        selected = bus.select_backend()
        assert selected.name == "cheap"

    def test_select_fastest(self):
        bus = ModelBus(strategy=SelectionStrategy.FASTEST)
        bus.add_backend(FakeLLM("slow"), name="slow", latency_ms=2000)
        bus.add_backend(FakeLLM("fast"), name="fast", latency_ms=50)
        selected = bus.select_backend()
        assert selected.name == "fast"

    def test_select_local_first(self):
        bus = ModelBus(strategy=SelectionStrategy.LOCAL_FIRST)
        bus.add_backend(FakeLLM("cloud"), name="cloud", privacy="cloud", priority=9)
        bus.add_backend(FakeLLM("local"), name="local", privacy="local", priority=5)
        selected = bus.select_backend()
        assert selected.name == "local"

    def test_select_round_robin(self):
        bus = ModelBus(strategy=SelectionStrategy.ROUND_ROBIN)
        bus.add_backend(FakeLLM("a"), name="a")
        bus.add_backend(FakeLLM("b"), name="b")
        s1 = bus.select_backend()
        s2 = bus.select_backend()
        # Deben ser distintos en round robin
        assert s1.name != s2.name

    def test_select_acd_aware_l0_prefers_local_fast(self):
        """L0 prefiere local + rápido + gratis."""
        bus = ModelBus(strategy=SelectionStrategy.ACD_AWARE)
        bus.add_backend(FakeLLM("cloud"), name="cloud", priority=9,
                        cost_per_1k=0.03, privacy="cloud", latency_ms=500,
                        tags=["cloud", "quality"])
        bus.add_backend(FakeLLM("local_small"), name="local_small", priority=8,
                        cost_per_1k=0.0, privacy="local", latency_ms=50,
                        tags=["local", "fast", "cheap"])
        selected = bus.select_backend(acd_level="L0_REFLEX")
        assert selected.name == "local_small"

    def test_select_acd_aware_l3_prefers_quality(self):
        """L3 prefiere máxima calidad."""
        bus = ModelBus(strategy=SelectionStrategy.ACD_AWARE)
        bus.add_backend(FakeLLM("local_small"), name="local_small", priority=10,
                        cost_per_1k=0.0, privacy="local", latency_ms=50,
                        tags=["local", "fast", "cheap"])
        bus.add_backend(FakeLLM("cloud_quality"), name="cloud_quality", priority=9,
                        cost_per_1k=0.03, privacy="cloud", latency_ms=800,
                        tags=["cloud", "quality"], max_tokens=8192)
        selected = bus.select_backend(acd_level="L3_DEEP")
        assert selected.name == "cloud_quality"

    def test_select_sensitive_domain_excludes_cloud(self):
        """Dominio sensible excluye cloud."""
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        bus.add_backend(FakeLLM("cloud"), name="cloud", priority=10, privacy="cloud")
        bus.add_backend(FakeLLM("local"), name="local", priority=5, privacy="local")
        selected = bus.select_backend(sensitive_domain=True)
        assert selected.name == "local"

    def test_select_no_backends_available(self):
        bus = ModelBus()
        assert bus.select_backend() is None

    def test_select_all_marked_unavailable(self):
        bus = ModelBus()
        bus.add_backend(FakeLLM("a"), name="a")
        bus.mark_unavailable("a")
        assert bus.select_backend() is None


# ============================================================
# 4. ModelBus — generate con fallback
# ============================================================

class TestModelBusGenerate:

    @pytest.mark.asyncio
    async def test_generate_uses_selected_backend(self):
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        llm1 = FakeLLM("primary", response="response from primary")
        bus.add_backend(llm1, name="primary", priority=10)
        response = await bus.generate("test prompt")
        assert response == "response from primary"
        assert llm1._call_count == 1

    @pytest.mark.asyncio
    async def test_generate_fallback_on_failure(self):
        """Si el backend principal falla, usa el siguiente."""
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        failing = FakeLLM("failing", fail=True)
        working = FakeLLM("working", response="fallback response")
        bus.add_backend(failing, name="failing", priority=10)
        bus.add_backend(working, name="working", priority=5)
        response = await bus.generate("test")
        assert response == "fallback response"

    @pytest.mark.asyncio
    async def test_generate_all_fail(self):
        bus = ModelBus()
        bus.add_backend(FakeLLM("a", fail=True), name="a", priority=10)
        bus.add_backend(FakeLLM("b", fail=True), name="b", priority=5)
        response = await bus.generate("test")
        assert "all backends failed" in response

    @pytest.mark.asyncio
    async def test_generate_no_backends(self):
        bus = ModelBus()
        response = await bus.generate("test")
        assert "no backends available" in response

    @pytest.mark.asyncio
    async def test_generate_marks_unavailable_after_max_fails(self):
        """Tras max_fails, el backend se marca como no disponible."""
        bus = ModelBus()
        bus.add_backend(FakeLLM("failer", fail=True), name="failer", priority=10, max_fails=2)
        bus.add_backend(FakeLLM("backup", response="ok"), name="backup", priority=5)

        # Primera llamada: failer falla, backup funciona
        await bus.generate("test")
        assert bus._backends["failer"].fail_count == 1

        # Segunda llamada: failer falla de nuevo, llega a max_fails
        await bus.generate("test")
        assert bus._backends["failer"].fail_count == 2
        assert bus._backends["failer"].available is False

    @pytest.mark.asyncio
    async def test_generate_acd_aware_selection(self):
        """Generate con acd_level selecciona el backend correcto."""
        bus = ModelBus(strategy=SelectionStrategy.ACD_AWARE)
        local = FakeLLM("local", response="local response")
        cloud = FakeLLM("cloud", response="cloud response")
        bus.add_backend(local, name="local", priority=8, cost_per_1k=0.0,
                        privacy="local", tags=["local", "fast", "cheap"])
        bus.add_backend(cloud, name="cloud", priority=9, cost_per_1k=0.03,
                        privacy="cloud", tags=["cloud", "quality"])

        # L0 → local
        r = await bus.generate("hola", acd_level="L0_REFLEX")
        assert r == "local response"

        # L3 → cloud (quality)
        r = await bus.generate("analiza", acd_level="L3_DEEP")
        assert r == "cloud response"

    @pytest.mark.asyncio
    async def test_generate_sensitive_domain_excludes_cloud(self):
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        local = FakeLLM("local", response="local")
        cloud = FakeLLM("cloud", response="cloud")
        bus.add_backend(cloud, name="cloud", priority=10, privacy="cloud")
        bus.add_backend(local, name="local", priority=5, privacy="local")
        r = await bus.generate("medical advice", sensitive_domain=True)
        assert r == "local"


# ============================================================
# 5. ModelBus — streaming
# ============================================================

class TestModelBusStreaming:

    @pytest.mark.asyncio
    async def test_streaming_from_selected_backend(self):
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        llm = FakeLLM("stream", response="hello world from bus")
        bus.add_backend(llm, name="stream", priority=10, streaming=True)
        chunks = []
        async for chunk in bus.generate_streaming("test"):
            chunks.append(chunk)
        assert len(chunks) > 1
        full = "".join(chunks)
        assert "hello world" in full

    @pytest.mark.asyncio
    async def test_streaming_fallback_to_non_streaming(self):
        """Si el backend seleccionado no soporta streaming, usa generate."""
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        llm = FakeLLM("no_stream", response="non streaming response")
        bus.add_backend(llm, name="no_stream", priority=10, streaming=False)
        chunks = []
        async for chunk in bus.generate_streaming("test"):
            chunks.append(chunk)
        assert len(chunks) == 1
        assert "non streaming" in chunks[0]

    @pytest.mark.asyncio
    async def test_streaming_fallback_on_failure(self):
        """Si el streaming falla, hace fallback a generate."""
        bus = ModelBus(strategy=SelectionStrategy.PRIORITY)
        failing = FakeLLM("fail", fail=True)
        working = FakeLLM("work", response="fallback stream")
        bus.add_backend(failing, name="fail", priority=10, streaming=True)
        bus.add_backend(working, name="work", priority=5, streaming=True)
        chunks = []
        async for chunk in bus.generate_streaming("test"):
            chunks.append(chunk)
        full = "".join(chunks)
        assert "fallback" in full


# ============================================================
# 6. ModelBus — stats y health
# ============================================================

class TestModelBusStats:

    @pytest.mark.asyncio
    async def test_stats_track_requests(self):
        bus = ModelBus()
        bus.add_backend(FakeLLM("a", response="ok"), name="a", priority=10)
        await bus.generate("test1")
        await bus.generate("test2")
        stats = bus.get_stats()
        assert stats["total_requests"] == 2
        assert stats["successful_requests"] == 2
        assert stats["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_stats_track_failures(self):
        bus = ModelBus()
        bus.add_backend(FakeLLM("a", fail=True), name="a", priority=10)
        bus.add_backend(FakeLLM("b", fail=True), name="b", priority=5)
        await bus.generate("test")
        stats = bus.get_stats()
        assert stats["failed_requests"] >= 1

    @pytest.mark.asyncio
    async def test_stats_track_fallbacks(self):
        bus = ModelBus()
        bus.add_backend(FakeLLM("a", fail=True), name="a", priority=10)
        bus.add_backend(FakeLLM("b", response="ok"), name="b", priority=5)
        await bus.generate("test")
        stats = bus.get_stats()
        assert stats["fallback_count"] >= 1

    @pytest.mark.asyncio
    async def test_health_check(self):
        bus = ModelBus()
        assert await bus.health_check() is False
        bus.add_backend(FakeLLM("a"), name="a")
        assert await bus.health_check() is True
        bus.mark_unavailable("a")
        assert await bus.health_check() is False

    def test_stats_show_backends(self):
        bus = ModelBus()
        bus.add_backend(FakeLLM("a"), name="a", priority=7)
        bus.add_backend(FakeLLM("b"), name="b", priority=5)
        stats = bus.get_stats()
        assert stats["total_backends"] == 2
        assert stats["available_backends"] == 2
        assert len(stats["backends"]) == 2


# ============================================================
# 7. ModelBus — from_resource_graph
# ============================================================

class TestModelBusFromResourceGraph:

    def test_from_resource_graph_empty(self):
        """Grafo vacío produce bus vacío."""
        graph = ResourceGraph()
        bus = ModelBus.from_resource_graph(graph)
        assert len(bus.list_backends()) == 0

    def test_from_resource_graph_with_ollama(self):
        """Grafo con Ollama produce backends para cada modelo."""
        graph = ResourceGraph()
        graph.add_node(ResourceNode(
            id="ollama_local",
            type=ResourceType.OLLAMA,
            name="Ollama (local)",
            address="http://localhost:11434",
            models=["qwen2.5:3b", "qwen2.5:7b"],
            privacy_level="local",
            latency_ms=100.0,
        ))
        bus = ModelBus.from_resource_graph(graph)
        backends = bus.list_backends()
        names = [b["name"] for b in backends]
        assert "ollama_qwen2.5:3b" in names
        assert "ollama_qwen2.5:7b" in names

    def test_from_resource_graph_small_model_higher_priority(self):
        """Modelo pequeño (3B) tiene mayor prioridad que grande (7B) para L0."""
        graph = ResourceGraph()
        graph.add_node(ResourceNode(
            id="ollama_local",
            type=ResourceType.OLLAMA,
            name="Ollama",
            address="http://localhost:11434",
            models=["qwen2.5:3b", "qwen2.5:7b"],
            privacy_level="local",
        ))
        bus = ModelBus.from_resource_graph(graph)
        small = bus._backends.get("ollama_qwen2.5:3b")
        large = bus._backends.get("ollama_qwen2.5:7b")
        assert small is not None
        assert large is not None
        # 3B debe tener prioridad >= 7B (rápido para L0)
        assert small.priority >= large.priority

    def test_from_resource_graph_with_cloud(self):
        """Grafo con cloud API produce backend cloud."""
        import os
        os.environ["OPENAI_API_KEY"] = "test-key"
        try:
            graph = ResourceGraph()
            graph.add_node(ResourceNode(
                id="cloud_openai",
                type=ResourceType.CLOUD_API,
                name="OpenAI",
                address="https://api.openai.com/v1",
                models=["gpt-4o"],
                privacy_level="cloud",
                cost_per_1k_tokens=0.03,
                latency_ms=500.0,
            ))
            bus = ModelBus.from_resource_graph(graph)
            backends = bus.list_backends()
            names = [b["name"] for b in backends]
            assert "cloud_openai" in names
        finally:
            del os.environ["OPENAI_API_KEY"]
