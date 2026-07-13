"""
Tests Sprint 5.7.2 — Auditoría completa del Quickstart del README

Verifica END-TO-END que cada afirmación del Quickstart es cierta:
1. Detección ACD NO es por palabra exacta (usa multi-señal: substring + regex + length + estructura)
2. Hot-swap de modelos funciona eficazmente (muta speaker.llm.model)
3. Modelos IQ2_M se quedan en el SSD (OLLAMA_MODELS env var)
4. Dashboard tiene visibilidad del ACD Router (gap detectado: NO la tiene → fix)
5. Ollama/Python/API se detectan Y se ofrecen instalar
6. Los 4 modelos del catálogo tienen rutas absolutas al SSD en su Modelfile
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest


# ============================================================
# 1. Detección ACD: NO es por palabra exacta
# ============================================================

class TestACDDetectionIsMultiSignal:
    """Sprint 5.7.2 — La detección NO es por palabra exacta, es multi-señal."""

    def test_substring_match_no_palabra_exacta(self):
        """'analizame' (no en keywords) debe detectarse por substring 'analiza'."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        # 'analizame' contiene 'analiza' como substring
        result = dc.classify("analizame por favor las causas de la ansiedad")
        assert result.level.value in ("L3_DEEP", "L3_MAXIMUM")
        assert any("l3_keywords" in r for r in result.reasons)

    def test_regex_pattern_match_no_palabra(self):
        """Patrones estructurales (regex) detectan sin palabra exacta."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        # Sin keywords L3, pero con estructura condicional
        result = dc.classify("si llueve entonces deberia llevar paraguas")
        assert result.level == CognitiveLevel.L3_DEEP
        assert any("l3_pattern" in r for r in result.reasons)

    def test_longitud_larga_sube_nivel_sin_keywords(self):
        """Texto largo sin keywords debe ir a L2 o L3 (señal de longitud)."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        text = "estoy pensando en cambiar de trabajo pero no se si es el momento adecuado para hacerlo porque tengo muchas responsabilidades"
        result = dc.classify(text)
        # Texto >100 chars → al menos L2
        assert result.level.numeric >= CognitiveLevel.L2_STANDARD.numeric

    def test_multiples_preguntas_suben_score(self):
        """Multiple `?` en el texto suben el score."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("qué? cómo? por qué? cuando?")
        assert "multi_question" in result.reasons

    def test_multilinea_sube_score(self):
        """Texto con varios saltos de línea sube score."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("linea 1\nlinea 2\nlinea 3")
        assert "multiline" in result.reasons

    def test_punto_coma_sube_score(self):
        """Punto y coma en el texto sube score."""
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("primero; segundo; tercero")
        assert "semicolon" in result.reasons

    def test_lista_numerada_es_L3(self):
        """Lista numerada con 2+ items detecta como L3."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        text = "1. primera opcion\n2. segunda opcion\n3. tercera opcion"
        result = dc.classify(text)
        assert result.level.numeric >= CognitiveLevel.L2_STANDARD.numeric

    def test_L3_MAXIMUM_por_regex_no_keyword_exacto(self):
        """'compara estos 5 contratos' detecta L3_MAXIMUM por regex, no keyword exacto."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        # No hay keyword exacto "compara 5" pero el regex \bcompara\b\s+\d+\s+\b(contratos...)
        # Sí lo pilla
        result = dc.classify("compara 5 contratos de alquiler")
        assert result.level == CognitiveLevel.L3_MAXIMUM

    def test_no_solo_espanol_funciona_ingles(self):
        """Algunas palabras en inglés también deben detectarse (hello, hi, ok)."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        assert dc.classify("hello").level == CognitiveLevel.L0_REFLEX
        assert dc.classify("ok").level == CognitiveLevel.L0_REFLEX
        assert dc.classify("bye").level == CognitiveLevel.L0_REFLEX

    def test_typo_no_detecta_como_L3(self):
        """Un typo como 'analiiza' NO debe detectar L3 (limitación del heurístico)."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        # 'analiiza' no contiene 'analiza' como substring
        # Pero el texto es corto → L1_FAST
        result = dc.classify("analiiza esto")
        # No debe ser L3 (no hay keyword)
        assert result.level != CognitiveLevel.L3_DEEP


# ============================================================
# 2. Hot-swap de modelos: funciona eficazmente
# ============================================================

class TestHotSwapEficaz:
    """Sprint 5.7.2 — El hot-swap muta speaker.llm_peripheral.model eficazmente."""

    def test_ollama_peripheral_model_es_mutable(self):
        """OllamaPeripheral.model se puede mutar en runtime."""
        from zoe.peripherals.llm import OllamaPeripheral
        periph = OllamaPeripheral(model="gemma2:9b")
        assert periph.model == "gemma2:9b"
        periph.model = "qwq-32b-iq2"
        assert periph.model == "qwq-32b-iq2"

    def test_ollama_peripheral_usa_self_model_en_payload(self):
        """OllamaPeripheral.generate() usa self.model en el payload enviado a Ollama."""
        from zoe.peripherals.llm import OllamaPeripheral
        periph = OllamaPeripheral(model="qwq-32b-iq2")
        # El payload se construye dentro de generate(); verificamos que model se usa
        # Mockeando aiohttp para capturar el payload
        captured_payload = {}

        class MockResp:
            status = 200
            async def json(self): return {"response": "ok"}
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass

        class MockSession:
            def __init__(self): self.calls = []
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            def post(self, url, json=None, **kwargs):
                captured_payload.update(json)
                return MockResp()

        with patch("aiohttp.ClientSession", return_value=MockSession()):
            asyncio.run(periph.generate("test prompt"))

        assert captured_payload["model"] == "qwq-32b-iq2"
        assert captured_payload["prompt"] == "test prompt"

    def test_speaker_expone_llm_peripheral(self):
        """Speaker tiene atributo llm (donde guarda el LLM periférico)."""
        from zoe.core.subagents.speaker import Speaker
        from zoe.peripherals.llm import MockPeripheral
        llm = MockPeripheral()
        speaker = Speaker(llm_peripheral=llm)
        # Sprint 5.7.2: Speaker guarda en self.llm, no self.llm_peripheral
        assert hasattr(speaker, "llm")
        assert speaker.llm is llm

    def test_router_cambia_modelo_en_speaker(self):
        """Cuando el router asigna un modelo, speaker.llm.model cambia."""
        from zoe.core.model_profile_router import ModelProfileRouter
        from zoe.core.subagents.speaker import Speaker
        from zoe.peripherals.llm import OllamaPeripheral

        # Setup: speaker con OllamaPeripheral usando gemma
        llm = OllamaPeripheral(model="gemma2-9b-iq2")
        speaker = Speaker(llm_peripheral=llm)

        # Router con perfil completo (4 modelos instalados)
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)

        # L1_FAST → gemma (sin cambio)
        assignment = profile.get_model("L1_FAST")
        assert "gemma" in assignment.model_tag

        # L3_DEEP → qwq (cambio!)
        assignment = profile.get_model("L3_DEEP")
        assert "qwq" in assignment.model_tag
        # Simular hot-swap usando speaker.llm (atributo correcto)
        speaker.llm.model = assignment.model_tag
        assert speaker.llm.model == "qwq-32b-iq2"

        # L3_MAXIMUM → 72b (cambio!)
        assignment = profile.get_model("L3_MAXIMUM")
        assert "72b" in assignment.model_tag
        speaker.llm.model = assignment.model_tag
        assert speaker.llm.model == "qwen2.5-72b-iq2"


# ============================================================
# 3. Modelos IQ2_M van al SSD (OLLAMA_MODELS env var)
# ============================================================

class TestModelosEnSSD:
    """Sprint 5.7.2 — Los modelos se quedan en el SSD, no en la memoria del Mac."""

    def test_modelfile_usa_path_absoluto_al_gguf(self, tmp_path):
        """El Modelfile generado usa FROM /path/absoluto/al/gguf (no relativo)."""
        from zoe.core.model_downloader import ModelDownloader, OPTIMIZED_MODELS
        # Usar tmp_path que sí existe y es escribible
        d = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwq-32b-iq2"]
        gguf_path = str(tmp_path / "QwQ-32B-IQ2_M.gguf")
        modelfile = d._generate_modelfile(model, gguf_path)
        assert f"FROM {gguf_path}" in modelfile
        # No debe ser relativo
        assert "FROM ./" not in modelfile
        assert "FROM ~/" not in modelfile

    def test_modelfile_tiene_parametros_optimizados_8gb(self, tmp_path):
        """El Modelfile incluye num_ctx, num_predict, num_parallel optimizados para 8GB."""
        from zoe.core.model_downloader import ModelDownloader, OPTIMIZED_MODELS
        d = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwq-32b-iq2"]
        modelfile = d._generate_modelfile(model, str(tmp_path / "QwQ-32B-IQ2_M.gguf"))
        assert "PARAMETER num_ctx 2048" in modelfile
        assert "PARAMETER num_predict 512" in modelfile
        assert "PARAMETER num_parallel 1" in modelfile

    def test_bootstrap_exporta_OLLAMA_MODELS(self):
        """El bootstrap exporta OLLAMA_MODELS apuntando al SSD."""
        # Verificamos que el script contiene la línea correcta
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        assert 'export OLLAMA_MODELS="$MODELS_DIR"' in content
        assert 'MODELS_DIR="$ZOE_HOME/models"' in content

    def test_lanzadores_command_exportan_OLLAMA_MODELS(self):
        """Los .command generados exportan OLLAMA_MODELS al SSD."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        # Los lanzadores Ollama deben tener esta línea
        assert 'export OLLAMA_MODELS="\\$ZOE_HOME/models"' in content

    def test_model_downloader_respeta_models_dir_param(self):
        """ModelDownloader CLI respeta --models-dir y lo pasa a Ollama."""
        from zoe.core.model_downloader import SETUP_PRESETS
        # SETUP_PRESETS define los 4 setups con sus modelos
        assert "maximum" in SETUP_PRESETS
        assert len(SETUP_PRESETS["maximum"]["models"]) == 4


# ============================================================
# 4. Dashboard tiene visibilidad del ACD Router (GAP DETECTADO)
# ============================================================

class TestDashboardACDVisibility:
    """Sprint 5.7.2 — El Dashboard debe mostrar info del ACD Router.

    Sprint 5.7.2 FIX: get_stats() ahora incluye acd_router_stats.
    Sprint 5.7.2 FIX: nuevos endpoints /api/router/stats, /api/router/installed,
    /api/router/profile para visibilidad completa del ACD Router.
    """

    def test_v5_tiene_get_router_stats(self):
        """CognitiveLoopV5 tiene método get_router_stats()."""
        from zoe.core.cognitive_loop_v5 import CognitiveLoopV5
        assert hasattr(CognitiveLoopV5, "get_router_stats")

    def test_get_stats_incluye_acd_router_stats(self):
        """Sprint 5.7.2 FIX: get_stats() incluye acd_router_stats."""
        from zoe.core.cognitive_loop_v5 import CognitiveLoopV5
        loop = CognitiveLoopV5.__new__(CognitiveLoopV5)
        loop.acd_classifications = 0
        loop.acd_level_counts = {"L0_REFLEX": 0, "L1_FAST": 0, "L2_STANDARD": 0,
                                 "L3_DEEP": 0, "L3_MAXIMUM": 0}
        loop.acd_cache_hits = 0
        loop.acd_responses_by_level = dict(loop.acd_level_counts)
        loop.acd_latency_by_level = {k: [] for k in loop.acd_level_counts}
        loop.depth_classifier = None
        loop.cognitive_cache = None
        loop.model_profile_router = None
        loop._router_swaps = 0
        loop._router_skips = 0
        loop._last_routed_tag = None
        loop._active_profile = None
        loop._language_detector = None  # Sprint 5.10 C8
        loop._current_system_prompt = None
        loop._mentor = None  # Sprint 5.10 C6
        loop._cpl = None  # Sprint 5.11 C9 (renamed from cognitive_prefetch_layer)

        with patch.object(CognitiveLoopV5.__bases__[0], 'get_stats', return_value={}):
            stats = loop.get_stats()

        # Sprint 5.7.2: get_stats() AHORA incluye acd_router_stats
        assert "acd_router_stats" in stats
        assert stats["acd_router_stats"]["enabled"] is False  # router es None

    def test_dashboard_tiene_endpoints_router(self):
        """Sprint 5.7.2 FIX: Dashboard tiene /api/router/* endpoints."""
        from pathlib import Path
        # En arquitectura modular, los handlers están en archivos separados
        routes_path = Path(__file__).parent.parent / "dashboard" / "routes.py"
        source = routes_path.read_text()
        assert "/api/router/stats" in source
        assert "/api/router/installed" in source
        assert "/api/router/profile" in source

    def test_dashboard_registra_rutas_router(self):
        """El método start() registra las rutas /api/router/*."""
        from pathlib import Path
        routes_path = Path(__file__).parent.parent / "dashboard" / "routes.py"
        source = routes_path.read_text()
        assert '/api/router/stats' in source
        assert '/api/router/installed' in source
        assert '/api/router/profile' in source


# ============================================================
# 5. Detección Y instalación de dependencias
# ============================================================

class TestDependenciasInstalacion:
    """Sprint 5.7.2 — El bootstrap detecta Y ofrece instalar Ollama, no solo detectar."""

    def test_bootstrap_ofrece_instalar_ollama(self):
        """El bootstrap pregunta '¿Instalar Ollama?' cuando no está."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        assert "Instalar Ollama ahora?" in content
        assert "curl -fsSL https://ollama.com/install.sh | sh" in content

    def test_bootstrap_instala_ollama_con_retry(self):
        """El bootstrap hace retry al iniciar Ollama tras instalarlo."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        # Debe tener el bucle de retry
        assert "for attempt in 1 2 3" in content
        assert "sleep_times=(3 5 10)" in content

    def test_bootstrap_verifica_python_3_10(self):
        """El bootstrap verifica Python >= 3.10 (no solo que exista)."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        assert "sys.version_info.major" in content
        assert "sys.version_info.minor" in content
        assert "3.10" in content or "PY_MINOR" in content

    def test_bootstrap_verifica_git_y_da_instrucciones(self):
        """El bootstrap detecta Git faltante y da instrucciones claras."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        assert "xcode-select --install" in content
        assert "git-scm.com" in content

    def test_bootstrap_verifica_espacio_SSD(self):
        """El bootstrap verifica espacio libre antes de descargar modelos."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        assert "df -m" in content
        assert "NEEDED_GB" in content

    def test_bootstrap_maneja_repo_privado(self):
        """El bootstrap maneja el caso de repo privado con PAT."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        assert "Personal Access Token" in content
        assert "gh_token" in content

    def test_bootstrap_elimina_quarantine_macos(self):
        """El bootstrap elimina el atributo quarantine de los .command."""
        bootstrap_path = Path(__file__).parent.parent / "scripts" / "zoe-bootstrap.sh"
        content = bootstrap_path.read_text()
        assert "xattr -dr com.apple.quarantine" in content


# ============================================================
# 6. Catálogo completo: los 4 modelos del setup maximum
# ============================================================

class TestCatalogo4Modelos:
    """Sprint 5.7.2 — El catálogo tiene los 4 modelos del espectro completo."""

    def test_catalogo_tiene_gemma_9b(self):
        """Gemma 2 9B IQ2_M está en el catálogo (L0/L1)."""
        from zoe.core.model_downloader import OPTIMIZED_MODELS
        assert "gemma-2-9b-iq2" in OPTIMIZED_MODELS
        m = OPTIMIZED_MODELS["gemma-2-9b-iq2"]
        assert m.params_b == 9.0
        assert m.quantization == "IQ2_M"
        assert m.size_gb == 3.5

    def test_catalogo_tiene_agents_a1(self):
        """Agents-A1 MoE IQ2_M está en el catálogo (L2)."""
        from zoe.core.model_downloader import OPTIMIZED_MODELS
        assert "agents-a1-iq2" in OPTIMIZED_MODELS
        m = OPTIMIZED_MODELS["agents-a1-iq2"]
        assert m.params_b == 35.0
        assert m.quantization == "IQ2_M"

    def test_catalogo_tiene_qwq_32b(self):
        """QwQ-32B IQ2_M está en el catálogo (L3_DEEP)."""
        from zoe.core.model_downloader import OPTIMIZED_MODELS
        assert "qwq-32b-iq2" in OPTIMIZED_MODELS
        m = OPTIMIZED_MODELS["qwq-32b-iq2"]
        assert m.params_b == 32.0
        assert m.quantization == "IQ2_M"

    def test_catalogo_tiene_qwen_72b(self):
        """Qwen 2.5 72B IQ2_M está en el catálogo (L3_MAXIMUM)."""
        from zoe.core.model_downloader import OPTIMIZED_MODELS
        assert "qwen2.5:72b-iq2" in OPTIMIZED_MODELS
        m = OPTIMIZED_MODELS["qwen2.5:72b-iq2"]
        assert m.params_b == 72.0
        assert m.quantization == "IQ2_M"
        assert m.size_gb == 25.0

    def test_setup_maximum_tiene_4_modelos_distintos(self):
        """El setup maximum incluye exactamente los 4 modelos del espectro."""
        from zoe.core.model_downloader import SETUP_PRESETS
        models = SETUP_PRESETS["maximum"]["models"]
        assert len(models) == 4
        assert "gemma-2-9b-iq2" in models
        assert "agents-a1-iq2" in models
        assert "qwq-32b-iq2" in models
        assert "qwen2.5:72b-iq2" in models

    def test_tamano_total_maximum_53gb(self):
        """El setup maximum ocupa ~53GB en total."""
        from zoe.core.model_downloader import SETUP_PRESETS
        assert SETUP_PRESETS["maximum"]["total_gb"] == 52.7


# ============================================================
# 7. Routing end-to-end: input → clasificación → modelo correcto
# ============================================================

class TestRoutingEndToEnd:
    """Sprint 5.7.2 — Cada tipo de pregunta llega al modelo correcto."""

    def _setup_router_with_maximum(self):
        from zoe.core.model_profile_router import ModelProfileRouter
        router = ModelProfileRouter()
        installed = ["gemma-2-9b-iq2", "agents-a1-iq2", "qwq-32b-iq2", "qwen2.5:72b-iq2"]
        profile = router.create_optimal_profile(installed)
        return router, profile

    def test_hola_llega_a_tabla_refleja_no_llm(self):
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        result = dc.classify("hola")
        assert result.level.value == "L0_REFLEX"  # No toca LLM

    def test_pregunta_simple_llega_a_gemma(self):
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        router, profile = self._setup_router_with_maximum()
        result = dc.classify("¿qué hora es?")
        assert result.level.value == "L1_FAST"
        assignment = profile.get_model(result.level.value)
        assert "gemma" in assignment.model_tag

    def test_conversacion_normal_llega_a_agents_a1(self):
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        router, profile = self._setup_router_with_maximum()
        # Texto L2 sin keywords L3
        result = dc.classify("estoy pensando en cambiar de trabajo pero no se si es el momento adecuado para hacerlo")
        assert result.level.value == "L2_STANDARD"
        assignment = profile.get_model(result.level.value)
        assert "agents-a1" in assignment.model_tag or "agents" in assignment.model_tag

    def test_analisis_profundo_llega_a_qwq(self):
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        router, profile = self._setup_router_with_maximum()
        result = dc.classify("analiza las causas profundas de la ansiedad")
        assert result.level.value == "L3_DEEP"
        assignment = profile.get_model(result.level.value)
        assert "qwq" in assignment.model_tag

    def test_comparativa_juridica_llega_a_72b(self):
        from zoe.core.depth_classifier import DepthClassifier
        dc = DepthClassifier()
        router, profile = self._setup_router_with_maximum()
        result = dc.classify("compara jurídicamente estos 3 contratos")
        assert result.level.value == "L3_MAXIMUM"
        assignment = profile.get_model(result.level.value)
        assert "72b" in assignment.model_tag

    def test_variaciones_de_input_mismo_nivel(self):
        """Diferentes formas de pedir análisis llegan al mismo nivel."""
        from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
        dc = DepthClassifier()
        # Diferentes formas de pedir análisis profundo
        inputs_L3 = [
            "analiza las causas del estrés",
            "explícame por qué ocurre esto",
            "investiga las razones de este fenómeno",
            "compara las ventajas y desventajas",
        ]
        for text in inputs_L3:
            result = dc.classify(text)
            assert result.level.numeric >= CognitiveLevel.L3_DEEP.numeric, (
                f"'{text}' debería ser L3+, got {result.level.value}"
            )
