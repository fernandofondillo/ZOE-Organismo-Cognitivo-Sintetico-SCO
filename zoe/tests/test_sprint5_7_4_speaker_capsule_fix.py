"""
Tests Sprint 5.7.4 — Fix Speaker.register_validators y add_specialized_prompt

Verifica que:
1. Speaker tiene register_validators() y add_specialized_prompt()
2. Speaker tiene _specialized_prompts y _validators atributos
3. Learner tiene register_validators()
4. Los prompts especializados se incluyen en _build_prompt
5. El fix resuelve el bug de capsule_manager (hasattr devuelve True)
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock


class TestSpeakerCapsuleIntegration:
    """Sprint 5.7.4 — Speaker soporta cápsulas (register_validators, add_specialized_prompt)."""

    def test_speaker_tiene_specialized_prompts_attr(self):
        """Speaker.__init__ inicializa _specialized_prompts."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        assert hasattr(s, "_specialized_prompts")
        assert s._specialized_prompts == {}

    def test_speaker_tiene_validators_attr(self):
        """Speaker.__init__ inicializa _validators."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        assert hasattr(s, "_validators")
        assert s._validators == {}

    def test_speaker_register_validators_exists(self):
        """Speaker tiene método register_validators."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        assert hasattr(s, "register_validators")
        assert callable(s.register_validators)

    def test_speaker_add_specialized_prompt_exists(self):
        """Speaker tiene método add_specialized_prompt."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        assert hasattr(s, "add_specialized_prompt")
        assert callable(s.add_specialized_prompt)

    def test_speaker_register_validators_funciona(self):
        """register_validators añade el módulo al dict."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        mock_module = MagicMock()
        s.register_validators("elder_care_knowledge", mock_module)
        assert "elder_care_knowledge" in s._validators
        assert s._validators["elder_care_knowledge"] is mock_module

    def test_speaker_add_specialized_prompt_funciona(self):
        """add_specialized_prompt añade el contenido al dict."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        prompt_content = "## Cuidado de mayores\nCuando hables de ancianos..."
        s.add_specialized_prompt("elder_care_knowledge", prompt_content)
        assert "elder_care_knowledge" in s._specialized_prompts
        assert s._specialized_prompts["elder_care_knowledge"] == prompt_content

    def test_speaker_get_specialized_prompts(self):
        """get_specialized_prompts devuelve copia del dict."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        s.add_specialized_prompt("cap1", "prompt1")
        s.add_specialized_prompt("cap2", "prompt2")
        prompts = s.get_specialized_prompts()
        assert len(prompts) == 2
        assert prompts["cap1"] == "prompt1"
        assert prompts["cap2"] == "prompt2"

    def test_speaker_get_validators(self):
        """get_validators devuelve copia del dict."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        mock_mod = MagicMock()
        s.register_validators("cap1", mock_mod)
        validators = s.get_validators()
        assert len(validators) == 1
        assert validators["cap1"] is mock_mod

    def test_build_prompt_includes_specialized_prompts(self):
        """_build_prompt incluye los specialized_prompts cuando los hay."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        s.add_specialized_prompt("elder_care_knowledge", "## Cuidado de mayores\nReglas importantes")
        context = {
            "action": "autonomous_thought",
            "state": {"energy": 1.0, "fatigue": 0.0, "arousal": 0.0, "iteration_count": 1},
            "recent_observations": [],
            "surprise": 0.0,
            "recent_thoughts": [],
        }
        prompt = s._build_prompt(context, "autonomous_thought")
        assert "CONOCIMIENTO ESPECIALIZADO" in prompt
        assert "elder_care_knowledge" in prompt
        assert "Cuidado de mayores" in prompt

    def test_build_prompt_no_includes_specialized_si_vacio(self):
        """_build_prompt NO incluye la sección specialized si no hay."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        context = {
            "action": "autonomous_thought",
            "state": {"energy": 1.0, "fatigue": 0.0, "arousal": 0.0, "iteration_count": 1},
            "recent_observations": [],
            "surprise": 0.0,
            "recent_thoughts": [],
        }
        prompt = s._build_prompt(context, "autonomous_thought")
        assert "CONOCIMIENTO ESPECIALIZADO" not in prompt

    def test_build_prompt_trunca_specialized_a_500_chars(self):
        """_build_prompt trunca cada specialized_prompt a 500 chars."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        long_prompt = "A" * 1000  # 1000 chars
        s.add_specialized_prompt("cap_long", long_prompt)
        context = {
            "action": "autonomous_thought",
            "state": {"energy": 1.0, "fatigue": 0.0, "arousal": 0.0, "iteration_count": 1},
            "recent_observations": [],
            "surprise": 0.0,
            "recent_thoughts": [],
        }
        prompt = s._build_prompt(context, "autonomous_thought")
        # Debe contener los primeros 500 chars + "..."
        assert "A" * 500 in prompt
        assert "..." in prompt
        # NO debe contener 1000 As seguidos
        assert "A" * 1000 not in prompt


class TestLearnerCapsuleIntegration:
    """Sprint 5.7.4 — Learner soporta register_validators."""

    def test_learner_tiene_register_validators(self):
        """Learner tiene método register_validators."""
        from zoe.core.subagents.phase2_subagents import Learner
        l = Learner()
        assert hasattr(l, "register_validators")
        assert callable(l.register_validators)

    def test_learner_tiene_capsule_validators_attr(self):
        """Learner.__init__ inicializa _capsule_validators."""
        from zoe.core.subagents.phase2_subagents import Learner
        l = Learner()
        assert hasattr(l, "_capsule_validators")
        assert l._capsule_validators == {}

    def test_learner_register_validators_funciona(self):
        """register_validators añade el módulo al dict."""
        from zoe.core.subagents.phase2_subagents import Learner
        l = Learner()
        mock_module = MagicMock()
        l.register_validators("pharmacy_interactions", mock_module)
        assert "pharmacy_interactions" in l._capsule_validators
        assert l._capsule_validators["pharmacy_interactions"] is mock_module


class TestCapsuleManagerHasattrFix:
    """Sprint 5.7.4 — Verifica que el capsule_manager ahora SÍ encontrará los métodos."""

    def test_capsule_manager_hasattr_speaker_register_validators(self):
        """hasattr(speaker, 'register_validators') devuelve True (antes False)."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        assert hasattr(s, "register_validators") is True  # antes era False

    def test_capsule_manager_hasattr_speaker_add_specialized_prompt(self):
        """hasattr(speaker, 'add_specialized_prompt') devuelve True (antes False)."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        assert hasattr(s, "add_specialized_prompt") is True  # antes era False

    def test_capsule_manager_hasattr_learner_register_validators(self):
        """hasattr(learner, 'register_validators') devuelve True (antes False)."""
        from zoe.core.subagents.phase2_subagents import Learner
        l = Learner()
        assert hasattr(l, "register_validators") is True  # antes era False


class TestSpeakerBackwardCompat:
    """Sprint 5.7.4 — El fix no rompe la API existente del Speaker."""

    def test_speaker_init_sin_args_funciona(self):
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        assert s.llm is None
        assert s.max_thought_length == 300
        assert s._recent_thoughts == []

    def test_speaker_init_con_llm_funciona(self):
        from zoe.core.subagents.speaker import Speaker
        from zoe.peripherals.llm import MockPeripheral
        mock = MockPeripheral()
        s = Speaker(llm_peripheral=mock)
        assert s.llm is mock

    def test_speaker_set_llm_funciona(self):
        from zoe.core.subagents.speaker import Speaker
        from zoe.peripherals.llm import MockPeripheral
        s = Speaker()
        mock = MockPeripheral()
        s.set_llm(mock)
        assert s.llm is mock

    def test_speaker_generate_thought_sin_llm_usa_template(self):
        """Sin LLM, generate_thought usa _template_thought (fallback)."""
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        context = {
            "action": "autonomous_thought",
            "state": {"iteration_count": 5},
            "surprise": 0.0,
        }
        result = asyncio.run(s.generate_thought(context))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_speaker_sanitize_funciona(self):
        from zoe.core.subagents.speaker import Speaker
        s = Speaker()
        text = "Como modelo de lenguaje, no tengo emociones. Hola."
        result = s._sanitize(text)
        assert "como modelo" not in result.lower()
        assert "no tengo emociones" not in result.lower()
        assert "Hola" in result
