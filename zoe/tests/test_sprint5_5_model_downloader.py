"""
Tests Sprint 5.5 — Model Downloader + Modelfile Integration

Valida que ZOE puede descargar modelos IQ2_M de HuggingFace y
registrarlos en Ollama vía Modelfile.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from zoe.core.model_downloader import (
    ModelDownloader, OptimizedModel, ModelSource,
    OPTIMIZED_MODELS,
)


# ============================================================
# 1. Catálogo de modelos optimizados
# ============================================================

class TestOptimizedModelsCatalog:

    def test_catalog_has_models(self):
        """El catálogo tiene modelos."""
        assert len(OPTIMIZED_MODELS) >= 9  # 5 originales + 4 nuevos

    def test_qwen_32b_iq2_exists(self):
        """Qwen 2.5 32B IQ2_M está en el catálogo."""
        assert "qwen2.5:32b-iq2" in OPTIMIZED_MODELS

    def test_qwen_72b_iq2_exists(self):
        """Qwen 2.5 72B IQ2_M está en el catálogo."""
        assert "qwen2.5:72b-iq2" in OPTIMIZED_MODELS

    def test_llama_70b_iq2_exists(self):
        """Llama 3.1 70B IQ2_M está en el catálogo."""
        assert "llama3.1:70b-iq2" in OPTIMIZED_MODELS

    def test_qwq_32b_iq2_exists(self):
        """QwQ-32B IQ2_M está en el catálogo."""
        assert "qwq-32b-iq2" in OPTIMIZED_MODELS
        model = OPTIMIZED_MODELS["qwq-32b-iq2"]
        assert "razonamiento" in model.description.lower()

    def test_qwen_coder_32b_iq2_exists(self):
        """Qwen 2.5 Coder 32B IQ2_M está en el catálogo."""
        assert "qwen2.5-coder-32b-iq2" in OPTIMIZED_MODELS
        model = OPTIMIZED_MODELS["qwen2.5-coder-32b-iq2"]
        assert "programación" in model.description.lower() or "programacion" in model.description.lower()

    def test_gemma_2_9b_iq2_exists(self):
        """Gemma 2 9B IQ2_M está en el catálogo."""
        assert "gemma-2-9b-iq2" in OPTIMIZED_MODELS
        model = OPTIMIZED_MODELS["gemma-2-9b-iq2"]
        assert model.size_gb <= 5.0  # ligero
        assert model.recommended_ram_gb == 4.0  # funciona con poca RAM

    def test_agents_a1_iq2_exists(self):
        """Agents-A1 IQ2_M está en el catálogo."""
        assert "agents-a1-iq2" in OPTIMIZED_MODELS
        model = OPTIMIZED_MODELS["agents-a1-iq2"]
        assert "MoE" in model.display_name or "agente" in model.description.lower()

    def test_all_models_have_hf_repo(self):
        """Todos los modelos tienen repo de HuggingFace."""
        for key, model in OPTIMIZED_MODELS.items():
            assert model.hf_repo, f"{key} has empty hf_repo"
            assert "huggingface.co" not in model.hf_repo  # solo el repo, no la URL

    def test_all_models_have_hf_filename(self):
        """Todos los modelos tienen filename de HuggingFace."""
        for key, model in OPTIMIZED_MODELS.items():
            assert model.hf_filename, f"{key} has empty hf_filename"
            assert model.hf_filename.endswith(".gguf")

    def test_all_models_have_ollama_tag(self):
        """Todos los modelos tienen tag de Ollama."""
        for key, model in OPTIMIZED_MODELS.items():
            assert model.ollama_tag, f"{key} has empty ollama_tag"

    def test_all_models_have_recommended_ram(self):
        """Todos los modelos tienen RAM recomendada."""
        for key, model in OPTIMIZED_MODELS.items():
            assert model.recommended_ram_gb > 0, f"{key} has no recommended_ram_gb"

    def test_all_models_have_estimated_speed(self):
        """Todos los modelos tienen velocidad estimada."""
        for key, model in OPTIMIZED_MODELS.items():
            assert model.estimated_tokens_s, f"{key} has no estimated_tokens_s"

    def test_all_models_have_description(self):
        """Todos los modelos tienen descripción."""
        for key, model in OPTIMIZED_MODELS.items():
            assert model.description, f"{key} has empty description"

    def test_model_sources_are_valid(self):
        """Todas las fuentes son válidas."""
        for model in OPTIMIZED_MODELS.values():
            assert isinstance(model.source, ModelSource)


# ============================================================
# 2. ModelDownloader — creación y listado
# ============================================================

class TestModelDownloader:

    def test_creation(self, tmp_path):
        """Se puede crear ModelDownloader."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        assert downloader is not None

    def test_creates_models_dir(self, tmp_path):
        """Crea el directorio de modelos si no existe."""
        models_dir = tmp_path / "models"
        downloader = ModelDownloader(models_dir=str(models_dir))
        assert models_dir.exists()

    def test_list_available(self, tmp_path):
        """list_available devuelve lista."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.list_available()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_list_available_has_required_fields(self, tmp_path):
        """list_available tiene campos requeridos."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.list_available()
        for item in result:
            assert "key" in item
            assert "display_name" in item
            assert "size_gb" in item
            assert "downloaded" in item
            assert "registered_in_ollama" in item

    def test_get_model_info(self, tmp_path):
        """get_model_info devuelve info del modelo."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        info = downloader.get_model_info("qwen2.5:32b-iq2")
        assert info is not None
        assert info.display_name == "Qwen 2.5 32B (IQ2_M)"

    def test_get_model_info_unknown(self, tmp_path):
        """get_model_info devuelve None para modelo desconocido."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        info = downloader.get_model_info("nonexistent")
        assert info is None


# ============================================================
# 3. ModelDownloader — recomendaciones por RAM
# ============================================================

class TestRecommendForRam:

    def test_recommend_8gb(self, tmp_path):
        """Recomienda modelos para 8GB RAM."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.recommend_for_ram(8.0)
        assert len(result) > 0
        # Qwen 32B IQ2_M debería estar (recommended_ram_gb=8.0)
        keys = [r["key"] for r in result]
        assert "qwen2.5:32b-iq2" in keys

    def test_recommend_4gb(self, tmp_path):
        """Para 4GB, menos modelos recomendados."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.recommend_for_ram(4.0)
        # Los modelos optimizados requieren 8GB mínimo
        # Puede que no haya ninguno para 4GB
        assert isinstance(result, list)

    def test_recommend_sorted_by_size(self, tmp_path):
        """Recomendaciones ordenadas por tamaño (más pequeño primero)."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.recommend_for_ram(32.0)
        sizes = [r["size_gb"] for r in result]
        assert sizes == sorted(sizes)

    def test_recommend_includes_status(self, tmp_path):
        """Recomendaciones incluyen si está descargado/registrado."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.recommend_for_ram(8.0)
        for item in result:
            assert "downloaded" in item
            assert "registered" in item


# ============================================================
# 4. ModelDownloader — registro en Ollama
# ============================================================

class TestOllamaRegistration:

    def test_is_registered_false_when_not_registered(self, tmp_path):
        """_is_registered_in_ollama devuelve False si no está registrado."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="NAME\tSIZE\nqwen2.5:3b\t2GB"
            )
            result = downloader._is_registered_in_ollama("qwen2.5-32b-iq2")
            assert result is False

    def test_is_registered_true_when_registered(self, tmp_path):
        """_is_registered_in_ollama devuelve True si está registrado."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="NAME\tSIZE\nqwen2.5-32b-iq2\t12.5GB"
            )
            result = downloader._is_registered_in_ollama("qwen2.5-32b-iq2")
            assert result is True

    def test_is_registered_false_when_ollama_not_available(self, tmp_path):
        """Si Ollama no está disponible, devuelve False."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = downloader._is_registered_in_ollama("test")
            assert result is False

    def test_generate_modelfile(self, tmp_path):
        """_generate_modelfile genera contenido correcto."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        modelfile = downloader._generate_modelfile(model, "/path/to/model.gguf")

        assert "FROM /path/to/model.gguf" in modelfile
        assert "PARAMETER num_ctx 2048" in modelfile
        assert "PARAMETER num_predict 512" in modelfile
        assert "PARAMETER num_parallel 1" not in modelfile  # Sprint 5.21: removed (unsupported)
        assert "TEMPLATE" in modelfile
        assert "im_start" in modelfile  # Qwen template
        assert "ZOE" in modelfile

    def test_register_in_ollama_success(self, tmp_path):
        """register_in_ollama registra correctamente."""
        downloader = ModelDownloader(models_dir=str(tmp_path))

        # Crear GGUF fake
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        gguf_path.write_bytes(b"fake gguf content")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            with patch.object(downloader, "_is_registered_in_ollama", return_value=False):
                result = downloader.register_in_ollama("qwen2.5:32b-iq2")
                assert result is True

    def test_register_already_registered(self, tmp_path):
        """Si ya está registrado, devuelve True sin hacer nada."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        # Crear GGUF fake para que el path exista
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        gguf_path.write_bytes(b"fake")
        
        with patch.object(downloader, "_is_registered_in_ollama", return_value=True):
            result = downloader.register_in_ollama("qwen2.5:32b-iq2")
            assert result is True

    def test_register_gguf_not_found(self, tmp_path):
        """Si el GGUF no existe, devuelve False."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        with patch.object(downloader, "_is_registered_in_ollama", return_value=False):
            result = downloader.register_in_ollama("qwen2.5:32b-iq2")
            assert result is False

    def test_register_unknown_model(self, tmp_path):
        """Modelo desconocido devuelve False."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.register_in_ollama("nonexistent")
        assert result is False

    def test_register_ollama_not_available(self, tmp_path):
        """Si Ollama no está disponible, devuelve False."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        gguf_path.write_bytes(b"fake")

        with patch("subprocess.run", side_effect=FileNotFoundError):
            with patch.object(downloader, "_is_registered_in_ollama", return_value=False):
                result = downloader.register_in_ollama("qwen2.5:32b-iq2")
                assert result is False


# ============================================================
# 5. ModelDownloader — descarga
# ============================================================

class TestModelDownload:

    def test_download_already_exists(self, tmp_path):
        """Si el archivo ya existe Y es GGUF valido, no descarga."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        # Sprint 5.21: escribir magic bytes GGUF + contenido minimo
        gguf_path.write_bytes(b"GGUF" + b"\x00" * 1024)

        result = downloader.download("qwen2.5:32b-iq2")
        assert result is not None
        assert result == str(gguf_path)

    def test_download_unknown_model(self, tmp_path):
        """Modelo desconocido devuelve None."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        result = downloader.download("nonexistent")
        assert result is None

    def test_download_with_progress_callback(self, tmp_path):
        """Descarga con callback de progreso."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        # Sprint 5.21: escribir magic bytes GGUF + contenido minimo
        gguf_path.write_bytes(b"GGUF" + b"\x00" * 1024)

        progress_calls = []
        def callback(pct, msg):
            progress_calls.append((pct, msg))

        downloader.download("qwen2.5:32b-iq2", progress_callback=callback)
        assert len(progress_calls) > 0
        assert progress_calls[-1][0] == 100.0

    def test_download_and_register_already_downloaded(self, tmp_path):
        """download_and_register con archivo ya descargado."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        # Sprint 5.21: escribir magic bytes GGUF validos
        gguf_path.write_bytes(b"GGUF" + b"\x00" * 1024)

        with patch.object(downloader, "_is_registered_in_ollama", return_value=False):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = downloader.download_and_register("qwen2.5:32b-iq2")
                assert result is True


# ============================================================
# 6. ModelDownloader — stats
# ============================================================

class TestDownloaderStats:

    def test_get_stats(self, tmp_path):
        """get_stats devuelve dict con info."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        stats = downloader.get_stats()
        assert "downloads" in stats
        assert "registrations" in stats
        assert "models_dir" in stats
        assert "available_models" in stats
        assert "downloaded_models" in stats
        assert stats["available_models"] > 0

    def test_stats_downloaded_models_zero_initially(self, tmp_path):
        """Inicialmente no hay modelos descargados."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        stats = downloader.get_stats()
        assert stats["downloaded_models"] == 0

    def test_stats_downloaded_models_after_fake_download(self, tmp_path):
        """Después de crear un GGUF fake, downloaded_models sube."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        gguf_path.write_bytes(b"fake")

        stats = downloader.get_stats()
        assert stats["downloaded_models"] >= 1


# ============================================================
# 7. Integración — estructura completa
# ============================================================

class TestModelDownloaderIntegration:

    def test_all_components_exist(self):
        """Todos los componentes existen."""
        assert ModelDownloader is not None
        assert OptimizedModel is not None
        assert ModelSource is not None
        assert OPTIMIZED_MODELS is not None

    def test_model_source_enum(self):
        """ModelSource enum tiene valores correctos."""
        assert ModelSource.HUGGINGFACE_MRADERMACHER.value == "mradermacher"
        assert ModelSource.HUGGINGFACE_BARTOWSKI.value == "bartowski"
        assert ModelSource.OLLAMA_OFFICIAL.value == "ollama"

    def test_optimized_model_dataclass(self):
        """OptimizedModel es un dataclass con todos los campos."""
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        assert model.name == "qwen2.5:32b-iq2"
        assert model.params_b == 32.0
        assert model.quantization == "IQ2_M"
        assert model.size_gb == 12.5
        assert model.source == ModelSource.HUGGINGFACE_MRADERMACHER

    def test_full_pipeline(self, tmp_path):
        """Pipeline completo: listar → recomendar → descargar (mock) → registrar (mock)."""
        downloader = ModelDownloader(models_dir=str(tmp_path))

        # 1. Listar
        available = downloader.list_available()
        assert len(available) > 0

        # 2. Recomendar
        recommended = downloader.recommend_for_ram(8.0)
        assert len(recommended) > 0

        # 3. Crear GGUF fake
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        gguf_path = tmp_path / model.hf_filename
        gguf_path.write_bytes(b"fake gguf")

        # 4. Registrar (mock)
        with patch.object(downloader, "_is_registered_in_ollama", return_value=False):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = downloader.register_in_ollama("qwen2.5:32b-iq2")
                assert result is True

    def test_modelfile_has_qwen_template(self, tmp_path):
        """El Modelfile generado tiene template de Qwen."""
        downloader = ModelDownloader(models_dir=str(tmp_path))
        model = OPTIMIZED_MODELS["qwen2.5:32b-iq2"]
        modelfile = downloader._generate_modelfile(model, "/path/to/model.gguf")
        assert "im_start" in modelfile
        assert "im_end" in modelfile
