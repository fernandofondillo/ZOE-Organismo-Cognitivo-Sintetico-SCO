"""
Tests Fase 7A — Resource Discovery Sense
"""

import asyncio
import pytest
import os
import time

from zoe.peripherals.resource_discovery import (
    ResourceDiscoverySense, ResourceGraph, ResourceNode, ResourceType,
)


class TestResourceGraph:

    def test_add_and_get_node(self):
        g = ResourceGraph()
        node = ResourceNode(id="test1", type=ResourceType.CPU, name="Test CPU")
        g.add_node(node)
        assert g.get_node("test1") is not None
        assert g.get_node("test1").name == "Test CPU"

    def test_remove_node(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="test1", type=ResourceType.CPU, name="Test"))
        g.remove_node("test1")
        assert g.get_node("test1") is None

    def test_get_by_type(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="cpu1", type=ResourceType.CPU, name="CPU1"))
        g.add_node(ResourceNode(id="gpu1", type=ResourceType.GPU, name="GPU1"))
        g.add_node(ResourceNode(id="cpu2", type=ResourceType.CPU, name="CPU2"))
        cpus = g.get_by_type(ResourceType.CPU)
        assert len(cpus) == 2

    def test_get_available_models(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="ollama1", type=ResourceType.OLLAMA, name="Ollama",
                                models=["qwen2.5:3b", "qwen2.5:7b"]))
        g.add_node(ResourceNode(id="cloud1", type=ResourceType.CLOUD_API, name="OpenAI",
                                models=["gpt-4o"]))
        models = g.get_available_models()
        assert "qwen2.5:3b" in models
        assert "gpt-4o" in models
        assert len(models) == 3

    def test_get_ollama_nodes(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="ollama1", type=ResourceType.OLLAMA, name="O1"))
        g.add_node(ResourceNode(id="cpu1", type=ResourceType.CPU, name="C1"))
        ollama = g.get_ollama_nodes()
        assert len(ollama) == 1

    def test_get_cloud_apis(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="openai", type=ResourceType.CLOUD_API, name="OpenAI"))
        g.add_node(ResourceNode(id="anthropic", type=ResourceType.CLOUD_API, name="Claude"))
        apis = g.get_cloud_apis()
        assert len(apis) == 2

    def test_get_local_hardware(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="cpu", type=ResourceType.CPU, name="CPU"))
        g.add_node(ResourceNode(id="gpu", type=ResourceType.GPU, name="GPU"))
        g.add_node(ResourceNode(id="cloud", type=ResourceType.CLOUD_API, name="Cloud"))
        hw = g.get_local_hardware()
        assert len(hw) == 2

    def test_stats(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="cpu", type=ResourceType.CPU, name="CPU"))
        g.add_node(ResourceNode(id="ollama", type=ResourceType.OLLAMA, name="Ollama",
                                models=["qwen2.5:3b"]))
        stats = g.get_stats()
        assert stats["total_nodes"] == 2
        assert stats["available_models"] == 1

    def test_to_dict(self):
        g = ResourceGraph()
        g.add_node(ResourceNode(id="cpu", type=ResourceType.CPU, name="CPU"))
        d = g.to_dict()
        assert "nodes" in d
        assert d["node_count"] == 1
        assert "available_models" in d


class TestResourceDiscoverySense:

    def setup_method(self):
        self.sense = ResourceDiscoverySense(scan_interval=10)

    @pytest.mark.asyncio
    async def test_observe_returns_observations(self):
        """observe() devuelve lista de observaciones."""
        observations = await self.sense.observe()
        assert len(observations) >= 1
        assert observations[0].source == "resource_discovery"

    @pytest.mark.asyncio
    async def test_scan_finds_hardware(self):
        """El scan encuentra al menos CPU local."""
        await self.sense.observe()
        graph = self.sense.get_graph()
        hw = graph.get_local_hardware()
        assert len(hw) >= 1  # al menos CPU

    @pytest.mark.asyncio
    async def test_scan_finds_storage(self):
        """El scan encuentra al menos disco local."""
        await self.sense.observe()
        graph = self.sense.get_graph()
        storage = graph.get_by_type(ResourceType.STORAGE)
        assert len(storage) >= 1  # al menos disco local

    @pytest.mark.asyncio
    async def test_cloud_apis_detected_if_env_set(self):
        """Si OPENAI_API_KEY está en el entorno, se detecta."""
        os.environ["OPENAI_API_KEY"] = "test-key-12345"
        try:
            sense = ResourceDiscoverySense()
            await sense.observe()
            cloud = sense.get_graph().get_cloud_apis()
            assert any("openai" in n.id for n in cloud)
        finally:
            del os.environ["OPENAI_API_KEY"]

    @pytest.mark.asyncio
    async def test_multiple_scans_increment_count(self):
        """Múltiples scans incrementan el contador."""
        await self.sense.observe()
        await self.sense.observe()
        stats = self.sense.get_stats()
        assert stats["scans_performed"] == 2

    @pytest.mark.asyncio
    async def test_graph_has_stats(self):
        await self.sense.observe()
        stats = self.sense.get_stats()
        assert "total_nodes" in stats
        assert "available_nodes" in stats
        assert "by_type" in stats
        assert stats["total_nodes"] >= 2  # CPU + storage mínimo

    def test_add_zoe_peer(self):
        self.sense.add_zoe_peer("zoe_2", "http://192.168.1.100:8642", ["qwen2.5:3b"])
        peers = self.sense.get_graph().get_zoe_peers()
        assert len(peers) == 1
        assert peers[0].name == "ZOE peer: zoe_2"
        assert "qwen2.5:3b" in peers[0].models

    @pytest.mark.asyncio
    async def test_observation_metadata_has_node_count(self):
        observations = await self.sense.observe()
        assert "node_count" in observations[0].metadata
        assert observations[0].metadata["node_count"] >= 2

    @pytest.mark.asyncio
    async def test_observation_metadata_has_models(self):
        observations = await self.sense.observe()
        assert "available_models" in observations[0].metadata
        assert isinstance(observations[0].metadata["available_models"], list)
