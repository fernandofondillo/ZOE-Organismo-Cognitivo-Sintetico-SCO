# Fase 0 — Demo de bucle cognitivo

> **Objetivo:** validar que el bucle cognitivo continuo genera pensamientos autónomos significativos. Si esta fase no convence, abortamos y ejecutamos Plan B. Coste de abortar: 2 semanas.

**Estado:** 🟡 En construcción
**Duración estimada:** 2 semanas
**Validación go/no-go:** 20 pensamientos autónomos coherentes en 24h sin input

---

## Sub-fases

ZOE v1.0 sigue metodología científica por sub-fases. Cada sub-fase tiene:
- Objetivo concreto
- Implementación real (no pseudocódigo)
- Tests que deben pasar
- Commit a la rama `zoe-v1-sco`

### Sub-fase 0.1 — Esqueleto del bucle cognitivo (días 1-2)

**Objetivo:** implementar `CognitiveLoop` con bucle asíncrono observar-predecir-evaluar-decidir-actuar.

**Implementación:**
- `zoe/core/cognitive_loop.py` — clase con `async def run()` que ejecuta el bucle cada N segundos
- `zoe/core/state.py` — estado interno mínimo (atención, energía, arousal)
- `zoe/peripherals/senses.py` — sentido de reloj interno (tiempo transcurrido)

**Tests:**
- `tests/test_cognitive_loop.py` — el bucle ejecuta 5 iteraciones sin input y registra cada una
- `tests/test_state.py` — estado interno se actualiza correctamente

**Criterio de éxito:** el bucle corre 60 segundos sin crash, registra 5+ iteraciones.

### Sub-fase 0.2 — LLM periférico (días 3-4)

**Objetivo:** implementar abstracción de LLM periférico con múltiples backends.

**Implementación:**
- `zoe/peripherals/llm.py` — clase abstracta `LLMPeripheral` con implementaciones:
  - `OllamaPeripheral` (producción, local)
  - `OpenAICompatiblePeripheral` (cualquier API OpenAI-compatible)
  - `ZAIPeripheral` (uso en desarrollo con z-ai CLI)
  - `MockPeripheral` (tests determinísticos)

**Tests:**
- `tests/test_llm_peripheral.py` — cada backend responde a un prompt simple
- MockPeripheral genera respuestas determinísticas para tests

**Criterio de éxito:** al menos un backend real funciona (ZAI en este entorno), Mock pasa tests.

### Sub-fase 0.3 — World Model mínimo (días 5-6)

**Objetivo:** implementar predictor del entorno que genera "sorpresa" cuando la realidad difiere de la predicción.

**Implementación:**
- `zoe/core/world_model.py` — predice próximo input basado en historial
- En Fase 0: predictor simple basado en embeddings (no neural network compleja)
- Calcula `surprise = distance(predicted, actual)`

**Tests:**
- `tests/test_world_model.py` — predice correctamente secuencia repetitiva
- `tests/test_world_model.py` — genera sorpresa alta cuando input es novedoso

**Criterio de éxito:** World Model distingue input predecible de novedoso.

### Sub-fase 0.4 — Sub-agentes Society of Mind (días 7-9)

**Objetivo:** implementar 4 sub-agentes mínimos.

**Implementación:**
- `zoe/core/subagents/perceiver.py` — procesa inputs de sentidos
- `zoe/core/subagents/forecaster.py` — usa World Model para predecir
- `zoe/core/subagents/speaker.py` — genera pensamientos en lenguaje (usa LLM periférico)
- `zoe/core/subagents/critic.py` — evalúa coherencia de pensamientos

**Tests:**
- `tests/test_subagents.py` — cada sub-agente procesa input correctamente
- `tests/test_subagents.py` — Critic rechaza pensamientos incoherentes

**Criterio de éxito:** los 4 sub-agentes cooperan en una iteración del bucle.

### Sub-fase 0.5 — Demo de pensamiento autónomo (días 10-12)

**Objetivo:** demostración end-to-end de 20 pensamientos autónomos sin input.

**Implementación:**
- `zoe/examples/demo_phase0.py` — script que arranca ZOE sin input y genera 20 pensamientos
- Cada pensamiento se registra con timestamp, sorpresa asociada, justificación

**Tests:**
- `tests/test_phase0_demo.py` — el demo genera 20 pensamientos en menos de 5 minutos
- Los pensamientos son diversos (no repetitivos)
- Los pensamientos son coherentes (Critic los aprueba)

**Criterio de éxito GO/NO-GO:**
- ✅ GO: 20 pensamientos autónomos, ≥80% aprobados por Critic, ≥70% diversos
- ❌ NO-GO: menos de 20, o <50% aprobados, o <50% diversos → ejecutar Plan B

### Sub-fase 0.6 — Documentación y decisión (días 13-14)

**Objetivo:** documentar resultados y decidir go/no-go para Fase 1.

**Entregables:**
- `phases/PHASE_0_RESULTS.md` — resultados detallados del demo
- `phases/PHASE_0_DECISION.md` — decisión go/no-go con justificación
- Si GO: crear `phases/PHASE_1_PLAN.md`
- Si NO-GO: documentar lecciones y ejecutar Plan B

**Criterio de éxito:** decisión documentada con evidencia.

---

## Métricas de validación Fase 0

| Métrica | Objetivo | Cómo se mide |
|---|---|---|
| Pensamientos autónomos generados | ≥20 | Conteo en demo |
| Pensamientos aprobados por Critic | ≥80% | Log de Critic |
| Diversidad de pensamientos | ≥70% | Similitud coseno entre embeddings |
| Estabilidad del bucle | 60+ min sin crash | Uptime del demo |
| Latencia por pensamiento | <30s | Timestamps |
| Sin input externo | 100% | Sin inputs durante demo |

---

## Riesgos de Fase 0

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| LLM periférico no disponible en entorno | Media | ZAIPeripheral como fallback |
| Bucle consume demasiada memoria | Baja | State mínimo en Fase 0 |
| Pensamientos triviales o repetitivos | Alta | Critic + métrica de diversidad |
| World Model no genera sorpresa útil | Media | Predictor simple basado en embeddings |

---

## Plan B (si Fase 0 es NO-GO)

Si el demo no genera 20 pensamientos autónomos significativos:

1. **Análisis de causa raíz:** ¿LLM periférico débil? ¿World Model inútil? ¿Bucle mal diseñado?
2. **Iteración 1:** ajustar prompts del Speaker, ajustar thresholds del Critic
3. **Iteración 2:** si sigue fallando, simplificar bucle (menos sub-agentes)
4. **NO-GO definitivo:** si tras 2 iteraciones no hay mejora, ejecutar Plan B del doc 14 (Hermes + LLM local + Obsidian)

**Coste de abortar:** 2 semanas. Asumible.

---

*Fase 0 en construcción. Sub-fase 0.1 iniciada.*
