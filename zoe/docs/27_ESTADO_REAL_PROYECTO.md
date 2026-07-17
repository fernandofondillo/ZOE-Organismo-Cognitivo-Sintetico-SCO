# ZOE — Estado Real del Proyecto (Julio 2026)

> Documento de referencia interna. Auditado contra código real del repositorio
> y experiencia de despliegue real en MacBook Air M3 8GB + SSD Crucial X9.

---

## 1. LO QUE ZOE ES HOY (verificado en código)

### ✅ Funciona al 100%
- **Identidad soberana**: SHA-256 inmutable, 9 vectores, 7 valores, guardado en `identity_vault.json`
- **Trayectoria inmutable**: Blockchain de mutaciones con SHA-256, guardado en `trajectory_chain.json`
- **Metabolismo funcional**: AWAKE/DROWSY/SLEEPING/WAKING con umbrales de fatiga
- **5 cápsulas base**: 162 entradas cargadas automáticamente al nacer
- **LanguageDetector**: Detecta es/en/fr/de sin LLM (<10ms)
- **MentorAgent**: Activo por defecto, evalúa pensamientos autónomos
- **ReflectionEngine**: Cableado al metabolismo, se activa durante SLEEPING
- **Dashboard web**: Chat funcional, panel de estado, cápsulas, memoria
- **Persistencia en SSD**: SQLite + JSON en `data/` del SSD
- **15 cápsulas disponibles**: 5 base + 10 de especialidad

### ⚠️ Funciona parcialmente
- **Memoria**: Guarda en SQLite (525+ entradas) y recupera, pero:
  - Solo usa tipo `episodic`. Los otros 10 tipos existen pero no se crean automáticamente
  - Búsqueda es Jaccard (léxica), no semántica
- **Reflexión autónoma**: Funciona pero los insights no se muestran en el chat
- **Tutor**: Evalúa pero sus intervenciones solo van a logs, no al chat
- **Sub-agentes**: 12 definidos pero solo 3-4 participan en respuestas ACD
- **Exploración del entorno**: FilesystemSense activado pero solo observa `data/`

### ❌ No funciona / No implementado
- **Memoria semántica automática**: No extrae hechos del diálogo
- **Memoria emotional/social/prospective**: No se crean automáticamente
- **Búsqueda semántica**: Requiere `sentence-transformers` (no instalado)
- **Internet/herramientas**: ZOE no puede navegar internet ni usar herramientas externas
- **ACD con MiniMax**: El ACD Router solo funciona con `--backend ollama --model auto`.
  Con `--backend anthropic`, todas las preguntas van al mismo modelo

---

## 2. GAP ENTRE PROMESA (Manual 22) Y REALIDAD

| Promesa del manual | Realidad del código | Gap | Prioridad |
|---|---|---|---|
| "11 tipos de memoria" | Solo `episodic` se usa | 10 tipos no se crean | ALTA |
| "Recuerda entre sesiones" | ✅ Funciona (fix Sprint 5.21) | Cerrado | — |
| "Explora su entorno digital" | FilesystemSense solo observa `data/` | Limitado | MEDIA |
| "Reflexión con DeepSeek-R1" | ReflectionEngine usa el modelo configurado | Funciona con MiniMax | — |
| "Tutor visible" | Intervenciones solo en logs | No visible en chat | MEDIA |
| "12 sub-agentes compiten" | Solo 3-4 en pipeline ACD | 8 no participan | BAJA |
| "ACD elige modelo óptimo" | Solo con Ollama. Con API, todo al mismo | No hay ACD con cloud | ALTA |
| "No requiere internet" | ✅ Con Ollama funciona offline | Cerrado | — |
| "Démosle manos" | No tiene herramientas ni internet | No implementado | ALTA |

---

## 3. PROBLEMAS DE DESPLIEGUE REAL (verificados en MacBook Air M3)

| Problema | Causa | Solución aplicada | Estado |
|---|---|---|---|
| Ollama no arranca en macOS | Gatekeeper bloquea .app | xattr -cr + open | ✅ Fixeado |
| `num_parallel` error | Modelfile incompatible | Eliminado parámetro | ✅ Fixeado |
| GGUF no válido | HuggingFace devuelve HTML | GGUF validation + ollama pull fallback | ✅ Fixeado |
| CSS sin estilos | CSP no permitía style-src | Añadido style-src unsafe-inline | ✅ Fixeado |
| `model 'auto' not found` | Router no detectaba ollama list | Añadido mapeo nombres estándar | ✅ Fixeado |
| Dashboard no funcional | SyntaxError en JS (comillas, newlines) | Reescrito JS limpio + node --check | ✅ Fixeado |
| Auth bloqueaba localhost | Token requerido para todo | Auth skip para 127.0.0.1 | ✅ Fixeado |
| No scroll en dashboard | overflow: hidden en body | Cambiado a overflow-y: auto | ✅ Fixeado |
| ZOE no recuerda nombre | Speaker no incluía memorias | Añadido relevant_memories al prompt | ✅ Fixeado |
| Puerto 8642 en uso | Procesos previos no cerrados | Launcher mata procesos + git pull | ✅ Fixeado |
| Mac se bloquea con L3 | Modelos 32B en 8GB RAM | Usar MiniMax-M3 cloud | ✅ Solucionado |
| API key manual cada vez | .env no se carga automáticamente | Pendiente | 🔧 EN PROCESO |

---

## 4. CAMBIOS PENDIENTES DE IMPLEMENTACIÓN

### 4.1 API key persistente en .env (ALTA)
**Problema**: El usuario tiene que poner `ANTHROPIC_API_KEY="..."` cada vez que arranca.
**Solución**: El launcher lee `.env` del SSD que ya tiene la API key guardada.
**Archivo**: `INICIAR-DASHBOARD.command` ya hace `source .env` pero el modelo y base-url no se pasan.

### 4.2 ACD con cloud backend (ALTA)
**Problema**: Con `--backend anthropic`, no hay ACD. Todas las preguntas van al mismo modelo.
**Solución**: Cuando el backend es cloud, usar el ACD solo para clasificar (mostrar badge) pero
enviar todo al modelo cloud. No hay hot-swap necesario.
**Archivo**: `cognitive_loop_v5.py`

### 4.3 Memoria semántica automática (ALTA)
**Problema**: ZOE solo guarda `episodic`. No extrae "el usuario se llama Fernando" como `semantic`.
**Solución**: Después de cada respuesta, extraer hechos y guardarlos como `semantic`.
**Archivo**: `cognitive_loop_v5.py` — después de `self.memory.add(content=f"User: ...")`

### 4.4 Pensamientos visibles en el chat (MEDIA)
**Problema**: Los pensamientos autónomos aparecen en el panel derecho pero no influyen en respuestas.
**Solución**: Incluir últimos 2-3 pensamientos en el prompt del Speaker.
**Archivo**: `speaker.py _build_prompt`

### 4.5 Tutor visible en el chat (MEDIA)
**Problema**: Las intervenciones del MentorAgent solo van a logs.
**Solución**: Enviar intervenciones como mensajes del sistema en el WebSocket.
**Archivo**: `cli_chat.py on_thought callback`

### 4.6 Herramientas/Internet para ZOE (ALTA — "démosle manos")
**Problema**: ZOE no puede buscar en internet ni usar herramientas.
**Solución**: Añadir un `WebSearchActuator` que permita a ZOE buscar en internet.
**Archivo**: Nuevo `zoe/peripherals/web_search.py`

---

## 5. CONFIGURACIÓN ACTUAL DEL USUARIO

- **Hardware**: MacBook Air M3 8GB RAM + SSD Crucial X9 1TB
- **Backend**: MiniMax-M3 via API (compatible Anthropic)
- **URL**: https://api.minimax.io/anthropic
- **Modelos Ollama instalados**: gemma2-9b-iq2, qwq:latest, qwen2.5:32b, deepseek-r1:32b
- **Modelo principal**: MiniMax-M3 (cloud, no bloquea Mac)
- **Memoria**: 525+ entradas en SQLite en SSD
- **Identidad**: hash 66577182772f9dbf... (85 mutaciones)
- **Cápsulas**: 5 base cargadas (162 entradas)

---

## 6. HISTORIAL DE COMMITS (Sprint 5.21)

```
6992ec2 feat(zoe): Activar FilesystemSense + fix scroll + mejorar prompts
70203b6 fix(CRITICAL): Speaker NO incluía memorias relevantes en el prompt
1ba0e5b fix(ROOT CAUSE): Fix JS SyntaxError: missing ) after argument list
cc58e6b fix(tests): Actualizar tests para auth localhost skip
d66db44 fix(DEFINITIVE): Eliminar auth para localhost + eliminar TODO el código JS de tokens
e532105 fix(critical): Launcher auto-actualiza + mata procesos previos
42c3212 fix(critical): Inyectar token via meta tag en vez de script injection
06b6ccd fix(critical): Fix CSS blocked by CSP + model 'auto' not found
ec3da11 fix(critical): GGUF validation + ollama pull fallback
236a893 fix(critical): Fix QwQ-32B GGUF source (bartowski → mradermacher)
6eb44be fix(critical): Eliminar num_parallel de Modelfile
a8dc46d fix(macros): Fix instalación Ollama en macOS (Gatekeeper)
```
