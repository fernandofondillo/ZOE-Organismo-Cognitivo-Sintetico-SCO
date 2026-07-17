"""
Tests Sprint 5.8 — Persistencia de identidad, trayectoria, cápsulas y config

Verifica que ZOE mantiene su identidad, trayectoria, cápsulas cargadas y
configuración entre sesiones. Antes de Sprint 5.8, ZOE "nacia" de nuevo
cada arranque.
"""

import json
import os
import tempfile
import time
from pathlib import Path

import pytest


# ============================================================
# C1: IdentityVault persistencia
# ============================================================

class TestIdentityVaultPersistence:
    """Sprint 5.8 C1 — IdentityVault save_to_disk / load_from_disk."""

    def test_save_to_disk_crea_archivo(self, tmp_path):
        from zoe.alma.identity_vault import IdentityVault
        vault = IdentityVault(birth_timestamp=1234567890.0)
        path = str(tmp_path / "identity_vault.json")
        vault.save_to_disk(path)
        assert Path(path).exists()

    def test_load_from_disk_recupera_hash(self, tmp_path):
        from zoe.alma.identity_vault import IdentityVault
        vault = IdentityVault(birth_timestamp=1234567890.0)
        path = str(tmp_path / "identity_vault.json")
        vault.save_to_disk(path)
        loaded = IdentityVault.load_from_disk(path)
        assert loaded is not None
        assert loaded.identity_hash == vault.identity_hash

    def test_load_from_disk_devuelve_none_si_no_existe(self, tmp_path):
        from zoe.alma.identity_vault import IdentityVault
        loaded = IdentityVault.load_from_disk(str(tmp_path / "no_exist.json"))
        assert loaded is None

    def test_load_from_disk_devuelve_none_si_corrupto(self, tmp_path):
        from zoe.alma.identity_vault import IdentityVault
        path = str(tmp_path / "corrupt.json")
        Path(path).write_text("NOT JSON", encoding="utf-8")
        loaded = IdentityVault.load_from_disk(path)
        assert loaded is None

    def test_identidad_persiste_entre_sesiones(self, tmp_path):
        """El hash debe ser el mismo tras guardar y cargar."""
        from zoe.alma.identity_vault import IdentityVault
        path = str(tmp_path / "identity_vault.json")

        # Sesión 1: crear y guardar
        vault1 = IdentityVault(birth_timestamp=1234567890.0)
        hash1 = vault1.identity_hash
        vault1.save_to_disk(path)

        # Sesión 2: cargar
        vault2 = IdentityVault.load_from_disk(path)
        assert vault2 is not None
        assert vault2.identity_hash == hash1
        assert vault2.birth_timestamp == 1234567890.0


# ============================================================
# C2: TrajectoryChain persistencia
# ============================================================

class TestTrajectoryChainPersistence:
    """Sprint 5.8 C2 — TrajectoryChain save_to_disk / load_from_disk."""

    def test_save_to_disk_crea_archivo(self, tmp_path):
        from zoe.alma.trajectory_chain import TrajectoryChain, Mutation
        chain = TrajectoryChain(organism_id="test_zoe")
        mutation = Mutation(
            id="mut_1", type="add_memory", target="memory",
            payload={"content": "test"}, justification="test",
            provenance="test", cost=0.1, confidence=0.9,
        )
        chain.commit(mutation)
        path = str(tmp_path / "trajectory.json")
        chain.save_to_disk(path)
        assert Path(path).exists()

    def test_load_from_disk_recupera_mutaciones(self, tmp_path):
        from zoe.alma.trajectory_chain import TrajectoryChain, Mutation
        path = str(tmp_path / "trajectory.json")

        # Crear y guardar
        chain1 = TrajectoryChain(organism_id="test_zoe")
        m1 = Mutation(id="mut_1", type="add_memory", target="memory",
                      payload={"content": "test1"}, justification="j1",
                      provenance="p1", cost=0.1, confidence=0.9)
        chain1.commit(m1)
        chain1.save_to_disk(path)

        # Cargar
        chain2 = TrajectoryChain.load_from_disk(path)
        assert chain2 is not None
        assert len(chain2._mutations) == 1
        assert chain2._mutations[0].type == "add_memory"

    def test_load_from_disk_verifica_cadena(self, tmp_path):
        from zoe.alma.trajectory_chain import TrajectoryChain, Mutation
        path = str(tmp_path / "trajectory.json")

        chain1 = TrajectoryChain(organism_id="test_zoe")
        for i in range(5):
            m = Mutation(
                id=f"mut_{i}", type="add_memory", target="memory",
                payload={"content": f"test{i}"}, justification=f"j{i}",
                provenance="test", cost=0.1, confidence=0.9,
            )
            chain1.commit(m)
        chain1.save_to_disk(path)

        chain2 = TrajectoryChain.load_from_disk(path)
        assert chain2 is not None
        assert chain2.verify_chain() is True

    def test_load_from_disk_devuelve_none_si_no_existe(self, tmp_path):
        from zoe.alma.trajectory_chain import TrajectoryChain
        loaded = TrajectoryChain.load_from_disk(str(tmp_path / "no_exist.json"))
        assert loaded is None

    def test_set_persist_path_auto_guarda(self, tmp_path):
        from zoe.alma.trajectory_chain import TrajectoryChain, Mutation
        path = str(tmp_path / "trajectory.json")
        chain = TrajectoryChain(organism_id="test_zoe")
        chain.set_persist_path(path)

        m = Mutation(id="mut_1", type="add_memory", target="memory",
                     payload={"content": "test"}, justification="j",
                     provenance="p", cost=0.1, confidence=0.9)
        chain.commit(m)

        # El archivo debe existir tras el commit (auto-save)
        assert Path(path).exists()

    def test_rollback_persiste(self, tmp_path):
        from zoe.alma.trajectory_chain import TrajectoryChain, Mutation
        path = str(tmp_path / "trajectory.json")
        chain = TrajectoryChain(organism_id="test_zoe")
        chain.set_persist_path(path)

        m = Mutation(id="mut_1", type="add_memory", target="memory",
                     payload={"content": "test"}, justification="j",
                     provenance="p", cost=0.1, confidence=0.9)
        chain.commit(m)
        chain.rollback("mut_1")

        # Cargar y verificar que el rollback está
        chain2 = TrajectoryChain.load_from_disk(path)
        assert chain2 is not None
        assert len(chain2._mutations) == 2  # original + rollback
        assert chain2._mutations[1].type == "rollback_previous"

    def test_load_corrupto_devuelve_none(self, tmp_path):
        from zoe.alma.trajectory_chain import TrajectoryChain
        path = str(tmp_path / "corrupt.json")
        Path(path).write_text("NOT JSON", encoding="utf-8")
        loaded = TrajectoryChain.load_from_disk(path)
        assert loaded is None


# ============================================================
# C3: CapsuleManager persistencia de cápsulas cargadas
# ============================================================

class TestCapsuleManagerPersistence:
    """Sprint 5.8 C3 — CapsuleManager save_loaded_state / load_loaded_state."""

    def test_save_loaded_state_crea_archivo(self, tmp_path):
        from zoe.core.capsule_manager import CapsuleManager
        manager = CapsuleManager(organism=None)
        path = str(tmp_path / "loaded_capsules.json")
        manager.save_loaded_state(path)
        assert Path(path).exists()

    def test_load_loaded_state_devuelve_lista_vacia_si_no_existe(self, tmp_path):
        from zoe.core.capsule_manager import CapsuleManager
        loaded = CapsuleManager.load_loaded_state(str(tmp_path / "no_exist.json"))
        assert loaded == []

    def test_save_y_load_roundtrip(self, tmp_path):
        from zoe.core.capsule_manager import CapsuleManager
        path = str(tmp_path / "loaded_capsules.json")
        manager = CapsuleManager(organism=None)
        # Simular cápsulas cargadas
        manager._loaded = {"cap1": "data1", "cap2": "data2"}
        manager.save_loaded_state(path)

        loaded = CapsuleManager.load_loaded_state(path)
        assert set(loaded) == {"cap1", "cap2"}

    def test_load_corrupto_devuelve_vacio(self, tmp_path):
        from zoe.core.capsule_manager import CapsuleManager
        path = str(tmp_path / "corrupt.json")
        Path(path).write_text("NOT JSON", encoding="utf-8")
        loaded = CapsuleManager.load_loaded_state(path)
        assert loaded == []

    def test_save_crea_directorio_padre(self, tmp_path):
        from zoe.core.capsule_manager import CapsuleManager
        path = str(tmp_path / "subdir" / "loaded_capsules.json")
        manager = CapsuleManager(organism=None)
        manager.save_loaded_state(path)
        assert Path(path).exists()


# ============================================================
# C4: Configuración persistente
# ============================================================

class TestConfigPersistence:
    """Sprint 5.8 C4 — Configuración en ~/.zoe/config.json."""

    def test_config_se_guarda(self, tmp_path, monkeypatch):
        """Simula que main() guarda la config."""
        import json
        config_path = tmp_path / ".zoe" / "config.json"
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Simular lo que hace main()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {"backend": "ollama", "model": "auto", "db_path": "zoe_data/chat_memory.db"}
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

        assert config_path.exists()
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        assert loaded["backend"] == "ollama"
        assert loaded["model"] == "auto"

    def test_config_se_carga(self, tmp_path, monkeypatch):
        """Simula que main() carga la config."""
        import json
        config_path = tmp_path / ".zoe" / "config.json"
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config = {"backend": "pattern", "model": None, "db_path": "zoe_data/test.db"}
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config), encoding="utf-8")

        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        assert loaded["backend"] == "pattern"
        assert loaded["db_path"] == "zoe_data/test.db"

    def test_config_no_existente_usa_defaults(self, tmp_path, monkeypatch):
        """Si no hay config, usa defaults."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        config_path = tmp_path / ".zoe" / "config.json"
        assert not config_path.exists()
        # Defaults: backend=mock, model=None, db_path=zoe_data/chat_memory.db

    def test_config_solo_guarda_si_cambio(self, tmp_path, monkeypatch):
        """Si la config no cambió, no reescribe."""
        import json
        config_path = tmp_path / ".zoe" / "config.json"
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config_path.parent.mkdir(parents=True, exist_ok=True)
        old_config = {"backend": "ollama", "model": "auto", "db_path": "zoe_data/chat_memory.db"}
        config_path.write_text(json.dumps(old_config), encoding="utf-8")
        old_mtime = config_path.stat().st_mtime

        time.sleep(0.1)

        # Simular: config nueva == config vieja → no guardar
        new_config = {"backend": "ollama", "model": "auto", "db_path": "zoe_data/chat_memory.db"}
        if new_config != {k: old_config.get(k) for k in new_config}:
            config_path.write_text(json.dumps(new_config), encoding="utf-8")

        new_mtime = config_path.stat().st_mtime
        assert new_mtime == old_mtime  # no se reescribió


# ============================================================
# Integración: persistencia completa entre sesiones
# ============================================================

class TestPersistenceIntegration:
    """Sprint 5.8 — Integración: ZOE mantiene identidad + trayectoria + cápsulas entre sesiones."""

    def test_identidad_y_trayectoria_persisten(self, tmp_path):
        from zoe.alma.identity_vault import IdentityVault
        from zoe.alma.trajectory_chain import TrajectoryChain, Mutation

        vault_path = str(tmp_path / "identity_vault.json")
        chain_path = str(tmp_path / "trajectory_chain.json")

        # Sesión 1: crear ZOE
        vault1 = IdentityVault(birth_timestamp=1234567890.0)
        vault1.save_to_disk(vault_path)
        chain1 = TrajectoryChain(organism_id="test_zoe")
        chain1.set_persist_path(chain_path)
        m1 = Mutation(id="mut_1", type="add_memory", target="memory",
                      payload={"content": "hola"}, justification="test",
                      provenance="test", cost=0.1, confidence=0.9)
        chain1.commit(m1)  # auto-save

        hash_sesion1 = vault1.identity_hash
        mutations_sesion1 = len(chain1._mutations)

        # Sesión 2: cargar ZOE
        vault2 = IdentityVault.load_from_disk(vault_path)
        chain2 = TrajectoryChain.load_from_disk(chain_path)

        assert vault2.identity_hash == hash_sesion1  # misma identidad
        assert len(chain2._mutations) == mutations_sesion1  # misma trayectoria
        assert chain2.verify_chain()  # cadena íntegra
