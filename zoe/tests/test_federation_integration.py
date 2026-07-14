"""
Tests de integracion: dos instancias ZOE con peers.json compartido.

Verifica que:
1. Cada ZOE se anuncia en peers.json
2. Cada ZOE descubre a la otra
3. Mejoras publicadas por ZOE A aparecen como pending para ZOE B
"""

from __future__ import annotations

import json
import os
import time

import pytest

from zoe.core.federation_discovery import FederationDiscovery


class TestFederationDiscoveryIntegration:
    """Test discovery de peers via filesystem compartido."""

    def test_two_zoes_discover_each_other(self, tmp_path):
        """Dos ZOEs con el mismo peers_file deben descubrirse mutuamente."""
        peers_file = str(tmp_path / "peers.json")

        # ZOE A
        zoe_a = FederationDiscovery(
            organism_id="zoe_a",
            base_url="http://zoe-a.local:8642",
            discovery_mode="filesystem",
            peers_file=peers_file,
        )

        # ZOE B
        zoe_b = FederationDiscovery(
            organism_id="zoe_b",
            base_url="http://zoe-b.local:8642",
            discovery_mode="filesystem",
            peers_file=peers_file,
        )

        # Ambas se anuncian
        assert zoe_a.announce() is True
        assert zoe_b.announce() is True

        # Cada una descubre a la otra
        peers_a = zoe_a.discover()
        peers_b = zoe_b.discover()

        assert len(peers_a) == 1
        assert len(peers_b) == 1
        assert peers_a[0]["organism_id"] == "zoe_b"
        assert peers_b[0]["organism_id"] == "zoe_a"

    def test_stale_peers_filtered(self, tmp_path):
        """Peers con last_seen > 5 min deben ser filtrados."""
        peers_file = str(tmp_path / "peers.json")

        # Crear peers.json con un peer stale
        with open(peers_file, "w", encoding="utf-8") as f:
            json.dump({
                "zoe_stale": {
                    "organism_id": "zoe_stale",
                    "base_url": "http://stale.local:8642",
                    "last_seen": time.time() - 400,  # > 5 min
                }
            }, f)

        zoe = FederationDiscovery(
            organism_id="zoe_test",
            base_url="http://test.local:8642",
            discovery_mode="filesystem",
            peers_file=peers_file,
        )

        peers = zoe.discover()
        assert len(peers) == 0  # Stale peer filtrado

    def test_cleanup_stale(self, tmp_path):
        """cleanup_stale debe eliminar peers antiguos."""
        peers_file = str(tmp_path / "peers.json")

        with open(peers_file, "w", encoding="utf-8") as f:
            json.dump({
                "zoe_fresh": {
                    "organism_id": "zoe_fresh",
                    "base_url": "http://fresh.local:8642",
                    "last_seen": time.time(),
                },
                "zoe_stale": {
                    "organism_id": "zoe_stale",
                    "base_url": "http://stale.local:8642",
                    "last_seen": time.time() - 400,
                },
            }, f)

        zoe = FederationDiscovery(
            organism_id="zoe_test",
            base_url="http://test.local:8642",
            discovery_mode="filesystem",
            peers_file=peers_file,
        )

        removed = zoe.cleanup_stale(max_age_seconds=300)
        assert removed == 1

        with open(peers_file, "r", encoding="utf-8") as f:
            peers = json.load(f)
        assert "zoe_fresh" in peers
        assert "zoe_stale" not in peers


class TestPhylogeneticDistributed:
    """Test PhylogeneticMotor con pool compartido en disco."""

    def test_two_zoes_share_pool(self, tmp_path):
        """Dos PhylogeneticMotor con el mismo pool_path comparten mejoras."""
        pool_path = str(tmp_path / "phylo_pool.json")

        from zoe.core.phylogenetic_motor import (
            PhylogeneticMotor,
            ArchitecturalImprovement,
        )

        zoe_a = PhylogeneticMotor(zoe_id="zoe_a", pool_path=pool_path)
        # Pequena pausa para asegurar diferencia de mtime en filesystem
        time.sleep(0.05)
        zoe_b = PhylogeneticMotor(zoe_id="zoe_b", pool_path=pool_path)

        # ZOE A publica una mejora
        imp = ArchitecturalImprovement(
            id="test_imp_1",
            proposer="zoe_a",
            timestamp=time.time(),
            change_type="add_subagent",
            description="Test improvement",
            payload={"module": "test_module"},
            metrics_before={},
            metrics_after={},
            status="proposed",
            tested_by=[],
            incorporated_by=[],
        )
        zoe_a.pool.publish(imp)

        # Pequena pausa para que el mtime del archivo cambie
        time.sleep(0.05)

        # ZOE B debe verla como pending
        pending = zoe_b.pool.get_pending("zoe_b")
        assert len(pending) == 1
        assert pending[0].id == "test_imp_1"

        # ZOE B la prueba y valida
        zoe_b.pool.record_test_result("test_imp_1", "zoe_b", True, {}, {})

        # Necesita 2 validaciones: zoe_c tambien valida
        time.sleep(0.05)
        zoe_a.pool.record_test_result("test_imp_1", "zoe_c", True, {}, {})

        time.sleep(0.05)
        validated = zoe_b.pool.get_validated()
        assert len(validated) == 1
        assert validated[0].status == "validated"
