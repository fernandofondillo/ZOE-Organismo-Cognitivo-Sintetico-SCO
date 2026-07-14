"""
ZOE V1.5 — Seed Mode (Fase 7E)

El pendrive contiene el ALMA de ZOE (IdentityVault + TrajectoryChain +
configuración del organismo) y los MOTORES (código + dependencias).
Al conectarlo a cualquier ordenador:

1. El Seed detecta el hardware anfitrión (7A Resource Discovery)
2. Construye el ModelBus con los backends disponibles localmente (7B)
3. El ResourcePlanner planifica el cuerpo óptimo (7C)
4. El EmbodimentComposer instancia el cuerpo (7D)
5. El bucle cognitivo arranca y ZOE "despierta" en su nuevo cuerpo

Es decir: el alma viaja, el cuerpo se reconstruye en cada host.

Metáfora biológica:
- Una semilla (roble) contiene el ADN del árbol y nutrientes para arrancar.
- La semilla no sabe en qué suelo caerá (arena, arcilla, humedad).
- Al germinar, detecta el entorno y construye raíces/tronco/ramas adaptados.
- El ADN (alma) es el mismo; el cuerpo (recursos) varía según el entorno.

ZOE Seed = ADN del organismo cognitivo. Cualquier Mac/Linux lo puede
"germinar" y ZOE despierta con su identidad, memoria y trayectoria
intactas, adaptándose al hardware disponible.

Componentes del Seed:
- seed.json: manifiesto (organism_id, versión, cápsulas requeridas)
- identity/: IdentityVault (hash + claves criptográficas)
- trajectory/: TrajectoryChain (cadena firmada de mutaciones)
- memory/: SQLite con memoria persistente (semantic, episodic, procedural)
- capsules/: cápsulas instaladas (descargadas del marketplace)
- config/: preferencias del organismo (idioma, valores, restricciones)
- venv/: entorno virtual Python (los motores)
- zoe/: código del repositorio (clonado en instalación)

Pipeline de germinación:
1. detect_seed_volume() → busca /Volumes/*/ZOE/seed.json
2. load_seed_manifest() → lee manifiesto y valida integridad
3.EmbodimentComposer.bootstrap_from_scratch() → construye cuerpo óptimo
4. seed_germinate() → carga alma + memoria + cápsulas en el cuerpo
5. Embodiment ready → bucle cognitivo arranca

Sin desconstruir: es la capa superior que orquesta 7A-7D. No toca
el bucle cognitivo ni el metabolismo. Añade el concepto de "semilla
portátil" que viaja entre hosts.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import sys
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Enums
# ============================================================

class SeedStatus(str, Enum):
    """Estado de la semilla."""
    DORMANT = "dormant"           # en el pendrive, no germinada
    DETECTED = "detected"         # volumen encontrado, manifiesto leído
    VALIDATED = "validated"       # integridad verificada
    GERMINATING = "germinating"   # cuerpo siendo construido
    GROWING = "growing"           # alma + memoria cargándose en el cuerpo
    ALIVE = "alive"               # ZOE despierta en su nuevo cuerpo
    FAILED = "failed"             # no pudo germinar
    WITHERED = "withered"         # era ALIVE pero cerró limpiamente


class GerminationError(str, Enum):
    """Razones de fallo de germinación."""
    NO_SEED_FOUND = "no_seed_found"
    INVALID_MANIFEST = "invalid_manifest"
    CORRUPTED_IDENTITY = "corrupted_identity"
    INCOMPATIBLE_VERSION = "incompatible_version"
    NO_RESOURCES = "no_resources"
    EMBODIMENT_FAILED = "embodiment_failed"
    CAPSULE_MISSING = "capsule_missing"
    MEMORY_LOAD_FAILED = "memory_load_failed"


# ============================================================
# Dataclasses
# ============================================================

@dataclass
class SeedManifest:
    """
    Manifiesto de la semilla — el ADN de ZOE.

    Vive en /Volumes/<pendrive>/ZOE/seed.json y describe qué es ZOE
    en este pendrive: identidad, versión, cápsulas requeridas, etc.
    """
    # Identidad
    organism_id: str = ""
    organism_name: str = "ZOE"
    version: str = "1.5.0"

    # Trazas criptográficas
    identity_hash: str = ""           # hash del IdentityVault
    trajectory_root_hash: str = ""    # hash raíz de la trayectoria

    # Requisitos mínimos del host
    min_ram_gb: float = 4.0
    min_python_version: str = "3.10"
    requires_ollama: bool = False     # si True, falla si no hay Ollama
    allows_cloud: bool = True         # si False, no usa cloud aunque haya API key

    # Cápsulas requeridas (must-have para germinar)
    required_capsules: List[str] = field(default_factory=list)

    # Cápsulas opcionales (cargar si están disponibles)
    optional_capsules: List[str] = field(default_factory=list)

    # Configuración del organismo
    default_use_case: str = "asistente_crece_contigo"
    default_acd_level: str = "L2_STANDARD"
    language: str = "es"

    # Metadata de creación
    created_at: float = 0.0
    last_germinated_at: float = 0.0
    germination_count: int = 0
    last_host: str = ""               # hostname del último host donde germinó

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeedManifest":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: str) -> "SeedManifest":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class SeedVolume:
    """Un volumen que contiene una semilla ZOE detectada."""
    volume_path: str                  # /Volumes/MyDrive
    zoe_home: str                     # /Volumes/MyDrive/ZOE
    seed_manifest_path: str           # /Volumes/MyDrive/ZOE/seed.json
    identity_path: str                # /Volumes/MyDrive/ZOE/identity/
    trajectory_path: str              # /Volumes/MyDrive/ZOE/trajectory/
    memory_path: str                  # /Volumes/MyDrive/ZOE/data/memory.db
    capsules_path: str                # /Volumes/MyDrive/ZOE/capsules/
    config_path: str                  # /Volumes/MyDrive/ZOE/config/
    volume_name: str = ""
    free_space_gb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GerminationReport:
    """Resultado de germinar una semilla."""
    success: bool
    status: str                       # SeedStatus.value
    seed_volume: Optional[Dict[str, Any]] = None
    manifest: Optional[Dict[str, Any]] = None
    embodiment: Optional[Dict[str, Any]] = None
    capsules_loaded: List[str] = field(default_factory=list)
    capsules_missing: List[str] = field(default_factory=list)
    memory_entries_loaded: int = 0
    error: Optional[str] = None
    error_type: Optional[str] = None
    duration_ms: float = 0.0
    host_info: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    auto_started: bool = False
    auto_start_status: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# ZOESeed
# ============================================================

class ZOESeed:
    """
    Una semilla ZOE: alma + motores listos para germinar en cualquier host.

    Uso típico (germinar desde pendrive):
        seed = ZOESeed()
        report = seed.germinate()
        if report.success:
            print(f"ZOE despierta en {report.host_info['hostname']}")
            # El Embodiment está RUNNING, listo para pensar

    Uso de creación (sembrar una semilla nueva):
        seed = ZOESeed()
        seed.create(
            volume_path="/Volumes/MyDrive",
            organism_id="zoe_fernando_v1",
            required_capsules=["base_ethics", "basic_psychology"],
        )
    """

    ZOE_DIR_NAME = "ZOE"
    SEED_MANIFEST_NAME = "seed.json"
    IDENTITY_DIR = "identity"
    TRAJECTORY_DIR = "trajectory"
    MEMORY_DIR = "data"
    MEMORY_DB_NAME = "memory.db"
    CAPSULES_DIR = "capsules"
    CONFIG_DIR = "config"

    def __init__(self):
        self._last_report: Optional[GerminationReport] = None
        self._germination_count: int = 0
        self._detection_count: int = 0

    # ------------------------------------------------------------
    # 1. Detección de semilla
    # ------------------------------------------------------------

    def detect_seed_volume(
        self,
        custom_paths: Optional[List[str]] = None,
    ) -> Optional[SeedVolume]:
        """
        Busca un volumen montado que contenga una semilla ZOE.

        Orden de búsqueda:
        1. custom_paths (si se proporcionan)
        2. /Volumes/* en macOS (pendrives USB)
        3. /media/* en Linux
        4. ~/.zoe-seed/ (modo desarrollo sin pendrive)
        5. ZOE_SEED_PATH env var
        """
        self._detection_count += 1
        candidate_paths = []

        if custom_paths:
            candidate_paths.extend(custom_paths)

        # Env var
        env_path = os.environ.get("ZOE_SEED_PATH")
        if env_path:
            candidate_paths.append(env_path)

        # macOS pendrives
        if platform.system() == "Darwin" and os.path.isdir("/Volumes"):
            for vol in os.listdir("/Volumes"):
                if vol in ("Macintosh HD", "MacintoshHD"):
                    continue
                candidate_paths.append(f"/Volumes/{vol}")

        # Linux mounts
        if platform.system() == "Linux" and os.path.isdir("/media"):
            for user_dir in os.listdir("/media"):
                user_path = f"/media/{user_dir}"
                if os.path.isdir(user_path):
                    for vol in os.listdir(user_path):
                        candidate_paths.append(f"{user_path}/{vol}")

        # Windows: drives D: to Z:
        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                if letter == "C":
                    continue
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    candidate_paths.append(drive_path)

        # Dev mode: ~/.zoe-seed/
        dev_seed = os.path.expanduser("~/.zoe-seed")
        if os.path.isdir(dev_seed):
            candidate_paths.append(dev_seed)

        # Buscar en cada candidato
        for path in candidate_paths:
            vol = self._validate_seed_volume(path)
            if vol:
                logger.info(f"ZOESeed: seed detected at {vol.zoe_home}")
                return vol

        return None

    def _validate_seed_volume(self, volume_path: str) -> Optional[SeedVolume]:
        """Valida que un volumen tenga una semilla ZOE válida."""
        if not os.path.isdir(volume_path):
            return None

        zoe_home = os.path.join(volume_path, self.ZOE_DIR_NAME)
        if not os.path.isdir(zoe_home):
            return None

        seed_manifest = os.path.join(zoe_home, self.SEED_MANIFEST_NAME)
        if not os.path.isfile(seed_manifest):
            return None

        # Calcular espacio libre
        try:
            usage = shutil.disk_usage(volume_path)
            free_gb = round(usage.free / (1024**3), 1)
        except Exception:
            free_gb = 0.0

        return SeedVolume(
            volume_path=volume_path,
            zoe_home=zoe_home,
            seed_manifest_path=seed_manifest,
            identity_path=os.path.join(zoe_home, self.IDENTITY_DIR),
            trajectory_path=os.path.join(zoe_home, self.TRAJECTORY_DIR),
            memory_path=os.path.join(zoe_home, self.MEMORY_DIR, self.MEMORY_DB_NAME),
            capsules_path=os.path.join(zoe_home, self.CAPSULES_DIR),
            config_path=os.path.join(zoe_home, self.CONFIG_DIR),
            volume_name=os.path.basename(volume_path.rstrip("/")),
            free_space_gb=free_gb,
        )

    def list_seed_paths(self) -> List[Dict[str, Any]]:
        """Lista todos los caminos donde se busca una semilla (para debug)."""
        paths = []

        env_path = os.environ.get("ZOE_SEED_PATH")
        if env_path:
            paths.append({"path": env_path, "source": "env_var"})

        if platform.system() == "Darwin" and os.path.isdir("/Volumes"):
            for vol in os.listdir("/Volumes"):
                if vol not in ("Macintosh HD", "MacintoshHD"):
                    paths.append({"path": f"/Volumes/{vol}", "source": "macos_volumes"})

        if platform.system() == "Linux" and os.path.isdir("/media"):
            for user_dir in os.listdir("/media"):
                user_path = f"/media/{user_dir}"
                if os.path.isdir(user_path):
                    for vol in os.listdir(user_path):
                        paths.append({"path": f"{user_path}/{vol}", "source": "linux_media"})

        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                if letter == "C":
                    continue
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    paths.append({"path": drive_path, "source": "windows_drives"})

        dev_seed = os.path.expanduser("~/.zoe-seed")
        if os.path.isdir(dev_seed):
            paths.append({"path": dev_seed, "source": "dev_mode"})

        return paths

    # ------------------------------------------------------------
    # 2. Creación de semilla (sembrar)
    # ------------------------------------------------------------

    def create(
        self,
        volume_path: str,
        organism_id: str,
        organism_name: str = "ZOE",
        version: str = "1.5.0",
        required_capsules: Optional[List[str]] = None,
        optional_capsules: Optional[List[str]] = None,
        default_use_case: str = "asistente_crece_contigo",
        default_acd_level: str = "L2_STANDARD",
        language: str = "es",
        min_ram_gb: float = 4.0,
        requires_ollama: bool = False,
        allows_cloud: bool = True,
        identity_vault: Any = None,
        trajectory_chain: Any = None,
    ) -> GerminationReport:
        """
        Crea una nueva semilla ZOE en el volumen especificado.

        Args:
            volume_path: ruta al volumen (e.g. /Volumes/MyDrive)
            organism_id: ID único del organismo (e.g. "zoe_fernando_v1")
            identity_vault: IdentityVault ya inicializado (opcional)
            trajectory_chain: TrajectoryChain ya inicializada (opcional)

        Returns:
            GerminationReport con success=True si se creó OK
        """
        start = time.time()
        if not os.path.isdir(volume_path):
            return self._fail_report(
                GerminationError.INVALID_MANIFEST.value,
                f"Volume not found: {volume_path}",
                duration_ms=(time.time() - start) * 1000,
            )

        zoe_home = os.path.join(volume_path, self.ZOE_DIR_NAME)
        os.makedirs(zoe_home, exist_ok=True)

        # Crear subdirectorios
        for subdir in (
            self.IDENTITY_DIR, self.TRAJECTORY_DIR, self.MEMORY_DIR,
            self.CAPSULES_DIR, self.CONFIG_DIR,
        ):
            os.makedirs(os.path.join(zoe_home, subdir), exist_ok=True)

        # Hashes (de los componentes si se proporcionan, o placeholders)
        identity_hash = ""
        trajectory_root_hash = ""
        if identity_vault is not None:
            identity_hash = getattr(identity_vault, "identity_hash", "")
            # Guardar el vault serializado
            try:
                vault_data = identity_vault.to_dict() if hasattr(identity_vault, "to_dict") else {}
                with open(os.path.join(zoe_home, self.IDENTITY_DIR, "vault.json"), "w") as f:
                    json.dump(vault_data, f, indent=2, default=str)
            except Exception as e:
                logger.warning(f"ZOESeed: failed to save identity vault: {e}")

        if trajectory_chain is not None:
            trajectory_root_hash = getattr(trajectory_chain, "root_hash", "")
            try:
                chain_data = trajectory_chain.to_dict() if hasattr(trajectory_chain, "to_dict") else {}
                with open(os.path.join(zoe_home, self.TRAJECTORY_DIR, "chain.json"), "w") as f:
                    json.dump(chain_data, f, indent=2, default=str)
            except Exception as e:
                logger.warning(f"ZOESeed: failed to save trajectory chain: {e}")

        # Crear manifiesto
        manifest = SeedManifest(
            organism_id=organism_id,
            organism_name=organism_name,
            version=version,
            identity_hash=identity_hash,
            trajectory_root_hash=trajectory_root_hash,
            min_ram_gb=min_ram_gb,
            requires_ollama=requires_ollama,
            allows_cloud=allows_cloud,
            required_capsules=list(required_capsules or []),
            optional_capsules=list(optional_capsules or []),
            default_use_case=default_use_case,
            default_acd_level=default_acd_level,
            language=language,
            created_at=time.time(),
        )

        manifest_path = os.path.join(zoe_home, self.SEED_MANIFEST_NAME)
        manifest.to_json(manifest_path)

        # Crear config por defecto
        default_config = {
            "language": language,
            "default_use_case": default_use_case,
            "default_acd_level": default_acd_level,
            "allows_cloud": allows_cloud,
        }
        with open(os.path.join(zoe_home, self.CONFIG_DIR, "organism.json"), "w") as f:
            json.dump(default_config, f, indent=2)

        duration_ms = (time.time() - start) * 1000
        vol = self._validate_seed_volume(volume_path)
        return GerminationReport(
            success=True,
            status=SeedStatus.VALIDATED.value,
            seed_volume=vol.to_dict() if vol else None,
            manifest=manifest.to_dict(),
            duration_ms=duration_ms,
            host_info=self._get_host_info(),
        )

    # ------------------------------------------------------------
    # 3. Validación de semilla
    # ------------------------------------------------------------

    def validate_seed(self, seed_volume: SeedVolume) -> Tuple[bool, List[str]]:
        """
        Valida la integridad de una semilla antes de germinar.

        Returns:
            (ok, list_of_issues) — ok=True si la semilla es válida
        """
        issues = []

        # 1. Manifiesto legible
        try:
            manifest = SeedManifest.from_json(seed_volume.seed_manifest_path)
        except Exception as e:
            return False, [f"Cannot read manifest: {e}"]

        # 2. Directorio de identidad existe
        if not os.path.isdir(seed_volume.identity_path):
            issues.append("Identity directory missing")

        # 3. Directorio de trayectoria existe
        if not os.path.isdir(seed_volume.trajectory_path):
            issues.append("Trajectory directory missing")

        # 4. Directorio de memoria existe (aunque DB puede no existir aún)
        if not os.path.isdir(os.path.dirname(seed_volume.memory_path)):
            issues.append("Memory directory missing")

        # 5. Versión compatible
        try:
            major, minor, _ = manifest.version.split(".")
            if int(major) < 1:
                issues.append(f"Version too old: {manifest.version}")
        except Exception:
            issues.append(f"Invalid version format: {manifest.version}")

        # 6. organism_id no vacío
        if not manifest.organism_id:
            issues.append("organism_id is empty in manifest")

        return len(issues) == 0, issues

    # ------------------------------------------------------------
    # 4. Germinación
    # ------------------------------------------------------------

    def germinate(
        self,
        custom_paths: Optional[List[str]] = None,
        acd_level: Optional[str] = None,
        force_allow_cloud: bool = True,
        auto_start: bool = False,
    ) -> GerminationReport:
        """
        Germina una semilla ZOE en el host actual.

        Pipeline:
        1. detect_seed_volume → encuentra el pendrive
        2. validate_seed → verifica integridad
        3.EmbodimentComposer.bootstrap_from_scratch → construye cuerpo
        4. Cargar cápsulas requeridas
        5. Cargar memoria desde SQLite
        6. Marcar germinación en el manifiesto

        Returns:
            GerminationReport con el resultado
        """
        start = time.time()
        self._germination_count += 1
        host_info = self._get_host_info()

        # 1. Detectar semilla
        vol = self.detect_seed_volume(custom_paths=custom_paths)
        if vol is None:
            return self._fail_report(
                GerminationError.NO_SEED_FOUND.value,
                "No ZOE seed found in any mounted volume",
                duration_ms=(time.time() - start) * 1000,
                host_info=host_info,
            )

        # 2. Validar
        ok, issues = self.validate_seed(vol)
        if not ok:
            return self._fail_report(
                GerminationError.INVALID_MANIFEST.value,
                f"Seed validation failed: {'; '.join(issues)}",
                seed_volume=vol,
                duration_ms=(time.time() - start) * 1000,
                host_info=host_info,
            )

        # 3. Leer manifiesto
        try:
            manifest = SeedManifest.from_json(vol.seed_manifest_path)
        except Exception as e:
            return self._fail_report(
                GerminationError.INVALID_MANIFEST.value,
                f"Cannot read manifest: {e}",
                seed_volume=vol,
                duration_ms=(time.time() - start) * 1000,
                host_info=host_info,
            )

        # 4. Verificar RAM mínima
        try:
            from .embodiment_composer import EmbodimentComposer
            composer = EmbodimentComposer()
            available_ram = composer._detect_available_ram()
            if available_ram < manifest.min_ram_gb:
                return self._fail_report(
                    GerminationError.NO_RESOURCES.value,
                    f"Insufficient RAM: {available_ram}GB < {manifest.min_ram_gb}GB required",
                    seed_volume=vol,
                    manifest=manifest.to_dict(),
                    duration_ms=(time.time() - start) * 1000,
                    host_info=host_info,
                )
        except Exception as e:
            logger.warning(f"ZOESeed: RAM check failed: {e}")

        # 5. Verificar cápsulas requeridas presentes
        capsules_loaded = []
        capsules_missing = []
        if manifest.required_capsules:
            for cap_name in manifest.required_capsules:
                cap_path = os.path.join(vol.capsules_path, cap_name)
                if os.path.isdir(cap_path):
                    capsules_loaded.append(cap_name)
                else:
                    # Cápsula podría estar en el repo (no en el pendrive)
                    # Asumimos disponible si existe en el código
                    repo_capsules = os.path.join(
                        os.path.dirname(__file__), "..", "capsules", cap_name
                    )
                    if os.path.isdir(repo_capsules):
                        capsules_loaded.append(cap_name)
                    else:
                        capsules_missing.append(cap_name)

        if capsules_missing:
            return self._fail_report(
                GerminationError.CAPSULE_MISSING.value,
                f"Missing required capsules: {', '.join(capsules_missing)}",
                seed_volume=vol,
                manifest=manifest.to_dict(),
                capsules_loaded=capsules_loaded,
                capsules_missing=capsules_missing,
                duration_ms=(time.time() - start) * 1000,
                host_info=host_info,
            )

        # 6. Cargar cápsulas opcionales disponibles
        for cap_name in manifest.optional_capsules:
            if cap_name in capsules_loaded:
                continue
            cap_path = os.path.join(vol.capsules_path, cap_name)
            if os.path.isdir(cap_path):
                capsules_loaded.append(cap_name)
            else:
                repo_capsules = os.path.join(
                    os.path.dirname(__file__), "..", "capsules", cap_name
                )
                if os.path.isdir(repo_capsules):
                    capsules_loaded.append(cap_name)

        # 7. Bootstrap del cuerpo (7A→7B→7C→7D)
        try:
            from .embodiment_composer import EmbodimentComposer
            composer = EmbodimentComposer()

            # Decidir allow_cloud
            allow_cloud = manifest.allows_cloud and force_allow_cloud

            # Si requires_ollama y no hay Ollama, fallar rápido
            if manifest.requires_ollama:
                ollama_ok = composer._check_ollama_running()
                if not ollama_ok and not allow_cloud:
                    return self._fail_report(
                        GerminationError.NO_RESOURCES.value,
                        "Seed requires Ollama but it's not running and cloud is disabled",
                        seed_volume=vol,
                        manifest=manifest.to_dict(),
                        duration_ms=(time.time() - start) * 1000,
                        host_info=host_info,
                    )

            # Si cloud deshabilitado, limpiar API keys temporalmente
            env_backup = {}
            if not allow_cloud:
                for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"):
                    if key in os.environ:
                        env_backup[key] = os.environ.pop(key)

            try:
                emb = composer.bootstrap_from_scratch(
                    acd_level=acd_level or manifest.default_acd_level,
                    metabolic_state="awake",
                    sensitive_domain=False,
                    capsules=capsules_loaded,
                    memory_db_path=vol.memory_path if os.path.isfile(vol.memory_path) else None,
                )
            finally:
                # Restaurar env vars
                for key, value in env_backup.items():
                    os.environ[key] = value

        except Exception as e:
            return self._fail_report(
                GerminationError.EMBODIMENT_FAILED.value,
                f"Embodiment bootstrap failed: {e}",
                seed_volume=vol,
                manifest=manifest.to_dict(),
                capsules_loaded=capsules_loaded,
                duration_ms=(time.time() - start) * 1000,
                host_info=host_info,
            )

        # 8. Verificar que el embodiment está vivo
        if not emb.is_running:
            error_msg = "; ".join(emb.errors) if emb.errors else "Unknown embodiment failure"
            return self._fail_report(
                GerminationError.EMBODIMENT_FAILED.value,
                error_msg,
                seed_volume=vol,
                manifest=manifest.to_dict(),
                embodiment=emb.to_dict(),
                capsules_loaded=capsules_loaded,
                duration_ms=(time.time() - start) * 1000,
                host_info=host_info,
            )

        # 9. Cargar memoria desde SQLite (si existe)
        memory_entries_loaded = 0
        if os.path.isfile(vol.memory_path):
            try:
                # El memory store ya está conectado vía bootstrap_from_scratch
                # Solo contamos entries para el report
                if emb.memory_store and hasattr(emb.memory_store, "count_entries"):
                    memory_entries_loaded = emb.memory_store.count_entries()
                else:
                    # Estimar por tamaño de archivo
                    size = os.path.getsize(vol.memory_path)
                    memory_entries_loaded = max(0, int(size / 1024))  # ~1KB por entry
            except Exception as e:
                logger.warning(f"ZOESeed: memory load check failed: {e}")

        # 10. Actualizar manifiesto (germination_count, last_host, last_germinated_at)
        try:
            manifest.last_germinated_at = time.time()
            manifest.germination_count += 1
            manifest.last_host = host_info.get("hostname", "")
            manifest.to_json(vol.seed_manifest_path)
        except Exception as e:
            logger.warning(f"ZOESeed: failed to update manifest: {e}")

        # 11. Reporte final
        duration_ms = (time.time() - start) * 1000
        report = GerminationReport(
            success=True,
            status=SeedStatus.ALIVE.value,
            seed_volume=vol.to_dict(),
            manifest=manifest.to_dict(),
            embodiment=emb.to_dict(),
            capsules_loaded=capsules_loaded,
            capsules_missing=[],
            memory_entries_loaded=memory_entries_loaded,
            duration_ms=duration_ms,
            host_info=host_info,
        )
        self._last_report = report
        logger.info(
            f"ZOESeed: germinated successfully in {duration_ms:.0f}ms "
            f"(host={host_info.get('hostname', '?')}, "
            f"backend={emb.backend_name}, capsules={len(capsules_loaded)})"
        )

        # 10. Auto-start (opt-in)
        if auto_start:
            try:
                from ..cli_chat import ZoeChat
                chat = ZoeChat(
                    backend="ollama" if manifest.requires_ollama else "mock",
                    db_path=os.path.join(vol.volume_path, "zoe_data", "memory.db"),
                )
                # Importar asyncio y arrancar
                import asyncio
                loop_async = asyncio.new_event_loop()
                asyncio.set_event_loop(loop_async)
                loop_async.run_until_complete(chat.initialize())
                report.auto_started = True
                report.auto_start_status = "running"
                logger.info("ZOESeed: ZOE auto-started after germination")
            except Exception as e:
                report.auto_started = False
                report.auto_start_status = f"failed: {e}"
                logger.warning(f"ZOESeed: auto-start failed: {e}")
        else:
            report.auto_started = False
            report.auto_start_status = "skipped (auto_start=False)"

        return report

    # ------------------------------------------------------------
    # 5. Utilidades
    # ------------------------------------------------------------

    def get_last_report(self) -> Optional[GerminationReport]:
        return self._last_report

    def get_stats(self) -> Dict[str, Any]:
        return {
            "germination_count": self._germination_count,
            "detection_count": self._detection_count,
            "last_status": self._last_report.status if self._last_report else None,
            "last_success": self._last_report.success if self._last_report else None,
        }

    def _fail_report(
        self,
        error_type: str,
        error_msg: str,
        seed_volume: Optional[SeedVolume] = None,
        manifest: Optional[Dict[str, Any]] = None,
        embodiment: Optional[Dict[str, Any]] = None,
        capsules_loaded: Optional[List[str]] = None,
        capsules_missing: Optional[List[str]] = None,
        duration_ms: float = 0.0,
        host_info: Optional[Dict[str, Any]] = None,
    ) -> GerminationReport:
        """Construye un GerminationReport de fallo."""
        report = GerminationReport(
            success=False,
            status=SeedStatus.FAILED.value,
            seed_volume=seed_volume.to_dict() if seed_volume else None,
            manifest=manifest,
            embodiment=embodiment,
            capsules_loaded=capsules_loaded or [],
            capsules_missing=capsules_missing or [],
            error=error_msg,
            error_type=error_type,
            duration_ms=duration_ms,
            host_info=host_info or self._get_host_info(),
        )
        self._last_report = report
        logger.warning(f"ZOESeed: germination failed ({error_type}): {error_msg}")
        return report

    def _get_host_info(self) -> Dict[str, Any]:
        """Info del host actual donde se intenta germinar."""
        try:
            import socket
            return {
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "platform_release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor() or "unknown",
                "python_version": platform.python_version(),
                "cpu_cores": os.cpu_count() or 1,
            }
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------
    # 6. Inspección de semilla sin germinar
    # ------------------------------------------------------------

    def inspect(self, custom_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Inspecciona una semilla sin germinarla.

        Devuelve info del manifiesto + estado de archivos sin arrancar
        ningún embodiment. Útil para diagnosticar antes de germinar.
        """
        vol = self.detect_seed_volume(custom_paths=custom_paths)
        if vol is None:
            return {
                "found": False,
                "searched_paths": self.list_seed_paths(),
            }

        try:
            manifest = SeedManifest.from_json(vol.seed_manifest_path)
        except Exception as e:
            return {
                "found": True,
                "valid": False,
                "error": str(e),
                "seed_volume": vol.to_dict(),
            }

        ok, issues = self.validate_seed(vol)

        # Verificar cápsulas
        capsules_status = {}
        for cap_name in manifest.required_capsules + manifest.optional_capsules:
            cap_path = os.path.join(vol.capsules_path, cap_name)
            in_pendrive = os.path.isdir(cap_path)
            repo_capsules = os.path.join(
                os.path.dirname(__file__), "..", "capsules", cap_name
            )
            in_repo = os.path.isdir(repo_capsules)
            capsules_status[cap_name] = {
                "in_pendrive": in_pendrive,
                "in_repo": in_repo,
                "available": in_pendrive or in_repo,
            }

        return {
            "found": True,
            "valid": ok,
            "issues": issues,
            "seed_volume": vol.to_dict(),
            "manifest": manifest.to_dict(),
            "capsules_status": capsules_status,
            "host_info": self._get_host_info(),
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ZOE Seed Mode — Germinar una semilla ZOE")
    parser.add_argument(
        "--paths",
        nargs="+",
        help="Rutas personalizadas para buscar la semilla",
    )
    parser.add_argument(
        "--acd-level",
        default=None,
        help="Nivel ACD para el embodiment (ej: L0_FAST, L1_BASIC, L2_STANDARD, L3_DEEP)",
    )
    parser.add_argument(
        "--auto-start",
        action="store_true",
        dest="auto_start",
        help="Arrancar ZOE automaticamente tras germinar",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Inspeccionar la semilla sin germinarla",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar logs detallados",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    seed = ZOESeed()

    if args.inspect:
        result = seed.inspect(custom_paths=args.paths)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return

    print("ZOE Seed Mode — Germinando...")
    report = seed.germinate(
        custom_paths=args.paths,
        acd_level=args.acd_level,
        auto_start=args.auto_start,
    )

    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False, default=str))

    if report.success:
        print("\nGerminacion exitosa. ZOE esta viva.")
        if report.auto_started:
            print(f"Auto-start: {report.auto_start_status}")
        elif not args.auto_start:
            print("Pasa --auto-start para arrancar ZOE automaticamente.")
    else:
        print(f"\nGerminacion fallida: {report.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
