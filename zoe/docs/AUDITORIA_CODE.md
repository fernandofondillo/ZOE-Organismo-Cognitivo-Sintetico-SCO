# AUDITORIA DE CODIGO PYTHON — PROYECTO ZOE v1.8.0

**Auditor:** ZOE_AUDITOR_CODE  
**Fecha:** 2025-01-28  
**Version auditada:** 1.8.0 (Sprint 5)  
**Repositorio:** `/mnt/agents/output/zoe_repo`  
**Archivos Python analizados:** 166  

---

## 1. METRICAS GENERALES DEL CODIGO

| Metrica | Valor |
|---------|-------|
| Archivos Python (.py) | 166 |
| Archivos fuente (excl. tests) | 105 |
| Archivos de test | 61 |
| Lineas totales | 53,541 |
| Lineas de codigo (excl. comentarios/blancos) | 41,801 |
| Clases | 376 |
| Funciones/Metodos | 2,742 |
| Declaraciones de import | 1,838 |
| Ratio test/codigo | 57.8% |
| Entry points (`__main__`) | 14 |
| Versiones del cognitive loop | 5 (v0, v05, v3, v4, v5) |

### Distribucion por directorio

| Directorio | Archivos | Descripcion |
|------------|----------|-------------|
| `zoe/tests/` | 61 | Tests (unitarios, integracion, sprints) |
| `zoe/core/` | 39 | Nucleo cognitivo (loops, estado, leyes, fisica) |
| `zoe/peripherals/` | 11 | LLM, voz, multimodal, model_bus, actuadores |
| `zoe/alma/` | 5 | Identidad, ontogenia, trayectoria |
| `zoe/capsules/` | 5 | Loader, registry, schema, scaffold |
| `zoe/memory/` | 4 | Sistema de memoria (SQLite, 11 tipos) |
| `zoe/metabolism/` | 2 | Metabolismo (ciclos suenio/despertar) |
| `zoe/marketplace/` | 2 | Marketplace de capsulas |
| `zoe/use_cases/` | 2 | Ejecucion de casos de uso |

### Archivos mas grandes (TOP 10)

| Archivo | Lineas | Funcs | Clases | Nota |
|---------|--------|-------|--------|------|
| `zoe/web_dashboard.py` | 3,006 | 91 | 1 | Monolito web, CC excesiva |
| `zoe/cli_chat.py` | 1,066 | 19 | 1 | CLI principal |
| `zoe/core/seed_mode.py` | 877 | 18 | 6 | Seed mode (Fase 7E) |
| `zoe/peripherals/voice_first.py` | 798 | 32 | 6 | Modo voz-first |
| `zoe/core/embodiment_composer.py` | 773 | 20 | 6 | Composer (Fase 7D) |
| `zoe/core/cognitive_loop_v5.py` | 686 | 12 | 1 | Loop principal (v5) |
| `zoe/core/cognitive_optimization.py` | 686 | 19 | 8 | Optimizacion cognitiva |
| `zoe/peripherals/llm.py` | 661 | 32 | 6 | Perifericos LLM |
| `zoe/peripherals/multimodal.py` | 637 | 26 | 4 | Multimodal |
| `zoe/core/cognitive_loop_v05.py` | 598 | 16 | 1 | Loop v0.5 |

---

## 2. HALLAZGOS POR SEVERIDAD

### 2.1 CRITICO (riesgo de fallo, seguridad, corrupcion de datos)

| # | Hallazgo | Archivos | Severidad |
|---|----------|----------|-----------|
| C1 | **34 bloques `except: pass` vacios** que tragan excepciones silenciosamente | `web_dashboard.py`(3), `cli_chat.py`(3), `cognitive_loop_v5.py`(5), `embodiment_composer.py`(2), `federation.py`(1), `model_downloader.py`(2), `model_profile_router.py`(1), `zoe_packager.py`(2), `zoe_runtime.py`(3), `enhanced_pattern_speaker.py`(3), `llm.py`(2), `voice_first.py`(1), `zoe_setup.py`(3), `test_phase7g_hardware_endpoints.py`(1) | CRITICO |
| C2 | **Uso de MD5 para hashing** de claims en federacion epistemica (hash debil, no cryptografico) | `epistemic_federation.py`, `world_model_v2.py`, `test_phase6a_epistemic.py`, `test_phase6b_marketplace.py` | CRITICO |
| C3 | **`subprocess.exec()` sin sanitizacion** de paths en actuadores | `actuators.py`, `multimodal.py`, `voice_first.py` | CRITICO |
| C4 | **19 `bare except:`** que capturan KeyboardInterrupt, SystemExit, etc. | 9 archivos | CRITICO |
| C5 | **Herencia lineal de 5 niveles** en CognitiveLoop (V0 -> V05 -> V3 -> V4 -> V5) con acoplamiento fuerte | `zoe/core/cognitive_loop*.py` | CRITICO |
| C6 | **CognitiveLoopV5 tiene ~300 lineas de codigo duplicado** de metodos `_observe`, `_predict`, `_evaluate`, `_act`, `run`, `stop`, `get_stats` heredados pero no reutilizados correctamente | `cognitive_loop*.py` | CRITICO |
| C7 | **web_dashboard.py (3,006 lineas)** con 91 funciones en 1 clase — monolito inmantenible, CC media extremadamente alta | `web_dashboard.py` | CRITICO |

### 2.2 ALTO (malas practicas, deuda tecnica significativa)

| # | Hallazgo | Archivos | Severidad |
|---|----------|----------|-----------|
| A1 | **134 de 166 archivos (80.7%) tienen imports no usados** — deuda de mantenimiento masiva | 134 archivos | ALTO |
| A2 | **61.7% de funciones SIN type hints** (1,692 de 2,742) | Todos | ALTO |
| A3 | **30.2% de funciones SIN docstring** (828 de 2,742) | Todos | ALTO |
| A4 | **38.6% de clases SIN docstring** (145 de 376) | Todos | ALTO |
| A5 | **34 funciones con complejidad ciclomatica >= 15** (muy alta) — dificil testear y mantener | Ver tabla abajo | ALTO |
| A6 | **52 funciones con CC >= 10** (alta) | Ver tabla abajo | ALTO |
| A7 | **CognitiveLoopV5.process_user_input_acd (CC=34)** — funcion monolitica que hace de todo | `cognitive_loop_v5.py:134` | ALTO |
| A8 | **CapsuleManager._inject (CC=63)** — la funcion mas compleja del sistema | `capsule_manager.py` | ALTO |
| A9 | **Falta de interfaz comun** entre versiones del loop — cada version redefine metodos basicos | `cognitive_loop*.py` | ALTO |
| A10 | **SeedMode.germinate (CC=31)** — orquestacion monolitica de 11 pasos secuenciales | `seed_mode.py:531` | ALTO |
| A11 | **CognitivePhysics.update (CC=23)** — 12 magnitudes calculadas en una sola funcion | `cognitive_physics.py:64` | ALTO |
| A12 | **Imports de `random` dentro de metodos** (no a nivel de modulo) | `cognitive_loop.py:249`, `cognitive_loop_v05.py:441` | ALTO |
| A13 | **API keys hardcoded en ejemplos/docstrings** (aunque sean placeholders) | `model_bus.py`, `zoe_setup.py` | ALTO |
| A14 | **ZOE v0.5 usa `CognitiveLoopV05` que inicializa TODOS los componentes por defecto** sin lazy loading | `cognitive_loop_v05.py:74-80` | ALTO |

### 2.3 MEDIO (mejoras recomendadas, inconsistencias)

| # | Hallazgo | Archivos | Severidad |
|---|----------|----------|-----------|
| M1 | **6 TODOs pendientes** en 4 archivos | `scaffold.py`(3), `cognitive_laws.py`(1), `embodiment_composer.py`(1), `elder_care_knowledge/validators.py`(1) | MEDIO |
| M2 | **16 archivos con marcas experimental/legacy/stub** | `web_dashboard.py`(17), `cognitive_loop_v5.py`(6), etc. | MEDIO |
| M3 | **Funcion `score()` en ModelBus._select_acd_aware definida dentro de otra funcion** (closure innecesaria, no testeable) | `model_bus.py:241` | MEDIO |
| M4 | **Duplicacion de Jaccard** — `_jaccard()` definida en LivingMemory, CognitivePhysics, y posiblemente mas | 3+ archivos | MEDIO |
| M5 | **CognitiveLoopV3 hereda de V05 que hereda de V0, pero V05 no usa `super()`** para llamar a `_tick` de V0 | `cognitive_loop_v05.py` | MEDIO |
| M6 | **LivingMemory.search() usa Jaccard simple en lugar de embeddings** — busqueda por texto plano muy basica | `living_memory.py:125` | MEDIO |
| M7 | **Metabolism usa composicion (no herencia) de InternalState** pero expone todas sus propiedades manualmente | `metabolism.py:54-101` | MEDIO |
| M8 | **ActiveInference.expected_surprise() formula matematica incorrecta** (entropia: `-prob * (prob + 0.01)` no es entropia de Shannon) | `active_inference.py:113` | MEDIO |
| M9 | **FederationServer maneja ImportError de aiohttp como stub** pero no hay alternativa funcional | `federation.py:307-308` | MEDIO |
| M10 | **ModelDownloader usa `curl` via subprocess** en lugar de requests/aiohttp | `model_downloader.py:290` | MEDIO |
| M11 | **CognitiveCache sin expiracion/TTL** — cache crece indefinidamente | `cognitive_cache.py` | MEDIO |
| M12 | **DepthClassifier usa heuristica basada en palabras clave** sin ML ni embeddings | `depth_classifier.py` | MEDIO |
| M13 | **Solo 38.3% de funciones tienen type hints** | Todos | MEDIO |
| M14 | **14 entry points diferentes** (fragmentacion de interfaces de usuario) | 14 archivos | MEDIO |

### 2.4 BAJO (optimizaciones, estilo)

| # | Hallazgo | Archivos | Severidad |
|---|----------|----------|-----------|
| B1 | `__future__.annotations` importado pero no siempre aprovechado para forward references | Varios | BAJO |
| B2 | **CognitiveLoopV5._L0_REFLEX_RESPONSES** hardcoded en espanol/ingles mezclado | `cognitive_loop_v5.py:34-72` | BAJO |
| B3 | **web_dashboard usa `asyncio.run()` dentro de handlers HTTP** (anti-patron) | `web_dashboard.py` | BAJO |
| B4 | **Nombre `cognitive_loop_v05.py` inconsistente** (v05 vs v5) | `zoe/core/` | BAJO |
| B5 | **Falta de `.pyi` stub files** para la API publica | Todos | BAJO |
| B6 | **Tests usan `pytest` en algunos y `unittest` en otros** (inconsistencia) | `zoe/tests/` | BAJO |

---

## 3. TABLA DE ARCHIVOS ANALIZADOS CON PROBLEMAS

| Archivo | L | F | C | CC>15 | Import+ | Except Pass | Doc- | Type- | Notas |
|---------|---|---|---|-------|---------|-------------|------|-------|-------|
| `zoe/core/cognitive_loop.py` | 344 | 11 | 3 | 0 | Si | 0 | 3 | 5 | V0 base, ok estructura |
| `zoe/core/cognitive_loop_v05.py` | 598 | 16 | 1 | 0 | Si | 0 | 5 | 8 | V0.5 extiende V0, codigo duplicado |
| `zoe/core/cognitive_loop_v3.py` | 564 | 10 | 1 | 1 | Si | 0 | 2 | 4 | V3 hereda V05, tick complejo |
| `zoe/core/cognitive_loop_v4.py` | 255 | 9 | 1 | 0 | Si | 1 | 3 | 5 | V4 hereda V3, signal handlers |
| `zoe/core/cognitive_loop_v5.py` | 686 | 12 | 1 | 2 | Si | 5 | 3 | 6 | V5 hereda V4, 5 except:pass, CC=34 |
| `zoe/core/state.py` | 84 | 6 | 1 | 0 | No | 0 | 0 | 0 | Limpio, bien estructurado |
| `zoe/core/active_inference.py` | 183 | 12 | 1 | 0 | No | 0 | 1 | 3 | Formula entropia incorrecta |
| `zoe/core/global_workspace.py` | 183 | 9 | 2 | 0 | No | 0 | 0 | 2 | Limpio, bien disenado |
| `zoe/core/federation.py` | 449 | 20 | 4 | 0 | No | 1 | 3 | 8 | Federacion basica, aiohttp stub |
| `zoe/core/epistemic_federation.py` | 330 | 18 | 3 | 0 | No | 0 | 2 | 5 | MD5 para hashing, bien estructurado |
| `zoe/core/living_memory.py` | 379 | 23 | 2 | 0 | No | 0 | 2 | 4 | Busqueda Jaccard muy basica |
| `zoe/core/cognitive_laws.py` | 288 | 12 | 3 | 0 | No | 0 | 0 | 2 | 1 TODO, bien documentado |
| `zoe/core/cognitive_physics.py` | 268 | 11 | 1 | 1 | No | 0 | 1 | 3 | CC=23 en update(), formula entropy OK |
| `zoe/core/seed_mode.py` | 877 | 18 | 6 | 2 | Si | 0 | 4 | 8 | CC=31 en germinate(), bien estructurado |
| `zoe/core/embodiment_composer.py` | 773 | 20 | 6 | 1 | No | 2 | 5 | 8 | 2 except:pass, CC=19 |
| `zoe/core/zoe_runtime.py` | 500 | 20 | 1 | 0 | Si | 3 | 5 | 8 | 3 bare excepts, 3 except:pass |
| `zoe/core/model_downloader.py` | 647 | 12 | 3 | 0 | No | 2 | 3 | 6 | 2 except:pass, usa curl subprocess |
| `zoe/core/model_profile_router.py` | 386 | 14 | 4 | 0 | No | 1 | 3 | 6 | 1 except:pass |
| `zoe/peripherals/llm.py` | 661 | 32 | 6 | 0 | Si | 2 | 8 | 12 | 2 except:pass, bien disenado |
| `zoe/peripherals/model_bus.py` | 578 | 18 | 3 | 2 | No | 0 | 4 | 8 | CC=17, closure score() interna |
| `zoe/metabolism/metabolism.py` | 260 | 16 | 2 | 0 | No | 0 | 2 | 4 | Composicion manual de InternalState |
| `zoe/capsules/loader.py` | 355 | 18 | 4 | 0 | No | 0 | 3 | 5 | Bien disenado, carga dinamica segura |
| `zoe/capsules/registry.py` | 218 | 14 | 3 | 0 | No | 0 | 2 | 4 | Limpio |
| `zoe/capsules/schema.py` | 288 | 12 | 4 | 1 | No | 0 | 2 | 4 | CC=15 en validate_capsule_yaml |
| `zoe/web_dashboard.py` | 3006 | 91 | 1 | 4 | Si | 3 | 25 | 40 | **Monolito critico**, CC alto, 3 except:pass |
| `zoe/cli_chat.py` | 1066 | 19 | 1 | 1 | Si | 3 | 5 | 10 | 3 except:pass, CC=30 |

*L=Lineas, F=Funciones, C=Clases, CC>15=funciones con complejidad ciclomatica >15, Import+=tiene imports no usados, Except Pass=bloques except:pass, Doc-=funciones sin docstring, Type-=funciones sin type hints*

---

## 4. PROBLEMAS ARQUITECTONICOS

### 4.1 Jerarquia de herencia lineal del Cognitive Loop (CRITICO)

```
CognitiveLoop (v0, 344 lines)
    └── CognitiveLoopV05 (v0.5, 598 lines)  [herencia]
            └── CognitiveLoopV3 (v3, 564 lines)  [herencia]
                    └── CognitiveLoopV4 (v4, 255 lines)  [herencia]
                            └── CognitiveLoopV5 (v5, 686 lines)  [herencia]
```

**Problema:** La herencia lineal de 5 niveles viola el Principio de Sustitucion de Liskov y crea un acoplamiento extremo. Cada version depende de TODAS las anteriores. Un cambio en V0 puede romper V5.

**Impacto:**
- CognitiveLoopV5 pesa 686 lineas pero hereda ~1,500+ de sus padres
- Metodos como `_observe`, `_predict`, `_evaluate` se duplican entre V0 y V05 en lugar de reutilizarse
- No hay interfaz/base class comun que defina el contrato del loop
- Testing de V5 requiere inicializar toda la cadena de herencia

**Recomendacion:** Refactorizar a composicion con Strategy pattern. Un `CognitiveLoop` base con `PipelineStage` inyectables.

### 4.2 Monolito web_dashboard.py (CRITICO)

**Problema:** 3,006 lineas, 91 funciones, 1 clase. Es un monolito que mezcla:
- Servidor HTTP
- API REST
- WebSocket
- Renderizado HTML
- Logica de negocio
- Manejo de capsulas
- Dashboard en tiempo real

**Impacto:** Inmantenible, imposible de testear unitariamente, single point of failure.

### 4.3 Acoplamiento del sistema de memoria (ALTO)

**Problema:** `LivingMemory` usa busqueda por Jaccard de texto plano. No hay capa de abstraccion para el motor de busqueda (embeddings, vector DB). En 11 tipos de memoria, todos usan el mismo mecanismo basico.

### 4.4 Ausencia de capa de persistencia abstracta (ALTO)

**Problema:** La persistencia se maneja de forma ad-hoc:
- `persistent_memory.save_to_disk()` en V4 (interface no definida)
- `memory.db` SQLite accedido directamente
- `trajectory_chain.json` serializado manualmente
- Capsulas cargadas desde YAML+JSONL

No hay `StorageBackend` abstracto que unifique estos mecanismos.

### 4.5 14 entry points (ALTO)

Cada uno es una interfaz de usuario independiente:
- `cli_chat.py` — CLI interactivo
- `web_dashboard.py` — Dashboard web
- `serve.py` — Servidor API
- `zoe_runtime.py` — Runtime minimo
- `voice_first.py` — Modo voz
- `telegram_bridge.py` — Bot Telegram
- 8 demos/examples

Esto fragmenta la experiencia de usuario y duplica logica de inicializacion.

---

## 5. CODIGO MUERTO IDENTIFICADO

### 5.1 Cognitive Loop V0, V05, V3, V4 potencialmente no usados

**Analisis:** V5 es la version mas reciente y la que se usa en produccion. Las versiones anteriores (V0-V4) existen para "compatibilidad hacia atras" pero:
- No hay tests que verifiquen que V0/V3/V4 siguen funcionando
- Los tests de integracion usan V5
- `CognitiveLoopV3` y `CognitiveLoopV4` nunca se instancian en el codigo de produccion (solo en tests)

**Recomendacion:** Consolidar en V5 y eliminar/marcar como deprecated V0-V4.

### 5.2 FederationServer como stub

Si `aiohttp` no esta disponible, el servidor de federacion es un stub que no hace nada (lineas 307-308 de `federation.py`). No hay servidor alternativo.

### 5.3 Active Inference como esqueleto

El modelo de transiciones (`_transition_model`) nunca se usa en produccion. Solo se consulta (`select_action`) pero los resultados no afectan las decisiones del loop principal.

---

## 6. CODIGO DUPLICADO IDENTIFICADO

### 6.1 Metodos duplicados entre versiones del Cognitive Loop

| Metodo | Versiones | Lineas duplicadas |
|--------|-----------|-------------------|
| `__init__` | V0, V05, V3, V4, V5 | ~50 cada uno |
| `_observe` | V0, V05 | 20 lineas identicas |
| `_predict` | V0, V05 | 15 lineas identicas |
| `_evaluate` | V0, V05 | 15 lineas identicas |
| `_act` | V0, V05 | ~80 lineas (V05 anade contexto) |
| `_decide` | V0, V05 | ~60 lineas (V05 anade intenciones) |
| `run` | V0, V05 | ~25 lineas identicas |
| `stop` | V0, V05 | 2 lineas identicas |
| `get_stats` | V0, V05, V3, V4, V5 | ~10 lineas cada uno |
| `_tick` | V0, V05, V3, V4 | V3/V4 llaman a super()._tick() |

**Total estimado:** ~400 lineas de codigo duplicado entre versiones.

### 6.2 Jaccard similarity duplicada

`_jaccard()` esta definida en:
- `LivingMemory._jaccard()`
- `CognitivePhysics._jaccard()`
- Posiblemente en otros archivos

### 6.3 Context building duplicado

Todos los `_act()`, `_decide()`, `_process_lX()` construyen un dict de contexto con las mismas keys:
`state`, `recent_thoughts`, `recent_observations`, `tensions`, `physics`, `fields` — copiado y pegado en 5+ metodos.

---

## 7. INCONSISTENCIAS ENTRE COMPONENTES

| Inconsistencia | Detalle |
|----------------|---------|
| **Nomenclatura de versiones** | `v05` vs `v3` vs `v4` vs `v5` (no hay V1 ni V2) |
| **Import de random** | Algunos modulos importan `random` dentro de metodos, otros a nivel de modulo |
| **Manejo de excepciones** | Unos usan `logger.warning`, otros `logger.debug`, otros `logger.error`, otros `pass` |
| **Acceso a InternalState** | V0 accede directamente; Metabolism usa composicion; Physics usa `getattr()` defensivo |
| **Streaming** | `LLMPeripheral.generate_streaming()` tiene implementacion por defecto que no es streaming real; solo Ollama y OpenAI implementan streaming verdadero |
| **Configuracion** | V4 carga YAML; otros usan dicts hardcoded; Runtime usa argparse |
| **Tests** | Algunos usan pytest, otros unittest, otros mock manual |

---

## 8. PUNTUACION DE CODIGO (0-10)

### Puntuacion final: **5.2 / 10**

#### Desglose

| Criterio | Peso | Nota | Ponderado |
|----------|------|------|-----------|
| Estructura/Arquitectura | 20% | 4.0 | 0.80 |
| Calidad de codigo | 20% | 5.0 | 1.00 |
| Documentacion | 15% | 6.5 | 0.98 |
| Testing | 15% | 7.0 | 1.05 |
| Seguridad | 15% | 4.0 | 0.60 |
| Mantenibilidad | 15% | 4.5 | 0.68 |
| **Total** | **100%** | | **5.11** |

#### Justificacion

**Puntos fuertes:**
- Arquitectura conceptual muy ambiciosa y bien documentada (Fases 0-7, Sprints 1-5)
- Sistema de capsulas bien disenado con loader seguro (sin exec/eval en loader.py)
- ModelBus con fallback automatico es un buen patron
- Seed Mode es una idea innovadora bien implementada
- 57.8% de ratio test/codigo es bueno
- 69.8% de funciones con docstring es aceptable
- No hay imports circulares
- Cada archivo se importa desde algun lugar (no hay codigo completamente muerto)

**Puntos debiles:**
- 34 bloques `except: pass` es inaceptable para produccion
- 80.7% de archivos con imports no usados indica falta de herramientas de linting
- Herencia lineal de 5 niveles en el componente mas critico
- Monolito de 3,006 lineas (web_dashboard.py)
- Solo 38.3% de type hints
- Uso de MD5 para hashing en contextos de integridad
- 86 funciones con complejidad ciclomatica >= 10

---

## 9. FUNCIONES CON MAYOR COMPLEJIDAD CICLOMATICA (CC >= 15)

| CC | Funcion | Archivo |
|----|---------|---------|
| 63 | `_inject` | `zoe/core/capsule_manager.py` |
| 34 | `process_user_input_acd` | `zoe/core/cognitive_loop_v5.py` |
| 32 | `cmd_validate` | `zoe/capsules/scaffold.py` |
| 31 | `classify` | `zoe/core/depth_classifier.py` |
| 31 | `germinate` | `zoe/core/seed_mode.py` |
| 30 | `initialize` | `zoe/cli_chat.py` |
| 30 | `run_integrated_demo` | `zoe/examples/demo_integrated.py` |
| 25 | `generate` | `zoe/core/intentionality_motor.py` |
| 24 | `run_chat` | `zoe/cli_chat.py` |
| 23 | `cmd_create` | `zoe/capsules/scaffold.py` |
| 23 | `update` | `zoe/core/cognitive_physics.py` |
| 22 | `plan` | `zoe/core/resource_planner.py` |
| 22 | `run_demo` | `zoe/examples/demo_phase0.py` |
| 19 | `validate_prerequisites` | `zoe/core/embodiment_composer.py` |
| 19 | `detect_seed_volume` | `zoe/core/seed_mode.py` |
| 19 | `run_demo` | `zoe/examples/demo_phase0_5.py` |
| 19 | `run_use_case` | `zoe/use_cases/run_use_case.py` |
| 18 | `_handle_capsule_validate` | `zoe/web_dashboard.py` |
| 18 | `_process_l2` | `zoe/core/cognitive_loop_v5.py` |
| 18 | `run_phase1_demo` | `zoe/examples/demo_phase1.py` |
| 18 | `evaluate` | `zoe/core/subagents/critic.py` |
| 17 | `validate_new_knowledge` | `zoe/core/epistemic_validator.py` |
| 17 | `package` | `zoe/core/zoe_packager.py` |
| 17 | `_select_acd_aware` | `zoe/peripherals/model_bus.py` |
| 17 | `score` | `zoe/peripherals/model_bus.py` |
| 17 | `main` | `zoe/scripts/zoe_setup.py` |
| 16 | `get_thought_trigger` | `zoe/core/cognitive_tensions.py` |
| 16 | `evaluate_thought` | `zoe/core/mentor.py` |
| 16 | `list_seed_paths` | `zoe/core/seed_mode.py` |
| 16 | `from_resource_graph` | `zoe/peripherals/model_bus.py` |
| 15 | `validate_capsule_yaml` | `zoe/capsules/schema.py` |
| 15 | `recommend_for_acd` | `zoe/core/model_optimizer.py` |
| 15 | `compute_surprise` | `zoe/core/world_model_v2.py` |
| 15 | `_detect_backends` | `zoe/core/zoe_runtime.py` |

---

## 10. RECOMENDACIONES PRIORITARIAS

### Inmediatas (CRITICO)

1. **Reemplazar TODOS los `except: pass` por manejo explicito** — al menos loggear el error
2. **Refactorizar web_dashboard.py** — dividir en modulos (routes, API, HTML, WS)
3. **Eliminar herencia lineal del loop** — usar composicion con Strategy pattern
4. **Reemplazar MD5 por SHA-256** en federacion epistemica
5. **Sanitizar inputs de subprocess** en actuadores

### Corto plazo (ALTO)

6. **Ejecutar `autoflake`/`ruff`** para eliminar 134 archivos de imports no usados
7. **Anadir type hints** a las 1,692 funciones sin ellos (empezar por API publica)
8. **Anadir docstrings** a las 828 funciones y 145 clases sin ellas
9. **Extraer interfaz `CognitiveLoopInterface`** y hacer que V0-V5 la implementen
10. **Refactorizar funciones con CC >= 15** (empezar por las de CC >= 25)

### Medio plazo (MEDIO)

11. **Implementar capa de persistencia abstracta** (`StorageBackend`)
12. **Mejorar LivingMemory.search()** con embeddings opcionales
13. **Consolidar entry points** en un unico `zoe.main` con subcomandos
14. **Anadir mypy/pyright** al CI para type checking
15. **Unificar framework de testing** (pytest para todo)

---

*Fin del informe de auditoria*
