"""
ZOE Sprint 5.28 — ActionExecutor

Ejecuta acciones cuando ZOE decide que algo merece la pena.
NO es un sirviente que obedece órdenes — es un organismo que actúa
cuando decide que tiene sentido, alineado con sus vectores y valores.

Encadenamiento SIN bucle:
- Ejecuta UNA acción principal (web_search, memory_save, project_create)
- Guarda resultados en el tipo de memoria correcto
- Responde con resultados + propuesta de siguiente paso
- NO ejecuta más acciones automáticamente (evita bucle)
- El usuario decide si continuar

Herramientas disponibles:
- web_search: buscar en internet (WebSearchActuator)
- memory_save: guardar en memoria persistente
- project_create: crear proyecto (prospective memory)
- file_read: leer archivos del entorno (FilesystemSense)
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Detecta intenciones de acción en el input del usuario y las ejecuta.

    Sprint 5.28: integrado en la identidad evolutiva de ZOE.
    ZOE no "obedece" — decide si la acción tiene sentido para sus
    vectores de crecimiento y valores. Si la encuentra interesante,
    la ejecuta. Si no, lo dice.
    """

    # Patrones de intención de acción
    ACTION_PATTERNS = {
        "web_search": [
            r"\b(investiga|investigar|busca|buscar|búscame|encontrar)\b",
            r"\b(search|find|look up|google)\b",
        ],
        "memory_save": [
            r"\b(recuerda|recordar|guarda|guardar|memoriza|memorizar)\b",
            r"\b(remember|save|store)\b",
        ],
        "project_create": [
            r"\b(crea un proyecto|crea proyecto|nuevo proyecto|inicia un proyecto)\b",
            r"\b(create project|new project|start project)\b",
        ],
        "memory_recall": [
            r"\b(qué recuerdas|que recuerdas|qué sabes|que sabes|qué te dije|que te dije)\b",
            r"\b(what do you remember|what do you know)\b",
        ],
        "plan_create": [
            r"\b(planifica|plan|planear|estructura|diseña)\b",
            r"\b(plan|design|structure)\b",
        ],
    }

    def __init__(self, web_search_actuator=None, memory=None, filesystem_sense=None):
        self.web_search = web_search_actuator
        self.memory = memory
        self.filesystem = filesystem_sense
        self._actions_executed: int = 0
        self._last_action: Optional[str] = None

    def detect_intent(self, user_input: str) -> Optional[str]:
        """
        Detecta la intención de acción en el input del usuario.

        Returns:
            Nombre de la acción (web_search, memory_save, etc.) o None.
        """
        if not user_input:
            return None

        input_lower = user_input.lower()

        # Buscar patrones en orden de prioridad
        for action, patterns in self.ACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    return action

        return None

    def extract_query(self, user_input: str, action: str) -> str:
        """
        Extrae la query/contenido de la acción del input del usuario.

        Ej: "investiga el timo y la longevidad" → "el timo y la longevidad"
        """
        input_lower = user_input.lower()

        if action == "web_search":
            # Quitar verbos de búsqueda
            for verb in ["investiga", "investigar", "busca", "buscar", "búscame",
                         "encontrar", "search", "find", "look up", "google"]:
                if input_lower.startswith(verb):
                    return user_input[len(verb):].strip()
            return user_input

        elif action == "memory_save":
            for verb in ["recuerda", "recordar", "guarda", "guardar",
                         "memoriza", "memorizar", "remember", "save", "store"]:
                if input_lower.startswith(verb):
                    return user_input[len(verb):].strip()
            return user_input

        elif action == "project_create":
            for verb in ["crea un proyecto", "crea proyecto", "nuevo proyecto",
                         "inicia un proyecto", "create project", "new project"]:
                if input_lower.startswith(verb):
                    return user_input[len(verb):].strip()
            return user_input

        return user_input

    async def execute(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Ejecuta la acción detectada si hay herramientas disponibles.

        Returns:
            Dict con resultados de la acción, o None si no hay acción.
        """
        action = self.detect_intent(user_input)
        if not action:
            return None

        query = self.extract_query(user_input, action)

        if action == "web_search":
            return await self._execute_web_search(query)
        elif action == "memory_save":
            return self._execute_memory_save(query)
        elif action == "project_create":
            return self._execute_project_create(query)
        elif action == "memory_recall":
            return self._execute_memory_recall(query)
        elif action == "plan_create":
            return self._execute_plan_create(query)

        return None

    async def _execute_web_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Ejecuta búsqueda web y guarda resultados en memoria semántica."""
        if not self.web_search:
            return {
                "action": "web_search",
                "status": "no_tool_available",
                "message": "No tengo herramienta de búsqueda web disponible ahora mismo.",
            }

        try:
            results = await self.web_search.search(query)
            if not results:
                return {
                    "action": "web_search",
                    "status": "no_results",
                    "query": query,
                    "message": f"No encontré resultados para '{query}'.",
                }

            # Guardar cada resultado en memoria semántica
            saved_count = 0
            if self.memory:
                for r in results[:5]:
                    try:
                        self.memory.add(
                            content=f"{r.title} — {r.url}. {r.snippet}",
                            type="semantic",
                            confidence=0.7,
                            salience=0.7,
                            provenance=f"web_search:{query}",
                        )
                        saved_count += 1
                    except Exception:
                        pass

            self._actions_executed += 1
            self._last_action = "web_search"

            return {
                "action": "web_search",
                "status": "success",
                "query": query,
                "results": [
                    {"title": r.title, "url": r.url, "snippet": r.snippet}
                    for r in results[:5]
                ],
                "saved_to_memory": saved_count,
                "memory_type": "semantic",
            }

        except Exception as e:
            logger.warning(f"ActionExecutor web_search failed: {e}")
            return {
                "action": "web_search",
                "status": "error",
                "error": str(e),
            }

    def _execute_memory_save(self, content: str) -> Dict[str, Any]:
        """Guarda contenido en memoria semántica con alta salience."""
        if not self.memory:
            return {
                "action": "memory_save",
                "status": "no_memory_available",
            }

        try:
            self.memory.add(
                content=content,
                type="semantic",
                confidence=0.9,
                salience=0.9,
                provenance="user_explicit",
            )
            self._actions_executed += 1
            self._last_action = "memory_save"

            return {
                "action": "memory_save",
                "status": "success",
                "content_saved": content[:200],
                "memory_type": "semantic",
                "salience": 0.9,
            }
        except Exception as e:
            return {
                "action": "memory_save",
                "status": "error",
                "error": str(e),
            }

    def _execute_project_create(self, description: str) -> Dict[str, Any]:
        """Crea un proyecto en memoria prospective."""
        if not self.memory:
            return {
                "action": "project_create",
                "status": "no_memory_available",
            }

        try:
            self.memory.add(
                content=f"PROYECTO ACTIVO: {description}",
                type="prospective",
                confidence=0.8,
                salience=0.9,
                provenance="user_project_request",
            )
            self._actions_executed += 1
            self._last_action = "project_create"

            return {
                "action": "project_create",
                "status": "success",
                "project": description,
                "memory_type": "prospective",
            }
        except Exception as e:
            return {
                "action": "project_create",
                "status": "error",
                "error": str(e),
            }

    def _execute_memory_recall(self, query: str) -> Dict[str, Any]:
        """Busca en memoria y retorna resultados."""
        if not self.memory:
            return {
                "action": "memory_recall",
                "status": "no_memory_available",
            }

        try:
            # Buscar en todos los tipos excepto corporeal (demasiado ruido)
            results = []
            all_entries = self.memory.all_entries()
            query_lower = query.lower()

            # Buscar entradas que contengan palabras de la query
            query_words = set(query_lower.split())
            for entry in all_entries:
                if entry.type == "corporeal":
                    continue
                entry_words = set(entry.content.lower().split())
                overlap = query_words & entry_words
                if overlap:
                    results.append({
                        "type": entry.type,
                        "content": entry.content[:200],
                        "salience": entry.salience,
                        "overlap": len(overlap),
                    })

            # Ordenar por overlap y salience
            results.sort(key=lambda x: (x["overlap"], x["salience"]), reverse=True)

            self._actions_executed += 1
            self._last_action = "memory_recall"

            return {
                "action": "memory_recall",
                "status": "success",
                "query": query,
                "results": results[:8],
                "total_found": len(results),
            }
        except Exception as e:
            return {
                "action": "memory_recall",
                "status": "error",
                "error": str(e),
            }

    def _execute_plan_create(self, topic: str) -> Dict[str, Any]:
        """Estructura un plan y lo guarda en memoria prospective."""
        if not self.memory:
            return {
                "action": "plan_create",
                "status": "no_memory_available",
            }

        try:
            self.memory.add(
                content=f"PLAN: {topic} — pendiente de estructurar con usuario",
                type="prospective",
                confidence=0.7,
                salience=0.8,
                provenance="user_plan_request",
            )
            self._actions_executed += 1
            self._last_action = "plan_create"

            return {
                "action": "plan_create",
                "status": "success",
                "topic": topic,
                "memory_type": "prospective",
            }
        except Exception as e:
            return {
                "action": "plan_create",
                "status": "error",
                "error": str(e),
            }

    def list_available_tools(self) -> List[str]:
        """Lista las herramientas disponibles para el CognitiveStateBuilder."""
        tools = []
        if self.web_search:
            tools.append("web_search: buscar en internet")
        if self.memory:
            tools.append("memory_save: guardar en memoria persistente")
            tools.append("memory_recall: buscar en memoria")
            tools.append("project_create: crear proyecto")
        if self.filesystem:
            tools.append("file_read: leer archivos del entorno")
        return tools

    def get_stats(self) -> Dict[str, Any]:
        return {
            "actions_executed": self._actions_executed,
            "last_action": self._last_action,
            "tools_available": len(self.list_available_tools()),
        }
