# Fase 2 — Mente completa (refinada con lecciones de Fases 0-1)

> **Plan refinado.** Tras construir Fases 0, 0.5 y 1, el organismo tiene Alma, Cuerpo, Metabolismo y Evolución. Fase 2 completa la **Mente**: World Model neural, Active Inference, Society of Mind con 12 sub-agentes, System 1/2 con meta-cognición, y Global Workspace como espacio de competencia.

**Estado:** 🟡 Pendiente
**Duración estimada:** 4 semanas (6 sub-fases)
**Validación:** 50 escenarios, System 2 se activa cuando debe, sub-agentes compiten en Global Workspace

---

## Lecciones de Fases 0-1 que informan Fase 2

| # | Lección | Cómo afecta Fase 2 |
|---|---|---|
| 1 | World Model usa hash embedding simple | Necesita sentence-transformers reales |
| 2 | Solo 4 sub-agentes (Perceiver, Forecaster, Speaker, Critic) | Faltan 8 para Society of Mind completa |
| 3 | No hay Active Inference | Falta pymdp para bucle basado en energía libre |
| 4 | No hay System 1/2 con meta-cognición | Falta detector de incertidumbre |
| 5 | Bucle es lineal (observar→decidir→actuar) | Debería ser ecología de procesos con Global Workspace |
| 6 | Mutaciones son básicas | Motor Ontogenético debería poder modificar arquitectura (crear/eliminar sub-agentes) |
| 7 | Las leyes verifican acciones pero no hay deliberación profunda | Faltan sub-agentes de razonamiento causal y científico |
| 8 | Los campos cognitivos existen pero los sub-agentes no los usan completamente | Fase 2 debe conectar todos los sub-agentes a campos |
| 9 | La física cognitiva calcula magnitudes pero no afecta decisiones complejas | Fase 2 debe usar física para decidir System 1 vs System 2 |
| 10 | El metabolismo duerme pero no hay consolidación profunda | Fase 2 debe conectar sueño con consolidación de World Model |

---

## Los 12 sub-agentes de Society of Mind

Fase 0 entregó 4. Fase 2 completa los 12:

| # | Sub-agente | Fase | Función |
|---|---|---|---|
| 1 | **Perceiver** | ✅ Fase 0 | Procesa observaciones en representación semántica |
| 2 | **Forecaster** | ✅ Fase 0 | Usa World Model para predecir |
| 3 | **Speaker** | ✅ Fase 0 | Genera pensamientos en lenguaje |
| 4 | **Critic** | ✅ Fase 0 | Evalúa coherencia |
| 5 | **Memorialist** | 🟡 Fase 2 | Recupera memoria relevante de los 11 tipos |
| 6 | **Learner** | 🟡 Fase 2 | Genera mutaciones de aprendizaje |
| 7 | **Curator** | 🟡 Fase 2 | Mantiene memoria limpia (olvido activo, consolidación) |
| 8 | **Creativity** | 🟡 Fase 2 | Genera hipótesis, combinaciones, analogías |
| 9 | **Causal Engine** | 🟡 Fase 2 | Razona sobre causa-efecto |
| 10 | **Emotional Motor** | 🟡 Fase 2 | Genera marcadores emocionales funcionales |
| 11 | **Ethical Motor** | 🟡 Fase 2 | Evalúa acciones contra 7 valores |
| 12 | **Scientific Engine** | 🟡 Fase 2 | Genera teorías y diseña experimentos |

---

## Las 6 sub-fases

### Sub-fase 2.1 — World Model neural (días 1-3)

**Objetivo:** reemplazar hash embedding con sentence-transformers reales.

**Implementación:**
- `zoe/core/world_model.py` — evolucionar a `WorldModelV2`
  - Encoder: sentence-transformers (`all-MiniLM-L6-v2`) para embeddings reales
  - Predictor: red feedforward simple que predice próximo estado latente
  - Sorpresa: distancia coseno en espacio latente real (no hash)
  - Aprendizaje online: cada observación actualiza el predictor
- Fallback: si sentence-transformers no disponible, usar hash embedding de Fase 0
- Integración con CognitivePhysics: `uncertainty_pressure` se alimenta de sorpresa real

**Tests:**
- `test_world_model_v2.py`: embeddings reales, predicción, sorpresa, aprendizaje online
- Test de integración: WorldModelV2 funciona en CognitiveLoopV05

**Criterio de éxito:** World Model con embeddings reales distingue mejor que hash.

### Sub-fase 2.2 — Active Inference con pymdp (días 4-7)

**Objetivo:** bucle basado en Free Energy Principle (Friston).

**Implementación:**
- `zoe/core/active_inference.py` — `ActiveInferenceLoop`
  - Usa `pymdp` si disponible (fallback a heurística si no)
  - States discretizados para viabilidad
  - Minimiza energía libre variacional: F = E_q[log q(s|o) - log p(o,s)]
  - Acciones: sub-conjunto de actuadores disponibles
  - Integración con CognitiveTensions (curiosidad = reducción de incertidumbre esperada)
- Conectado con CognitivePhysics: `uncertainty_pressure` se reduce con inferencia activa

**Tests:**
- `test_active_inference.py`: minimización de energía libre, selección de acciones
- Test de integración: Active Inference afecta decisiones del bucle

**Criterio de éxito:** el organismo elige acciones que reducen sorpresa esperada.

### Sub-fase 2.3 — 8 sub-agentes nuevos (días 8-13)

**Objetivo:** completar Society of Mind con 8 sub-agentes nuevos.

**Implementación:**
Cada sub-agente sigue la interfaz de Fase 0 (`generate_thought(context) -> str`) y escribe en CognitiveFields:

- `zoe/core/subagents/memorialist.py` — recupera memoria relevante de los 11 tipos según contexto
- `zoe/core/subagents/learner.py` — genera mutaciones de aprendizaje (propone al OntogeneticMotor)
- `zoe/core/subagents/curator.py` — mantiene memoria limpia (olvido activo, consolidación en sueño)
- `zoe/core/subagents/creativity.py` — genera hipótesis, combinaciones, analogías
- `zoe/core/subagents/causal_engine.py` — razona sobre causa-efecto (usa CausalMemory)
- `zoe/core/subagents/emotional_motor.py` — genera marcadores emocionales (usa EmotionalMemory)
- `zoe/core/subagents/ethical_motor.py` — evalúa acciones contra 7 valores (conecta con Identity Vault)
- `zoe/core/subagents/scientific_engine.py` — genera teorías y diseña experimentos (usa CounterfactualMemory)

Cada sub-agente:
- Lee de CognitiveFields para contexto
- Escribe en CognitiveFields sus contribuciones
- Usa LivingMemory para almacenar/recuperar
- Respeta las 6 leyes cognitivas

**Tests:**
- `test_subagents_phase2.py`: cada sub-agente genera pensamientos coherentes
- Test de integración: los 12 sub-agentes cooperan en el bucle

**Criterio de éxito:** los 12 sub-agentes generan pensamientos distintos y coherentes.

### Sub-fase 2.4 — System 1 / System 2 con meta-cognición (días 14-16)

**Objetivo:** meta-cognición que decide cuándo pasar de respuesta rápida (System 1) a deliberación profunda (System 2).

**Implementación:**
- `zoe/core/meta_cognition.py` — `MetaCognition`
  - `evaluate_confidence(response) -> float` — evalúa confianza de System 1
  - `should_deliberate(confidence, stakes) -> bool` — decide si activar System 2
  - `deliberate(context) -> str` — activa bucle completo con World Model + Society of Mind
  - Thresholds configurables (ajustados por Motor Ontogenético)
- Integración con CognitivePhysics:
  - `uncertainty_pressure` alta → System 2
  - `creative_potential` alta → System 2 (explorar opciones)
  - `energy_cognitive` baja → System 1 (ahorrar)
- Logging: siempre registrar qué sistema se usó

**Tests:**
- `test_meta_cognition.py`: confianza, should_deliberate, deliberación
- Test de integración: System 2 se activa en escenarios de alta incertidumbre

**Criterio de éxito:** System 2 se activa en >80% de escenarios de alta incertidumbre.

### Sub-fase 2.5 — Global Workspace (días 17-19)

**Objetivo:** reemplazar bucle lineal por ecología de procesos que compiten por acceso al workspace.

**Implementación:**
- `zoe/core/global_workspace.py` — `GlobalWorkspace`
  - Espacio compartido de capacidad limitada (como conciencia de Baars)
  - Sub-agentes "compiten" por acceso al workspace
  - El ganador hace "broadcast" a todos los demás
  - Selección por: relevancia, urgencia, novedad, energía disponible
- Modificación de `CognitiveLoopV05`:
  - En vez de secuencia lineal (observar→predecir→decidir→actuar), los sub-agentes proponen acciones al workspace
  - El workspace selecciona la acción ganadora
  - Broadcast a todos los sub-agentes para actualización de estado

**Tests:**
- `test_global_workspace.py`: competición, selección, broadcast
- Test de integración: el bucle usa Global Workspace en vez de secuencia lineal

**Criterio de éxito:** múltiples sub-agentes proponen acciones; el workspace selecciona la mejor.

### Sub-fase 2.6 — Integración + demo + validación (días 20-21)

**Objetivo:** integrar todo + demo + 50 escenarios de validación.

**Implementación:**
- Extender `CognitiveLoopV05` con World Model V2, Active Inference, 12 sub-agentes, System 1/2, Global Workspace
- `zoe/examples/demo_phase2.py` — demo de organismo Fase 2 completo
- Tests de integración: 50 escenarios, System 2 se activa cuando debe, sub-agentes compiten

**Criterio de éxito GO/NO-GO:**
- ✅ GO: 50 escenarios, System 2 activa en >80% de alta incertidumbre, 12 sub-agentes compiten en workspace, diversidad >0.5
- ❌ NO-GO: cualquiera falla → revisar

---

## Métricas de validación Fase 2

| Métrica | Objetivo |
|---|---|
| Escenarios sin crash | ≥50 |
| System 2 se activa en alta incertidumbre | ≥80% |
| Sub-agentes proponen acciones distintas | ≥8/12 |
| Global Workspace selecciona ganador | 100% |
| World Model V2 mejor que V1 | Sorpresa más precisa |
| Active Inference reduce sorpresa esperada | Sí |
| Tests pasan | 100% previos + nuevos |
| Demo Fase 2 funcional | Sí |
| Diversidad de pensamientos | ≥0.5 |

---

## Lo que NO se construye en Fase 2 (queda para fases posteriores)

- ❌ 11 tipos de memoria con backing stores persistentes (Fase 3)
- ❌ Emociones funcionales completas (Fase 3)
- ❌ Motor Ontogenético avanzado (modificar arquitectura, Fase 3-4)
- ❌ Federación distribuida con quorum (Fase 4)
- ❌ Deploy en VPS CEO con caso de uso real (Fase 4)

---

## Riesgos de Fase 2

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| sentence-transformers no disponible | Media | Medio | Fallback a hash embedding de Fase 0 |
| pymdp no disponible o complejo | Alta | Medio | Implementar Active Inference simplificado sin pymdp |
| 12 sub-agentes colapsan a pocos dominantes | Media | Medio | Global Workspace con regularización de entropía |
| Meta-cognición no calibra bien | Media | Medio | Logs detallados, ajuste continuo |
| Global Workspace no escala | Baja | Medio | Limitar número de propuestas por iteración |

---

*Fase 2 pendiente. Plan refinado con lecciones de Fases 0-1.*
