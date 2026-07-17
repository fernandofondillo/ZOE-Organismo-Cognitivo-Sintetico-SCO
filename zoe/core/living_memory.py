"""
ZOE v1.0 — Living Memory

Memoria que piensa. No solo almacena: reorganiza, olvida, fusiona,
resume, generaliza, detecta contradicciones, genera hipótesis.

Diferencia con memoria pasiva:
- Memoria pasiva: entries se almacenan hasta que se consultan
- Memoria viva: entries se transforman activamente

Operaciones (ejecuta una por iteración o en ciclos de sueño):
1. reorganize: mueve entries entre tipos (episódica → semántica)
2. forget: poda entries de baja saliencia/confianza
3. merge: combina entries similares
4. summarize: comprime entries antiguas en resúmenes
5. generalize: extrae patrones
6. detect_contradictions: marca entries opuestas
7. generate_hypotheses: propone nuevas entries
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Una entry en la memoria viva."""

    id: str
    type: str  # episodic | semantic | procedural | causal | emotional | ...
    content: str
    embedding: Optional[List[float]] = None
    confidence: float = 0.5
    salience: float = 0.5  # cuán relevante/útil es
    provenance: str = ""  # fuente (3ra ley cognitiva)
    timestamp: float = field(default_factory=time.time)
    last_access: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    merged_from: List[str] = field(default_factory=list)  # IDs fusionados
    contradictions: List[str] = field(default_factory=list)  # IDs contradictorios

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "confidence": self.confidence,
            "salience": self.salience,
            "provenance": self.provenance,
            "timestamp": self.timestamp,
            "last_access": self.last_access,
            "access_count": self.access_count,
            "metadata": self.metadata,
            "merged_from": self.merged_from,
            "contradictions": self.contradictions,
        }


class LivingMemory:
    """
    Memoria viva que piensa activamente.

    En Fase 0.5 es un esqueleto funcional con operaciones básicas.
    En Fase 3 evoluciona a 11 tipos especializados con backing stores.
    """

    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self._entries: Dict[str, MemoryEntry] = {}
        self._next_id = 0
        self._operations_log: List[Dict[str, Any]] = []
        self._last_operation: str = ""

    def add(
        self,
        content: str,
        type: str = "episodic",
        confidence: float = 0.5,
        salience: float = 0.5,
        provenance: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Añade una entry. Devuelve su ID."""
        # 3ra ley: todo conocimiento debe justificar su origen
        if not provenance:
            logger.warning("LivingMemory.add sin provenance (3ra ley)")
            provenance = "unknown"

        entry_id = f"mem_{self._next_id}"
        self._next_id += 1

        entry = MemoryEntry(
            id=entry_id,
            type=type,
            content=content,
            confidence=max(0.0, min(1.0, confidence)),
            salience=max(0.0, min(1.0, salience)),
            provenance=provenance,
            metadata=metadata or {},
        )
        self._entries[entry_id] = entry

        # Si excedemos max_entries, olvidar las de menor saliencia
        if len(self._entries) > self.max_entries:
            self._forget_low_salience(n=10)

        # Invalidar cache semantica si existe
        if hasattr(self, "_semantic_search") and self._semantic_search:
            self._semantic_search.invalidate_cache(entry_id)

        return entry_id

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Obtiene una entry por ID."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.last_access = time.time()
            entry.access_count += 1
        return entry

    def search(
        self, query: str, n: int = 5, use_semantic: bool = False
    ) -> List[MemoryEntry]:
        """Busca entries por similitud de texto (Jaccard + embeddings opcionales)."""
        # Si se solicita busqueda semantica, intentar primero
        if use_semantic:
            try:
                from ..memory.semantic_search import SemanticSearch

                # Singleton lazy
                if not hasattr(self, "_semantic_search"):
                    self._semantic_search = SemanticSearch()
                if self._semantic_search.is_available:
                    results = self._semantic_search.search(
                        query, self._entries, n=n
                    )
                    if results:
                        logger.debug(
                            f"SemanticSearch: {len(results)} results for "
                            f"'{query[:30]}...'"
                        )
                        return [entry for _, entry in results]
                    # Si no hay resultados semanticos, fallback a Jaccard
            except ImportError:
                pass  # Fallback a Jaccard

        # Jaccard (default, backward-compatible)
        query_words = set(query.lower().split())
        scored = []
        for entry in self._entries.values():
            entry_words = set(entry.content.lower().split())
            if not query_words or not entry_words:
                continue
            intersection = query_words & entry_words
            union = query_words | entry_words
            score = len(intersection) / len(union) if union else 0
            scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:n]]

    def all_entries(self) -> List[MemoryEntry]:
        """Devuelve todas las entries."""
        return list(self._entries.values())

    def count(self) -> int:
        return len(self._entries)

    def get_recent(
        self, memory_type: Optional[str] = None, limit: int = 20
    ) -> List[MemoryEntry]:
        """
        Devuelve las N entries más recientes, opcionalmente filtradas por tipo.

        Sprint 5.23 F0-1 (BUG-001 fix): método requerido por
        ``ReflectionEngine._get_recent_memories`` para seleccionar
        memorias de alta saliencia durante SLEEPING. Antes de este
        fix, ``ReflectionEngine`` retornaba ``[]`` porque
        ``LivingMemory`` no tenía ``get_recent``.

        Orden: timestamp DESC (más reciente primero).
        """
        if memory_type:
            entries = [
                e for e in self._entries.values() if e.type == memory_type
            ]
        else:
            entries = list(self._entries.values())
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def get_salient(
        self, memory_type: Optional[str] = None, limit: int = 20
    ) -> List[MemoryEntry]:
        """
        Devuelve las N entries más salientes, opcionalmente filtradas por tipo.

        Sprint 5.23 F0-1 (BUG-001 fix): variante de ``get_recent``
        que ordena por ``salience`` DESC, luego ``timestamp`` DESC.
        Usada por ``ReflectionEngine._select_salient_memories``.
        """
        if memory_type:
            entries = [
                e for e in self._entries.values() if e.type == memory_type
            ]
        else:
            entries = list(self._entries.values())
        entries.sort(
            key=lambda e: (e.salience, e.timestamp), reverse=True
        )
        return entries[:limit]

    # ===== OPERACIONES DE MEMORIA VIVA =====

    def think(self) -> Dict[str, Any]:
        """
        Ejecuta una operación de memoria viva.
        Elige la operación más necesaria según el estado de la memoria.
        """
        # Decidir qué operación ejecutar
        if self._has_contradictions():
            op = "detect_contradictions"
        elif len(self._entries) > 50 and self._has_mergeable():
            op = "merge"
        elif len(self._entries) > 100:
            op = "summarize"
        elif self._has_generalizable():
            op = "generalize"
        else:
            op = "reorganize"

        # Ejecutar operación
        if op == "reorganize":
            result = self._reorganize()
        elif op == "merge":
            result = self._merge_similar()
        elif op == "summarize":
            result = self._summarize_old()
        elif op == "generalize":
            result = self._generalize()
        elif op == "detect_contradictions":
            result = self._detect_contradictions()
        else:
            result = {"operation": "none", "changes": 0}

        result["operation"] = op
        result["timestamp"] = time.time()
        result["entry_count_before"] = len(self._entries)
        self._operations_log.append(result)
        self._last_operation = op
        return result

    def _reorganize(self) -> Dict[str, Any]:
        """Reorganiza entries entre tipos."""
        # Mover entries episódicas antiguas y accedidas frecuentemente a semántica
        changes = 0
        now = time.time()
        for entry in list(self._entries.values()):
            if (
                entry.type == "episodic"
                and entry.access_count > 3
                and (now - entry.timestamp) > 3600  # más de 1h
            ):
                entry.type = "semantic"
                entry.salience = min(1.0, entry.salience + 0.1)
                changes += 1

        return {"operation": "reorganize", "changes": changes}

    def _forget_low_salience(self, n: int = 10) -> Dict[str, Any]:
        """Olvida entries de baja saliencia."""
        sorted_entries = sorted(
            self._entries.values(),
            key=lambda e: (e.salience, e.confidence, -e.access_count),
        )
        forgotten = 0
        for entry in sorted_entries[:n]:
            if entry.confidence < 0.3:  # no olvidar lo que tiene confianza
                del self._entries[entry.id]
                forgotten += 1

        return {"operation": "forget", "changes": forgotten}

    def _merge_similar(self) -> Dict[str, Any]:
        """Fusiona entries similares."""
        changes = 0
        entries = list(self._entries.values())
        merged_ids: Set[str] = set()

        for i, entry_a in enumerate(entries):
            if entry_a.id in merged_ids:
                continue
            for entry_b in entries[i + 1 :]:
                if entry_b.id in merged_ids:
                    continue
                if entry_a.type != entry_b.type:
                    continue
                # Similitud alta
                sim = self._jaccard(entry_a.content, entry_b.content)
                if sim > 0.7:
                    # Fusionar B en A
                    entry_a.content = f"{entry_a.content} [fusionado con: {entry_b.content[:50]}...]"
                    entry_a.confidence = max(entry_a.confidence, entry_b.confidence)
                    entry_a.salience = max(entry_a.salience, entry_b.salience)
                    entry_a.merged_from.append(entry_b.id)
                    entry_a.access_count += entry_b.access_count
                    merged_ids.add(entry_b.id)
                    changes += 1

        # Eliminar fusionadas
        for mid in merged_ids:
            if mid in self._entries:
                del self._entries[mid]

        return {"operation": "merge", "changes": changes}

    def _summarize_old(self) -> Dict[str, Any]:
        """Comprime entries antiguas en un resumen."""
        now = time.time()
        old_entries = [
            e
            for e in self._entries.values()
            if (now - e.timestamp) > 7200 and e.type == "episodic"  # >2h
        ]

        if len(old_entries) < 5:
            return {"operation": "summarize", "changes": 0}

        # Crear entry de resumen
        summary_content = "Resumen de eventos pasados: " + " | ".join(
            e.content[:50] for e in old_entries[:5]
        )
        summary_id = self.add(
            content=summary_content,
            type="semantic",
            confidence=0.6,
            salience=0.4,
            provenance="living_memory:summarize",
            metadata={"summarized_count": len(old_entries)},
        )

        # Eliminar entries antiguas (consolidadas en el resumen)
        for entry in old_entries:
            if entry.id != summary_id:
                del self._entries[entry.id]

        return {"operation": "summarize", "changes": len(old_entries)}

    def _generalize(self) -> Dict[str, Any]:
        """Extrae patrones de entries múltiples."""
        # Buscar patrones simples: palabras que aparecen en múltiples entries
        word_counts: Dict[str, int] = {}
        for entry in self._entries.values():
            words = set(entry.content.lower().split())
            for w in words:
                if len(w) > 4:  # solo palabras largas
                    word_counts[w] = word_counts.get(w, 0) + 1

        # Palabras que aparecen en 3+ entries
        patterns = [w for w, c in word_counts.items() if c >= 3]

        if not patterns:
            return {"operation": "generalize", "changes": 0}

        # Crear entry de patrón
        pattern_content = f"Patrón detectado: palabras recurrentes ({', '.join(patterns[:5])})"
        self.add(
            content=pattern_content,
            type="semantic",
            confidence=0.5,
            salience=0.6,
            provenance="living_memory:generalize",
            metadata={"patterns": patterns[:10]},
        )

        return {"operation": "generalize", "changes": 1, "patterns": len(patterns)}

    def _detect_contradictions(self) -> Dict[str, Any]:
        """Detecta entries que se oponen."""
        # Simplificado: buscar entries con "no" + mismo contenido
        changes = 0
        entries = list(self._entries.values())
        for i, entry_a in enumerate(entries):
            for entry_b in entries[i + 1 :]:
                if entry_a.type != entry_b.type:
                    continue
                # Si A dice X y B dice no X
                if (
                    entry_b.content.lower().startswith("no ")
                    and entry_a.content.lower() in entry_b.content.lower()
                ):
                    entry_a.contradictions.append(entry_b.id)
                    entry_b.contradictions.append(entry_a.id)
                    entry_a.confidence *= 0.7  # reducir confianza
                    entry_b.confidence *= 0.7
                    changes += 1

        return {"operation": "detect_contradictions", "changes": changes}

    def _has_contradictions(self) -> bool:
        return any(e.contradictions for e in self._entries.values())

    def _has_mergeable(self) -> bool:
        entries = list(self._entries.values())
        for i, a in enumerate(entries[:20]):  # muestra
            for b in entries[i + 1 : 20]:
                if a.type == b.type and self._jaccard(a.content, b.content) > 0.7:
                    return True
        return False

    def _has_generalizable(self) -> bool:
        return len(self._entries) > 20

    def _jaccard(self, a: str, b: str) -> float:
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de la memoria."""
        type_counts: Dict[str, int] = {}
        for entry in self._entries.values():
            type_counts[entry.type] = type_counts.get(entry.type, 0) + 1

        return {
            "total_entries": len(self._entries),
            "type_counts": type_counts,
            "operations_count": len(self._operations_log),
            "last_operation": self._last_operation,
            "contradictions_count": sum(
                len(e.contradictions) for e in self._entries.values()
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": {eid: e.to_dict() for eid, e in self._entries.items()},
            "stats": self.get_stats(),
        }
