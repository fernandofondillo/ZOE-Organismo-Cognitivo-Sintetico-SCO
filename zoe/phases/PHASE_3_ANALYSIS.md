# Análisis para Fase 3 — Implicaciones de Fases 0-2 y refinamientos necesarios

> **Análisis crítico.** Antes de implementar Fase 3, analiza qué implicaciones tiene lo construido en Fases 0-2 y qué hay que refinar, ampliar y/o mejorar.

**Fecha:** 8 julio 2026
**Base:** 398/398 tests pasan, sistema completo funcional

---

## Las 10 implicaciones de Fases 0-2 para Fase 3

### Implicación 1 — Los 12 sub-agentes existen pero NO están integrados en el bucle

**Estado actual:** Los 8 sub-agentes de Fase 2 (Memorialist, Learner, Curator, Creativity, CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine) existen como clases independientes con tests propios, pero `CognitiveLoopV05` no los invoca durante el bucle.

**Implicación para Fase 3:** Fase 3 debe integrar los 12 sub-agentes en el bucle cognitivo. Esto requiere:
- Modificar `CognitiveLoopV05._act()` para invocar sub-agentes adicionales
- Cada sub-agente debe poder contribuir al Global Workspace
- El bucle debe poder seleccionar qué sub-agente activar según contexto

### Implicación 2 — El Global Workspace existe pero el bucle no lo usa

**Estado actual:** `GlobalWorkspace` está implementado con `submit()`, `compete()`, `broadcast()`, pero `CognitiveLoopV05` sigue usando secuencia lineal (observar → predecir → decidir → actuar).

**Implicación para Fase 3:** Fase 3 debe reemplazar la secuencia lineal por el Global Workspace. Esto requiere:
- En cada iteración, los sub-agentes proponen acciones al workspace
- El workspace selecciona ganadores por score
- El broadcast notifica a todos los sub-agentes
- Es un cambio arquitectural significativo

### Implicación 3 — La meta-cognición existe pero no se invoca

**Estado actual:** `MetaCognition` con `evaluate_confidence()`, `should_deliberate()`, pero no se llama desde el bucle.

**Implicación para Fase 3:** Fase 3 debe integrar meta-cognición en el bucle:
- Tras generar respuesta de System 1, evaluar confianza
- Si confianza baja o stakes altos, activar System 2
- System 2 activa todos los sub-agentes para deliberación

### Implicación 4 — Active Inference existe pero no conecta con decisiones

**Estado actual:** `ActiveInferenceLoop` aprende transiciones y selecciona acciones, pero el bucle no lo consulta.

**Implicación para Fase 3:** Fase 3 debe conectar Active Inference:
- El bucle consulta Active Inference para selección de acción
- Active Inference alimenta su modelo con resultados del bucle
- Integración con CognitivePhysics (uncertainty_pressure)

### Implicación 5 — Los 11 tipos de memoria no tienen backing stores persistentes

**Estado actual:** Las 11 clases de memoria existen como dataclasses, pero `LivingMemory` las almacena en memoria (dict). No hay persistencia a disco.

**Implicación para Fase 3:** Fase 3 debe añadir backing stores:
- SQLite para memoria episódica, semántica, procedural
- JSON files para memoria evolutiva, cultural
- Vector index para memoria social, emocional
- Persistencia entre sesiones

### Implicación 6 — Las emociones son básicas, no afectan decisiones

**Estado actual:** `EmotionalMotor` genera marcadores, pero estos no afectan el comportamiento del bucle.

**Implicación para Fase 3:** Fase 3 debe hacer que las emociones afecten decisiones:
- Marcador de sorpresa alta → priorizar exploración
- Marcador de fatiga → reducir profundidad de razonamiento
- Marcador de satisfacción → consolidar en vez de explorar
- Conexión con CognitiveTensions y CognitivePhysics

### Implicación 7 — El Motor Ontogenético solo hace mutaciones de memoria

**Estado actual:** 8 tipos de mutación (add_memory, strengthen_belief, etc.), pero ninguna modifica arquitectura (crear/eliminar sub-agentes).

**Implicación para Fase 3:** Fase 3 debe extender el Motor Ontogenético:
- `add_subagent` — crear nuevo sub-agente
- `remove_subagent` — eliminar sub-agente obsoleto
- `merge_subagents` — fusionar sub-agentes redundantes
- `modify_threshold` — ajustar parámetros de meta-cognición
- Todas verificadas por las 6 leyes + Identity Vault

### Implicación 8 — No hay consolidación profunda durante el sueño

**Estado actual:** `Metabolism` ejecuta operaciones de `LivingMemory.think()` durante el sueño, pero no hay consolidación profunda (reorganizar entre tipos, extraer patrones, generar hipótesis).

**Implicación para Fase 3:** Fase 3 debe implementar consolidación profunda:
- Durante SLEEPING: mover episódica → semántica
- Extraer patrones de múltiples entries
- Generar hipótesis desde ScientificEngine
- Reforzar creencias con confianza alta
- Olvidar entries de baja saliencia + baja confianza

### Implicación 9 — Los sub-agentes no leen campos cognitivos completamente

**Estado actual:** Los sub-agentes de Fase 0 reciben contexto como dict, pero no leen `CognitiveFields` directamente.

**Implicación para Fase 3:** Fase 3 debe conectar sub-agentes a campos:
- `Perceiver` escribe en campo `attention`
- `EmotionalMotor` escribe en campo `emotional`
- `CausalEngine` escribe en campo `causal`
- `EthicalMotor` escribe en campo `ethical`
- Todos leen campos para contexto

### Implicación 10 — Falta integrar todo en un demo Fase 2 completo

**Estado actual:** Hay demos para Fase 0, 0.5, integrado, y Fase 1, pero no para Fase 2 con todos los componentes.

**Implicación para Fase 3:** Antes de Fase 3, crear `demo_phase2.py` que muestre:
- World Model V2 aprendiendo
- Active Inference seleccionando acciones
- 12 sub-agentes compitiendo en Global Workspace
- Meta-cognición decidiendo System 1 vs System 2
- Mutaciones firmadas + memoria viva + metabolismo + leyes

---

## Lo que Fase 3 debe refinar, ampliar y/o mejorar

### Refinar (mejorar lo existente)

| Componente | Refinamiento |
|---|---|
| CognitiveLoopV05 | Integrar Global Workspace + meta-cognición + Active Inference |
| Sub-agentes Fase 2 | Conectar a CognitiveFields |
| EmotionalMotor | Hacer que emociones afecten decisiones |
| Motor Ontogenético | Añadir mutaciones arquitecturales |
| Metabolism | Consolidación profunda durante sueño |
| LivingMemory |Backing stores persistentes |

### Ampliar (añadir nuevo)

| Componente | Ampliación |
|---|---|
| Backing stores | SQLite para 11 tipos de memoria |
| Consolidación profunda | Reorganización entre tipos en sueño |
| Mutaciones arquitecturales | add_subagent, remove_subagent, merge_subagents |
| Integración sub-agentes → bucle | 12 sub-agentes activos en bucle |
| Demo Fase 2 | End-to-end con todos los componentes Fase 2 |

### Mejorar (optimizar)

| Componente | Mejora |
|---|---|
| World Model V2 | Usar sentence-transformers si disponible (ya tiene fallback) |
| Active Inference | Más acciones disponibles, mejor modelo de transiciones |
| Global Workspace | Regularización para evitar colapso a pocos sub-agentes |
| Meta-cognición | Ajuste automático de thresholds por Motor Ontogenético |

---

## Las 6 sub-fases propuestas para Fase 3

### Sub-fase 3.1 — Integrar 12 sub-agentes en el bucle (días 1-3)

**Objetivo:** los 12 sub-agentes participan en el bucle cognitivo.

**Implementación:**
- Modificar `CognitiveLoopV05` para invocar los 12 sub-agentes
- Cada sub-agente genera propuestas para el Global Workspace
- El bucle selecciona qué sub-agente activar según contexto
- Cada sub-agente lee/escribe CognitiveFields

### Sub-fase 3.2 — Integrar Global Workspace en el bucle (días 4-5)

**Objetivo:** reemplazar secuencia lineal por ecología de procesos.

**Implementación:**
- En cada iteración: sub-agentes proponen → workspace compite → ganador ejecuta → broadcast
- Eliminar la secuencia lineal actual
- El workspace selecciona por relevancia, urgencia, novedad, energía

### Sub-fase 3.3 — Integrar meta-cognición y Active Inference (días 6-8)

**Objetivo:** System 1/2 y Active Inference afectan decisiones del bucle.

**Implementación:**
- Tras generar respuesta de System 1, meta-cognición evalúa confianza
- Si confianza baja, activar System 2 (todos los sub-agentes deliberan)
- Active Inference selecciona acción que minimiza sorpresa esperada
- Conexión con CognitivePhysics (uncertainty_pressure → System 2)

### Sub-fase 3.4 — Backing stores persistentes para 11 memorias (días 9-12)

**Objetivo:** las 11 memorias persisten entre sesiones.

**Implementación:**
- SQLite backing para episódica, semántica, procedural, causal
- JSON backing para evolutiva, cultural, contrafactual
- Vector index (simple) para social, emocional
- API: `save_to_disk()`, `load_from_disk()`
- Test: reiniciar organismo y verificar que memoria persiste

### Sub-fase 3.5 — Motor Ontogenético avanzado + consolidación profunda (días 13-16)

**Objetivo:** mutaciones arquitecturales + consolidación profunda en sueño.

**Implementación:**
- Nuevos tipos de mutación: `add_subagent`, `remove_subagent`, `merge_subagents`, `modify_threshold`
- Durante SLEEPING: consolidación profunda (episódica → semántica, extraer patrones, generar hipótesis)
- Verificación de mutaciones arquitecturales por leyes + Identity Vault
- Test: organismo crea nuevo sub-agente y lo usa

### Sub-fase 3.6 — Integración + demo Fase 2/3 + validación (días 17-18)

**Objetivo:** demo completo + tests de integración.

**Implementación:**
- `demo_phase2_3.py` — organismo con TODO integrado
- Tests de integración: 12 sub-agentes en workspace, meta-cog activa System 2, Active Inference selecciona acciones, memoria persiste, consolidación profunda funciona
- 50 escenarios de validación

---

## Métricas de validación Fase 3

| Métrica | Objetivo |
|---|---|
| 12 sub-agentes activos en bucle | 12/12 |
| Global Workspace selecciona ganadores | 100% iteraciones |
| System 2 se activa con baja confianza | ≥80% |
| Active Inference selecciona acciones | Sí |
| Memoria persiste entre sesiones | Sí |
| Consolidación profunda en sueño | Sí |
| Motor Ontogenético crea sub-agente | Sí |
| Tests pasan | 100% previos + nuevos |
| Demo Fase 2/3 funcional | Sí |

---

*Análisis completado. Fase 3 planificada con refinamientos, ampliaciones y mejoras.*
