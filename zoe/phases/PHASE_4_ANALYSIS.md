# Análisis para Fase 4 — Implicaciones de Fases 0-3 y refinamientos necesarios

> **Análisis crítico.** Antes de implementar Fase 4 (Federación + Deploy), analiza qué implicaciones tiene lo construido en Fases 0-3 y qué hay que refinar, ampliar y/o mejorar.

**Fecha:** 8 julio 2026
**Base:** 464/464 tests pasan, organismo Fase 3 completo funcional

---

## Estado actual del organismo tras Fase 3

El organismo ZOE v1.0 tiene tras Fase 3:

- **CognitiveLoopV3** con 18 pasos por iteración (bucle completo)
- **12 sub-agentes** de Society of Mind integrados en el bucle
- **Global Workspace** activo (competición + broadcast)
- **Meta-cognición** System 1/System 2 activa
- **Active Inference** consultado en cada iteración
- **6 leyes cognitivas** verificadas en cada acción
- **12 magnitudes de física cognitiva** calculadas
- **6 campos cognitivos** compartidos
- **5 tensiones cognitivas** permanentes
- **Identity Vault** criptográfico (inmutable)
- **Trajectory Chain** firmada (mutaciones verificables y reversibles)
- **Ontogenetic Motor V2** arquitectural (crear/eliminar sub-agentes, ajustar thresholds)
- **Metabolism** con 4 estados (AWAKE/DROWSY/SLEEPING/WAKING)
- **11 tipos de memoria** especializados
- **Memoria viva** que reorganiza, fusiona, generaliza
- **Persistencia SQLite** (memoria entre sesiones)
- **Consolidación profunda** durante el sueño (7 operaciones)
- **5 sentidos** digitales (Clock, Filesystem, UserInput, Network, Agent)
- **4 actuadores** (Language, Code, Tool, Federation)
- **4 backends LLM** (Mock, ZAI, Ollama, OpenAI-compatible)
- **Motor Filogenético** (esqueleto de evolución de especie)
- **Motor de Intencionalidad** (generador de deseos cognitivos)

## Las 10 implicaciones de Fases 0-3 para Fase 4

### Implicación 1 — El Motor Filogenético existe pero solo en memoria

**Estado actual:** `PhylogeneticMotor` usa `PhylogeneticPool` que es un singleton en memoria. Si el organismo se reinicia, las mejoras publicadas se pierden. No hay federación entre instancias en máquinas distintas.

**Implicación para Fase 4:** Fase 4 debe implementar federación real:
- Protocolo HTTP/JSON para comunicación entre ZOEs
- Descubrimiento de instancias (multicast, DNS, o manual)
- Pool filogenético distribuido (no solo singleton)
- Sincronización de mutaciones entre instancias

### Implicación 2 — No hay quorum federativo implementado

**Estado actual:** El doc 14 definió quorum federativo (≥70% aprobación, veto por valores), pero no está implementado en código. El `PhylogeneticMotor` solo publica/prueba/incorpora sin verificar quorum.

**Implicación para Fase 4:** Fase 4 debe implementar:
- Quorum: una mutación requiere ≥70% de aprobación distribuida
- Veto por valores: cualquier Zoe puede vetar si viola valores
- Registro de votos firmados criptográficamente
- Resolución de conflictos cuando hay veto

### Implicación 3 — No hay deploy real en producción

**Estado actual:** El organismo corre en tests y demos, pero no hay un deploy real en VPS. No hay script de arranque, configuración de producción, ni servicio systemd.

**Implicación para Fase 4:** Fase 4 debe implementar:
- Script de deploy (`zoe/scripts/deploy.sh`)
- Configuración de producción (`zoe/config/production.yaml`)
- Servicio systemd para arranque automático
- Integración con Ollama en VPS
- Dashboard básico de monitoreo

### Implicación 4 — La persistencia existe pero no hay restauración automática

**Estado actual:** `PersistentLivingMemory` puede guardar/cargar, pero el bucle no carga automáticamente al arrancar. Hay que llamar `load_from_disk()` manualmente.

**Implicación para Fase 4:** Fase 4 debe:
- Cargar memoria automáticamente al iniciar el organismo
- Guardar memoria automáticamente al detener (graceful shutdown)
- Auto-save periódico durante operación
- Recovery tras crash (cargar último estado válido)

### Implicación 5 — El FederationActuator existe pero no comunica con otras ZOEs

**Estado actual:** `FederationActuator` tiene `send_message()` que solo encola mensajes localmente. No hay comunicación HTTP real.

**Implicación para Fase 4:** Fase 4 debe:
- Implementar cliente HTTP para comunicar con otras ZOEs
- Endpoint REST API para recibir mensajes de otras ZOEs
- Protocolo de federación: register, discover, sync_mutations, vote, broadcast
- Autenticación entre instancias (tokens firmados)

### Implicación 6 — No hay caso de uso real validado

**Estado actual:** Los demos generan pensamientos autónomos, pero no hay un caso de uso real con interacción humana sostenida.

**Implicación para Fase 4:** Fase 4 debe:
- Desplegar ZOE en VPS CEO
- Conectar vía Telegram bot (o CLI) para interacción humana
- 30 días de uso real
- Recopilar métricas de uso
- Validar que el organismo mantiene identidad, aprende, y es útil

### Implicación 7 — Las firmas criptográficas son simples hash

**Estado actual:** `TrajectoryChain` usa hash SHA-256 simple como firma. No hay claves criptográficas reales (ECDSA).

**Implicación para Fase 4:** Fase 4 debe (opcional, si hay tiempo):
- Generar par de claves ECDSA por instancia
- Firmar mutaciones con clave privada
- Verificar firmas con clave pública
- Identidad verificable entre instancias federadas

### Implicación 8 — No hay configuración de producción

**Estado actual:** No hay archivo de configuración de producción. Los parámetros se hardcodean en los demos.

**Implicación para Fase 4:** Fase 4 debe:
- `zoe/config/production.yaml` con todos los parámetros
- Perfiles: production, development, test
- Configuración de LLM periférico
- Configuración de sentidos activos
- Configuración de metabolismo (umbrales)
- Configuración de federación (peers)

### Implicación 9 — El bucle V3 no usa DeepConsolidation automáticamente

**Estado actual:** `DeepConsolidation` existe y funciona, pero `CognitiveLoopV3` no lo invoca durante SLEEPING. Hay que llamarlo manualmente.

**Implicación para Fase 4:** Fase 4 debe:
- Integrar `DeepConsolidation` en el bucle V3
- Cuando `metabolism.state == SLEEPING`, ejecutar consolidación profunda
- Conectar con `PersistentLivingMemory` para guardar tras consolidación

### Implicación 10 — No hay métricas de uso real ni dashboard

**Estado actual:** `get_stats()` devuelve estadísticas internas, pero no hay dashboard visual ni métricas exportables.

**Implicación para Fase 4:** Fase 4 debe:
- Endpoint `/stats` en API REST
- Log estructurado para análisis
- Métricas clave: pensamientos/día, mutaciones/día, ciclos sueño, etc.
- Dashboard básico (texto o JSON)

---

## Lo que Fase 4 debe refinar, ampliar y/o mejorar

### Refinar (mejorar lo existente)

| Componente | Refinamiento |
|---|---|
| CognitiveLoopV3 | Integrar DeepConsolidation durante SLEEPING |
| PersistentLivingMemory | Auto-cargar al iniciar, auto-guardar al detener |
| PhylogeneticMotor | Pool distribuido (no solo singleton en memoria) |
| FederationActuator | Comunicación HTTP real entre instancias |
| TrajectoryChain | Firmas ECDSA (opcional, si hay tiempo) |

### Ampliar (añadir nuevo)

| Componente | Ampliación |
|---|---|
| Federación HTTP | Protocolo REST entre ZOEs |
| Quorum federativo | ≥70% aprobación + veto por valores |
| Deploy VPS | Script + systemd + config producción |
| API REST | Endpoint para interacción externa |
| Dashboard | Métricas de uso real |
| Caso de uso | 30 días con interacción humana |

### Mejorar (optimizar)

| Componente | Mejora |
|---|---|
| Configuración | YAML con perfiles (production/development/test) |
| Logging | Estructurado para análisis post-deploy |
| Recovery | Cargar último estado válido tras crash |
| Auto-save | Periódico durante operación |

---

## Las 6 sub-fases propuestas para Fase 4

### Sub-fase 4.1 — Integrar DeepConsolidation en el bucle V3 (días 1-2)

**Objetivo:** el bucle ejecuta consolidación profunda durante SLEEPING automáticamente.

**Implementación:**
- Modificar `CognitiveLoopV3._tick()` para detectar SLEEPING
- Cuando SLEEPING, ejecutar `DeepConsolidation.consolidate()`
- Tras consolidación, guardar a disco con `PersistentLivingMemory.save_to_disk()`
- Tests: verificar que la consolidación se ejecuta durante el sueño

### Sub-fase 4.2 — Auto-carga y auto-guardado de memoria (días 3-4)

**Objetivo:** el organismo carga memoria al iniciar y guarda al detener.

**Implementación:**
- Al inicializar CognitiveLoopV3, llamar `load_from_disk()` si existe
- Al recibir SIGTERM/SIGINT, llamar `save_to_disk()` antes de cerrar
- Auto-save cada N iteraciones (configurable)
- Recovery: si crash, cargar último estado válido
- Tests: verificar persistencia entre sesiones

### Sub-fase 4.3 — Configuración de producción (días 5-6)

**Objetivo:** configuración YAML con perfiles.

**Implementación:**
- `zoe/config/production.yaml` con todos los parámetros
- `zoe/config/development.yaml` para desarrollo
- `zoe/config/test.yaml` para tests
- Carga automática según variable de entorno `ZOE_ENV`
- Tests: verificar carga de configuración

### Sub-fase 4.4 — Federación HTTP entre instancias (días 7-10)

**Objetivo:** ZOEs en máquinas distintas pueden comunicarse.

**Implementación:**
- `zoe/core/federation_server.py` — servidor HTTP REST
  - Endpoints: `/register`, `/discover`, `/sync_mutations`, `/vote`, `/broadcast`
  - Autenticación por token
- `zoe/core/federation_client.py` — cliente HTTP
  - Descubrimiento de peers
  - Sincronización de mutaciones
  - Votación de quorum
- Quorum federativo: ≥70% aprobación + veto por valores
- Tests: 2 instancias federadas, publicar mejora, votar, incorporar

### Sub-fase 4.5 — Deploy en VPS CEO (días 11-13)

**Objetivo:** ZOE corriendo en VPS con interacción humana.

**Implementación:**
- `zoe/scripts/deploy.sh` — script de deploy
- Servicio systemd (`zoe.service`)
- Integración con Ollama (Qwen 2.5 3B Q5)
- API REST para interacción básica
- Logging estructurado
- Dashboard de métricas (texto/JSON)
- Tests: smoke test en VPS

### Sub-fase 4.6 — Caso de uso real + validación (días 14-15)

**Objetivo:** 30 días de uso real con interacción humana.

**Implementación:**
- Interacción vía Telegram bot o CLI
- Recopilación de métricas diarias
- Validación de identidad persistente
- Validación de aprendizaje (mutaciones firmadas)
- Validación de memoria persistente
- Validación de federación (si hay múltiples instancias)
- Reporte final de validación

---

## Métricas de validación Fase 4

| Métrica | Objetivo |
|---|---|
| Organismo corre en VPS sin crash | ≥24h |
| Memoria persiste entre reinicios | Sí |
| Consolidación profunda ejecuta en sueño | Sí |
| Federación entre 2+ instancias | Sí |
| Quorum federativo funciona | Sí |
| Configuración de producción carga | Sí |
| Caso de uso real validado | 30 días |
| Pensamientos autónomos generados | ≥100 |
| Mutaciones firmadas aplicadas | ≥10 |
| Tests pasan | 100% previos + nuevos |
| Demo Fase 4 funcional | Sí |

---

*Análisis completado. Fase 4 planificada con refinamientos, ampliaciones y mejoras.*
