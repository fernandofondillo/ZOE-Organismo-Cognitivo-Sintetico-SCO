# ZOE — Plan de Resolución de Gaps Funcionales

> **Este documento identifica los gaps que impiden a ZOE ser realmente lo que dice ser, y propone un plan concreto para resolverlos.** Cada gap está priorizado por impacto y esfuerzo.
>
> **Versión:** V1.8.0 — Julio 2026 (Sprint 5.7.4)
> **Audiencia:** Equipo técnico, CTO, contribuidores
> **Veredicto:** ZOE hoy es un chatbot con memoria episódica persistente. Para ser un "organismo cognitivo que existe continuamente" necesita resolver 10 gaps críticos, mayormente de persistencia y conexión de componentes declarados pero muertos.

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Estado actual: lo que funciona y lo que no](#2-estado-actual-lo-que-funciona-y-lo-que-no)
3. [Gaps críticos (Prioridad 1-2)](#3-gaps-críticos-prioridad-1-2)
4. [Gaps menores (Prioridad 3-5)](#4-gaps-menores-prioridad-3-5)
5. [Plan de ejecución por Sprints](#5-plan-de-ejecución-por-sprints)
6. [Métricas de éxito](#6-métricas-de-éxito)

---

## 1. Resumen ejecutivo

### Lo que ZOE dice ser (docs 18/19)

Un organismo cognitivo sintético que:
- Existe continuamente
- Recuerda para siempre
- Evoluciona contigo
- Tiene identidad criptográfica soberana
- Tiene trayectoria firmada auditable
- Aprende en segundos con cápsulas
- Se guía por un mentor digital
- Ve imágenes (multimodal)
- Habla varios idiomas
- Conversa por voz tipo Her

### Lo que ZOE es hoy

Un chatbot con:
- ✅ Memoria episódica persistente (SQLite)
- ✅ Bucle cognitivo autónomo que genera pensamientos en background
- ✅ ACD Router que cambia de modelo Ollama en caliente
- ✅ 12 sub-agentes coordinados vía Global Workspace
- ✅ Federación epistémica HTTP real entre pares
- ✅ 15 cápsulas de conocimiento
- ❌ Identidad NO persiste (nace de nuevo cada arranque)
- ❌ Trayectoria NO persiste (la blockchain se pierde al reiniciar)
- ❌ Cápsulas cargadas NO persisten (hay que recargar cada vez)
- ❌ Configuración NO persiste (hay que pasar flags cada vez)
- ❌ Dashboard sin seguridad (expuesto a la red sin auth)
- ❌ Mentor digital NO conectado al bucle
- ❌ Visión NO conectada al Dashboard
- ❌ Detección de idioma NO conectada
- ❌ CognitiveOptimizationLayer (Sprint 5) completamente muerto
- ❌ Voice-first NO integrado en el Dashboard

### La distancia

**10 gaps críticos**, mayormente relacionados con:
1. **Persistencia** (identidad, trayectoria, cápsulas, config)
2. **Conexión de componentes declarados pero muertos** (mentor, vision, idioma, ZMAP/CPL/TPE, voice-first)
3. **Seguridad operacional** (Dashboard sin auth, sin métricas, sin backup)

### Recomendación brutal

Antes de añadir una sola feature nueva, cierra los 4 gaps de Prioridad 1. **Sin ellos, la promesa fundamental del proyecto es falsa.** La frase *"ZOE está siempre ahí… recordando… evolucionando contigo"* no es cierta hoy: cada vez que arrancas, ZOE olvida quién es, pierde su diario de vida, olvida qué cápsulas tenía cargadas y olvida qué backend/model usabas.

---

## 2. Estado actual: lo que funciona y lo que no

### ✅ Funciona (4 de 25 puntos auditados)

| # | Componente | Estado | Evidencia |
|---|---|---|---|
| 1 | Memoria episódica persistente | ✅ | `PersistentMemoryStore` SQLite + `loop.initialize()` carga en disco |
| 13 | Telegram bridge | ✅ | Modos "direct" y "api" ambos funcionales |
| 14 | Archivo .zoe portátil | ⚠️ Parcial | `ZoePackager.package()` funciona pero no hay persistence previa de identidad/trayectoria |
| 7 | Dashboard interactivo (chat) | ⚠️ Parcial | Chat WS usa ACD, pero el frontend no muestra router stats |

### ⚠️ Parcial (11 de 25)

| # | Componente | Qué funciona | Qué falta |
|---|---|---|---|
| 5 | Bucle autónomo | Corre en background, genera pensamientos | Auto-save cada 50 iteraciones (pérdida si crash) |
| 6 | ACD Router end-to-end | Hot-swap muta `speaker.llm.model` | No hay test E2E con Ollama real |
| 10 | Federación | HTTP real, no mock | Sin discovery automático de peers |
| 11 | Marketplace | Upload/download local | Sin servidor central |
| 15 | Seed mode | `/api/seed/*` expuesto | No arranca el bucle tras germinar |
| 16 | EmbodimentComposer | Endpoints REST | No conectado al bucle cognitivo |
| 21 | Logs | stdout | Sin archivo, sin rotación |
| 22 | Actualización | `git pull` preserva `data/` | Sin backup previo |

### ❌ No funciona (6 de 25)

| # | Componente | Impacto |
|---|---|---|
| 2 | Trayectoria persistente | La blockchain se pierde al reiniciar |
| 3 | Identidad persistente | ZOE "nace" de nuevo cada arranque |
| 4 | Cápsulas cargadas persistentes | Hay que recargar cada vez |
| 20 | Configuración persistente | Hay que pasar flags cada vez |
| 23 | Backup y restore | No existe |
| 24 | Métricas Prometheus | No existe |
| 25 | Seguridad Dashboard | Expuesto a la red sin auth |

### 💀 No conectado (7 de 25)

| # | Componente | LOC | Estado |
|---|---|---|---|
| 8 | Voice-first en Dashboard | 798 | CLI separado, sin integración web |
| 9 | Visión en Dashboard | 636 | `_handle_feed_upload` no invoca VLM |
| 12 | Mentor en bucle | 280 | Instanciado pero `evaluate_thought` nunca se llama |
| 17 | ResourcePlanner en ACD | 383 | No conectado a `process_user_input_acd` |
| 18 | CognitiveOptimizationLayer | 685 | Jamás se instancia en producción |
| 19 | LanguageDetector | 319 | No se invoca desde ningún sitio |

---

## 3. Gaps críticos (Prioridad 1-2)

### 🚨 C1 — Identidad NO persiste (ZOE "nace" cada arranque)

**Impacto:** CRÍTICO — la promesa "ZOE existe continuamente" es FALSA

**Archivo:** `zoe/alma/identity_vault.py` (falta `save_to_disk`/`load_from_disk`)
**Archivo:** `zoe/cli_chat.py:165` — `vault = IdentityVault(birth_timestamp=time.time())`

**El problema:** El hash SHA-256 incluye `birth_timestamp`. Cada vez que arrancas ZOE, `time.time()` es diferente → el hash cambia → ZOE "nace" de nuevo.

**Fix:**
```python
# En identity_vault.py, añadir:
def save_to_disk(self, path: str) -> None:
    Path(path).write_text(json.dumps(self.to_dict()))

@classmethod
def load_from_disk(cls, path: str) -> Optional["IdentityVault"]:
    p = Path(path)
    if not p.exists():
        return None
    return cls.from_dict(json.loads(p.read_text()))

# En cli_chat.py:165, cambiar:
vault_path = f"{self.db_path.rsplit('/', 1)[0]}/identity_vault.json"
vault = IdentityVault.load_from_disk(vault_path)
if vault is None:
    vault = IdentityVault(birth_timestamp=time.time())
    vault.save_to_disk(vault_path)
```

**Esfuerzo:** 2 horas
**Tests necesarios:** 5 tests (save, load, persistencia entre sesiones, hash inmutable, fallback si archivo corrupto)

---

### 🚨 C2 — Trayectoria NO persiste (la blockchain se pierde)

**Impacto:** CRÍTICO — la promesa "auditable" es FALSA

**Archivo:** `zoe/alma/trajectory_chain.py` (falta `save_to_disk`/`load_from_disk`)
**Archivo:** `zoe/cli_chat.py:166` — `chain = TrajectoryChain(organism_id="zoe_chat")` (vacío cada vez)

**El problema:** Cada mutación firmada se va a RAM. Al cerrar ZOE, toda la trayectoria se pierde.

**Fix:**
```python
# En trajectory_chain.py, añadir:
def save_to_disk(self, path: str) -> None:
    data = {
        "organism_id": self.organism_id,
        "mutations": [m.to_dict() for m in self._mutations],
        "total_commits": self._total_commits,
    }
    Path(path).write_text(json.dumps(data))

@classmethod
def load_from_disk(cls, path: str) -> Optional["TrajectoryChain"]:
    p = Path(path)
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    chain = cls(organism_id=data["organism_id"])
    for m_dict in data["mutations"]:
        mutation = Mutation.from_dict(m_dict)
        chain._mutations.append(mutation)
    chain._total_commits = data["total_commits"]
    return chain

# En cli_chat.py:166, cambiar:
chain_path = f"{self.db_path.rsplit('/', 1)[0]}/trajectory_chain.json"
chain = TrajectoryChain.load_from_disk(chain_path)
if chain is None:
    chain = TrajectoryChain(organism_id="zoe_chat")
    chain.save_to_disk(chain_path)

# En trajectory_chain.py commit(), después de añadir mutación:
self.save_to_disk(self._persist_path)  # persistir tras cada commit
```

**Esfuerzo:** 3 horas
**Tests necesarios:** 7 tests (save, load, persistencia, verify_chain tras load, rollback persiste, append tras load, fallback corrupto)

---

### 🚨 C3 — Cápsulas cargadas NO persisten

**Impacto:** CRÍTICO — la promesa "carga una cápsula y ZOE la recuerda" es FALSA entre sesiones

**Archivo:** `zoe/core/capsule_manager.py` (falta persistencia de `_loaded`)
**Archivo:** `zoe/cli_chat.py:321-332` — solo carga basal + use_case

**Fix:**
```python
# En capsule_manager.py, añadir:
def save_loaded_state(self, path: str) -> None:
    data = {"loaded": list(self._loaded.keys())}
    Path(path).write_text(json.dumps(data))

@classmethod
def load_loaded_state(cls, path: str) -> List[str]:
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text()).get("loaded", [])

# En cli_chat.py:321, después de cargar basal:
loaded_path = f"{self.db_path.rsplit('/', 1)[0]}/loaded_capsules.json"
saved_capsules = CapsuleManager.load_loaded_state(loaded_path)
for cap_name in saved_capsules:
    if cap_name != "zoe_basal_knowledge":  # ya cargada
        self.capsule_manager.load(cap_name)

# Al cerrar (cli_chat.py shutdown):
self.capsule_manager.save_loaded_state(loaded_path)
```

**Esfuerzo:** 2 horas
**Tests necesarios:** 5 tests (save, load, persistencia, recarga al iniciar, no duplica basal)

---

### 🚨 C4 — Configuración NO persiste (UX rota)

**Impacto:** CRÍTICO — cada arranque hay que pasar `--backend ollama --model auto`

**Archivo:** `zoe/cli_chat.py:893-909` (argparse, no lee config)
**Archivo:** `zoe/config/{development,production}.yaml` existen pero nadie los carga

**Fix:**
```python
# En cli_chat.py main(), antes de argparse:
import json
config_path = Path.home() / ".zoe" / "config.json"
saved_config = {}
if config_path.exists():
    saved_config = json.loads(config_path.read_text())

# argparse usa saved_config como defaults:
parser.add_argument("--backend", default=saved_config.get("backend", "mock"))
parser.add_argument("--model", default=saved_config.get("model"))

# Al cerrar, guardar config actual:
config_path.parent.mkdir(parents=True, exist_ok=True)
config_path.write_text(json.dumps({
    "backend": args.backend,
    "model": args.model,
    "db_path": args.db_path,
}))
```

**Esfuerzo:** 2 horas
**Tests necesarios:** 4 tests (save config, load config, CLI override, persistencia)

---

### 🚨 C5 — Dashboard SIN seguridad (expuesto a la red)

**Impacto:** CRÍTICO — imposible desplegar en VPS o compartir en red

**Archivo:** `zoe/web_dashboard.py:197` — `web.TCPSite(self._runner, "0.0.0.0", self.port)`

**Fix:**
```python
# 1. Bindear a 127.0.0.1 por defecto
parser.add_argument("--host", default="127.0.0.1",
    help="Host to bind (use 0.0.0.0 to expose to network)")

# 2. Añadir --auth-token
parser.add_argument("--auth-token", help="Token required for all requests")

# 3. Middleware que verifique token
@web.middleware
async def auth_middleware(request, handler):
    token = request.app.get("auth_token")
    if token:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {token}":
            return web.json_response({"error": "unauthorized"}, status=401)
    return await handler(request)

# 4. En start():
app = web.Application(middlewares=[auth_middleware] if token else [])
```

**Esfuerzo:** 3 horas
**Tests necesarios:** 6 tests (sin token = 401, con token = 200, host 127.0.0.1, host 0.0.0.0, WebSocket auth, sin auth-token flag = libre)

---

### 🚨 C6 — Mentor digital NO conectado al bucle

**Impacto:** ALTO — feature declarada pero inerte

**Archivo:** `zoe/core/mentor.py:154` — `evaluate_thought()` existe pero nadie la llama
**Archivo:** `zoe/cli_chat.py:317-319` — solo lo instancia para endpoints REST

**Fix:**
```python
# En cognitive_loop_v3.py _tick(), después de línea 200 (on_thought_callback):
if hasattr(self, 'mentor') and self.mentor:
    intervention = self.mentor.evaluate_thought(thought.content)
    if intervention:
        mentor_thought = Thought(
            content=intervention,
            trigger="mentor_intervention",
            timestamp=time.time(),
        )
        self.memory.add(
            content=f"Mentor: {intervention}",
            type="episodic",
            provenance="mentor",
        )
```

**Esfuerzo:** 2 horas
**Tests necesarios:** 4 tests (mentor evalúa thought, mentor interviene, no interviene si no hay, persistencia de intervención)

---

### 🚨 C7 — Visión NO conectada al Dashboard

**Impacto:** ALTO — la promesa "le pasas una foto y la describe" es FALSA desde el Dashboard

**Archivo:** `zoe/web_dashboard.py:354-399` — `_handle_feed_upload` solo guarda texto
**Archivo:** `zoe/peripherals/multimodal.py:41` — `VLMPeripheral` existe

**Fix:**
```python
# En _handle_feed_upload, detectar Content-Type:
content_type = part.headers.get("Content-Type", "")
if content_type.startswith("image/"):
    image_bytes = await part.read()
    vlm = VLMPeripheral(model="gpt-4o", api_key=os.environ.get("OPENAI_API_KEY"))
    description = await vlm.generate(
        prompt="Describe esta imagen en detalle.",
        images=[image_bytes],
    )
    self.chat.memory.add(
        content=f"Image: {description}",
        type="semantic",
        provenance="vision",
    )
    return web.json_response({"description": description})
```

**Esfuerzo:** 4 horas
**Tests necesarios:** 5 tests (upload imagen, VLM describe, memoria guarda, fallback sin API key, fallback sin VLM)

---

### 🚨 C8 — Detección de idioma NO conectada

**Impacto:** ALTO — la promesa "detecta automáticamente el idioma" es FALSA

**Archivo:** `zoe/core/language_detector.py` — clase completa, sin uso
**Archivo:** `zoe/cli_chat.py:577-597` — `_build_system_prompt()` devuelve texto en español siempre

**Fix:**
```python
# En cognitive_loop_v5.py process_user_input_acd, antes de generar respuesta:
from .language_detector import LanguageDetector, Language
detector = LanguageDetector()
detected_lang = detector.detect(user_input)
if detected_lang:
    system_prompt = detector.get_system_prompt(detected_lang)
    # Pasar al Speaker para que lo use en generate_thought
    context["system_prompt"] = system_prompt
    context["language"] = detected_lang.value

# En speaker.py generate_thought, usar context["system_prompt"] si existe
```

**Esfuerzo:** 3 horas
**Tests necesarios:** 5 tests (detecta español, detecta inglés, detecta francés, detecta alemán, fallback)

---

### 🚨 C9 — CognitiveOptimizationLayer (Sprint 5) completamente muerto

**Impacto:** ALTO — 685 LOC de código muerto cubierto por tests aislados

**Archivo:** `zoe/core/cognitive_optimization.py` (685 LOC)

**Fix:**
```python
# En cli_chat.py initialize(), después de crear el loop:
from .core.cognitive_optimization import CognitivePrefetchLayer
cpl = CognitivePrefetchLayer(
    memory=memory,
    model_optimizer=model_optimizer if hasattr(self, 'model_optimizer') else None,
)
loop.cognitive_prefetch_layer = cpl

# En cognitive_loop_v5.py process_user_input_acd, antes de _process_lN:
if hasattr(self, 'cognitive_prefetch_layer') and self.cognitive_prefetch_layer:
    prefetched_context = self.cognitive_prefetch_layer.prefetch(user_input)
    # Enriquecer context con prefetched_context
```

**Esfuerzo:** 4 horas
**Tests necesarios:** 6 tests (CPL activo, prefetch funciona, ZMAP carga, TPE predice, integración con ACD, no rompe backward compat)

---

### 🚨 C10 — Voice-first mode NO integrado en el Dashboard

**Impacto:** ALTO — la promesa "modo voice-first tipo Her" solo funciona como script aparte

**Archivo:** `zoe/peripherals/voice_first.py` (798 LOC)
**Archivo:** `zoe/web_dashboard.py` — no hay `/api/voice`

**Fix:**
```python
# En web_dashboard.py start(), añadir rutas:
app.router.add_post("/api/voice/start", self._handle_voice_start)
app.router.add_post("/api/voice/stop", self._handle_voice_stop)
app.router.add_get("/api/voice/status", self._handle_voice_status)

# Handlers:
async def _handle_voice_start(self, request):
    if not hasattr(self, '_voice_mode'):
        from .peripherals.voice_first import VoiceFirstMode, VoiceConfig
        config = VoiceConfig(wake_word="hey zoe")
        self._voice_mode = VoiceFirstMode(config, zoe_chat=self.chat)
    await self._voice_mode.start()
    return web.json_response({"status": "listening"})

async def _handle_voice_stop(self, request):
    if hasattr(self, '_voice_mode'):
        await self._voice_mode.stop()
    return web.json_response({"status": "stopped"})

# Frontend: botón micrófono que llama /api/voice/start
# WebRTC para capturar audio del micrófono del navegador
```

**Esfuerzo:** 8 horas (incluye frontend WebRTC)
**Tests necesarios:** 5 tests (start, stop, status, sin micrófono, wake word detection)

---

## 4. Gaps menores (Prioridad 3-5)

| # | Gap | Archivo | Fix | Esfuerzo |
|---|---|---|---|---|
| M1 | Dashboard no muestra router stats en UI | web_dashboard.py:187 | Frontend: poll `/api/router/stats` cada 2s | 2h |
| M2 | Auto-save cada 50 iteraciones (pérdida si crash) | cognitive_loop_v4.py:142 | Reducir a 5 iteraciones | 1h |
| M3 | Tests ACD no son E2E con Ollama real | tests/test_sprint5_7_acd_routing.py | Añadir test con Ollama disponible | 2h |
| M4 | Seed mode no arranca el bucle tras germinar | seed_mode.py:760 | Tras `bootstrap_from_scratch`, lanzar `loop.run()` | 3h |
| M5 | EmbodimentComposer no conectado al bucle | embodiment_composer.py | Permitir que V5 use el Embodiment activo | 4h |
| M6 | ResourcePlanner solapado con ModelProfileRouter | resource_planner.py + model_profile_router.py | Decidir uno (recomendado: ResourcePlanner) | 6h |
| M7 | Logs sin archivo ni rotación | cli_chat.py:911 | `RotatingFileHandler('zoe_data/zoe.log')` | 1h |
| M8 | Marketplace solo local | marketplace/core.py:109 | Documentar o añadir sync con GitHub repo | 2h |
| M9 | Actualización sin backup previo | zoe-bootstrap.sh:315 | Copiar `data/` a `data.backup.{timestamp}/` antes de git pull | 1h |
| M10 | No hay métricas Prometheus | (no existe) | Añadir `/metrics` con `prometheus_client` | 3h |
| M11 | No hay comando backup/restore | (no existe) | `python -m zoe.cli_chat --backup zoe_backup.tar.gz` | 3h |
| M12 | `.zoe` runtime no carga cápsulas activas | zoe_runtime.py:109 | `_load_capsules` debe cargar las activas | 2h |
| M13 | Federación sin discovery automático | epistemic_federation_server.py:68 | mDNS/broadcast para descubrir ZOEs en LAN | 6h |
| M14 | Auto-save inconsistente (50 vs 20) | serve.py:214 vs cli_chat.py:260 | Unificar a 20 | 30min |
| M15 | cli_chat.py y serve.py duplican inicialización (~200 LOC) | Ambos | Extraer `ZoeOrganismBuilder` compartido | 4h |

---

## 5. Plan de ejecución por Sprints

### Sprint 5.8 — Persistencia y soberanía (Prioridad 1)

**Objetivo:** Hacer que ZOE realmente exista continuamente con la misma identidad, trayectoria, cápsulas y configuración.

**Tareas:**
1. C1: IdentityVault.save_to_disk/load_from_disk + invocar en cli_chat.py y serve.py
2. C2: TrajectoryChain.save_to_disk/load_from_disk + invocar + persistir tras cada commit
3. C3: CapsuleManager.save_loaded_state/load_loaded_state + recargar al iniciar
4. C4: Cargar `~/.zoe/config.json` en cli_chat.py y web_dashboard.py

**Tests:** 21 tests nuevos (5+7+5+4)
**Esfuerzo total:** 9 horas
**Commit:** `feat: Sprint 5.8 — persistencia de identidad, trayectoria, cápsulas y config`

**Criterio de éxito:** tras reiniciar ZOE, la identidad (hash), la trayectoria (mutaciones), las cápsulas cargadas y la configuración (backend, model) se preservan.

---

### Sprint 5.9 — Seguridad y observabilidad (Prioridad 2)

**Objetivo:** Hacer que ZOE sea seguro de exponer en red y observable en producción.

**Tareas:**
1. C5: Dashboard bind a 127.0.0.1 por defecto + flag `--auth-token`
2. M7: Logging a archivo rotado (`zoe_data/zoe.log`)
3. M10: Endpoint `/metrics` Prometheus
4. M11: Comando `zoe backup`/`zoe restore`
5. M9: Backup automático pre-actualización en `zoe-bootstrap.sh`

**Tests:** 15 tests nuevos
**Esfuerzo total:** 11 horas
**Commit:** `feat: Sprint 5.9 — seguridad, logging, métricas y backup`

**Criterio de éxito:** Dashboard seguro por defecto, logs persisten, métricas expuestas, backup/restore funcional.

---

### Sprint 5.10 — Revivir componentes muertos (Prioridad 3)

**Objetivo:** Conectar los componentes declarados pero nunca activos.

**Tareas:**
1. C6: MentorAgent.evaluate_thought conectado al _tick de V3
2. C7: _handle_feed_upload conectado a VLMPeripheral
3. C8: LanguageDetector conectado al Speaker
4. C9: CognitiveOptimizationLayer (ZMAP/CPL/TPE) activo en cli_chat
5. M1: Frontend del Dashboard que muestre router stats en tiempo real

**Tests:** 25 tests nuevos
**Esfuerzo total:** 15 horas
**Commit:** `feat: Sprint 5.10 — mentor, vision, idioma, ZMAP/CPL/TPE activos`

**Criterio de éxito:** mentor guía a ZOE, visión funciona desde Dashboard, ZOE responde en el idioma detectado, ZMAP prefetching activo.

---

### Sprint 5.11 — Voice-first en Dashboard (Prioridad 4)

**Objetivo:** Integrar voice-first mode en el Dashboard web.

**Tareas:**
1. C10: Endpoints `/api/voice/start|stop|status`
2. Frontend WebRTC para capturar audio del navegador
3. Botón micrófono en el Dashboard
4. Wake word detection en navegador (opcional)
5. M3: Test E2E con Ollama real para ACD hot-swap

**Tests:** 10 tests nuevos
**Esfuerzo total:** 12 horas
**Commit:** `feat: Sprint 5.11 — voice-first integrado en Dashboard`

**Criterio de éxito:** puedes hablar con ZOE desde el navegador sin instalar nada extra.

---

### Sprint 5.12 — Limpieza arquitectónica (Prioridad 5)

**Objetivo:** Eliminar duplicaciones y consolidar componentes.

**Tareas:**
1. M6: Decidir ResourcePlanner vs ModelProfileRouter (eliminar uno)
2. M15: Extraer `ZoeOrganismBuilder` compartido
3. M5: Conectar EmbodimentComposer al bucle (o documentar como opcional)
4. M4: Seed mode arranca el bucle tras germinar
5. M12: `.zoe` runtime carga cápsulas activas
6. M13: Federación con discovery automático (mDNS)
7. M14: Unificar auto-save a 20 iteraciones

**Tests:** 15 tests nuevos
**Esfuerzo total:** 26 horas
**Commit:** `feat: Sprint 5.12 — limpieza arquitectónica y consolidación`

**Criterio de éxito:** no hay componentes muertos, no hay duplicaciones, seed mode arranca el bucle.

---

## 6. Métricas de éxito

### Tras Sprint 5.8 (Persistencia)

| Métrica | Antes | Después |
|---|---|---|
| Identidad persiste entre sesiones | ❌ | ✅ |
| Trayectoria persiste entre sesiones | ❌ | ✅ |
| Cápsulas cargadas persisten | ❌ | ✅ |
| Configuración persiste | ❌ | ✅ |
| Tests totales | 1.413 | 1.434 |

### Tras Sprint 5.9 (Seguridad)

| Métrica | Antes | Después |
|---|---|---|
| Dashboard seguro por defecto | ❌ (0.0.0.0) | ✅ (127.0.0.1) |
| Auth token opcional | ❌ | ✅ |
| Logs a archivo | ❌ | ✅ (rotación 10MB) |
| Métricas Prometheus | ❌ | ✅ |
| Backup/restore | ❌ | ✅ |
| Tests totales | 1.434 | 1.449 |

### Tras Sprint 5.10 (Componentes muertos)

| Métrica | Antes | Después |
|---|---|---|
| Mentor conectado al bucle | ❌ | ✅ |
| Visión desde Dashboard | ❌ | ✅ |
| Detección de idioma activa | ❌ | ✅ |
| ZMAP/CPL/TPE activo | ❌ | ✅ |
| Router stats en UI | ❌ | ✅ |
| Tests totales | 1.449 | 1.474 |

### Tras Sprint 5.11 (Voice-first)

| Métrica | Antes | Después |
|---|---|---|
| Voice-first desde Dashboard | ❌ | ✅ |
| Test E2E con Ollama real | ❌ | ✅ |
| Tests totales | 1.474 | 1.484 |

### Tras Sprint 5.12 (Limpieza)

| Métrica | Antes | Después |
|---|---|---|
| Componentes muertos | 7 | 0 |
| Duplicaciones arquitecturales | 3 | 0 |
| Tests totales | 1.484 | 1.499 |

### Estado final objetivo

| Métrica | Valor |
|---|---|
| Tests | ~1.500 |
| Componentes funcionales | 25/25 ✅ |
| Componentes muertos | 0 |
| Gaps críticos | 0 |
| Gaps menores | 0 |
| Persistencia | Identidad + trayectoria + cápsulas + config |
| Seguridad | Auth opcional + bind 127.0.0.1 por defecto |
| Observabilidad | Logs + métricas Prometheus + backup |
| Voice-first | Integrado en Dashboard |
| Multimodal | Visión desde Dashboard |
| Multi-idioma | Detección automática activa |
| Mentor | Conectado al bucle cognitivo |
| CognitiveOptimizationLayer | Activo en producción |

**En este punto, ZOE será realmente lo que dice ser: un organismo cognitivo que existe continuamente, recuerda, evoluciona, y es soberanamente tuyo.**

---

*ZOE V1.8.0 — Plan de Resolución de Gaps Funcionales*
*Julio 2026 — Sprint 5.7.4*
*"Sin resolver los 4 gaps de Prioridad 1, la promesa fundamental del proyecto es falsa."*
