"""
ZOE V1.7 — Enhanced Pattern Speaker (Sprint 3.6)

Mejora el PatternSpeaker con 3 capacidades nuevas:

1. Response Distillation: captura respuestas buenas de LLMs (GPT-4o, Claude)
   y las almacena en distilled_responses.jsonl. PatternSpeaker las recupera
   cuando el input es similar.

2. Retrieval-Augmented Patterns: busca en memory.db y capsules/ knowledge
   relevante y lo incorpora a la respuesta.

3. Dialog State Tracking: recuerda el flujo de conversación para respuestas
   contextualmente apropiadas (no solo templates aislados).

El resultado: PatternSpeaker pasa de "respuestas genéricas de template"
a "respuestas contextualmente ricas que combinan memoria + conocimiento
+ patrones destilados de LLM".

Sin deconstruir: hereda de PatternPeripheral (Sprint 3). Si EnhancedPatternSpeaker
no tiene datos destilados, hace fallback a PatternPeripheral normal.

Uso:
    from zoe.peripherals.pattern_speaker import EnhancedPatternPeripheral
    
    llm = EnhancedPatternPeripheral(
        memory=living_memory,
        distilled_responses_path="distilled_responses.jsonl",
        capsules_dir="zoe/capsules",
    )
    response = await llm.generate("Mi madre toma paracetamol, ¿puede con alcohol?")
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
import time
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path

from .pattern_speaker import (
    PatternPeripheral,
    classify_intent,
    INTENT_KEYWORDS,
    RESPONSE_TEMPLATES,
)

logger = logging.getLogger(__name__)


# ============================================================
# Response Distillation
# ============================================================

@dataclass
class DistilledResponse:
    """Una respuesta destilada de un LLM de calidad."""
    input_text: str
    response_text: str
    intent: str
    quality_score: float  # 0-1, cómo de buena fue la respuesta
    source: str  # "gpt-4o", "claude", "qwen-7b", etc.
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    domain: str = ""  # "healthcare", "psychology", etc.

    def to_dict(self) -> dict:
        return {
            "input_text": self.input_text,
            "response_text": self.response_text,
            "intent": self.intent,
            "quality_score": self.quality_score,
            "source": self.source,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "domain": self.domain,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DistilledResponse":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ResponseDistiller:
    """
    Captura respuestas buenas de LLMs y las almacena para reutilizar.
    
    Proceso:
    1. ZOE funciona con GPT-4o normalmente
    2. Cuando una respuesta es buena (quality_score > 0.7), se destila
    3. Se almacena en distilled_responses.jsonl
    4. Al empaquetar .zoe, se incluyen las respuestas destiladas
    5. PatternSpeaker las recupera cuando el input es similar
    
    Esto permite que un .zoe tenga "memoria de calidad" sin necesitar
    el LLM que generó las respuestas originalmente.
    """

    def __init__(self, storage_path: str = "distilled_responses.jsonl"):
        self.storage_path = Path(storage_path)
        self._responses: List[DistilledResponse] = []
        self._load()

    def _load(self):
        """Carga respuestas destiladas desde archivo."""
        if self.storage_path.exists():
            with open(self.storage_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            self._responses.append(DistilledResponse.from_dict(data))
                        except:
                            pass
        logger.info(f"ResponseDistiller: loaded {len(self._responses)} distilled responses")

    def distill(self, input_text: str, response_text: str, source: str = "unknown",
                quality_score: float = 0.8, tags: List[str] = None,
                domain: str = "") -> DistilledResponse:
        """
        Destila una respuesta buena.
        
        Args:
            input_text: lo que el usuario preguntó
            response_text: la respuesta que dio el LLM
            source: qué LLM la generó ("gpt-4o", "claude", etc.)
            quality_score: cómo de buena fue (0-1)
            tags: tags para categorizar
            domain: dominio del conocimiento
        """
        intent = classify_intent(input_text)
        distilled = DistilledResponse(
            input_text=input_text,
            response_text=response_text,
            intent=intent,
            quality_score=quality_score,
            source=source,
            tags=tags or [],
            domain=domain,
        )
        self._responses.append(distilled)
        self._save()
        logger.info(f"ResponseDistiller: distilled response from {source} (quality: {quality_score})")
        return distilled

    def retrieve(self, query: str, n: int = 3, min_similarity: float = 0.2) -> List[DistilledResponse]:
        """
        Recupera respuestas destiladas similares al query.
        
        Usa similitud léxica (Jaccard) para encontrar las más relevantes.
        Ordena por: similitud * quality_score.
        """
        if not self._responses:
            return []

        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return []

        scored = []
        for resp in self._responses:
            resp_tokens = set(self._tokenize(resp.input_text))
            if not resp_tokens:
                continue

            # Jaccard similarity
            intersection = len(query_tokens & resp_tokens)
            union = len(query_tokens | resp_tokens)
            similarity = intersection / union if union > 0 else 0

            if similarity >= min_similarity:
                # Score = similarity * quality
                score = similarity * resp.quality_score
                scored.append((score, resp))

        # Ordenar por score descendente
        scored.sort(key=lambda x: x[0], reverse=True)

        return [resp for _, resp in scored[:n]]

    def _save(self):
        """Guarda respuestas destiladas a archivo."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            for resp in self._responses:
                f.write(json.dumps(resp.to_dict(), ensure_ascii=False) + "\n")

    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto para comparación."""
        clean = re.sub(r'[^\w\s]', ' ', text.lower())
        return [t for t in clean.split() if len(t) > 2]  # ignorar palabras muy cortas

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_distilled": len(self._responses),
            "by_source": self._count_by_source(),
            "by_intent": self._count_by_intent(),
            "avg_quality": sum(r.quality_score for r in self._responses) / max(1, len(self._responses)),
            "storage_path": str(self.storage_path),
        }

    def _count_by_source(self) -> Dict[str, int]:
        counts = {}
        for r in self._responses:
            counts[r.source] = counts.get(r.source, 0) + 1
        return counts

    def _count_by_intent(self) -> Dict[str, int]:
        counts = {}
        for r in self._responses:
            counts[r.intent] = counts.get(r.intent, 0) + 1
        return counts


# ============================================================
# Capsule Knowledge Retriever
# ============================================================

class CapsuleRetriever:
    """
    Recupera conocimiento relevante de las cápsulas para enriquecer respuestas.
    
    Busca en semantic_memory.jsonl y procedural_skills.jsonl de las cápsulas
    instaladas, y devuelve facts/skills relevantes al input del usuario.
    
    Esto permite que PatternSpeaker no solo use templates genéricos, sino
    que incorpore conocimiento experto de las cápsulas en sus respuestas.
    """

    def __init__(self, capsules_dir: str = "zoe/capsules"):
        self.capsules_dir = Path(capsules_dir)
        self._knowledge: List[Dict[str, Any]] = []
        self._load_knowledge()

    def _load_knowledge(self):
        """Carga conocimiento de todas las cápsulas instaladas."""
        if not self.capsules_dir.exists():
            return

        for capsule_dir in self.capsules_dir.iterdir():
            if not capsule_dir.is_dir():
                continue

            # Cargar semantic_memory.jsonl
            sem_path = capsule_dir / "semantic_memory.jsonl"
            if sem_path.exists():
                with open(sem_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entry = json.loads(line)
                                entry["_capsule"] = capsule_dir.name
                                entry["_type"] = "semantic"
                                self._knowledge.append(entry)
                            except:
                                pass

            # Cargar procedural_skills.jsonl
            proc_path = capsule_dir / "procedural_skills.jsonl"
            if proc_path.exists():
                with open(proc_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entry = json.loads(line)
                                entry["_capsule"] = capsule_dir.name
                                entry["_type"] = "procedural"
                                self._knowledge.append(entry)
                            except:
                                pass

        logger.info(f"CapsuleRetriever: loaded {len(self._knowledge)} knowledge entries from capsules")

    def retrieve(self, query: str, n: int = 3, min_similarity: float = 0.15) -> List[Dict[str, Any]]:
        """
        Recupera knowledge relevante al query.
        
        Busca en facts y skills de las cápsulas, y devuelve los más
        relevantes por similitud léxica.
        """
        if not self._knowledge:
            return []

        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return []

        scored = []
        for entry in self._knowledge:
            # Texto a comparar: fact/content/description/skill_name + tags
            text = " ".join([
                str(entry.get("fact", "")),
                str(entry.get("content", "")),
                str(entry.get("description", "")),
                str(entry.get("skill_name", "")),
                " ".join(entry.get("tags", []) if isinstance(entry.get("tags"), list) else []),
            ])
            entry_tokens = set(self._tokenize(text))

            if not entry_tokens:
                continue

            # Jaccard similarity
            intersection = len(query_tokens & entry_tokens)
            union = len(query_tokens | entry_tokens)
            similarity = intersection / union if union > 0 else 0

            if similarity >= min_similarity:
                scored.append((similarity, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:n]]

    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto."""
        clean = re.sub(r'[^\w\s]', ' ', text.lower())
        return [t for t in clean.split() if len(t) > 2]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_entries": len(self._knowledge),
            "capsules_loaded": len(set(e["_capsule"] for e in self._knowledge)),
        }


# ============================================================
# Dialog State Tracker
# ============================================================

class DialogStateTracker:
    """
    Rastrea el estado de la conversación para generar respuestas contextualmente apropiadas.
    
    Recuerda:
    - Última intención del usuario
    - Estado emocional detectado
    - Temas mencionados
    - Turnos de conversación
    - Si hay una pregunta pendiente de respuesta
    
    Esto permite que PatternSpeaker no solo responda a cada mensaje aislado,
    sino que mantenga contexto conversacional.
    """

    def __init__(self):
        self._history: List[Dict[str, Any]] = []
        self._current_emotion: str = "neutral"
        self._current_topic: str = ""
        self._pending_question: bool = False
        self._turn_count: int = 0

    def update(self, user_input: str, response: str):
        """Actualiza el estado con un nuevo turno."""
        self._turn_count += 1
        intent = classify_intent(user_input)

        # Detectar emoción
        if intent == "emotion":
            text_lower = user_input.lower()
            if any(w in text_lower for w in ["triste", "sad", "lloro", "deprimido"]):
                self._current_emotion = "sad"
            elif any(w in text_lower for w in ["feliz", "happy", "alegre", "contento"]):
                self._current_emotion = "happy"
            elif any(w in text_lower for w in ["preocupado", "worried", "ansioso", "miedo"]):
                self._current_emotion = "worried"

        # Detectar tema
        self._current_topic = self._extract_topic(user_input)

        # Detectar pregunta pendiente
        self._pending_question = "?" in user_input

        self._history.append({
            "turn": self._turn_count,
            "user_input": user_input,
            "response": response,
            "intent": intent,
            "emotion": self._current_emotion,
            "topic": self._current_topic,
            "timestamp": time.time(),
        })

    def _extract_topic(self, text: str) -> str:
        """Extrae el tema principal del texto."""
        # Simple: las palabras más largas suelen ser temas
        tokens = [t for t in re.sub(r'[^\w\s]', ' ', text.lower()).split() if len(t) > 4]
        return tokens[0] if tokens else ""

    def get_context(self) -> Dict[str, Any]:
        """Devuelve el contexto conversacional actual."""
        return {
            "turn_count": self._turn_count,
            "current_emotion": self._current_emotion,
            "current_topic": self._current_topic,
            "pending_question": self._pending_question,
            "last_intent": self._history[-1]["intent"] if self._history else "unknown",
            "history_length": len(self._history),
        }

    def get_recent_history(self, n: int = 3) -> List[Dict[str, Any]]:
        """Devuelve los últimos N turnos."""
        return self._history[-n:]

    def reset(self):
        """Reset del estado (nueva conversación)."""
        self._history.clear()
        self._current_emotion = "neutral"
        self._current_topic = ""
        self._pending_question = False
        self._turn_count = 0


# ============================================================
# Enhanced Pattern Peripheral
# ============================================================

class EnhancedPatternPeripheral(PatternPeripheral):
    """
    PatternSpeaker mejorado con distillation, retrieval y dialog state.
    
    3 capas de generación:
    1. Distilled responses (calidad más alta — respuestas reales de LLM)
    2. Capsule knowledge + templates (calidad media — conocimiento experto)
    3. Basic templates (calidad básica — fallback)
    
    Además, DialogStateTracker mantiene contexto conversacional para
    que las respuestas no sean aisladas sino contextualmente apropiadas.
    """

    def __init__(self, memory=None, language_profile=None,
                 distilled_responses_path: str = None,
                 capsules_dir: str = None):
        super().__init__(memory=memory, language_profile=language_profile)

        self._distiller: Optional[ResponseDistiller] = None
        self._capsule_retriever: Optional[CapsuleRetriever] = None
        self._dialog_state = DialogStateTracker()

        # Cargar distiller si hay path
        if distilled_responses_path:
            self._distiller = ResponseDistiller(distilled_responses_path)
            logger.info(f"EnhancedPatternPeripheral: distiller loaded ({len(self._distiller._responses)} responses)")

        # Cargar capsule retriever si hay dir
        if capsules_dir:
            self._capsule_retriever = CapsuleRetriever(capsules_dir)
            logger.info(f"EnhancedPatternPeripheral: capsule retriever loaded ({len(self._capsule_retriever._knowledge)} entries)")

    async def generate(self, prompt: str, system: str = None,
                       max_tokens: int = 300, temperature: float = 0.7,
                       **kwargs) -> str:
        """
        Genera respuesta usando 3 capas:
        1. Distilled responses (si hay match)
        2. Capsule knowledge + templates (si hay conocimiento relevante)
        3. Basic templates (fallback)
        """
        self._response_count += 1

        # 1. Intent classification
        intent = classify_intent(prompt)
        if intent == "emotion":
            intent = self._refine_emotion_intent(prompt)

        # 2. Buscar en respuestas destiladas PRIMERO (calidad más alta)
        if self._distiller:
            distilled = self._distiller.retrieve(prompt, n=1, min_similarity=0.25)
            if distilled:
                self._memory_reused += 1
                response = distilled[0].response_text
                # Adaptar ligeramente
                response = self._contextualize(response, prompt)
                self._dialog_state.update(prompt, response)
                return response

        # 3. Buscar en memoria (si disponible)
        if self._memory and temperature > 0:
            similar = self._memory.search(prompt, n=1)
            if similar and similar[0].similarity > 0.6:
                self._memory_reused += 1
                response = self._adapt_from_memory(similar[0], prompt)
                self._dialog_state.update(prompt, response)
                return response

        # 4. Reflex map si disponible
        if self._language_profile:
            reflex_key = prompt.lower().strip()
            if reflex_key in self._language_profile.reflex_map:
                response = self._language_profile.reflex_map[reflex_key]
                self._dialog_state.update(prompt, response)
                return response

        # 5. Capsule knowledge + templates (calidad media)
        capsule_knowledge = []
        if self._capsule_retriever:
            capsule_knowledge = self._capsule_retriever.retrieve(prompt, n=2, min_similarity=0.15)

        if capsule_knowledge:
            response = self._compose_with_knowledge(prompt, intent, capsule_knowledge, temperature)
            self._templates_used += 1
            self._dialog_state.update(prompt, response)
            return response

        # 6. Basic templates (fallback)
        templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["statement"])
        if temperature == 0:
            response = templates[0]
        else:
            response = random.choice(templates)

        response = self._fill_template(response, prompt)
        self._templates_used += 1
        self._dialog_state.update(prompt, response)
        return response

    def _compose_with_knowledge(self, prompt: str, intent: str,
                                 knowledge: List[Dict[str, Any]],
                                 temperature: float) -> str:
        """
        Compone respuesta combinando template + conocimiento de cápsulas.
        
        Esto es lo que hace que PatternSpeaker sea mucho más capaz:
        en vez de solo "Te escucho. Cuéntame más.", puede decir
        "Te escucho. Sobre lo que mencionas, sé que [fact de cápsula]. ¿Quieres que profundice?"
        """
        # Seleccionar template base
        templates = RESPONSE_TEMPLATES.get(intent, RESPONSE_TEMPLATES["statement"])
        if temperature == 0:
            base = templates[0]
        else:
            base = random.choice(templates)

        # Extraer facts de knowledge
        facts = []
        for entry in knowledge:
            fact_text = entry.get("fact") or entry.get("content") or ""
            if entry.get("_type") == "semantic" and fact_text:
                facts.append(fact_text)
            elif entry.get("_type") == "procedural" and entry.get("skill_name"):
                facts.append(f"Sé cómo {entry['skill_name'].replace('_', ' ')}")

        if not facts:
            return base

        # Componer: template + knowledge
        knowledge_text = facts[0]
        if len(facts) > 1:
            knowledge_text += f" También sé que {facts[1]}"

        # Si el template es corto, añadir knowledge
        if len(base) < 80:
            response = f"{base} Sobre lo que mencionas: {knowledge_text}"
        else:
            response = f"{base}\n\nSobre lo que mencionas: {knowledge_text}"

        # Truncar si excede
        max_chars = 500
        if len(response) > max_chars:
            response = response[:max_chars - 3] + "..."

        return response

    def _contextualize(self, response: str, prompt: str) -> str:
        """Adapta una respuesta destilada al contexto actual."""
        # Si el usuario menciona a alguien específico, personalizar
        context = self._dialog_state.get_context()

        # Si hay emoción detectada, añadir validación
        if context["current_emotion"] == "sad" and "siento" not in response.lower():
            response = "Entiendo. " + response
        elif context["current_emotion"] == "worried" and "entiendo" not in response.lower():
            response = "Comprendo tu preocupación. " + response

        return response

    def get_stats(self) -> Dict[str, Any]:
        """Stats del EnhancedPatternSpeaker."""
        stats = super().get_stats()
        stats["enhanced"] = True
        stats["distiller_loaded"] = self._distiller is not None
        stats["distiller_responses"] = len(self._distiller._responses) if self._distiller else 0
        stats["capsule_retriever_loaded"] = self._capsule_retriever is not None
        stats["capsule_knowledge_entries"] = len(self._capsule_retriever._knowledge) if self._capsule_retriever else 0
        stats["dialog_turns"] = self._dialog_state._turn_count
        stats["current_emotion"] = self._dialog_state._current_emotion
        stats["current_topic"] = self._dialog_state._current_topic
        return stats

    def get_dialog_context(self) -> Dict[str, Any]:
        """Devuelve el contexto de diálogo actual."""
        return self._dialog_state.get_context()
