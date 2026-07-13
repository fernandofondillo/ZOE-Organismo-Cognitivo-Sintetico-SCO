# FASE 5 — Adaptive Cognitive Depth (ACD) + Streaming Parcial

> **Objetivo**: ZOE v1 responde a "hola" en <1s y a "analiza las causas de la inflación" en 15-30s. Sin desconstruir nada existente.

## Problema detectado (observación empírica del CEO)

Actualmente ZOE ejecuta SIEMPRE el bucle cognitivo completo, sin distinguir:

- "hola" → 8-15s (6-10 LLM calls)
- "¿qué tal?" → 8-15s (idem)
- "analiza las causas..." → 25-45s (idem)

El `CognitiveLoopV4` no tiene un clasificador de profundidad. El Perceiver, los 12 sub-agentes, el Critic y el Memorialist se ejecutan en cada tick.

**Consecuencia**: el organismo "se pierde en sus pensamientos" para interacciones triviales.

## Hipótesis científica

Un cerebro biológico usa **dos sistemas** (Kahneman, 2011):

- **Sistema 1**: rápido, automático, barato. Responde "hola" sin deliberar.
- **Sistema 2**: lento, deliberativo, caro. Razona sobre preguntas complejas.

La **meta-cognición de V3** ya decide system1 vs system2 PERO **después** de ejecutar los 12 sub-agentes. El coste ocurre antes de la decisión.

**Solución**: pre-clasificar la profundidad **antes** de entrar al bucle, usando una heurística local sin LLM.

## Diseño ACD (Adaptive Cognitive Depth)

### 4 niveles cognitivos

| Nivel | Nombre | Input típico | Sub-agentes activos | Latencia objetivo |
|-------|--------|--------------|---------------------|-------------------|
| **L0** | Reflex | "hola", "ok", "gracias", "vale", "adiós" | Solo Speaker (con cache) | <1s |
| **L1** | Fast | Pregunta factual, recordar dato, confirmación | Perceiver + Memorialist + Speaker | 2-4s |
| **L2** | Standard | Conversación normal, opinión, descripción | Fase 0 completa + algunos Fase 2 | 6-10s |
| **L3** | Deep | Análisis causal, dilema ético, creatividad, investigación | Los 12 sub-agentes + meta-cog + world model V2 | 15-30s |

### DepthClassifier (zoe/core/depth_classifier.py)

**Sin LLM.** Usa heurísticas combinadas:

1. **Longitud** del input (chars/tokens)
2. **Keywords de profundidad**:
   - L0: saludos, despedidas, acks (`hola`, `ok`, `gracias`, `vale`, `adiós`, `bye`, `k`, `sí`, `no`)
   - L3: `analiza`, `causas`, `consecuencias`, `por qué`, `compara`, `dilema`, `ético`, `ética`, `diseña`, `propón`, `investiga`, `critica`, `evalúa`, `sintetiza`
3. **Estructura sintáctica**: pregunta compuesta, condicional (`si...entonces`), múltiples oraciones
4. **Puntuación**: presencia de `?` múltiples,`;` (complejidad), listas numeradas
5. **Score agregado** → bucket a L0/L1/L2/L3

**Tiempo objetivo del clasificador**: <50ms (regex + dict lookups).

### Modificación del loop

El `CognitiveLoopV4` actual ejecuta el mismo pipeline siempre. La **Fase 5 añade un `pre_tick`** que:

1. Si hay input de usuario fresco (UserInputSense), clasificar profundidad.
2. Almacenar nivel en `state.acd_level` (nuevo campo).
3. El `_tick()` de V4 consulta `state.acd_level` y **ramifica**:
   - L0: solo `Speaker.respond()` + cache lookup
   - L1: Perceiver → Memorialist.search → Speaker
   - L2: pipeline completo Fase 0 + 4 sub-agentes principales
   - L3: pipeline completo Fase 3 (los 12)

**Compatibilidad hacia atrás**: si no hay `DepthClassifier`, comportamiento = V3 (sin ACD).

### Cognitive Cache (idempotencia)

Cache LRU en memoria (no en disco) con clave = hash del input normalizado.

- Tamaño: 100 entries por defecto
- TTL: 5 minutos
- Hit → respuesta cacheada en <50ms
- Miss → pipeline normal

### Streaming parcial

El `Speaker` actual espera al LLM completo antes de emitir. La Fase 5 añade `Speaker.generate_streaming()` que:

1. Llama al LLM con `stream=True`
2. Yields tokens incrementalmente vía `async for`
3. El CLI/Dashboard los muestra en tiempo real

Compatible con backend mock (yield de palabras) y ZAI/Ollama (yield real de tokens).

### Marcado en TrajectoryChain

Cada respuesta firmada incluye metadata `acd_level` para auditoría:

```python
mutation = ontogenetic_motor.propose_mutation(
    type="respond_to_user",
    target="speaker",
    payload={"content": response[:200], "acd_level": level},
    justification=f"ACD level {level} response",
    provenance=f"acd:{level}",
    cost=LEVEL_COSTS[level],  # L0=0.05, L1=0.1, L2=0.3, L3=0.6
    confidence=LEVEL_CONFIDENCE[level],
)
```

**Costes por nivel** (4ta ley — coste registrado):
- L0: 0.05 (casi gratis)
- L1: 0.10
- L2: 0.30
- L3: 0.60

## Plan de implementación

### Step 1: `zoe/core/depth_classifier.py`
- Clase `DepthClassifier` con `classify(input: str) -> CognitiveLevel`
- Enum `CognitiveLevel { L0_REFLEX, L1_FAST, L2_STANDARD, L3_DEEP }`
- Heurísticas: keywords + longitud + estructura + score
- Método `normalize(text)` para cache key

### Step 2: `zoe/core/cognitive_cache.py`
- Clase `CognitiveCache` LRU con TTL
- `get(key) -> Optional[str]`
- `put(key, value, level)`
- `stats()` → hit/miss/size

### Step 3: Modificar `CognitiveLoopV4`
- Nuevo parámetro `depth_classifier: Optional[DepthClassifier]`
- Nuevo parámetro `cognitive_cache: Optional[CognitiveCache]`
- `_tick()` comprueba si hay input fresco → clasifica → ramifica
- Métodos:
  - `_tick_l0()` — respuesta refleja
  - `_tick_l1()` — fast path
  - `_tick_l2()` — pipeline estándar (Fase 0)
  - `_tick_l3()` — pipeline completo (Fase 3)
- Si no hay ACD: delega a `super()._tick()` (compatibilidad)

### Step 4: Streaming en `Speaker`
- `async def generate_streaming(prompt, system, ...) -> AsyncIterator[str]`
- Detecta si el LLM soporta `stream=True`
- Yield incremental de tokens
- CLI/Dashboard usan `async for chunk in speaker.generate_streaming(...)`

### Step 5: Integración en `cli_chat.py` y `web_dashboard.py`
- `ZoeChat.send_message_streaming(message) -> AsyncIterator[str]`
- CLI imprime tokens en tiempo real
- Dashboard WebSocket envía chunks al frontend

### Step 6: Marcar nivel en TrajectoryChain
- Tras cada respuesta, registrar mutación con `acd_level` en payload y `provenance`
- Stats incluyen `acd_level_distribution: {L0: n, L1: n, L2: n, L3: n}`
- Tests verifican que la cadena es verificable y contiene el nivel

### Step 7: Tests (`test_phase5_acd.py`)
- `test_depth_classifier_l0`: "hola" → L0
- `test_depth_classifier_l3`: "analiza las causas de la inflación" → L3
- `test_depth_classifier_l1`: "¿cómo te llamas?" → L1
- `test_depth_classifier_l2`: "cuéntame sobre tu día" → L2
- `test_cache_hit_miss`: secuencia de puts/gets
- `test_loop_v4_acd_l0_fast`: medir que L0 < 200ms con mock
- `test_loop_v4_acd_l3_full`: L3 ejecuta 12 sub-agentes
- `test_loop_v4_backward_compat`: sin classifier → comportamiento V3
- `test_streaming_yields_chunks`: mock yields múltiples chunks
- `test_trajectory_marks_acd_level`: mutación incluye `acd_level`
- `test_latency_thresholds`: L0 <1s, L3 >1s (con mock, no LLM real)

### Step 8: Tests de no-regresión
- Ejecutar los 534 tests existentes
- Asegurar que todos siguen pasando
- Verificar que `CognitiveLoopV4` sin ACD sigue siendo 100% compatible

### Step 9: Documentación
- README actualizado con sección ACD
- Anexo B en `ZOE_V1_GUIDE.md` sobre ACD + streaming
- `PHASE_5_RESULTS.md` con métricas de latencia medidas

### Step 10: Commit + push
- Commit único con mensaje descriptivo
- Push a `zoe-v1-sco`
- Verificación final

## Métricas de éxito

| Métrica | Antes (V4) | Objetivo (V5) |
|---------|------------|---------------|
| Latencia L0 (mock) | 1-2s | <200ms |
| Latencia L1 (mock) | 1-2s | <500ms |
| Latencia L2 (mock) | 1-2s | 1-2s |
| Latencia L3 (mock) | 1-2s | 1-2s (mock no LLM) |
| LLM calls para "hola" | 6-10 | 0-1 |
| LLM calls para "analiza..." | 6-10 | 8-12 (justificado) |
| Tests passing | 534 | 545+ |
| Backward compat | - | 100% |

## Riesgos y mitigaciones

1. **Riesgo**: clasificador erróneo manda pregunta compleja a L0
   - **Mitigación**: si score L0 y longitud >100 chars, subir a L1
   - Si score L1 y contiene keywords L3, subir a L3

2. **Riesgo**: cache devuelve respuesta obsoleta
   - **Mitigación**: TTL 5min + invalidación por cambio de sesión

3. **Riesgo**: streaming rompe el CLI actual
   - **Mitigación**: `send_message()` (no streaming) sigue disponible; streaming es opt-in

4. **Riesgo**: tests de no-regresión fallan
   - **Mitigación**: ACD es opt-in, sin classifier V4 se comporta = V3
