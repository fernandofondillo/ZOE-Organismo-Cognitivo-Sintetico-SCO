"""
ZOE v1.0 — Deep Consolidation (Fase 3.5)

Consolidación profunda de memoria durante el sueño del organismo.

Operaciones de consolidación profunda:
1. Episódica → Semántica: entradas episódicas accedidas frecuentemente se convierten en semántica
2. Extracción de patrones: detecta patrones en múltiples entries y crea entradas semánticas
3. Refuerzo de creencias: aumenta confianza en entries con alta saliencia y acceso frecuente
4. Olvido profundo: elimina entries de baja saliencia Y baja confianza Y poco acceso
5. Generación de hipótesis: desde ScientificEngine, crea entradas counterfactual
6. Detección de contradicciones: marca entries opuestas y reduce confianza
7. Reorganización entre tipos: mueve entries al tipo más apropiado

Se ejecuta durante SLEEPING del metabolismo.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DeepConsolidation:
    """
    Consolidación profunda de memoria durante el sueño.

    Se ejecuta cuando el metabolismo está en estado SLEEPING.
    Realiza operaciones que no se pueden hacer durante AWAKE
    porque requieren acceso exclusivo a la memoria.
    
    Fase 6A: integra KnowledgeQuarantine para:
    - Poda entries de cuarentena expiradas (timeout >30 días)
    - NO promueve a semántica entries en cuarentena activa (no validadas)
    - NO refuerza creencias basadas en conocimiento no validado
    """

    def __init__(self, memory: Any = None, scientific_engine: Any = None, quarantine: Any = None):
        self.memory = memory
        self.scientific_engine = scientific_engine
        # Fase 6A: cuarentena para filtrar knowledge no validado
        self._quarantine = quarantine
        self._consolidation_history: List[Dict[str, Any]] = []
        self._total_consolidations: int = 0

    def set_memory(self, memory: Any) -> None:
        self.memory = memory

    def set_scientific_engine(self, engine: Any) -> None:
        self.scientific_engine = engine

    def set_quarantine(self, quarantine: Any) -> None:
        """Inyecta KnowledgeQuarantine (lo llama CapsuleManager)."""
        self._quarantine = quarantine

    def consolidate(self) -> Dict[str, Any]:
        """
        Ejecuta un ciclo de consolidación profunda.

        Returns:
            Resumen de operaciones realizadas
        """
        if not self.memory or self.memory.count() < 3:
            return {"operations": {}, "total_operations": 0, "reason": "insufficient_memory"}

        operations: Dict[str, int] = {
            "episodic_to_semantic": 0,
            "pattern_extraction": 0,
            "belief_reinforcement": 0,
            "deep_forgetting": 0,
            "hypothesis_generation": 0,
            "contradiction_detection": 0,
            "type_reorganization": 0,
        }

        # 1. Episódica → Semántica
        operations["episodic_to_semantic"] = self._episodic_to_semantic()

        # 2. Extracción de patrones
        operations["pattern_extraction"] = self._extract_patterns()

        # 3. Refuerzo de creencias
        operations["belief_reinforcement"] = self._reinforce_beliefs()

        # 4. Olvido profundo
        operations["deep_forgetting"] = self._deep_forget()

        # 5. Generación de hipótesis
        operations["hypothesis_generation"] = self._generate_hypotheses()

        # 6. Detección de contradicciones
        operations["contradiction_detection"] = self._detect_contradictions()

        # 7. Reorganización entre tipos
        operations["type_reorganization"] = self._reorganize_types()

        total_ops = sum(operations.values())
        self._total_consolidations += 1

        result = {
            "consolidation_number": self._total_consolidations,
            "timestamp": time.time(),
            "total_operations": total_ops,
            "operations": operations,
            "memory_count_after": self.memory.count() if self.memory else 0,
        }
        
        # Fase 6A: stats de cuarentena
        if self._quarantine:
            try:
                q_stats = self._quarantine.get_stats()
                result["quarantine_stats"] = q_stats
                # Limpieza adicional de expiradas durante consolidate
                expired = self._quarantine.cleanup_expired()
                if expired > 0:
                    result["quarantine_expired_during_consolidate"] = expired
            except Exception as e:
                logger.warning(f"DeepConsolidation: quarantine stats failed: {e}")
        
        self._consolidation_history.append(result)
        if len(self._consolidation_history) > 20:
            self._consolidation_history = self._consolidation_history[-10:]

        logger.info(
            f"DeepConsolidation #{self._total_consolidations}: "
            f"{total_ops} operations. Memory: {result['memory_count_after']} entries."
        )

        return result

    def _episodic_to_semantic(self) -> int:
        """Convierte entries episódicas frecuentemente accedidas en semánticas.
        
        Fase 6A: NO promueve entries en cuarentena (conocimiento no validado).
        El conocimiento no validado no debe consolidarse como hecho semántico.
        """
        count = 0
        now = time.time()

        for entry in list(self.memory.all_entries()):
            if (
                entry.type == "episodic"
                and entry.access_count > 3
                and (now - entry.timestamp) > 1800  # > 30 min old
            ):
                # Fase 6A: verificar si está en cuarentena
                if self._quarantine:
                    entry_id = getattr(entry, 'id', '')
                    if self._quarantine.is_quarantined(entry_id):
                        # No promover entries en cuarentena a semántica
                        continue
                
                entry.type = "semantic"
                entry.salience = min(1.0, entry.salience + 0.1)
                count += 1

        return count

    def _extract_patterns(self) -> int:
        """Extrae patrones de múltiples entries."""
        # Buscar palabras que aparecen en 3+ entries
        word_counts: Dict[str, int] = {}
        for entry in self.memory.all_entries():
            words = set(entry.content.lower().split())
            for w in words:
                if len(w) > 4:
                    word_counts[w] = word_counts.get(w, 0) + 1

        patterns = [w for w, c in word_counts.items() if c >= 3]

        if not patterns:
            return 0

        # Verificar si ya existe un entry de patrón similar
        existing = self.memory.search("Patrón detectado", n=5)
        existing_words = set()
        for e in existing:
            existing_words.update(e.content.lower().split())

        new_patterns = [p for p in patterns if p not in existing_words]
        if not new_patterns:
            return 0

        # Crear entry de patrón
        self.memory.add(
            content=f"Patrón consolidado en sueño: palabras recurrentes ({', '.join(new_patterns[:5])})",
            type="semantic",
            confidence=0.6,
            salience=0.7,
            provenance="deep_consolidation:pattern_extraction",
        )

        return 1

    def _reinforce_beliefs(self) -> int:
        """Refuerza creencias con alta saliencia y acceso frecuente.
        
        Fase 6A: NO refuerza entries en cuarentena (no validadas).
        El conocimiento no validado no debe ganar confianza durante el sueño.
        """
        count = 0

        for entry in self.memory.all_entries():
            if entry.salience > 0.7 and entry.access_count > 2:
                # Fase 6A: skip cuarentena
                if self._quarantine:
                    entry_id = getattr(entry, 'id', '')
                    if self._quarantine.is_quarantined(entry_id):
                        continue
                
                old_confidence = entry.confidence
                entry.confidence = min(1.0, entry.confidence + 0.05)
                if entry.confidence != old_confidence:
                    count += 1

        return count

    def _deep_forget(self) -> int:
        """Olvida entries de baja saliencia + baja confianza + poco acceso.
        
        Fase 6A: también poda entries de cuarentena expiradas.
        """
        to_forget = []

        for entry in self.memory.all_entries():
            entry_id = getattr(entry, 'id', '')
            
            # Fase 6A: si la entry está en cuarentena expirada → olvidar
            if self._quarantine:
                q_entry = self._quarantine.get_quarantine_entry(entry_id)
                if q_entry and q_entry.status == "expired":
                    to_forget.append(entry.id)
                    continue
            
            # Olvido estándar: baja saliencia + baja confianza + poco acceso
            if (
                entry.salience < 0.2
                and entry.confidence < 0.3
                and entry.access_count < 1
            ):
                to_forget.append(entry.id)

        for entry_id in to_forget:
            self.memory._entries.pop(entry_id, None)
            # Fase 6A: limpiar referencia en cuarentena si existe
            if self._quarantine and entry_id in self._quarantine._memory_entry_map:
                del self._quarantine._memory_entry_map[entry_id]

        return len(to_forget)

    def _generate_hypotheses(self) -> int:
        """Genera hipótesis desde el ScientificEngine durante el sueño."""
        if not self.scientific_engine:
            return 0

        # Si hay teorías pendientes, crear entradas counterfactual
        pending_theories = [
            t for t in self.scientific_engine._theories if t.get("status") == "proposed"
        ]

        count = 0
        for theory in pending_theories[:3]:  # máximo 3 por ciclo
            self.memory.add(
                content=f"Contradicción a investigar: {theory['hypothesis'][:80]}",
                type="counterfactual",
                confidence=0.4,
                salience=0.5,
                provenance="deep_consolidation:hypothesis",
                metadata={"theory_id": theory.get("timestamp", 0)},
            )
            count += 1

        return count

    def _detect_contradictions(self) -> int:
        """Detecta contradicciones entre entries."""
        count = 0
        entries = list(self.memory.all_entries())

        for i, entry_a in enumerate(entries):
            for entry_b in entries[i + 1:]:
                if entry_a.type != entry_b.type:
                    continue
                # Detectar contradicción simple: "no" + mismo contenido
                if (
                    entry_b.content.lower().startswith("no ")
                    and entry_a.content.lower() in entry_b.content.lower()
                ):
                    if entry_b.id not in entry_a.contradictions:
                        entry_a.contradictions.append(entry_b.id)
                        entry_b.contradictions.append(entry_a.id)
                        entry_a.confidence *= 0.7
                        entry_b.confidence *= 0.7
                        count += 1

        return count

    def _reorganize_types(self) -> int:
        """Reorganiza entries al tipo más apropiado."""
        count = 0

        for entry in self.memory.all_entries():
            # Si una entry emocional tiene alta confianza, mover a semántica
            if entry.type == "emotional" and entry.confidence > 0.8:
                entry.type = "semantic"
                count += 1
            # Si una entry contrafactual ha sido verificada, mover a causal
            elif entry.type == "counterfactual" and entry.access_count > 5:
                entry.type = "causal"
                count += 1

        return count

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_consolidations": self._total_consolidations,
            "history_count": len(self._consolidation_history),
            "last_consolidation": self._consolidation_history[-1] if self._consolidation_history else None,
        }

    def summary(self) -> str:
        return f"DeepConsolidation(consolidations={self._total_consolidations})"
