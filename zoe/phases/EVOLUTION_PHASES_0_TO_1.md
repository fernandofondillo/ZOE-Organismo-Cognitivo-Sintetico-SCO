# Evolución del proyecto ZOE v1.0 — De bucle cognitivo a organismo completo (Fases 0-1)

> **Documento de trazabilidad.** Registra la evolución técnica del proyecto ZOE desde el primer bucle cognitivo (Fase 0) hasta el organismo con Alma + Cuerpo + Metabolismo + Evolución (Fase 1). Cada fase se documenta con: qué se construyó, qué tests pasan, qué demo se ejecutó, y qué aprendizajes informaron la fase siguiente.

**Fecha:** 8 julio 2026
**Rama:** `zoe-v1-sco`
**Tests totales:** 305/305 pasan
**Estado:** Fase 1 completa, Fase 2 pendiente

---

## Tabla resumen de evolución

| Fase | Componentes añadidos | Tests | Demo checks | Commit |
|---|---|---|---|---|
| 0 | Bucle + State + WorldModel + 4 sub-agentes + 3 sentidos + 4 LLM backends | 63 | 4/4 GO | `d948188` |
| 0.5 | 6 leyes + 12 física + 6 campos + 5 tensiones + memoria viva + intencionalidad + filogenético | +86 = 149 | 6/6 GO | `dced26b` |
| Integración 0+0.5 | Tests de integración + demo integrado | +27 = 176 | 14/14 PASS | `267eef1` |
| 1.1-1.4 | Identity Vault + Trajectory Chain + Ontogenetic Motor + Metabolism + 11 Memory Types | +75 = 251 | — | `dbcd6f7` |
| 1.5-1.6 | Network/Agent senses + 4 actuadores + ActuatorManager + demo + tests integración | +54 = 305 | 16/16 PASS | `a38e201` |

---

## Fase 0 — Bucle cognitivo autónomo

### Qué se construyó

**Núcleo cognitivo mínimo:** un bucle asíncrono que piensa sin input externo.

- `CognitiveLoop` — bucle observar → predecir → evaluar → decidir → actuar
- `InternalState` — homeostasis básica (atención, energía, fatiga, arousal)
- `WorldModel` — predictor del entorno con cálculo de sorpresa
- 4 sub-agentes: `Perceiver`, `Forecaster`, `Speaker`, `Critic`
- 3 sentidos: `ClockSense`, `FilesystemSense`, `UserInputSense`
- 4 backends LLM: `MockPeripheral`, `ZAIPeripheral`, `OllamaPeripheral`, `OpenAICompatiblePeripheral`

### Tests

```
63 passed
```

### Demo

10 pensamientos autónomos sin input externo, diversidad 0.889, con LLM mock. Con LLM real (z-ai/GLM-4): 8 pensamientos, diversidad 0.826, sistema resiliente a fallos de API.

### Aprendizajes que informaron Fase 0.5

1. El bucle funciona pero es **reactivo en su estructura** — solo piensa cuando hay sorpresa o input. Faltaba iniciativa continua.
2. No hay **leyes que rijan** las acciones — cualquier acción puede ejecutarse. Faltaba verificación.
3. La memoria es **pasiva** — almacena pero no piensa. Faltaba memoria viva.
4. No hay **medición interna** — el estado es opaco. Faltaba física cognitiva.
5. No hay **conflicto interno** — el organismo no siente tensiones. Faltaban tensiones cognitivas.

---

## Fase 0.5 — Organismo cognitivo

### Qué se construyó

**7 innovaciones del CEO integradas** sin desconstruir Fase 0:

1. **6 Leyes Cognitivas** (`cognitive_laws.py`) — cada acción pasa por `verify_action()`. Las 6 leyes: utilidad, identidad, proveniencia, coste, confianza, modularidad.

2. **12 Magnitudes de Física Cognitiva** (`cognitive_physics.py`) — energía cognitiva, masa conceptual, temperatura cognitiva, presión de incertidumbre, potencial creativo, entropía semántica, gravedad de objetivos, inercia de identidad, resonancia conceptual, fricción cognitiva, elasticidad de memoria, densidad causal.

3. **6 Campos Cognitivos** (`cognitive_fields.py`) — atención, emocional, social, creativo, causal, ético. Los sub-agentes modifican campos compartidos en vez de mandarse mensajes.

4. **5 Tensiones Cognitivas Permanentes** (`cognitive_tensions.py`) — curiosidad vs eficiencia, identidad vs adaptación, descanso vs productividad, honestidad vs empatía, especialización vs generalización.

5. **Memoria Viva** (`living_memory.py`) — reorganiza, olvida, fusiona, resume, generaliza, detecta contradicciones, genera hipótesis.

6. **Motor de Intencionalidad** (`intentionality_motor.py`) — genera continuamente "deseos cognitivos" basados en tensiones, sorpresa, energía, memoria.

7. **Motor Filogenético** (`phylogenetic_motor.py`) — evolución de especie: publicar mejoras, probar en otras ZOEs, incorporar si validan.

### Tests

```
149 passed (63 Fase 0 + 86 Fase 0.5)
```

### Demo

8 pensamientos, diversidad 0.893, 0 violaciones de leyes, 12 magnitudes calculadas, 5 tensiones evolucionando, memoria viva ejecutando operaciones, intencionalidad generando intenciones.

### Aprendizajes que informaron Fase 1

1. Las leyes verifican acciones pero **no hay identidad persistente** — la 2da ley dice "preservar identidad" pero no hay Vault que la defina criptográficamente.
2. El estado interno es básico — **no hay ciclos dormir/despertar**. Faltaba metabolismo real.
3. La memoria viva funciona pero **solo tiene un tipo genérico** — faltaban los 11 tipos especializados.
4. Las mutaciones no se firman — **no hay trayectoria criptográfica**. Faltaba Trajectory Chain.
5. Los sentidos son limitados — **faltan red y otros agentes**. Faltaban sentidos completos.
6. No hay actuadores — **el organismo no puede actuar sobre el entorno**. Faltaban actuadores.

---

## Integración Fase 0 + 0.5

### Qué se construyó

27 tests de integración que validan que Fase 0 y Fase 0.5 funcionan como **un solo organismo**, no como componentes separados.

- Tests de funcionamiento conjunto
- Tests de no-interferencia entre componentes
- Tests de compatibilidad con Fase 0 pura (regression)
- Tests de filogenético entre instancias
- Tests de estabilidad en ejecución larga

### Tests

```
176 passed (149 previos + 27 integración)
```

### Demo integrado

14/14 checks de integridad PASS. El organismo Fase 0 + 0.5 funciona como unidad coherente.

---

## Fase 1 — Alma + Cuerpo + Metabolismo + Evolución

### Adaptaciones al plan original

Antes de implementar Fase 1, se reflexionó sobre qué adaptar tras Fase 0 + 0.5. **7 adaptaciones:**

1. Metabolismo como extensión de InternalState (no creación desde cero)
2. 11 tipos de memoria como especialización de LivingMemory (no creación nueva)
3. Identity Vault conectado con 2da ley (no standalone)
4. Trajectory Chain firma mutaciones del Motor Ontogenético (no solo log)
5. Sentidos con interfaz común validados por 6ta ley
6. Actuadores con `verify_action()` en cada acción
7. Sentidos y actuadores escriben en CognitiveFields

### Sub-fase 1.1 — Identity Vault + 2da Ley

**Qué se construyó:**

`IdentityVault` con hash SHA-256 de 9 vectores + 7 valores + propósito. Inmutable. Verificable. Portable. Implementa la 2da ley: rechaza mutaciones que tocan `vectors`, `values`, o `purpose`.

18 tests.

### Sub-fase 1.2 — Trajectory Chain + Ontogenetic Motor

**Qué se construyó:**

`TrajectoryChain` — cadena criptográfica de mutaciones con `prev_hash`, firma, y verificación de integridad. Rollback sin eliminar (añade mutación de rollback).

`OntogeneticMotor` — conecta Identity Vault + Trajectory Chain + CognitiveLaws. Propone, aplica (verificando leyes + identidad), y revierte mutaciones. 8 tipos de mutación.

22 tests.

### Sub-fase 1.3 — Metabolismo

**Qué se construyó:**

`Metabolism` (extiende InternalState) con 4 estados: AWAKE → DROWSY → SLEEPING → WAKING. Transiciones automáticas según fatiga/energía. Consolidación durante sueño. Presupuesto de cómputo. `stimulate()` puede despertar.

17 tests.

### Sub-fase 1.4 — 11 Memory Types

**Qué se construyó:**

11 tipos especializados, todos heredando de `MemoryEntry`:
- EpisodicEntry, SemanticEntry, ProceduralEntry, CausalEntry
- EmotionalEntry, CorporealEntry, SocialEntry, ProspectiveEntry
- CounterfactualEntry, EvolutionaryEntry, CulturalEntry

`create_entry()` factory. `MemoryTypeStats` estadísticas.

18 tests.

### Sub-fase 1.5 — Sentidos y actuadores completos

**Qué se construyó:**

2 sentidos nuevos:
- `NetworkSense` — monitorea endpoints HTTP, detecta caídas/recuperaciones
- `AgentSense` — detecta y modela otros agentes/ZOEs

4 actuadores nuevos:
- `LanguageActuator` — genera output vía LLM
- `CodeActuator` — ejecuta código en sandbox (Python/Bash, timeout, whitelist)
- `ToolActuator` — invoca tools registradas (sync y async)
- `FederationActuator` — publica/mejora/incorpora/envía mensajes

`ActuatorManager` — gestiona actuadores, verifica leyes antes de ejecutar.

38 tests.

### Sub-fase 1.6 — Integración + demo + validación

**Qué se construyó:**

Demo Fase 1 completo que integra TODOS los componentes de Fase 0 + 0.5 + 1. 16 tests de integración.

### Tests finales Fase 1

```
305 passed (176 previos + 75 Fase 1.1-1.4 + 38 Fase 1.5 + 16 Fase 1.6)
```

### Demo Fase 1

16/16 checks PASS:

```
✅ fase0_bucle_funciona
✅ fase0_genera_pensamientos
✅ fase05_leyes_activas
✅ fase05_fisica_calculada
✅ fase05_tensiones_presentes
✅ fase05_memoria_viva_funcional
✅ fase05_intencionalidad_funcional
✅ fase1_identity_vault_creado
✅ fase1_trajectory_chain_funcional
✅ fase1_mutaciones_aplicadas
✅ fase1_metabolismo_funcional
✅ fase1_11_memory_types
✅ fase1_actuadores_disponibles
✅ fase1_sentidos_completos
✅ diversidad_aceptable
✅ sin_crashes
```

### Aprendizajes que informarán Fase 2

1. El World Model actual usa hash embedding simple — **necesita sentence-transformers reales** para calidad.
2. Solo hay 4 sub-agentes — **faltan 8 más** para completar Society of Mind (Creativity, Causal Engine, Emotional Motor, Ethical Motor, Scientific Engine, Memorialist, Learner, Curator).
3. No hay Active Inference — **falta pymdp** para bucle basado en energía libre.
4. No hay System 1/System 2 con meta-cognición — **falta detector de incertidumbre** que decida cuándo deliberar.
5. El bucle actual es lineal (observar → decidir → actuar) — **debería ser ecología de procesos** que compiten por Global Workspace.
6. Las mutaciones del Motor Ontogenético son básicas (add_memory, strengthen_belief) — **deberían poder modificar arquitectura** (crear/eliminar sub-agentes).

---

## Estadísticas de código

| Componente | Líneas (aprox) | Tests |
|---|---|---|
| core/ (Fase 0) | 1.700 | 63 |
| core/ (Fase 0.5) | 2.000 | 86 |
| alma/ (Fase 1) | 800 | 40 |
| metabolism/ (Fase 1) | 200 | 17 |
| memory/ (Fase 1) | 400 | 18 |
| peripherals/ (Fase 1.5) | 700 | 49 |
| tests/ integración | 1.000 | 43 |
| examples/ | 1.500 | — |
| **Total** | **~8.300** | **305** |

---

*Documento de trazabilidad. Actualizado tras Fase 1 completa.*
