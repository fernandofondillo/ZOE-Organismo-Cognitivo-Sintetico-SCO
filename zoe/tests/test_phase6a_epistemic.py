"""
Tests Fase 6A — Epistemic Validation System + Capsule Manager

Cubre las 4 opciones:
1. EpistemicValidator (validación por fuente y dominio)
2. KnowledgeQuarantine (cuarentena activa)
3. CrossValidator (triple verificación multi-fuente)
4. EpistemicFederation (validación federada entre ZOEs)

Y CapsuleManager (carga runtime + integración con organismo)
"""

import asyncio
import pytest
import time

from zoe.core.epistemic_validator import (
    EpistemicValidator, ValidationResult, ValidationStatus,
    SOURCE_TRUST, SENSITIVE_DOMAINS,
    MAX_AUTO_LEARNED_CONFIDENCE, MAX_TRIPLE_VERIFIED_CONFIDENCE,
    MAX_FEDERATIVELY_VALIDATED_CONFIDENCE, MAX_CAPSULE_VERIFIED_CONFIDENCE,
)
from zoe.core.knowledge_quarantine import KnowledgeQuarantine, QuarantineEntry
from zoe.core.cross_validator import CrossValidator, CrossVerificationResult
from zoe.core.epistemic_federation import (
    EpistemicFederation, KnowledgeValidationRequest, KnowledgeValidationResponse,
)
from zoe.core.capsule_manager import CapsuleManager, CapsuleLoadResult


# ============================================================
# 1. EpistemicValidator
# ============================================================

class TestEpistemicValidator:

    def setup_method(self):
        self.v = EpistemicValidator()

    def test_source_trust_levels(self):
        """Las fuentes tienen confianza base correcta."""
        assert SOURCE_TRUST["capsule:verified"] == 0.95
        assert SOURCE_TRUST["llm:gpt-4o"] == 0.50
        assert SOURCE_TRUST["scientific:pubmed"] == 0.95
        assert SOURCE_TRUST["web:general"] == 0.30
        assert SOURCE_TRUST["unknown"] == 0.20

    def test_capsule_verified_accepted_high_confidence(self):
        """Cápsula verificada se acepta con confianza 0.95."""
        result = self.v.validate_new_knowledge(
            claim="Las benzodiacepinas aumentan riesgo de caídas en mayores.",
            source="capsule:verified",
            context={},
        )
        assert result.status == ValidationStatus.ACCEPTED
        assert result.confidence == 0.95
        assert not result.quarantine

    def test_llm_single_source_quarantined(self):
        """LLM fuente única → cuarentena con confianza ≤0.50."""
        result = self.v.validate_new_knowledge(
            claim="Los gatos maúllan para comunicarse con humanos.",
            source="llm:gpt-4o",
            context={},
        )
        assert result.status == ValidationStatus.ACCEPTED_WITH_QUARANTINE
        assert result.quarantine is True
        assert result.confidence <= MAX_AUTO_LEARNED_CONFIDENCE

    def test_sensitive_domain_requires_triple(self):
        """Dominio sensible con fuente no confiable → requiere triple."""
        result = self.v.validate_new_knowledge(
            claim="La dosis recomendada de paracetamol es 1g cada 6 horas.",
            source="llm:gpt-4o",
            context={},
        )
        assert result.status == ValidationStatus.NEEDS_TRIPLE_VALIDATION
        assert result.quarantine is True
        assert result.needs_verification_plan is True
        assert "sensitive_domain" in result.reason

    def test_contradicts_verified_knowledge_rejected(self):
        """Claim que contradice conocimiento verificado → rechazado."""
        verified = [
            {
                "content": "Las benzodiacepinas aumentan riesgo de caídas en mayores.",
                "confidence": 0.92,
                "provenance": "capsule:verified:elder_care",
            }
        ]
        result = self.v.validate_new_knowledge(
            claim="Las benzodiacepinas no aumentan riesgo de caídas en mayores.",
            source="llm:gpt-4o",
            context={"verified_knowledge": verified},
        )
        assert result.status == ValidationStatus.REJECTED
        assert "contradicts_verified" in result.reason

    def test_capsule_verified_in_sensitive_domain_accepted(self):
        """Cápsula verificada en dominio sensible → aceptada (es fuente confiable)."""
        result = self.v.validate_new_knowledge(
            claim="La escala GDS-15 es el cribado recomendado para depresión geriátrica.",
            source="capsule:verified",
            context={},
        )
        assert result.status == ValidationStatus.ACCEPTED
        assert not result.quarantine

    def test_federatively_validated_capped(self):
        """Conocimiento federativamente validado tiene cap 0.85."""
        result = self.v.validate_new_knowledge(
            claim="Algunos hecho validado federativamente.",
            source="federatively_validated:2plus_peers",
            context={},
        )
        assert result.status == ValidationStatus.ACCEPTED
        assert result.confidence <= MAX_FEDERATIVELY_VALIDATED_CONFIDENCE

    def test_triple_verified_capped(self):
        """Triple verificado tiene cap 0.75."""
        result = self.v.validate_new_knowledge(
            claim="Hecho validado por triple verificación multi-LLM.",
            source="multi_source:llm_cross_validated",
            context={},
        )
        assert result.status == ValidationStatus.ACCEPTED
        assert result.confidence <= MAX_TRIPLE_VERIFIED_CONFIDENCE

    def test_detect_domain_medical(self):
        """Detecta dominio médico correctamente."""
        assert self.v._detect_domain("hablo de medicación y dosis") == "medical"
        assert self.v._detect_domain("trastorno de ansiedad") == "psychological"
        assert self.v._detect_domain("contrato de compraventa") == "legal"
        assert self.v._detect_domain("alarma de emergencia") == "safety"
        assert self.v._detect_domain("inversión en banca") == "financial"
        assert self.v._detect_domain("el cielo es azul") is None

    def test_stats_track_validations(self):
        """Las estadísticas se actualizan con cada validación."""
        initial = self.v.validations
        self.v.validate_new_knowledge("test claim", "llm:gpt-4o", context={})
        self.v.validate_new_knowledge("test claim 2", "capsule:verified", context={})
        assert self.v.validations == initial + 2
        assert "llm:gpt-4o" in self.v.by_source
        assert "capsule:verified" in self.v.by_source

    def test_verification_plan_generated(self):
        """Cuando se requiere cuarentena, se genera plan de verificación."""
        result = self.v.validate_new_knowledge(
            claim="algo nuevo que aprender",
            source="llm:gpt-4o",
            context={},
        )
        assert result.verification_plan is not None
        assert "required_verifications" in result.verification_plan
        assert "timeout_days" in result.verification_plan
        assert result.verification_plan["timeout_days"] == 30


# ============================================================
# 2. KnowledgeQuarantine
# ============================================================

class TestKnowledgeQuarantine:

    def setup_method(self):
        self.q = KnowledgeQuarantine(default_timeout_days=30)

    def test_add_entry(self):
        entry = self.q.add(
            entry_id="q1",
            claim="test claim",
            source="llm:gpt-4o",
            confidence=0.5,
            domain="medical",
            reason="accepted_with_quarantine",
            verification_plan={"required_verifications": 2, "timeout_days": 30},
            memory_entry_id="mem1",
        )
        assert entry.entry_id == "q1"
        assert entry.status == "active"

    def test_is_quarantined(self):
        self.q.add(
            entry_id="q1",
            claim="test",
            source="llm:gpt-4o",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id="mem1",
        )
        assert self.q.is_quarantined("mem1") is True
        assert self.q.is_quarantined("mem_inexistente") is False

    def test_filter_safe_critical_context(self):
        """En contexto crítico, las entradas en cuarentena se eliminan."""
        self.q.add(
            entry_id="q1",
            claim="claim sensible",
            source="llm:gpt-4o",
            confidence=0.5,
            domain="medical",
            reason="test",
            verification_plan={},
            memory_entry_id="mem1",
        )
        entries = [
            {"id": "mem1", "content": "claim sensible"},
            {"id": "mem2", "content": "claim seguro"},
        ]
        safe = self.q.filter_safe(entries, critical_context=True)
        assert len(safe) == 1
        assert safe[0]["id"] == "mem2"

    def test_filter_safe_non_critical(self):
        """En contexto no crítico, se mantienen pero se marcan."""
        self.q.add(
            entry_id="q1",
            claim="claim sensible",
            source="llm:gpt-4o",
            confidence=0.5,
            domain="medical",
            reason="test",
            verification_plan={},
            memory_entry_id="mem1",
        )
        entries = [
            {"id": "mem1", "content": "claim sensible"},
            {"id": "mem2", "content": "claim seguro"},
        ]
        result = self.q.filter_safe(entries, critical_context=False)
        assert len(result) == 2
        # mem1 debe estar marcada
        mem1 = next(e for e in result if e["id"] == "mem1")
        assert mem1.get("metadata", {}).get("quarantine") is True

    def test_verify_promotes_after_enough_confirmations(self):
        """Tras suficientes verificaciones, se promueve."""
        self.q.add(
            entry_id="q1",
            claim="test",
            source="llm:gpt-4o",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={"required_verifications": 2, "timeout_days": 30},
            memory_entry_id="mem1",
        )
        # Primera verificación
        entry = self.q.verify("q1", "llm:qwen-7b", 0.65)
        assert entry.status == "active"  # aún no promovido (1 de 2)
        # Segunda verificación
        entry = self.q.verify("q1", "capsule:verified", 0.75)
        assert entry.status == "verified"  # promovido

    def test_reject(self):
        self.q.add(
            entry_id="q1",
            claim="test",
            source="llm:gpt-4o",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id="mem1",
        )
        entry = self.q.reject("q1", "capsule:verified", reason="contradicted")
        assert entry.status == "rejected"
        assert "capsule:verified" in entry.contradictions

    def test_cleanup_expired(self):
        """Las entradas expiradas se marcan correctamente."""
        q = KnowledgeQuarantine(default_timeout_days=1)
        # Forzar expires_at en el pasado
        q.add(
            entry_id="q1",
            claim="test",
            source="llm:gpt-4o",
            confidence=0.5,
            domain=None,
            reason="test",
            verification_plan={},
            memory_entry_id="mem1",
        )
        q._entries["q1"].expires_at = time.time() - 1  # ya expirado
        expired = q.cleanup_expired()
        assert expired == 1

    def test_stats(self):
        self.q.add(
            entry_id="q1", claim="a", source="llm", confidence=0.5,
            domain="medical", reason="t", verification_plan={},
        )
        self.q.add(
            entry_id="q2", claim="b", source="llm", confidence=0.5,
            domain="psychological", reason="t", verification_plan={},
        )
        self.q.promote("q1", 0.8, "test")
        stats = self.q.get_stats()
        assert stats["total"] == 2
        assert stats["active"] == 1
        assert stats["verified"] == 1


# ============================================================
# 3. CrossValidator
# ============================================================

class TestCrossValidator:

    def setup_method(self):
        self.v = EpistemicValidator()
        self.q = KnowledgeQuarantine()
        self.cv = CrossValidator(self.v, self.q)

    @pytest.mark.asyncio
    async def test_full_agreement(self):
        """3 fuentes que coinciden → confianza 0.75, ACCEPTED."""
        async def mock_query(claim):
            return "Las benzodiacepinas son peligrosas en mayores."
        
        self.cv.register_source("llm:gpt-4o", mock_query)
        self.cv.register_source("llm:qwen-7b", mock_query)
        self.cv.register_source("llm:claude-sonnet", mock_query)
        
        result = await self.cv.verify_triple(
            claim="Las benzodiacepinas son peligrosas en mayores.",
            sources=["llm:gpt-4o", "llm:qwen-7b", "llm:claude-sonnet"],
        )
        assert result.agreement == "full"
        assert result.final_confidence == MAX_TRIPLE_VERIFIED_CONFIDENCE
        assert result.final_status == ValidationStatus.ACCEPTED

    @pytest.mark.asyncio
    async def test_divergence(self):
        """3 fuentes divergentes → rechazo."""
        async def query_a(claim): return "Respuesta A sobre el tema."
        async def query_b(claim): return "Respuesta B completamente diferente."
        async def query_c(claim): return "Respuesta C totalmente distinta tambien."
        
        self.cv.register_source("llm:gpt-4o", query_a)
        self.cv.register_source("llm:qwen-7b", query_b)
        self.cv.register_source("llm:claude-sonnet", query_c)
        
        result = await self.cv.verify_triple(
            claim="test claim",
            sources=["llm:gpt-4o", "llm:qwen-7b", "llm:claude-sonnet"],
        )
        assert result.agreement == "divergent"
        assert result.final_status == ValidationStatus.REJECTED

    @pytest.mark.asyncio
    async def test_majority_agreement(self):
        """2 de 3 coinciden → mayoría, ACCEPTED_WITH_QUARANTINE."""
        async def query_a(claim): return "Las benzodiacepinas aumentan riesgo."
        async def query_b(claim): return "Las benzodiacepinas aumentan riesgo."
        async def query_c(claim): return "Las benzodiacepinas son seguras."
        
        self.cv.register_source("llm:gpt-4o", query_a)
        self.cv.register_source("llm:qwen-7b", query_b)
        self.cv.register_source("llm:claude-sonnet", query_c)
        
        result = await self.cv.verify_triple(
            claim="test",
            sources=["llm:gpt-4o", "llm:qwen-7b", "llm:claude-sonnet"],
        )
        assert result.agreement == "majority"
        assert result.final_status == ValidationStatus.ACCEPTED_WITH_QUARANTINE

    @pytest.mark.asyncio
    async def test_verify_and_promote(self):
        """verify_and_promote actualiza el estado en cuarentena."""
        # Añadir entrada en cuarentena
        self.q.add(
            entry_id="q1",
            claim="Las benzodiacepinas son peligrosas.",
            source="llm:gpt-4o",
            confidence=0.5,
            domain="medical",
            reason="test",
            verification_plan={"required_verifications": 2, "timeout_days": 30},
        )
        
        async def mock_query(claim):
            return "Las benzodiacepinas son peligrosas."
        
        self.cv.register_source("llm:gpt-4o", mock_query)
        self.cv.register_source("llm:qwen-7b", mock_query)
        self.cv.register_source("llm:claude-sonnet", mock_query)
        
        result = await self.cv.verify_and_promote(
            quarantine_entry_id="q1",
            claim="Las benzodiacepinas son peligrosas.",
            sources=["llm:gpt-4o", "llm:qwen-7b", "llm:claude-sonnet"],
        )
        assert result.final_status == ValidationStatus.ACCEPTED
        # Verificar que se promovió en cuarentena
        entry = self.q._entries.get("q1")
        assert entry.status == "verified"

    def test_lexical_similarity(self):
        """La similitud léxica funciona correctamente."""
        sim = self.cv._lexical_similarity(
            "las benzodiacepinas son peligrosas",
            "las benzodiacepinas son peligrosas",
        )
        assert sim == 1.0
        
        sim = self.cv._lexical_similarity(
            "las benzodiacepinas son peligrosas",
            "los gatos maúllan de noche",
        )
        assert sim < 0.3

    def test_stats_track_verifications(self):
        assert self.cv.cross_verifications == 0
        asyncio.run(self.test_full_agreement())
        assert self.cv.cross_verifications >= 1


# ============================================================
# 4. EpistemicFederation
# ============================================================

class TestEpistemicFederation:

    def setup_method(self):
        self.fed = EpistemicFederation(organism_id="zoe_test_1")

    def test_request_validation(self):
        """Solicitud de validación se registra como pendiente."""
        sent_to = []
        def send_callback(peer_id, msg):
            sent_to.append(peer_id)
        
        self.fed.register_send_callback(send_callback)
        
        req_id = self.fed.request_validation(
            claim="Las benzodiacepinas son seguras en mayores.",
            source="llm:gpt-4o",
            domain="medical",
            confidence_local=0.5,
            peer_ids=["zoe_test_2", "zoe_test_3"],
        )
        
        assert req_id.startswith("req_")
        assert len(sent_to) == 2  # enviado a 2 peers
        assert self.fed.requests_sent == 1
        assert req_id in self.fed._pending_requests

    def test_receive_validation_request_confirmed(self):
        """Peer confirma cuando tiene el claim indexado."""
        import hashlib
        claim = "Las benzodiacepinas son seguras en mayores."
        claim_hash = hashlib.sha256(claim.encode()).hexdigest()
        
        self.fed.index_local_knowledge(claim_hash, {
            "content": claim,
            "confidence": 0.85,
            "provenance": "capsule:verified",
        })
        
        request_data = {
            "request_id": "req_test_1",
            "claim": claim,
            "source": "zoe_other",
            "domain": "medical",
            "confidence_local": 0.5,
            "sender_id": "zoe_other",
            "timestamp": time.time(),
        }
        
        response = self.fed.receive_validation_request(request_data)
        assert response.response == "confirmed"
        assert response.confidence == 0.85
        assert self.fed.confirmations_sent == 1

    def test_receive_validation_request_unknown(self):
        """Si no conoce, responde unknown."""
        request_data = {
            "request_id": "req_test_2",
            "claim": "Algo que no conozco.",
            "source": "zoe_other",
            "sender_id": "zoe_other",
            "timestamp": time.time(),
        }
        
        response = self.fed.receive_validation_request(request_data)
        assert response.response == "unknown"
        assert self.fed.unknowns_sent == 1

    def test_receive_responses_and_promote(self):
        """Tras 2 confirmaciones, promueve (sale de cuarentena)."""
        sent_to = []
        self.fed.register_send_callback(lambda p, m: sent_to.append(p))
        
        req_id = self.fed.request_validation(
            claim="test claim federated",
            source="llm:gpt-4o",
            domain=None,
            confidence_local=0.5,
            peer_ids=["peer1", "peer2"],
        )
        
        # Simular 2 respuestas confirmed
        result = self.fed.receive_validation_response({
            "request_id": req_id,
            "responder_id": "peer1",
            "response": "confirmed",
            "confidence": 0.8,
            "evidence": "local_verified",
        })
        # Solo 1 confirmación → pendiente
        assert result is None
        
        result = self.fed.receive_validation_response({
            "request_id": req_id,
            "responder_id": "peer2",
            "response": "confirmed",
            "confidence": 0.75,
            "evidence": "local_verified",
        })
        # 2 confirmaciones → promovido
        assert result is not None
        assert result["status"] == "promoted"
        assert result["final_confidence"] == 0.85
        assert self.fed.promotions == 1

    def test_receive_contradiction_rejects(self):
        """1 contradicción es suficiente para rechazar."""
        self.fed.register_send_callback(lambda p, m: None)
        
        req_id = self.fed.request_validation(
            claim="test claim",
            source="llm:gpt-4o",
            domain=None,
            confidence_local=0.5,
            peer_ids=["peer1"],
        )
        
        result = self.fed.receive_validation_response({
            "request_id": req_id,
            "responder_id": "peer1",
            "response": "contradicted",
            "confidence": 0.7,
            "evidence": "local_contradiction",
        })
        assert result is not None
        assert result["status"] == "rejected"
        assert self.fed.rejections == 1

    def test_stats(self):
        stats = self.fed.get_stats()
        assert stats["organism_id"] == "zoe_test_1"
        assert "requests_sent" in stats
        assert "requests_received" in stats


# ============================================================
# 5. CapsuleManager
# ============================================================

class TestCapsuleManager:

    def test_load_capsule_standalone(self):
        """Carga una cápsula sin organismo (modo standalone)."""
        manager = CapsuleManager(organism=None)
        result = manager.load("elder_care_knowledge")
        assert result.success is True
        assert result.entries_loaded > 0
        assert "elder_care_knowledge" in [c["name"] for c in manager.list_loaded()]

    def test_load_nonexistent_fails(self):
        manager = CapsuleManager(organism=None)
        result = manager.load("nonexistent_capsule_xyz")
        assert result.success is False
        assert result.error == "capsule_not_found"

    def test_load_already_loaded_fails(self):
        manager = CapsuleManager(organism=None)
        manager.load("basic_psychology")
        result = manager.load("basic_psychology")
        assert result.success is False
        assert result.error == "already_loaded"

    def test_unload(self):
        manager = CapsuleManager(organism=None)
        manager.load("basic_psychology")
        ok = manager.unload("basic_psychology")
        assert ok is True
        assert "basic_psychology" not in [c["name"] for c in manager.list_loaded()]

    def test_unload_not_loaded_fails(self):
        manager = CapsuleManager(organism=None)
        ok = manager.unload("basic_psychology")
        assert ok is False

    def test_list_available(self):
        manager = CapsuleManager(organism=None)
        available = manager.list_available()
        names = [c["name"] for c in available]
        assert "elder_care_knowledge" in names
        assert "basic_psychology" in names
        assert "communication_skills" in names

    def test_get_info(self):
        manager = CapsuleManager(organism=None)
        info = manager.get_info("elder_care_knowledge")
        assert info is not None
        assert info["name"] == "elder_care_knowledge"
        assert info["trust_level"] == "verified"
        assert info["is_loaded"] is False

    def test_load_with_dependencies(self):
        """Cargar elder_care_knowledge carga basic_psychology automáticamente."""
        manager = CapsuleManager(organism=None)
        result = manager.load("elder_care_knowledge")
        assert result.success is True
        loaded = [c["name"] for c in manager.list_loaded()]
        assert "elder_care_knowledge" in loaded
        assert "basic_psychology" in loaded  # dependencia

    def test_load_for_use_case(self):
        """Carga por caso de uso funciona."""
        manager = CapsuleManager(organism=None)
        config = {
            "capsules": {
                "required": ["elder_care_knowledge", "communication_skills"],
                "recommended": ["basic_psychology"],
            }
        }
        results = manager.load_for_use_case("cuidado_personas_mayores", config)
        assert len(results) >= 3
        loaded = [c["name"] for c in manager.list_loaded()]
        assert "elder_care_knowledge" in loaded
        assert "communication_skills" in loaded
        assert "basic_psychology" in loaded

    def test_stats(self):
        manager = CapsuleManager(organism=None)
        manager.load("basic_psychology")
        stats = manager.get_stats()
        assert stats["loaded_count"] == 1
        assert stats["total_loads"] == 1
        assert "basic_psychology" in stats["loaded_names"]
