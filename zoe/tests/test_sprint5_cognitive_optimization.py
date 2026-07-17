"""
Tests Sprint 5 — Cognitive Optimization Layer (.zmap + CPL + TPE)

Valida las 3 capas de optimización sin deconstruir nada.
"""

import pytest
import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

from zoe.core.cognitive_optimization import (
    ZMAP, ZMAPLoader, ZMAPStrategy,
    LayerInfo, RAMStrategy,
    TensorPredictionEngine,
    CognitivePrefetchLayer, PrefetchResult,
)


# ============================================================
# 1. ZMAP — dataclass y estrategia
# ============================================================

class TestZMAP:

    def test_creation(self):
        """Se puede crear ZMAP."""
        zmap = ZMAP(model="qwen2.5:7b")
        assert zmap.model == "qwen2.5:7b"
        assert zmap.format == "gguf"

    def test_get_strategy_for_ram(self):
        """get_strategy_for_ram devuelve la mejor estrategia."""
        zmap = ZMAP(
            model="test",
            strategies=[
                RAMStrategy(ram_gb=4.0, keep_in_ram=["emb"], mmap=["attn"], prefetch_layers=2, strategy="mmap"),
                RAMStrategy(ram_gb=8.0, keep_in_ram=["emb", "attn"], mmap=["mlp"], prefetch_layers=4, strategy="mmap"),
                RAMStrategy(ram_gb=16.0, keep_in_ram=["all"], mmap=[], prefetch_layers=8, strategy="full"),
            ],
        )
        # 6GB → estrategia de 4GB
        s = zmap.get_strategy_for_ram(6.0)
        assert s is not None
        assert s.ram_gb == 4.0

        # 12GB → estrategia de 8GB
        s = zmap.get_strategy_for_ram(12.0)
        assert s is not None
        assert s.ram_gb == 8.0

        # 2GB → None (no hay estrategia)
        s = zmap.get_strategy_for_ram(2.0)
        assert s is None

    def test_get_zoe_optimization(self):
        """get_zoe_optimization devuelve optimización por ACD."""
        zmap = ZMAP(
            model="test",
            zoe_optimizations={
                "acd_l0reflex": {"use_layers": [0, 1], "pattern_first": True},
                "acd_l3deep": {"use_layers": "all", "pattern_first": False},
                "sensitive_domain": {"require_validation": True},
            },
        )
        opt = zmap.get_zoe_optimization("L0_REFLEX")
        assert opt["pattern_first"] is True

        opt = zmap.get_zoe_optimization("L3_DEEP")
        assert opt["use_layers"] == "all"

    def test_get_zoe_optimization_sensitive(self):
        """Optimización sensible combina ACD + sensitive."""
        zmap = ZMAP(
            model="test",
            zoe_optimizations={
                "acd_l3deep": {"use_layers": "all"},
                "sensitive_domain": {"require_validation": True},
            },
        )
        opt = zmap.get_zoe_optimization("L3_DEEP", sensitive_domain=True)
        assert opt["require_validation"] is True
        assert opt["use_layers"] == "all"

    def test_to_dict_roundtrip(self):
        """to_dict → from_dict roundtrip."""
        zmap = ZMAP(
            model="test",
            layers={"emb": LayerInfo(name="emb", size_gb=0.5, priority="critical", access_pattern="once")},
            strategies=[RAMStrategy(ram_gb=8.0, keep_in_ram=["emb"], mmap=["attn"], prefetch_layers=4, strategy="mmap")],
        )
        d = zmap.to_dict()
        zmap2 = ZMAP.from_dict(d)
        assert zmap2.model == "test"
        assert "emb" in zmap2.layers
        assert len(zmap2.strategies) == 1


# ============================================================
# 2. ZMAPLoader
# ============================================================

class TestZMAPLoader:

    def test_creation(self):
        """Se puede crear ZMAPLoader."""
        loader = ZMAPLoader()
        assert loader is not None

    def test_load_no_zmap(self):
        """load devuelve None si no hay .zmap."""
        loader = ZMAPLoader()
        result = loader.load("nonexistent_model")
        assert result is None

    def test_load_from_file(self, tmp_path):
        """load desde archivo .zmap."""
        zmap_data = {
            "model": "test_model",
            "format": "gguf",
            "version": "1.0",
            "layers": {"emb": {"name": "emb", "size_gb": 0.5, "priority": "critical", "access_pattern": "once"}},
            "strategies": [{"ram_gb": 8.0, "keep_in_ram": ["emb"], "mmap": ["attn"], "prefetch_layers": 4, "strategy": "mmap"}],
            "access_profile": {"total_layers": 32},
            "zoe_optimizations": {"acd_l0reflex": {"pattern_first": True}},
        }
        zmap_path = tmp_path / "test_model.zmap"
        with open(zmap_path, "w") as f:
            json.dump(zmap_data, f)

        loader = ZMAPLoader(zmap_dir=str(tmp_path))
        zmap = loader.load("test_model")
        assert zmap is not None
        assert zmap.model == "test_model"
        assert "emb" in zmap.layers

    def test_load_caches(self, tmp_path):
        """load cachea el .zmap."""
        zmap_data = {"model": "cached_model", "format": "gguf", "version": "1.0"}
        zmap_path = tmp_path / "cached_model.zmap"
        with open(zmap_path, "w") as f:
            json.dump(zmap_data, f)

        loader = ZMAPLoader(zmap_dir=str(tmp_path))
        zmap1 = loader.load("cached_model")
        zmap2 = loader.load("cached_model")
        assert zmap1 is zmap2  # mismo objeto (cacheado)

    def test_generate_default_zmap(self):
        """generate_default_zmap crea .zmap con heurísticas."""
        loader = ZMAPLoader()
        zmap = loader.generate_default_zmap("qwen2.5:7b", params_b=7.0, num_layers=32)
        assert zmap.model == "qwen2.5:7b"
        assert len(zmap.layers) == 4  # embedding, attention, mlp, output
        assert len(zmap.strategies) == 3  # 4GB, 8GB, 16GB
        assert "acd_l0reflex" in zmap.zoe_optimizations
        assert "acd_l3deep" in zmap.zoe_optimizations
        assert "sensitive_domain" in zmap.zoe_optimizations

    def test_save_zmap(self, tmp_path):
        """save_zmap escribe a disco."""
        loader = ZMAPLoader()
        zmap = loader.generate_default_zmap("test", 7.0)
        path = str(tmp_path / "test.zmap")
        loader.save_zmap(zmap, path)
        assert os.path.exists(path)

        # Verificar que se puede cargar
        with open(path) as f:
            data = json.load(f)
        assert data["model"] == "test"

    def test_get_stats(self):
        """get_stats del loader."""
        loader = ZMAPLoader()
        stats = loader.get_stats()
        assert "cached_zmaps" in stats
        assert "cached_models" in stats


# ============================================================
# 3. TensorPredictionEngine (TPE)
# ============================================================

class TestTensorPredictionEngine:

    def test_creation(self):
        """Se puede crear TPE."""
        tpe = TensorPredictionEngine()
        assert tpe is not None

    def test_predict_l0_reflex(self):
        """L0_REFLEX devuelve pattern_first."""
        tpe = TensorPredictionEngine()
        result = tpe.predict("qwen2.5:7b", "L0_REFLEX")
        assert result["pattern_first"] is True
        assert result["reason"].startswith("reflex")

    def test_predict_l1_fast(self):
        """L1_FAST devuelve pattern_first."""
        tpe = TensorPredictionEngine()
        result = tpe.predict("qwen2.5:7b", "L1_FAST")
        assert result["pattern_first"] is True

    def test_predict_l2_standard(self):
        """L2_STANDARD no usa pattern_first."""
        tpe = TensorPredictionEngine()
        result = tpe.predict("qwen2.5:7b", "L2_STANDARD")
        assert result["pattern_first"] is False
        assert result["use_layers"] == "all"

    def test_predict_l3_deep(self):
        """L3_DEEP carga todo."""
        tpe = TensorPredictionEngine()
        result = tpe.predict("qwen2.5:7b", "L3_DEEP")
        assert result["use_layers"] == "all"
        assert result["pattern_first"] is False

    def test_predict_low_energy(self):
        """Energía baja fuerza pattern_first."""
        tpe = TensorPredictionEngine()
        result = tpe.predict("qwen2.5:7b", "L3_DEEP", metabolic_energy=0.2)
        assert result["pattern_first"] is True
        assert "low_energy" in result["reason"]

    def test_predict_with_zmap(self, tmp_path):
        """Con .zmap, usa optimización del .zmap."""
        zmap_data = {
            "model": "test",
            "zoe_optimizations": {
                "acd_l0reflex": {"use_layers": [0, 1], "pattern_first": True, "skip_layers": [2, 3]},
            },
        }
        zmap_path = tmp_path / "test.zmap"
        with open(zmap_path, "w") as f:
            json.dump(zmap_data, f)

        loader = ZMAPLoader(zmap_dir=str(tmp_path))
        tpe = TensorPredictionEngine(loader)
        result = tpe.predict("test", "L0_REFLEX")
        assert result["zmap_used"] is True
        assert result["use_layers"] == [0, 1]

    def test_predict_without_zmap(self):
        """Sin .zmap, usa heurísticas."""
        tpe = TensorPredictionEngine()
        result = tpe.predict("nonexistent", "L0_REFLEX")
        assert result["zmap_used"] is False

    def test_get_stats(self):
        """get_stats del TPE."""
        tpe = TensorPredictionEngine()
        tpe.predict("test", "L0_REFLEX")
        stats = tpe.get_stats()
        assert stats["predictions_made"] == 1


# ============================================================
# 4. CognitivePrefetchLayer (CPL)
# ============================================================

class TestCognitivePrefetchLayer:

    def test_creation(self):
        """Se puede crear CPL."""
        cpl = CognitivePrefetchLayer()
        assert cpl is not None

    def test_prefetch_l0_with_pattern_speaker(self):
        """L0 con PatternSpeaker devuelve pattern_response."""
        import asyncio

        mock_pattern = MagicMock()
        mock_pattern.generate = AsyncMock(return_value="Hola. Estoy aquí, pensando en ti.")

        cpl = CognitivePrefetchLayer(pattern_speaker=mock_pattern)
        result = asyncio.run(cpl.prefetch(
            acd_level="L0_REFLEX",
            user_input="Hola",
        ))

        assert result.pattern_response == "Hola. Estoy aquí, pensando en ti."
        assert result.model_name == "pattern"
        assert "pattern_shortcut" in result.reason

    def test_prefetch_l3_without_pattern(self):
        """L3 sin PatternSpeaker prepara para LLM."""
        import asyncio

        cpl = CognitivePrefetchLayer()
        result = asyncio.run(cpl.prefetch(
            acd_level="L3_DEEP",
            user_input="Analiza este problema",
        ))

        assert result.context_built is True
        assert result.pattern_response is None
        assert "prefetched" in result.reason

    def test_prefetch_with_memory(self):
        """CPL recupera memoria relevante."""
        import asyncio

        mock_memory = MagicMock()
        mock_entry = MagicMock()
        mock_entry.content = "Memoria relevante"
        mock_entry.memory_type = "episodic"
        mock_memory.search = MagicMock(return_value=[mock_entry])

        cpl = CognitivePrefetchLayer()
        result = asyncio.run(cpl.prefetch(
            acd_level="L2_STANDARD",
            user_input="test",
            memory=mock_memory,
        ))

        assert result.context_built is True

    def test_prefetch_low_energy_uses_pattern(self):
        """Energía baja usa PatternSpeaker."""
        import asyncio

        mock_pattern = MagicMock()
        mock_pattern.generate = AsyncMock(return_value="Respuesta desde patrones del sistema.")

        mock_metabolism = MagicMock()
        mock_metabolism.energy = 0.2

        cpl = CognitivePrefetchLayer(pattern_speaker=mock_pattern)
        result = asyncio.run(cpl.prefetch(
            acd_level="L3_DEEP",
            user_input="test",
            metabolic_state=mock_metabolism,
        ))

        assert result.pattern_response == "Respuesta desde patrones del sistema."

    def test_prefetch_pattern_fails_fallback_to_llm(self):
        """Si PatternSpeaker falla, fallback a LLM."""
        import asyncio

        mock_pattern = MagicMock()
        mock_pattern.generate = AsyncMock(side_effect=Exception("Pattern failed"))

        cpl = CognitivePrefetchLayer(pattern_speaker=mock_pattern)
        result = asyncio.run(cpl.prefetch(
            acd_level="L0_REFLEX",
            user_input="test",
        ))

        # Pattern falló, pero CPL no crashea
        assert result.context_built is True or result.pattern_response is None

    def test_prefetch_stats(self):
        """get_stats del CPL."""
        import asyncio

        mock_pattern = MagicMock()
        mock_pattern.generate = AsyncMock(return_value="Hola, estoy aquí pensando en ti.")

        cpl = CognitivePrefetchLayer(pattern_speaker=mock_pattern)
        asyncio.run(cpl.prefetch(acd_level="L0_REFLEX", user_input="Hola"))

        stats = cpl.get_stats()
        assert stats["prefetches"] == 1
        assert stats["pattern_shortcuts"] == 1

    def test_prefetch_with_capsules(self):
        """CPL pasa info de cápsulas al contexto."""
        import asyncio

        cpl = CognitivePrefetchLayer()
        result = asyncio.run(cpl.prefetch(
            acd_level="L2_STANDARD",
            user_input="test",
            capsules=["base_ethics", "basic_psychology"],
        ))

        assert result.context_built is True

    def test_prefetch_time_saved(self):
        """CPL mide tiempo ahorrado."""
        import asyncio

        cpl = CognitivePrefetchLayer()
        result = asyncio.run(cpl.prefetch(
            acd_level="L2_STANDARD",
            user_input="test",
        ))

        assert result.time_saved_ms >= 0


# ============================================================
# 5. Integración — todas las capas juntas
# ============================================================

class TestCognitiveOptimizationIntegration:

    def test_all_components_exist(self):
        """Todos los componentes existen."""
        assert ZMAP is not None
        assert ZMAPLoader is not None
        assert TensorPredictionEngine is not None
        assert CognitivePrefetchLayer is not None

    def test_cpl_uses_tpe(self):
        """CPL usa TPE internamente."""
        cpl = CognitivePrefetchLayer()
        assert cpl.tpe is not None
        assert isinstance(cpl.tpe, TensorPredictionEngine)

    def test_tpe_uses_zmap_loader(self):
        """TPE usa ZMAPLoader internamente."""
        tpe = TensorPredictionEngine()
        assert tpe.zmap_loader is not None
        assert isinstance(tpe.zmap_loader, ZMAPLoader)

    def test_cpl_uses_zmap_loader(self):
        """CPL usa ZMAPLoader internamente."""
        cpl = CognitivePrefetchLayer()
        assert cpl.zmap_loader is not None
        assert isinstance(cpl.zmap_loader, ZMAPLoader)

    def test_full_pipeline(self):
        """Pipeline completo: ZMAP → TPE → CPL."""
        import asyncio

        # 1. Crear ZMAP
        loader = ZMAPLoader()
        zmap = loader.generate_default_zmap("qwen2.5:7b", 7.0)

        # 2. TPE usa ZMAP
        tpe = TensorPredictionEngine(loader)

        # 3. CPL usa TPE
        cpl = CognitivePrefetchLayer(zmap_loader=loader, tpe=tpe)

        # 4. Ejecutar prefetch
        result = asyncio.run(cpl.prefetch(
            acd_level="L0_REFLEX",
            user_input="Hola",
        ))

        assert result is not None
        assert isinstance(result, PrefetchResult)

    def test_zmap_strategy_enum(self):
        """ZMAPStrategy enum tiene valores correctos."""
        assert ZMAPStrategy.FULL_LOAD.value == "full_load"
        assert ZMAPStrategy.MMAP_SEQUENTIAL.value == "mmap_sequential"
        assert ZMAPStrategy.PATTERN_ONLY.value == "pattern_only"

    def test_default_zmap_has_all_acd_levels(self):
        """generate_default_zmap tiene optimizaciones para todos los ACD levels."""
        loader = ZMAPLoader()
        zmap = loader.generate_default_zmap("test", 7.0)
        assert "acd_l0reflex" in zmap.zoe_optimizations
        assert "acd_l1fast" in zmap.zoe_optimizations
        assert "acd_l2standard" in zmap.zoe_optimizations
        assert "acd_l3deep" in zmap.zoe_optimizations

    def test_default_zmap_has_sensitive_domain(self):
        """generate_default_zmap tiene optimización sensitive_domain."""
        loader = ZMAPLoader()
        zmap = loader.generate_default_zmap("test", 7.0)
        assert "sensitive_domain" in zmap.zoe_optimizations
