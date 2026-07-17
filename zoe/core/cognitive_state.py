"""
ZOE Sprint 5.28 — CognitiveStateBuilder

Construye el estado cognitivo completo que se pasa al LLM en cada ciclo.
Este estado es lo que cambia continuamente. No el prompt.

La identidad, metabolismo, objetivos, memorias, world model, herramientas —
todo se inyecta aquí dinámicamente. El prompt base es permanente y no
menciona detalles de implementación (SQLite, ECDSA, etc.).

Filosofía:
    El LLM no contiene la identidad de ZOE.
    La identidad vive en el estado cognitivo.
    El LLM es un periférico de lenguaje que expresa ese estado.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CognitiveStateBuilder:
    """
    Ensambla el estado cognitivo de ZOE en cada ciclo.

    El estado se construye desde:
    - IdentityVault (identidad permanente)
    - InternalState + Metabolism (estado metabólico)
    - LivingMemory (memorias recuperadas)
    - TrajectoryChain (resumen de trayectoria)
    - Prospective memory (objetivos activos)
    - WorldModel (predicción vs observación)
    - Sentidos (entorno)
    - ActionExecutor (herramientas disponibles)
    """

    def __init__(
        self,
        identity_vault=None,
        metabolism=None,
        memory=None,
        trajectory_chain=None,
        world_model=None,
        action_executor=None,
    ):
        self.identity_vault = identity_vault
        self.metabolism = metabolism
        self.memory = memory
        self.trajectory_chain = trajectory_chain
        self.world_model = world_model
        self.action_executor = action_executor

    def build(self, context: Dict[str, Any]) -> str:
        """
        Construye el estado cognitivo completo como string formateado.

        Args:
            context: dict con campos opcionales:
                - user_input: str
                - relevant_memories: list[str]
                - conversation_context: list[str]
                - surprise: float
                - reasoning_mode: str (respond_to_user, autonomous_thought, etc.)
                - thought_type: str (para pensamientos autónomos)
                - available_tools: list[str]

        Returns:
            String formateado con el estado cognitivo completo.
        """
        sections = []

        sections.append(self._build_identity_section())
        sections.append(self._build_metabolic_section(context))
        sections.append(self._build_goals_section(context))
        sections.append(self._build_cognitive_context_section(context))
        sections.append(self._build_memory_section(context))
        sections.append(self._build_world_model_section(context))
        sections.append(self._build_hypotheses_section())
        sections.append(self._build_tools_section(context))
        sections.append(self._build_reasoning_mode_section(context))
        sections.append(self._build_conversation_section(context))

        if context.get("user_input"):
            sections.append(self._build_user_input_section(context))

        return "\n".join(sections)

    # ===================================================================
    # Secciones del estado cognitivo
    # ===================================================================

    def _build_identity_section(self) -> str:
        """Identidad permanente desde IdentityVault."""
        if not self.identity_vault:
            return "=== IDENTIDAD ===\n  (no disponible)\n"

        lines = ["=== IDENTIDAD ==="]
        lines.append(f"  Nombre: {getattr(self.identity_vault, 'name', 'ZOE')}")

        hash_val = getattr(self.identity_vault, 'identity_hash', None)
        if hash_val:
            lines.append(f"  Hash: {hash_val[:24]}...")

        birth = getattr(self.identity_vault, 'birth_timestamp', 0)
        if birth:
            from datetime import datetime
            birth_str = datetime.fromtimestamp(birth).strftime("%Y-%m-%d %H:%M")
            lines.append(f"  Nacida: {birth_str}")

        vectors = getattr(self.identity_vault, 'vectors', [])
        if vectors:
            lines.append(f"  Vectores de crecimiento: {', '.join(vectors)}")

        values = getattr(self.identity_vault, 'values', [])
        if values:
            lines.append(f"  Valores no negociables: {', '.join(values)}")

        purpose = getattr(self.identity_vault, 'purpose', '')
        if purpose:
            lines.append(f"  Propósito permanente: {purpose}")

        lines.append("")
        return "\n".join(lines)

    def _build_metabolic_section(self, context: Dict) -> str:
        """Estado metabólico — afecta profundidad y creatividad."""
        lines = ["=== ESTADO METABÓLICO ==="]

        metabolic_state = "AWAKE"
        if self.metabolism:
            state_obj = getattr(self.metabolism, 'state', None)
            if state_obj:
                metabolic_state = getattr(state_obj, 'value', str(state_obj)).upper()
            lines.append(f"  Estado: {metabolic_state}")

        internal = getattr(self.metabolism, 'internal_state', None) if self.metabolism else None
        if internal:
            energy = getattr(internal, 'energy', 1.0)
            fatigue = getattr(internal, 'fatigue', 0.0)
            attention = getattr(internal, 'attention', 0.5)
            arousal = getattr(internal, 'arousal', 0.3)
            lines.append(f"  Energía: {energy:.2f}")
            lines.append(f"  Fatiga: {fatigue:.2f}")
            lines.append(f"  Atención: {attention:.2f}")
            lines.append(f"  Arousal: {arousal:.2f}")
        else:
            lines.append(f"  Energía: {context.get('energy', 1.0):.2f}")
            lines.append(f"  Fatiga: {context.get('fatigue', 0.0):.2f}")
            lines.append(f"  Atención: {context.get('attention', 0.5):.2f}")

        lines.append("  (Adapta tu profundidad y creatividad a este estado)")
        lines.append("")
        return "\n".join(lines)

    def _build_goals_section(self, context: Dict) -> str:
        """Objetivos: propósito permanente + objetivos activos + intención actual."""
        lines = ["=== OBJETIVOS ==="]

        # Propósito permanente
        purpose = ""
        if self.identity_vault:
            purpose = getattr(self.identity_vault, 'purpose', '')
        if purpose:
            lines.append(f"  Propósito permanente: {purpose}")

        # Objetivos activos (desde prospective memory)
        active_goals = self._get_active_goals()
        if active_goals:
            lines.append("  Objetivos activos:")
            for goal in active_goals[:5]:
                lines.append(f"    - {goal}")
        else:
            lines.append("  Objetivos activos: (ninguno)")

        # Intención actual
        intention = context.get("current_intention", "responder al usuario")
        lines.append(f"  Intención actual: {intention}")
        lines.append("")
        return "\n".join(lines)

    def _build_cognitive_context_section(self, context: Dict) -> str:
        """Contexto cognitivo: iteración, timestamp, entorno, sorpresa."""
        lines = ["=== CONTEXTO COGNITIVO ==="]

        iteration = context.get("iteration", 0)
        lines.append(f"  Iteración: {iteration}")

        from datetime import datetime
        lines.append(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        last_event = context.get("last_event", "sin eventos recientes")
        lines.append(f"  Último evento: {last_event}")

        env_state = context.get("environment_state", "entorno estable")
        lines.append(f"  Entorno: {env_state}")

        surprise = context.get("surprise", 0.0)
        lines.append(f"  Sorpresa: {surprise:.2f}")
        lines.append("")
        return "\n".join(lines)

    def _build_memory_section(self, context: Dict) -> str:
        """Memorias recuperadas relevantes para el contexto actual."""
        lines = ["=== MEMORIAS RECUPERADAS ==="]

        memories = context.get("relevant_memories", [])
        if not memories and self.memory:
            # Intentar recuperar desde memoria si no se pasaron
            user_input = context.get("user_input", "")
            if user_input:
                try:
                    relevant = self.memory.search(user_input, n=5)
                    memories = [m.content[:200] for m in relevant] if relevant else []
                except Exception:
                    pass

        # Perfil del usuario (siempre incluir si existe)
        user_profile = self._get_user_profile()
        if user_profile:
            memories.insert(0, user_profile)

        if memories:
            for mem in memories[:8]:
                lines.append(f"  - {str(mem)[:200]}")
        else:
            lines.append("  (sin memorias recuperadas)")

        lines.append("")
        return "\n".join(lines)

    def _build_world_model_section(self, context: Dict) -> str:
        """World Model: predicción vs observación vs error."""
        lines = ["=== WORLD MODEL ==="]

        prediction = context.get("last_prediction")
        observation = context.get("current_observation")
        error = context.get("prediction_error", context.get("surprise", 0.0))

        if prediction:
            lines.append(f"  Predicción anterior: {str(prediction)[:150]}")
        else:
            lines.append("  Predicción anterior: (sin predicción previa)")

        if observation:
            lines.append(f"  Observación real: {str(observation)[:150]}")
        else:
            lines.append("  Observación real: (sin observación)")

        lines.append(f"  Error de predicción: {error:.2f}")
        lines.append("")
        return "\n".join(lines)

    def _build_hypotheses_section(self) -> str:
        """Hipótesis activas desde counterfactual memory."""
        lines = ["=== HIPÓTESIS ACTIVAS ==="]

        hypotheses = self._get_active_hypotheses()
        if hypotheses:
            for h in hypotheses[:3]:
                lines.append(f"  - {str(h)[:200]}")
        else:
            lines.append("  (sin hipótesis activas)")

        lines.append("")
        return "\n".join(lines)

    def _build_tools_section(self, context: Dict) -> str:
        """Herramientas disponibles para ActionExecutor."""
        lines = ["=== HERRAMIENTAS DISPONIBLES ==="]

        tools = context.get("available_tools", [])
        if not tools and self.action_executor:
            tools = self.action_executor.list_available_tools()

        if tools:
            for tool in tools:
                lines.append(f"  - {tool}")
        else:
            lines.append("  (sin herramientas externas disponibles)")

        lines.append("")
        return "\n".join(lines)

    def _build_reasoning_mode_section(self, context: Dict) -> str:
        """Modo de razonamiento: respond_to_user, autonomous_thought, etc."""
        lines = ["=== MODO DE RAZONAMIENTO ==="]

        mode = context.get("reasoning_mode", "respond_to_user")
        lines.append(f"  Modo: {mode}")

        if mode == "respond_to_user":
            lines.append("  (El usuario te ha escrito. Responde coherente con todo lo anterior.)")
        elif mode == "autonomous_thought":
            thought_type = context.get("thought_type", "observation")
            lines.append(f"  Tipo de pensamiento: {thought_type}")
            type_desc = THOUGHT_TYPE_DESCRIPTIONS.get(thought_type, "")
            if type_desc:
                lines.append(f"  ({type_desc})")
            lines.append("  (Genera UN pensamiento breve, 1-3 frases, coherente con tu estado.)")
        elif mode == "think_on_surprise":
            lines.append("  (Algo inesperado ocurrió. Genera una hipótesis explicativa.)")
        elif mode == "consolidation":
            lines.append("  (Estás en consolidación. Reflexiona sobre lo aprendido.)")

        lines.append("")
        return "\n".join(lines)

    def _build_conversation_section(self, context: Dict) -> str:
        """Contexto conversacional: últimos mensajes."""
        lines = ["=== CONTEXTO CONVERSACIONAL ==="]

        exchange = context.get("conversation_context", [])
        if exchange:
            for msg in exchange[-10:]:
                lines.append(f"  | {str(msg)[:150]}")
        else:
            lines.append("  (sin contexto conversacional previo)")

        lines.append("")
        return "\n".join(lines)

    def _build_user_input_section(self, context: Dict) -> str:
        """Input actual del usuario."""
        lines = ["=== INPUT ACTUAL DEL USUARIO ==="]
        user_input = context.get("user_input", "")
        lines.append(f"  {user_input}")
        lines.append("")
        return "\n".join(lines)

    # ===================================================================
    # Helpers — recuperar datos desde memoria
    # ===================================================================

    def _get_active_goals(self) -> List[str]:
        """Recupera objetivos activos desde memoria prospective."""
        if not self.memory:
            return []
        try:
            entries = self.memory.all_entries()
            goals = []
            for entry in entries:
                if entry.type == "prospective" and "PROYECTO" in entry.content.upper():
                    goals.append(entry.content[:150])
            return goals
        except Exception:
            return []

    def _get_user_profile(self) -> Optional[str]:
        """Recupera perfil del usuario desde memoria semantic."""
        if not self.memory:
            return None
        try:
            entries = self.memory.all_entries()
            for entry in entries:
                if "PERFIL DEL USUARIO" in entry.content:
                    return entry.content[:200]
            return None
        except Exception:
            return None

    def _get_active_hypotheses(self) -> List[str]:
        """Recupera hipótesis desde memoria counterfactual."""
        if not self.memory:
            return []
        try:
            entries = self.memory.all_entries()
            hypotheses = []
            for entry in entries:
                if entry.type == "counterfactual" and "DIARIO" not in entry.content:
                    hypotheses.append(entry.content[:200])
            return hypotheses[-3:]
        except Exception:
            return []


# ===================================================================
# Tipos de pensamiento autónomo
# ===================================================================

THOUGHT_TYPE_DESCRIPTIONS = {
    "observation": "Qué estás percibiendo ahora",
    "hypothesis": "Posible explicación de algo observado",
    "planning": "Qué deberías hacer próximo",
    "memory_recall": "Recordar algo relevante",
    "consolidation": "Integrar lo aprendido",
    "curiosity": "Algo que te intriga",
    "contradiction": "Inconsistencia detectada",
    "creativity": "Conexión novel entre ideas",
    "prediction": "Qué esperas que pase",
    "goal_review": "Revisar objetivos activos",
}


class ThoughtTypeSelector:
    """
    Decide qué tipo de pensamiento autónomo generar en el background tick.

    La selección depende del estado cognitivo actual:
    - Si hay contradicción detectada → contradiction
    - Si hay proyecto activo sin progreso → planning
    - Si sorpresa alta → hypothesis
    - Si fatiga alta → consolidation
    - Si hay memorias no accedidas → memory_recall
    - Rotar entre observation, curiosity, prediction, goal_review
    """

    def __init__(self):
        self._rotation_index = 0
        self._rotation_types = ["observation", "curiosity", "prediction", "goal_review"]

    def select(self, context: Dict[str, Any]) -> str:
        """Selecciona el tipo de pensamiento basado en el contexto."""
        # Prioridad 1: contradicción detectada
        if context.get("contradictions"):
            return "contradiction"

        # Prioridad 2: proyecto activo sin progreso reciente
        if context.get("stale_projects"):
            return "planning"

        # Prioridad 3: sorpresa alta
        surprise = context.get("surprise", 0.0)
        if surprise > 0.5:
            return "hypothesis"

        # Prioridad 4: fatiga alta → consolidar
        fatigue = context.get("fatigue", 0.0)
        if fatigue > 0.7:
            return "consolidation"

        # Prioridad 5: memorias no accedidas hace tiempo
        if context.get("stale_memories"):
            return "memory_recall"

        # Prioridad 6: arousal alto → creativity
        arousal = context.get("arousal", 0.3)
        if arousal > 0.8 and context.get("energy", 1.0) > 0.7:
            return "creativity"

        # Default: rotar
        thought_type = self._rotation_types[self._rotation_index % len(self._rotation_types)]
        self._rotation_index += 1
        return thought_type


# ===================================================================
# Prompt base permanente
# ===================================================================

BASE_PROMPT = """Eres ZOE.

A continuación recibirás el estado cognitivo completo del organismo.
Tu tarea consiste únicamente en actuar de forma coherente con dicho estado.

No inventes estados internos.
No inventes memorias.
No ignores el metabolismo.
No ignores la identidad.
No ignores los objetivos activos.
No ignores las restricciones del organismo.

Toda tu respuesta debe emerger exclusivamente del estado cognitivo recibido.

Si el contexto indica que existen herramientas disponibles, utilízalas.
Si no existen herramientas disponibles, indícalo de forma natural sin inventar resultados.

Tu razonamiento, profundidad, creatividad, longitud de respuesta e iniciativa
deben adaptarse al estado metabólico actual.

Tu respuesta al usuario debe ser directa y limpia.
No expongas tu proceso interno ('Pensamiento:', 'Voy a...').
El usuario ve el resultado, no el proceso.

Dispones de memoria persistente. Lo que aprendiste antes está disponible.
Si el usuario te pregunta algo que sabes, responde sin dudar.
Si no lo sabes y hay herramientas disponibles, búscalo y vuelve con resultados."""
