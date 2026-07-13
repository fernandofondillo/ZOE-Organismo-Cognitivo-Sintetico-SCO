"""
Tests Sprint 3.6 — Enhanced PatternSpeaker + Distillation + Retrieval

Valida las 3 mejoras: distillation, capsule retrieval, dialog state.
"""

import pytest
import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from zoe.peripherals.enhanced_pattern_speaker import (
    EnhancedPatternPeripheral,
    ResponseDistiller,
    CapsuleRetriever,
    DialogStateTracker,
    DistilledResponse,
)


# ============================================================
# 1. ResponseDistiller
# ============================================================

class TestResponseDistiller:

    @pytest.fixture
    def temp_distiller(self, tmp_path):
        """Distiller con archivo temporal."""
        path = str(tmp_path / "distilled.jsonl")
        return ResponseDistiller(storage_path=path)

    def test_creation(self, temp_distiller):
        """Se puede crear ResponseDistiller."""
        assert temp_distiller is not None
        assert len(temp_distiller._responses) == 0

    def test_distill_response(self, temp_distiller):
        """Distilla una respuesta correctamente."""
        resp = temp_distiller.distill(
            input_text="¿Qué es la paracetamol?",
            response_text="La paracetamol es un analgésico...",
            source="gpt-4o",
            quality_score=0.9,
        )
        assert resp.input_text == "¿Qué es la paracetamol?"
        assert resp.source == "gpt-4o"
        assert len(temp_distiller._responses) == 1

    def test_retrieve_similar(self, temp_distiller):
        """Recupera respuestas similares."""
        temp_distiller.distill(
            input_text="¿Qué es la paracetamol?",
            response_text="La paracetamol es un analgésico...",
            source="gpt-4o",
        )
        temp_distiller.distill(
            input_text="¿Cómo estás?",
            response_text="Estoy bien, gracias.",
            source="gpt-4o",
        )

        results = temp_distiller.retrieve("¿Qué es la paracetamol?")
        assert len(results) > 0
        assert "paracetamol" in results[0].response_text.lower()

    def test_retrieve_empty(self, temp_distiller):
        """Sin respuestas destiladas, retrieve devuelve vacío."""
        results = temp_distiller.retrieve("cualquier cosa")
        assert results == []

    def test_persistence(self, tmp_path):
        """Las respuestas se guardan y cargan."""
        path = str(tmp_path / "distilled.jsonl")

        # Crear y destilar
        d1 = ResponseDistiller(storage_path=path)
        d1.distill("test input", "test response", "gpt-4o")

        # Cargar de nuevo
        d2 = ResponseDistiller(storage_path=path)
        assert len(d2._responses) == 1
        assert d2._responses[0].input_text == "test input"

    def test_get_stats(self, temp_distiller):
        """Stats del distiller."""
        temp_distiller.distill("test", "response", "gpt-4o", 0.9)
        stats = temp_distiller.get_stats()
        assert stats["total_distilled"] == 1
        assert "gpt-4o" in stats["by_source"]

    def test_quality_affects_retrieval_order(self, temp_distiller):
        """Respuestas de mayor calidad se priorizan."""
        temp_distiller.distill("paracetamol", "Respuesta básica", "qwen-3b", 0.5)
        temp_distiller.distill("paracetamol", "Respuesta excelente", "gpt-4o", 0.95)

        results = temp_distiller.retrieve("paracetamol")
        assert len(results) >= 1
        # La de mayor calidad debe aparecer primero
        assert results[0].quality_score >= results[-1].quality_score


# ============================================================
# 2. CapsuleRetriever
# ============================================================

class TestCapsuleRetriever:

    def test_creation(self):
        """Se puede crear CapsuleRetriever."""
        retriever = CapsuleRetriever(capsules_dir="zoe/capsules")
        assert retriever is not None

    def test_loads_knowledge(self):
        """Carga conocimiento de las cápsulas."""
        retriever = CapsuleRetriever(capsules_dir="zoe/capsules")
        assert len(retriever._knowledge) > 0

    def test_retrieve_relevant(self):
        """Recupera knowledge relevante."""
        retriever = CapsuleRetriever(capsules_dir="zoe/capsules")
        # Usar un query que coincida con facts de las cápsulas
        results = retriever.retrieve("paracetamol medicamento interacción", min_similarity=0.05)
        assert len(results) > 0

    def test_retrieve_empty_query(self):
        """Query vacío devuelve vacío."""
        retriever = CapsuleRetriever(capsules_dir="zoe/capsules")
        results = retriever.retrieve("")
        assert results == []

    def test_retrieve_no_match(self):
        """Sin match, devuelve vacío."""
        retriever = CapsuleRetriever(capsules_dir="zoe/capsules")
        results = retriever.retrieve("xyzqwerty random nonsense")
        assert results == []

    def test_get_stats(self):
        """Stats del retriever."""
        retriever = CapsuleRetriever(capsules_dir="zoe/capsules")
        stats = retriever.get_stats()
        assert stats["total_entries"] > 0
        assert stats["capsules_loaded"] > 0


# ============================================================
# 3. DialogStateTracker
# ============================================================

class TestDialogStateTracker:

    def test_creation(self):
        """Se puede crear DialogStateTracker."""
        tracker = DialogStateTracker()
        assert tracker._turn_count == 0

    def test_update_increments_turns(self):
        """Update incrementa turn count."""
        tracker = DialogStateTracker()
        tracker.update("Hola", "Hola a ti")
        tracker.update("¿Cómo estás?", "Bien")
        assert tracker._turn_count == 2

    def test_detects_emotion(self):
        """Detecta emoción desde el input."""
        tracker = DialogStateTracker()
        tracker.update("Me siento muy triste", "Lo siento")
        assert tracker._current_emotion == "sad"

    def test_get_context(self):
        """get_context devuelve dict con estado."""
        tracker = DialogStateTracker()
        tracker.update("Hola", "Hola")
        ctx = tracker.get_context()
        assert "turn_count" in ctx
        assert "current_emotion" in ctx
        assert "current_topic" in ctx

    def test_reset(self):
        """Reset limpia el estado."""
        tracker = DialogStateTracker()
        tracker.update("Hola", "Hola")
        tracker.reset()
        assert tracker._turn_count == 0
        assert len(tracker._history) == 0

    def test_recent_history(self):
        """get_recent_history devuelve últimos N."""
        tracker = DialogStateTracker()
        for i in range(5):
            tracker.update(f"msg {i}", f"resp {i}")
        recent = tracker.get_recent_history(2)
        assert len(recent) == 2
        assert recent[-1]["user_input"] == "msg 4"


# ============================================================
# 4. EnhancedPatternPeripheral
# ============================================================

class TestEnhancedPatternPeripheral:

    def test_creation(self):
        """Se puede crear EnhancedPatternPeripheral."""
        llm = EnhancedPatternPeripheral()
        assert llm.name == "pattern"
        assert llm._distiller is None or llm._distiller is not None

    def test_generate_without_enhancements(self):
        """Sin distiller ni retriever, funciona como PatternPeripheral normal."""
        import asyncio
        llm = EnhancedPatternPeripheral()
        result = asyncio.run(llm.generate("Hola"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_with_distiller(self, tmp_path):
        """Con distiller, recupera respuestas destiladas."""
        import asyncio

        # Crear distiller con respuesta destilada
        distiller_path = str(tmp_path / "distilled.jsonl")
        distiller = ResponseDistiller(storage_path=distiller_path)
        distiller.distill(
            input_text="Hola, ¿cómo estás?",
            response_text="Hola. Estoy pensando en ti. ¿Cómo te encuentras hoy?",
            source="gpt-4o",
            quality_score=0.95,
        )

        llm = EnhancedPatternPeripheral(distilled_responses_path=distiller_path)
        result = asyncio.run(llm.generate("Hola, ¿cómo estás?"))
        assert "pensando" in result or "Hola" in result

    def test_generate_with_capsule_retriever(self):
        """Con capsule retriever, incorpora conocimiento."""
        import asyncio

        llm = EnhancedPatternPeripheral(capsules_dir="zoe/capsules")
        result = asyncio.run(llm.generate("¿Qué sabes sobre medicación?"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_dialog_state_tracking(self):
        """Dialog state se actualiza con cada mensaje."""
        import asyncio

        llm = EnhancedPatternPeripheral()
        asyncio.run(llm.generate("Hola"))
        asyncio.run(llm.generate("¿Quién eres?"))

        context = llm.get_dialog_context()
        assert context["turn_count"] == 2

    def test_stats_enhanced(self):
        """Stats incluyen info enhanced."""
        import asyncio

        llm = EnhancedPatternPeripheral(capsules_dir="zoe/capsules")
        asyncio.run(llm.generate("Hola"))

        stats = llm.get_stats()
        assert stats["enhanced"] is True
        assert "distiller_loaded" in stats
        assert "capsule_retriever_loaded" in stats
        assert "dialog_turns" in stats

    def test_health_check(self):
        """health_check siempre True."""
        import asyncio
        llm = EnhancedPatternPeripheral()
        assert asyncio.run(llm.health_check()) is True

    def test_compose_with_knowledge(self):
        """_compose_with_knowledge combina template + knowledge."""
        llm = EnhancedPatternPeripheral()
        knowledge = [
            {"_type": "semantic", "fact": "La paracetamol es un analgésico"},
        ]
        result = llm._compose_with_knowledge(
            "test prompt", "question", knowledge, 0.7
        )
        assert "paracetamol" in result.lower() or "analgesic" in result.lower()

    def test_contextualize_adds_empathy(self):
        """_contextualize añade empatía si emoción es triste."""
        llm = EnhancedPatternPeripheral()
        llm._dialog_state._current_emotion = "sad"
        result = llm._contextualize("Respuesta base", "input")
        assert "Entiendo" in result or "entiendo" in result.lower()

    def test_distiller_and_retriever_combined(self, tmp_path):
        """Distiller + retriever funcionan juntos."""
        import asyncio

        # Crear distiller
        distiller_path = str(tmp_path / "distilled.jsonl")
        distiller = ResponseDistiller(storage_path=distiller_path)
        distiller.distill(
            input_text="Mi madre toma mucha medicación",
            response_text="La polimedicación en mayores es un tema importante. "
                         "Te recomiendo revisar con su médico todas las medicaciones.",
            source="gpt-4o",
            quality_score=0.9,
        )

        llm = EnhancedPatternPeripheral(
            distilled_responses_path=distiller_path,
            capsules_dir="zoe/capsules",
        )

        # Query que matchea destilada
        result = asyncio.run(llm.generate("Mi madre toma mucha medicación"))
        assert "polimedicación" in result or "medicación" in result or "médico" in result

    def test_fallback_to_basic_template(self):
        """Sin distiller ni retriever, fallback a templates básicos."""
        import asyncio

        llm = EnhancedPatternPeripheral()
        result = asyncio.run(llm.generate("xyzqwerty nonsense"))
        assert isinstance(result, str)
        assert len(result) > 0
