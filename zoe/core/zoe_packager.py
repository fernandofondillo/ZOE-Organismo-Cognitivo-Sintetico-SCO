"""
ZOE V1.7 — Zoe Packager (Sprint 3)

Empaqueta y desempaqueta organismos ZOE completos en formato .zoe.

Un archivo .zoe es un tarball comprimido que contiene TODO lo necesario
para que ZOE funcione en cualquier sitio:

- seed.json          — Identity Vault + Trajectory Chain hash
- memory.db          — SQLite con toda la memoria persistente
- capsules/          — Cápsulas de conocimiento instaladas
- language_patterns/ — Patrones para PatternSpeaker (generación sin LLM)
- config.yaml        — Configuración del organismo
- manifest.json      — Metadata del .zoe (versión, fecha, tamaño)

El .zoe permite:
1. Portabilidad absoluta: un archivo = un organismo completo
2. Sin dependencias: no necesitas Ollama, ni pip, ni git
3. Heredable: pasas el .zoe a alguien y ZOE despierta
4. Comercializable: vendes .zoe preconfigurados

Sin deconstruir: el .zoe NO reemplaza el ZOE Seed Mode (Fase 7E) ni
ningún otro mecanismo existente. Es un formato ADICIONAL de distribución.

Uso:
    from zoe.core.zoe_packager import ZoePackager

    # Empaquetar
    packager = ZoePackager()
    path = packager.package(
        output_path="mi_zoe.zoe",
        organism_id="zoe_fernando_v1",
        memory_db="zoe_data/memory.db",
        capsules_dir="zoe/capsules",
        config_path="zoe/config/production.yaml",
    )

    # Desempaquetar
    packager.unpackage("mi_zoe.zoe", output_dir="/tmp/zoe_extracted")
"""

from __future__ import annotations

import json
import logging
import os
import tarfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


@dataclass
class ZoePackageManifest:
    """Manifest de un archivo .zoe."""
    format_version: str = "1.0"
    organism_id: str = ""
    zoe_version: str = "1.7.0"
    created_at: float = field(default_factory=time.time)
    size_bytes: int = 0
    has_memory: bool = False
    has_capsules: bool = False
    has_language_patterns: bool = False
    has_embedded_model: bool = False
    has_config: bool = False
    capsule_count: int = 0
    memory_entries: int = 0
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format_version": self.format_version,
            "organism_id": self.organism_id,
            "zoe_version": self.zoe_version,
            "created_at": self.created_at,
            "size_bytes": self.size_bytes,
            "has_memory": self.has_memory,
            "has_capsules": self.has_capsules,
            "has_language_patterns": self.has_language_patterns,
            "has_embedded_model": self.has_embedded_model,
            "has_config": self.has_config,
            "capsule_count": self.capsule_count,
            "memory_entries": self.memory_entries,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoePackageManifest":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ZoePackager:
    """
    Empaqueta y desempaquetar organismos ZOE en formato .zoe.

    El formato .zoe es un tarball (.tar.gz) con estructura definida.
    """

    MANIFEST_NAME = "manifest.json"

    def package(
        self,
        output_path: str,
        organism_id: str,
        memory_db: str = None,
        capsules_dir: str = None,
        language_patterns_dir: str = None,
        config_path: str = None,
        embedded_model_path: str = None,
        identity_vault_path: str = None,
        trajectory_chain_path: str = None,
        description: str = "",
    ) -> str:
        """
        Empaqueta un organismo ZOE en formato .zoe.

        Args:
            output_path: path del archivo .zoe a crear
            organism_id: ID del organismo
            memory_db: path a SQLite de memoria (opcional)
            capsules_dir: directorio de cápsulas (opcional)
            language_patterns_dir: directorio de patrones de lenguaje (opcional)
            config_path: path a config YAML (opcional)
            embedded_model_path: path a modelo GGUF embebido (opcional)
            identity_vault_path: path a identity_vault.json (opcional)
            trajectory_chain_path: path a trajectory_chain.json (opcional)
            description: descripción del organismo

        Returns:
            Path del archivo .zoe creado
        """
        manifest = ZoePackageManifest(
            organism_id=organism_id,
            description=description,
        )

        # Crear tarball
        with tarfile.open(output_path, "w:gz") as tar:
            # Añadir memory.db
            if memory_db and os.path.exists(memory_db):
                tar.add(memory_db, arcname="memory.db")
                manifest.has_memory = True
                manifest.memory_entries = self._count_memory_entries(memory_db)
                logger.info(f"ZoePackager: added memory.db ({manifest.memory_entries} entries)")

            # Añadir capsules/
            if capsules_dir and os.path.isdir(capsules_dir):
                capsule_count = self._count_capsules(capsules_dir)
                if capsule_count > 0:
                    tar.add(capsules_dir, arcname="capsules")
                    manifest.has_capsules = True
                    manifest.capsule_count = capsule_count
                    logger.info(f"ZoePackager: added {capsule_count} capsules")

            # Añadir language_patterns/
            if language_patterns_dir and os.path.isdir(language_patterns_dir):
                tar.add(language_patterns_dir, arcname="language_patterns")
                manifest.has_language_patterns = True
                logger.info("ZoePackager: added language_patterns")

            # Añadir config.yaml
            if config_path and os.path.exists(config_path):
                tar.add(config_path, arcname="config.yaml")
                manifest.has_config = True
                logger.info("ZoePackager: added config.yaml")

            # Añadir embedded model (opcional)
            if embedded_model_path and os.path.exists(embedded_model_path):
                tar.add(embedded_model_path, arcname="embedded_model.gguf")
                manifest.has_embedded_model = True
                logger.info("ZoePackager: added embedded model")

            # Añadir identity vault
            if identity_vault_path and os.path.exists(identity_vault_path):
                tar.add(identity_vault_path, arcname="identity_vault.json")
                logger.info("ZoePackager: added identity_vault.json")

            # Añadir trajectory chain
            if trajectory_chain_path and os.path.exists(trajectory_chain_path):
                tar.add(trajectory_chain_path, arcname="trajectory_chain.json")
                logger.info("ZoePackager: added trajectory_chain.json")

            # Calcular tamaño
            manifest.size_bytes = os.path.getsize(output_path)

            # Añadir manifest
            manifest_data = json.dumps(manifest.to_dict(), indent=2).encode()
            import io
            manifest_file = tarfile.TarInfo(name=self.MANIFEST_NAME)
            manifest_file.size = len(manifest_data)
            manifest_file.mtime = time.time()
            tar.addfile(manifest_file, io.BytesIO(manifest_data))

        logger.info(f"ZoePackager: created {output_path} ({manifest.size_bytes} bytes)")
        return output_path

    def unpackage(self, zoe_path: str, output_dir: str) -> ZoePackageManifest:
        """
        Desempaqueta un archivo .zoe a un directorio.

        Args:
            zoe_path: path al archivo .zoe
            output_dir: directorio donde extraer

        Returns:
            ZoePackageManifest con la metadata del paquete
        """
        os.makedirs(output_dir, exist_ok=True)

        with tarfile.open(zoe_path, "r:gz") as tar:
            tar.extractall(output_dir)

        # Leer manifest
        manifest_path = os.path.join(output_dir, self.MANIFEST_NAME)
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                manifest = ZoePackageManifest.from_dict(json.load(f))
        else:
            manifest = ZoePackageManifest()

        logger.info(f"ZoePackager: extracted to {output_dir}")
        logger.info(f"  organism_id: {manifest.organism_id}")
        logger.info(f"  has_memory: {manifest.has_memory}")
        logger.info(f"  has_capsules: {manifest.has_capsules}")
        logger.info(f"  capsule_count: {manifest.capsule_count}")

        return manifest

    def inspect(self, zoe_path: str) -> ZoePackageManifest:
        """
        Inspecciona un .zoe sin desempaquetarlo.

        Args:
            zoe_path: path al archivo .zoe

        Returns:
            ZoePackageManifest con la metadata
        """
        with tarfile.open(zoe_path, "r:gz") as tar:
            try:
                manifest_file = tar.extractfile(self.MANIFEST_NAME)
                if manifest_file:
                    manifest_data = json.loads(manifest_file.read().decode())
                    return ZoePackageManifest.from_dict(manifest_data)
            except KeyError:
                pass

        return ZoePackageManifest()

    def _count_memory_entries(self, db_path: str) -> int:
        """Cuenta entries en SQLite."""
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            total = 0
            for table in ["episodic", "semantic", "procedural", "causal",
                          "emotional", "corporeal", "social", "prospective",
                          "counterfactual", "evolutionary", "cultural"]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total += cursor.fetchone()[0]
                except sqlite3.Error as e:
                    logger.debug(f"SQLite table {table} query failed: {e}")
            conn.close()
            return total
        except sqlite3.Error as e:
            logger.warning(f"SQLite database access failed: {e}")
            return 0

    def _count_capsules(self, capsules_dir: str) -> int:
        """Cuenta cápsulas en un directorio."""
        count = 0
        for item in os.listdir(capsules_dir):
            item_path = os.path.join(capsules_dir, item)
            if os.path.isdir(item_path):
                yaml_path = os.path.join(item_path, "capsule.yaml")
                if os.path.exists(yaml_path):
                    count += 1
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Stats del packager."""
        return {
            "format_version": "1.0",
            "supported_extensions": [".zoe"],
            "compression": "gzip",
        }
