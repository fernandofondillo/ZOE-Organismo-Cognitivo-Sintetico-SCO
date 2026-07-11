"""
Tests Fase 6A Punto 2 + 3 + Fase 6B Marketplace

Cubre:
- Punto 2: federación epistémica real (server + client + endpoints)
- Punto 3: cuarentena en Dashboard (stats, list, promote, reject)
- Punto 4: marketplace (catalog, upload, download, license)
"""

import asyncio
import json
import pytest
import tempfile
import time
from pathlib import Path

from zoe.core.epistemic_federation import EpistemicFederation
from zoe.core.epistemic_federation_server import (
    EpistemicFederationServer, EpistemicFederationClient, PeerEndpoint,
)
from zoe.core.knowledge_quarantine import KnowledgeQuarantine
from zoe.marketplace import (
    MarketplaceCatalog, MarketplaceEntry, CapsuleLicense, LicenseType,
    CapsulePackager, MarketplaceUploader, MarketplaceDownloader, LicenseChecker,
)


# ============================================================
# Punto 2: Federación epistémica server/client
# ============================================================

class TestEpistemicFederationServer:

    def test_server_init(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        server = EpistemicFederationServer(fed)
        assert server.federation.organism_id == "zoe_1"
        assert len(server._peers) == 0

    def test_register_peer(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        server = EpistemicFederationServer(fed)
        server.register_peer("zoe_2", "http://zoe-2.local:8642")
        assert "zoe_2" in server._peers
        assert server._peers["zoe_2"].base_url == "http://zoe-2.local:8642"

    @pytest.mark.asyncio
    async def test_handle_validate_request_confirmed(self):
        """Server responde 'confirmed' si tiene el claim indexado."""
        fed = EpistemicFederation(organism_id="zoe_1")
        # Indexar claim local
        import hashlib
        claim = "Las benzodiacepinas son peligrosas en mayores."
        claim_hash = hashlib.md5(claim.encode()).hexdigest()
        fed.index_local_knowledge(claim_hash, {
            "content": claim,
            "confidence": 0.9,
            "provenance": "capsule:verified",
        })
        
        server = EpistemicFederationServer(fed)
        
        request_data = {
            "request_id": "req_1",
            "claim": claim,
            "source": "llm:gpt-4o",
            "domain": "medical",
            "confidence_local": 0.5,
            "sender_id": "zoe_2",
            "timestamp": time.time(),
        }
        
        result = await server.handle_validate_request(request_data)
        assert result["status"] == "ok"
        assert result["response"]["response"] == "confirmed"
        assert result["response"]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_handle_validate_request_unknown(self):
        """Server responde 'unknown' si no conoce el claim."""
        fed = EpistemicFederation(organism_id="zoe_1")
        server = EpistemicFederationServer(fed)
        
        request_data = {
            "request_id": "req_2",
            "claim": "Algo que no conozco.",
            "source": "zoe_3",
            "sender_id": "zoe_3",
            "timestamp": time.time(),
        }
        
        result = await server.handle_validate_request(request_data)
        assert result["response"]["response"] == "unknown"

    @pytest.mark.asyncio
    async def test_handle_knowledge_query(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        import hashlib
        claim = "test claim"
        claim_hash = hashlib.md5(claim.encode()).hexdigest()
        fed.index_local_knowledge(claim_hash, {"content": claim, "confidence": 0.8})
        
        server = EpistemicFederationServer(fed)
        result = await server.handle_knowledge_query(claim_hash)
        assert result["found"] is True
        assert result["confidence"] == 0.8

    @pytest.mark.asyncio
    async def test_handle_knowledge_query_not_found(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        server = EpistemicFederationServer(fed)
        result = await server.handle_knowledge_query("nonexistent_hash")
        assert result["found"] is False

    @pytest.mark.asyncio
    async def test_handle_register_peer(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        server = EpistemicFederationServer(fed)
        
        result = await server.handle_register_peer({
            "organism_id": "zoe_2",
            "base_url": "http://zoe-2:8642",
        })
        assert result["status"] == "ok"
        assert "zoe_2" in server._peers

    def test_get_stats(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        server = EpistemicFederationServer(fed)
        server.register_peer("zoe_2", "http://zoe-2:8642")
        stats = server.get_stats()
        assert stats["peers_count"] == 1
        assert "federation_stats" in stats


class TestEpistemicFederationClient:

    def test_client_init(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        client = EpistemicFederationClient(fed)
        assert client.federation.organism_id == "zoe_1"
        assert len(client._peers) == 0

    def test_add_remove_peer(self):
        fed = EpistemicFederation(organism_id="zoe_1")
        client = EpistemicFederationClient(fed)
        client.add_peer("zoe_2", "http://zoe-2:8642")
        assert "zoe_2" in client.list_peers()
        client.remove_peer("zoe_2")
        assert "zoe_2" not in client.list_peers()

    @pytest.mark.asyncio
    async def test_request_validation_no_peers(self):
        """Sin peers, devuelve no_peers."""
        fed = EpistemicFederation(organism_id="zoe_1")
        client = EpistemicFederationClient(fed)
        result = await client.request_validation_from_peers(
            claim="test", source="llm", domain=None, confidence_local=0.5
        )
        assert result["final_status"] == "no_peers"

    @pytest.mark.asyncio
    async def test_request_validation_with_mock_peers(self):
        """Con peers que no responden (timeout), devuelve pending."""
        fed = EpistemicFederation(organism_id="zoe_1")
        client = EpistemicFederationClient(fed)
        # Añadir peer con URL inválida (timeout)
        client.add_peer("zoe_2", "http://nonexistent-zoe-2:9999")
        
        result = await client.request_validation_from_peers(
            claim="test claim",
            source="llm:gpt-4o",
            domain=None,
            confidence_local=0.5,
            timeout_per_peer=1.0,  # corto
        )
        # Como el peer no responde, se trata como unknown
        assert result["final_status"] in ("pending", "incomplete")
        assert result["unknowns"] >= 1


# ============================================================
# Punto 3: Cuarentena (re-verifica que endpoints funcionarían)
# ============================================================

class TestQuarantineEndpoints:

    def test_quarantine_list_active(self):
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q1", claim="test1", source="llm",
            confidence=0.5, domain="medical", reason="test",
            verification_plan={}, memory_entry_id="mem1",
        )
        q.add(
            entry_id="q2", claim="test2", source="llm",
            confidence=0.5, domain=None, reason="test",
            verification_plan={}, memory_entry_id="mem2",
        )
        active = q.list_active()
        assert len(active) == 2
        
        # Filtrar por dominio
        medical = q.list_active(domain="medical")
        assert len(medical) == 1
        assert medical[0].entry_id == "q1"

    def test_quarantine_promote(self):
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q1", claim="test", source="llm",
            confidence=0.5, domain=None, reason="test",
            verification_plan={}, memory_entry_id="mem1",
        )
        entry = q.promote("q1", 0.85, "manual_test")
        assert entry.status == "verified"
        assert entry.confidence == 0.85

    def test_quarantine_reject(self):
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q1", claim="test", source="llm",
            confidence=0.5, domain=None, reason="test",
            verification_plan={}, memory_entry_id="mem1",
        )
        entry = q.reject("q1", "admin", "manual_rejection")
        assert entry.status == "rejected"
        assert "admin" in entry.contradictions

    def test_quarantine_stats(self):
        q = KnowledgeQuarantine()
        q.add(
            entry_id="q1", claim="a", source="llm",
            confidence=0.5, domain="medical", reason="t",
            verification_plan={},
        )
        q.add(
            entry_id="q2", claim="b", source="llm",
            confidence=0.5, domain=None, reason="t",
            verification_plan={},
        )
        q.promote("q1", 0.85, "test")
        stats = q.get_stats()
        assert stats["total"] == 2
        assert stats["active"] == 1
        assert stats["verified"] == 1
        # Domain None se cuenta como "unknown" en stats
        assert stats["by_domain_active"].get("unknown", 0) == 1


# ============================================================
# Punto 4: Marketplace
# ============================================================

class TestMarketplaceCatalog:

    def test_catalog_init(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        assert catalog.catalog_dir.exists()
        assert (catalog.catalog_dir / "capsules").exists()
        assert (catalog.catalog_dir / "use_cases").exists()
        assert (catalog.catalog_dir / "metadata").exists()

    def test_add_and_get_entry(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        entry = MarketplaceEntry(
            name="test_capsule",
            version="1.0.0",
            description="Test",
            author="test_author",
            type="capsule",
            license=CapsuleLicense(type=LicenseType.FREE),
        )
        catalog.add(entry)
        
        retrieved = catalog.get("test_capsule")
        assert retrieved is not None
        assert retrieved.name == "test_capsule"
        assert retrieved.author == "test_author"

    def test_list_capsules_and_use_cases(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        catalog.add(MarketplaceEntry(
            name="cap1", version="1.0", description="d", author="a", type="capsule"
        ))
        catalog.add(MarketplaceEntry(
            name="uc1", version="1.0", description="d", author="a", type="use_case"
        ))
        
        assert len(catalog.list_capsules()) == 1
        assert len(catalog.list_use_cases()) == 1
        assert len(catalog.list_all()) == 2

    def test_search(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        catalog.add(MarketplaceEntry(
            name="elder_care", version="1.0", description="Cuidado de mayores",
            author="a", type="capsule", domain="healthcare.elders",
            tags=["elderly", "care"],
        ))
        catalog.add(MarketplaceEntry(
            name="devops_mon", version="1.0", description="DevOps monitoring",
            author="a", type="capsule", domain="tech.devops",
        ))
        
        results = catalog.search("elder")
        assert len(results) == 1
        assert results[0].name == "elder_care"
        
        results = catalog.search("devops")
        assert len(results) == 1
        assert results[0].name == "devops_mon"

    def test_remove(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        catalog.add(MarketplaceEntry(
            name="test", version="1.0", description="d", author="a", type="capsule"
        ))
        assert catalog.remove("test") is True
        assert catalog.get("test") is None

    def test_increment_downloads(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        catalog.add(MarketplaceEntry(
            name="test", version="1.0", description="d", author="a", type="capsule"
        ))
        assert catalog.get("test").downloads == 0
        catalog.increment_downloads("test")
        assert catalog.get("test").downloads == 1

    def test_add_rating(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        catalog.add(MarketplaceEntry(
            name="test", version="1.0", description="d", author="a", type="capsule"
        ))
        catalog.add_rating("test", 4.0)
        catalog.add_rating("test", 5.0)
        entry = catalog.get("test")
        assert entry.rating_count == 2
        assert entry.rating == 4.5

    def test_stats(self, tmp_path):
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        catalog.add(MarketplaceEntry(
            name="cap1", version="1.0", description="d", author="a", type="capsule",
            license=CapsuleLicense(type=LicenseType.FREE),
        ))
        catalog.add(MarketplaceEntry(
            name="cap2", version="1.0", description="d", author="a", type="capsule",
            license=CapsuleLicense(type=LicenseType.PAID, price=9.99),
        ))
        catalog.add(MarketplaceEntry(
            name="uc1", version="1.0", description="d", author="a", type="use_case",
        ))
        
        stats = catalog.get_stats()
        assert stats["total"] == 3
        assert stats["capsules"] == 2
        assert stats["use_cases"] == 1
        assert stats["by_license"]["free"] == 2
        assert stats["by_license"]["paid"] == 1

    def test_persistence(self, tmp_path):
        """Las entries persisten entre instancias del catálogo."""
        catalog1 = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        catalog1.add(MarketplaceEntry(
            name="persistent", version="1.0", description="d", author="a", type="capsule"
        ))
        
        # Nueva instancia carga el catálogo desde disco
        catalog2 = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        assert catalog2.get("persistent") is not None


class TestCapsulePackager:

    def test_package_and_unpackage_capsule(self, tmp_path):
        """Empaqueta y desempaqueta una cápsula correctamente."""
        # Crear cápsula de prueba
        cap_dir = tmp_path / "test_capsule"
        cap_dir.mkdir()
        (cap_dir / "capsule.yaml").write_text("name: test\ndescription: test\n")
        (cap_dir / "semantic_memory.jsonl").write_text('{"content": "test"}\n')
        
        # Empaquetar
        output = tmp_path / "test.zcap"
        content_hash = CapsulePackager.package_capsule(cap_dir, output)
        
        assert output.exists()
        assert content_hash.startswith("sha256:")
        
        # Desempaquetar
        target = tmp_path / "unpacked"
        target.mkdir()
        ok = CapsulePackager.unpackage(output, target)
        assert ok is True
        # El contenido se extrae en subdirectorio test_capsule/
        assert (target / "test_capsule" / "capsule.yaml").exists() or \
               (target / "capsule.yaml").exists()

    def test_package_use_case(self, tmp_path):
        yaml_path = tmp_path / "test_case.yaml"
        yaml_path.write_text("use_case:\n  name: test\n")
        
        output = tmp_path / "test.zyaml"
        content_hash = CapsulePackager.package_use_case(yaml_path, output)
        
        assert output.exists()
        assert content_hash.startswith("sha256:")


class TestMarketplaceUploader:

    def test_upload_capsule(self, tmp_path):
        """Sube una cápsula existente al marketplace."""
        # Crear cápsula
        capsules_dir = tmp_path / "capsules"
        capsules_dir.mkdir()
        cap_dir = capsules_dir / "test_cap"
        cap_dir.mkdir()
        (cap_dir / "capsule.yaml").write_text(
            "name: test_cap\nversion: 1.0.0\ndescription: Test\ndomain: test\ntrust_level: community\n"
        )
        (cap_dir / "semantic_memory.jsonl").write_text('{"content": "test"}\n')
        
        # Marketplace
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        use_cases_dir = tmp_path / "use_cases"
        use_cases_dir.mkdir()
        
        uploader = MarketplaceUploader(catalog, capsules_dir, use_cases_dir)
        ok, hash_or_msg = uploader.upload_capsule(
            capsule_name="test_cap",
            author="test_author",
            description="Test capsule",
            license_data={"type": "free"},
            tags=["test"],
        )
        
        assert ok is True
        assert hash_or_msg.startswith("sha256:")
        
        # Verificar que está en el catálogo
        entry = catalog.get("test_cap")
        assert entry is not None
        assert entry.author == "test_author"
        assert entry.license.type == "free"

    def test_upload_use_case(self, tmp_path):
        # Crear caso de uso
        use_cases_dir = tmp_path / "use_cases"
        use_cases_dir.mkdir()
        yaml_path = use_cases_dir / "test_uc.yaml"
        yaml_path.write_text("use_case:\n  name: test_uc\n")
        
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        capsules_dir = tmp_path / "capsules"
        capsules_dir.mkdir()
        
        uploader = MarketplaceUploader(catalog, capsules_dir, use_cases_dir)
        ok, hash_or_msg = uploader.upload_use_case(
            use_case_name="test_uc",
            author="test_author",
            description="Test use case",
            license_data={"type": "opensource"},
        )
        
        assert ok is True
        entry = catalog.get("test_uc")
        assert entry is not None
        assert entry.type == "use_case"


class TestMarketplaceDownloader:

    def test_download_capsule(self, tmp_path):
        """Descarga e instala una cápsula desde el marketplace."""
        # Setup: crear y subir cápsula
        capsules_dir = tmp_path / "capsules"
        capsules_dir.mkdir()
        cap_dir = capsules_dir / "downloadable_cap"
        cap_dir.mkdir()
        (cap_dir / "capsule.yaml").write_text(
            "name: downloadable_cap\nversion: 1.0.0\ndescription: Test\ndomain: test\ntrust_level: community\n"
        )
        (cap_dir / "semantic_memory.jsonl").write_text('{"content": "test"}\n')
        
        catalog = MarketplaceCatalog(catalog_dir=tmp_path / "marketplace")
        use_cases_dir = tmp_path / "use_cases"
        use_cases_dir.mkdir()
        
        uploader = MarketplaceUploader(catalog, capsules_dir, use_cases_dir)
        uploader.upload_capsule(
            capsule_name="downloadable_cap",
            author="author",
            description="Test",
            license_data={"type": "free"},
        )
        
        # Eliminar la cápsula original
        import shutil
        shutil.rmtree(cap_dir)
        assert not cap_dir.exists()
        
        # Descargar desde marketplace
        downloader = MarketplaceDownloader(catalog, capsules_dir, use_cases_dir)
        ok, msg = downloader.download_capsule("downloadable_cap")
        
        assert ok is True
        assert "installed" in msg
        # Verificar que se instaló
        assert (capsules_dir / "downloadable_cap").exists() or \
               any(capsules_dir.glob("*downloadable_cap*"))
        
        # Verificar que downloads incrementó
        entry = catalog.get("downloadable_cap")
        assert entry.downloads == 1


class TestLicenseChecker:

    def test_free_license_always_allowed(self):
        entry = MarketplaceEntry(
            name="free_cap", version="1.0", description="d", author="a",
            license=CapsuleLicense(type=LicenseType.FREE),
        )
        ok, _ = LicenseChecker.can_use(entry, user_has_paid=False)
        assert ok is True

    def test_paid_license_requires_payment(self):
        entry = MarketplaceEntry(
            name="paid_cap", version="1.0", description="d", author="a",
            license=CapsuleLicense(type=LicenseType.PAID, price=19.99),
        )
        ok, reason = LicenseChecker.can_use(entry, user_has_paid=False)
        assert ok is False
        assert reason == "payment_required"
        
        ok, _ = LicenseChecker.can_use(entry, user_has_paid=True)
        assert ok is True

    def test_subscription_license(self):
        entry = MarketplaceEntry(
            name="sub_cap", version="1.0", description="d", author="a",
            license=CapsuleLicense(type=LicenseType.SUBSCRIPTION, price=9.99, subscription_period="monthly"),
        )
        ok, reason = LicenseChecker.can_use(entry, user_has_paid=False)
        assert ok is False
        assert reason == "subscription_required"

    def test_opensource_license(self):
        entry = MarketplaceEntry(
            name="os_cap", version="1.0", description="d", author="a",
            license=CapsuleLicense(type=LicenseType.OPENSOURCE),
        )
        ok, _ = LicenseChecker.can_use(entry, user_has_paid=False)
        assert ok is True

    def test_research_license(self):
        entry = MarketplaceEntry(
            name="res_cap", version="1.0", description="d", author="a",
            license=CapsuleLicense(type=LicenseType.RESEARCH),
        )
        ok, _ = LicenseChecker.can_use(entry, user_has_paid=False)
        assert ok is True

    def test_get_payment_info(self):
        entry = MarketplaceEntry(
            name="paid_cap", version="1.0", description="d", author="author_name",
            author_url="https://example.com",
            license=CapsuleLicense(type=LicenseType.PAID, price=29.99, currency="EUR"),
        )
        info = LicenseChecker.get_payment_info(entry)
        assert info["license_type"] == "paid"
        assert info["price"] == 29.99
        assert info["currency"] == "EUR"
        assert info["author"] == "author_name"
