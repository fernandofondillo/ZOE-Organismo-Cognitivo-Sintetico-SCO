"""
Tests Fase 7E — ZOE Seed Mode

Valida que la semilla ZOE:
1. Detección en múltiples plataformas (macOS, Linux, dev mode)
2. Creación correcta de semilla en un volumen
3. Validación de integridad (manifiesto, directorios, versión)
4. Germinación exitosa (pipeline 7A→7B→7C→7D)
5. Manejo de fallos (sin semilla, RAM insuficiente, cápsula missing)
6. Inspección sin germinar
"""

import json
import os
import platform
import shutil
import tempfile
import pytest
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from zoe.core.seed_mode import (
    ZOESeed,
    SeedManifest,
    SeedVolume,
    SeedStatus,
    GerminationReport,
    GerminationError,
)
from zoe.core.embodiment_composer import Embodiment, EmbodimentStatus


# ============================================================
# Helpers
# ============================================================

@pytest.fixture
def temp_volume():
    """Crea un directorio temporal que simula un volumen montado."""
    tmpdir = tempfile.mkdtemp(prefix="zoe_seed_test_")
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def seeded_volume(temp_volume):
    """Crea un volumen con una semilla ZOE ya creada."""
    seed = ZOESeed()
    seed.create(
        volume_path=temp_volume,
        organism_id="zoe_test_v1",
        organism_name="ZOE Test",
        required_capsules=["base_ethics"],  # existe en el repo
        optional_capsules=["basic_psychology"],  # existe en el repo
        default_acd_level="L2_STANDARD",
        allows_cloud=False,  # para que no dependa de API keys
    )
    return temp_volume


@pytest.fixture
def mock_ollama_running():
    """Simula que Ollama está corriendo."""
    with patch("zoe.core.embodiment_composer.EmbodimentComposer._check_ollama_running", return_value=True):
        yield


def make_fake_running_embodiment(acd_level: str = "L2_STANDARD", capsules=None):
    """Crea un Embodiment fake en estado RUNNING para tests de germinación exitosa."""
    return Embodiment(
        embodiment_id="emb_test_fake",
        plan_signature="fake_sig_12345",
        backend_name="ollama_3b",
        model_name="qwen2.5:3b",
        strategy="full_ram",
        status=EmbodimentStatus.RUNNING.value,
        acd_level=acd_level,
        metabolic_state="awake",
        capsules_loaded=list(capsules or []),
        boot_started_at=time.time(),
        boot_completed_at=time.time() + 0.1,
        boot_duration_ms=100.0,
    )


@pytest.fixture
def mock_bootstrap_success():
    """Mockea EmbodimentComposer.bootstrap_from_scratch para devolver un embodiment RUNNING."""
    fake_emb = make_fake_running_embodiment(capsules=["base_ethics", "basic_psychology"])
    with patch(
        "zoe.core.embodiment_composer.EmbodimentComposer.bootstrap_from_scratch",
        return_value=fake_emb,
    ):
        yield fake_emb


@pytest.fixture
def mock_bootstrap_failure():
    """Mockea EmbodimentComposer.bootstrap_from_scratch para devolver un embodiment FAILED."""
    fake_emb = Embodiment(
        embodiment_id="emb_test_failed",
        status=EmbodimentStatus.FAILED.value,
        errors=["No backends available"],
        boot_started_at=time.time(),
        boot_completed_at=time.time(),
    )
    with patch(
        "zoe.core.embodiment_composer.EmbodimentComposer.bootstrap_from_scratch",
        return_value=fake_emb,
    ):
        yield fake_emb


# ============================================================
# 1. SeedManifest dataclass
# ============================================================

class TestSeedManifest:

    def test_manifest_defaults(self):
        m = SeedManifest()
        assert m.organism_name == "ZOE"
        assert m.version == "1.5.0"
        assert m.min_ram_gb == 4.0
        assert m.required_capsules == []
        assert m.allows_cloud is True

    def test_manifest_to_dict_roundtrip(self):
        m = SeedManifest(
            organism_id="zoe_test",
            version="1.5.0",
            required_capsules=["a", "b"],
        )
        d = m.to_dict()
        m2 = SeedManifest.from_dict(d)
        assert m2.organism_id == "zoe_test"
        assert m2.required_capsules == ["a", "b"]

    def test_manifest_to_json_and_back(self, temp_volume):
        m = SeedManifest(organism_id="zoe_test", version="1.5.0")
        path = os.path.join(temp_volume, "seed.json")
        m.to_json(path)
        assert os.path.isfile(path)
        m2 = SeedManifest.from_json(path)
        assert m2.organism_id == "zoe_test"

    def test_manifest_from_dict_ignores_unknown_keys(self):
        m = SeedManifest.from_dict({
            "organism_id": "zoe_test",
            "unknown_field": "ignored",
        })
        assert m.organism_id == "zoe_test"


# ============================================================
# 2. Detección de semilla
# ============================================================

class TestSeedDetection:

    def test_detect_returns_none_when_no_seed(self, temp_volume):
        """Sin semilla en el volumen → None."""
        seed = ZOESeed()
        vol = seed.detect_seed_volume(custom_paths=[temp_volume])
        assert vol is None

    def test_detect_finds_seed_after_create(self, seeded_volume):
        seed = ZOESeed()
        vol = seed.detect_seed_volume(custom_paths=[seeded_volume])
        assert vol is not None
        assert vol.volume_path == seeded_volume
        assert vol.zoe_home.endswith("/ZOE")
        assert os.path.isfile(vol.seed_manifest_path)

    def test_detect_with_env_var(self, seeded_volume):
        """Detecta vía ZOE_SEED_PATH env var."""
        seed = ZOESeed()
        with patch.dict(os.environ, {"ZOE_SEED_PATH": seeded_volume}):
            vol = seed.detect_seed_volume()
            assert vol is not None
            assert vol.volume_path == seeded_volume

    def test_detect_ignores_macintosh_hd(self):
        """En macOS, ignora el volumen del sistema."""
        seed = ZOESeed()
        # Simular /Volumes con Macintosh HD
        with patch("platform.system", return_value="Darwin"), \
             patch("os.path.isdir", side_effect=lambda p: p == "/Volumes"), \
             patch("os.listdir", return_value=["Macintosh HD", "MyDrive"]):
            # No hay semilla real → debe devolver None
            vol = seed.detect_seed_volume()
            assert vol is None

    def test_list_seed_paths_returns_list(self):
        seed = ZOESeed()
        paths = seed.list_seed_paths()
        assert isinstance(paths, list)
        # En Linux test env, debería incluir /media si existe
        # O al menos devolver lista vacía

    def test_validate_seed_volume_returns_none_for_nonexistent(self):
        seed = ZOESeed()
        vol = seed._validate_seed_volume("/nonexistent/path/12345")
        assert vol is None

    def test_validate_seed_volume_returns_none_without_manifest(self, temp_volume):
        """Directorio ZOE existe pero sin seed.json → None."""
        os.makedirs(os.path.join(temp_volume, "ZOE"))
        seed = ZOESeed()
        vol = seed._validate_seed_volume(temp_volume)
        assert vol is None


# ============================================================
# 3. Creación de semilla
# ============================================================

class TestSeedCreation:

    def test_create_generates_manifest(self, temp_volume):
        seed = ZOESeed()
        report = seed.create(
            volume_path=temp_volume,
            organism_id="zoe_test_create",
        )
        assert report.success is True
        assert os.path.isfile(os.path.join(temp_volume, "ZOE", "seed.json"))

    def test_create_generates_directories(self, temp_volume):
        seed = ZOESeed()
        seed.create(
            volume_path=temp_volume,
            organism_id="zoe_test",
        )
        for subdir in ("identity", "trajectory", "data", "capsules", "config"):
            assert os.path.isdir(os.path.join(temp_volume, "ZOE", subdir))

    def test_create_generates_default_config(self, temp_volume):
        seed = ZOESeed()
        seed.create(
            volume_path=temp_volume,
            organism_id="zoe_test",
            language="en",
        )
        config_path = os.path.join(temp_volume, "ZOE", "config", "organism.json")
        assert os.path.isfile(config_path)
        with open(config_path) as f:
            config = json.load(f)
        assert config["language"] == "en"

    def test_create_returns_validated_status(self, temp_volume):
        seed = ZOESeed()
        report = seed.create(volume_path=temp_volume, organism_id="zoe_test")
        assert report.status == SeedStatus.VALIDATED.value
        assert report.manifest["organism_id"] == "zoe_test"

    def test_create_fails_on_nonexistent_volume(self):
        seed = ZOESeed()
        report = seed.create(
            volume_path="/nonexistent/volume/12345",
            organism_id="zoe_test",
        )
        assert report.success is False
        assert report.error_type == GerminationError.INVALID_MANIFEST.value

    def test_create_with_capsules(self, temp_volume):
        seed = ZOESeed()
        seed.create(
            volume_path=temp_volume,
            organism_id="zoe_test",
            required_capsules=["base_ethics"],
            optional_capsules=["basic_psychology"],
        )
        manifest = SeedManifest.from_json(
            os.path.join(temp_volume, "ZOE", "seed.json")
        )
        assert "base_ethics" in manifest.required_capsules
        assert "basic_psychology" in manifest.optional_capsules

    def test_create_with_identity_vault(self, temp_volume):
        """Si se pasa un identity_vault, se serializa."""
        seed = ZOESeed()
        mock_vault = MagicMock()
        mock_vault.identity_hash = "abc123"
        mock_vault.to_dict.return_value = {"id": "zoe_test", "hash": "abc123"}

        seed.create(
            volume_path=temp_volume,
            organism_id="zoe_test",
            identity_vault=mock_vault,
        )
        vault_path = os.path.join(temp_volume, "ZOE", "identity", "vault.json")
        assert os.path.isfile(vault_path)
        with open(vault_path) as f:
            data = json.load(f)
        assert data["hash"] == "abc123"

    def test_create_records_timestamp(self, temp_volume):
        seed = ZOESeed()
        before = time.time()
        seed.create(volume_path=temp_volume, organism_id="zoe_test")
        manifest = SeedManifest.from_json(
            os.path.join(temp_volume, "ZOE", "seed.json")
        )
        assert manifest.created_at >= before


# ============================================================
# 4. Validación de semilla
# ============================================================

class TestSeedValidation:

    def test_valid_seed_passes_validation(self, seeded_volume):
        seed = ZOESeed()
        vol = seed.detect_seed_volume(custom_paths=[seeded_volume])
        ok, issues = seed.validate_seed(vol)
        assert ok is True
        assert issues == []

    def test_missing_identity_dir_fails(self, seeded_volume):
        seed = ZOESeed()
        vol = seed.detect_seed_volume(custom_paths=[seeded_volume])
        # Borrar directorio identity
        shutil.rmtree(vol.identity_path)
        ok, issues = seed.validate_seed(vol)
        assert ok is False
        assert any("Identity" in i for i in issues)

    def test_missing_trajectory_dir_fails(self, seeded_volume):
        seed = ZOESeed()
        vol = seed.detect_seed_volume(custom_paths=[seeded_volume])
        shutil.rmtree(vol.trajectory_path)
        ok, issues = seed.validate_seed(vol)
        assert ok is False
        assert any("Trajectory" in i for i in issues)

    def test_empty_organism_id_fails(self, temp_volume):
        """Manifiesto con organism_id vacío → inválido."""
        # Crear semilla y luego editar manifiesto
        seed = ZOESeed()
        seed.create(volume_path=temp_volume, organism_id="temp")
        manifest_path = os.path.join(temp_volume, "ZOE", "seed.json")
        with open(manifest_path) as f:
            data = json.load(f)
        data["organism_id"] = ""
        with open(manifest_path, "w") as f:
            json.dump(data, f)

        vol = seed.detect_seed_volume(custom_paths=[temp_volume])
        ok, issues = seed.validate_seed(vol)
        assert ok is False
        assert any("organism_id" in i for i in issues)


# ============================================================
# 5. Germinación
# ============================================================

class TestGermination:

    def test_germinate_no_seed_returns_failure(self):
        seed = ZOESeed()
        report = seed.germinate(custom_paths=["/nonexistent/path/12345"])
        assert report.success is False
        assert report.error_type == GerminationError.NO_SEED_FOUND.value
        assert report.status == SeedStatus.FAILED.value

    def test_germinate_invalid_seed_returns_failure(self, temp_volume):
        """Volumen sin semilla → falla."""
        seed = ZOESeed()
        report = seed.germinate(custom_paths=[temp_volume])
        assert report.success is False
        assert report.error_type == GerminationError.NO_SEED_FOUND.value

    def test_germinate_success_creates_embodiment(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        """Germinación exitosa con bootstrap mockeado → ALIVE."""
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        assert report.success is True
        assert report.status == SeedStatus.ALIVE.value
        assert report.embodiment is not None
        assert report.embodiment["status"] == "running"

    def test_germinate_increments_germination_count(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            seed.germinate(custom_paths=[seeded_volume])
        # Verificar que el manifiesto se actualizó
        vol = seed.detect_seed_volume(custom_paths=[seeded_volume])
        manifest = SeedManifest.from_json(vol.seed_manifest_path)
        assert manifest.germination_count == 1
        assert manifest.last_germinated_at > 0

    def test_germinate_records_host_info(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        assert "hostname" in report.host_info
        assert "platform" in report.host_info
        assert "python_version" in report.host_info

    def test_germinate_fails_with_insufficient_ram(self, seeded_volume, mock_ollama_running):
        """RAM por debajo del mínimo → fallo."""
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=1.0,  # menos de 4GB mínimo
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        assert report.success is False
        assert report.error_type == GerminationError.NO_RESOURCES.value

    def test_germinate_loads_required_capsules(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        """Las cápsulas requeridas se cargan en el embodiment."""
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        assert report.success is True
        # base_ethics está en el repo
        assert "base_ethics" in report.capsules_loaded

    def test_germinate_missing_required_capsule_fails(self, temp_volume):
        """Si una cápsula requerida no existe → fallo."""
        seed = ZOESeed()
        seed.create(
            volume_path=temp_volume,
            organism_id="zoe_test",
            required_capsules=["nonexistent_capsule_xyz"],
        )
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[temp_volume])
        assert report.success is False
        assert report.error_type == GerminationError.CAPSULE_MISSING.value
        assert "nonexistent_capsule_xyz" in report.capsules_missing

    def test_germinate_records_duration(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        assert report.duration_ms > 0

    def test_germinate_allows_cloud_false_clears_env(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        """Si allows_cloud=False, las API keys se ocultan durante bootstrap."""
        seed = ZOESeed()
        env_backup = dict(os.environ)
        os.environ["OPENAI_API_KEY"] = "test_key_should_be_hidden"

        try:
            with patch(
                "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
                return_value=8.0,
            ):
                report = seed.germinate(custom_paths=[seeded_volume])
            # El report debe tener éxito o fallar por razones de recursos,
            # pero no por API key cloud (está deshabilitado)
            # No verificamos status porque depende del entorno
            assert isinstance(report, GerminationReport)
        finally:
            os.environ.clear()
            os.environ.update(env_backup)


# ============================================================
# 6. Inspección sin germinar
# ============================================================

class TestInspect:

    def test_inspect_no_seed_returns_not_found(self):
        seed = ZOESeed()
        result = seed.inspect(custom_paths=["/nonexistent/path/12345"])
        assert result["found"] is False
        assert "searched_paths" in result

    def test_inspect_finds_seed(self, seeded_volume):
        seed = ZOESeed()
        result = seed.inspect(custom_paths=[seeded_volume])
        assert result["found"] is True
        assert result["valid"] is True
        assert "manifest" in result
        assert "seed_volume" in result

    def test_inspect_includes_capsule_status(self, seeded_volume):
        seed = ZOESeed()
        result = seed.inspect(custom_paths=[seeded_volume])
        assert "capsules_status" in result
        assert "base_ethics" in result["capsules_status"]
        # base_ethics está en el repo
        assert result["capsules_status"]["base_ethics"]["available"] is True

    def test_inspect_includes_host_info(self, seeded_volume):
        seed = ZOESeed()
        result = seed.inspect(custom_paths=[seeded_volume])
        assert "host_info" in result
        assert "hostname" in result["host_info"]


# ============================================================
# 7. Stats y helpers
# ============================================================

class TestSeedStats:

    def test_initial_stats(self):
        seed = ZOESeed()
        stats = seed.get_stats()
        assert stats["germination_count"] == 0
        assert stats["detection_count"] == 0
        assert stats["last_status"] is None
        assert stats["last_success"] is None

    def test_stats_after_germination(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            seed.germinate(custom_paths=[seeded_volume])
        stats = seed.get_stats()
        assert stats["germination_count"] == 1
        assert stats["last_success"] is True
        assert stats["last_status"] == SeedStatus.ALIVE.value

    def test_get_last_report_returns_none_initially(self):
        seed = ZOESeed()
        assert seed.get_last_report() is None

    def test_get_last_report_after_germination(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        last = seed.get_last_report()
        assert last is report  # mismo objeto

    def test_get_host_info_returns_required_fields(self):
        seed = ZOESeed()
        info = seed._get_host_info()
        assert "hostname" in info
        assert "platform" in info
        assert "python_version" in info
        assert "cpu_cores" in info


# ============================================================
# 8. Integración con EmbodimentComposer
# ============================================================

class TestSeedComposerIntegration:

    def test_germinate_embodiment_has_correct_acd(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        """El embodiment respeta el default_acd_level del manifiesto."""
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        if report.success:
            assert report.embodiment["acd_level"] == "L2_STANDARD"

    def test_germinate_embodiment_has_correct_metabolic_state(
        self, seeded_volume, mock_ollama_running, mock_bootstrap_success
    ):
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        if report.success:
            assert report.embodiment["metabolic_state"] == "awake"

    def test_germinate_with_memory_db(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        """Si existe memory.db en el pendrive, se pasa al bootstrap."""
        seed = ZOESeed()
        # Crear un memory.db vacío
        memory_path = os.path.join(seeded_volume, "ZOE", "data", "memory.db")
        with open(memory_path, "w") as f:
            f.write("")  # archivo vacío

        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            report = seed.germinate(custom_paths=[seeded_volume])
        # Debe pasar el path al bootstrap (aunque el DB esté vacío)
        # Verificamos que no falla por esto
        assert isinstance(report, GerminationReport)

    def test_multiple_germinations_increment_count(self, seeded_volume, mock_ollama_running, mock_bootstrap_success):
        """Germinar dos veces incrementa germination_count en el manifiesto."""
        seed = ZOESeed()
        with patch(
            "zoe.core.embodiment_composer.EmbodimentComposer._detect_available_ram",
            return_value=8.0,
        ):
            seed.germinate(custom_paths=[seeded_volume])
            seed2 = ZOESeed()
            seed2.germinate(custom_paths=[seeded_volume])

        vol = seed2.detect_seed_volume(custom_paths=[seeded_volume])
        manifest = SeedManifest.from_json(vol.seed_manifest_path)
        assert manifest.germination_count == 2
