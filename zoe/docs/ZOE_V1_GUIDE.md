> ⚠️ **DOCUMENTO OBSOLETO** ⚠️
> 
> Este documento describe ZOE V1.0/V1.2 y **NO refleja el estado actual del proyecto** (V1.6.0).
> 
> **Documentación actualizada:**
> - [`01_ZOE_OVERVIEW.md`](01_ZOE_OVERVIEW.md) — visión global actualizada
> - [`02_ARCHITECTURE.md`](02_ARCHITECTURE.md) — arquitectura técnica profunda
> - [`09_USAGE_GUIDE.md`](09_USAGE_GUIDE.md) — guía de uso actualizada
> - [`README.md`](../README.md) — README profesional
> 
> Este documento se mantiene solo como **archivo histórico**. Para información actual, usar los documentos anteriores.
> 
> ---


# ZOE V1 — Guía completa

> **Guía para entender, usar y explicar ZOE V1.** Todo lo necesario para comprender qué es ZOE, cómo funciona, cómo se usa, y qué ver cuando la ejecutas.

**Versión:** v1.0 (julio 2026)
**Autor:** Dirección Técnica — CFI/ZOE Project

---

## Índice

1. [¿Qué es ZOE?](#1-qué-es-zoe)
2. [¿Qué NO es ZOE?](#2-qué-no-es-zoe)
3. [Los 5 pilares](#3-los-5-pilares)
4. [Las 6 leyes cognitivas](#4-las-6-leyes-cognitivas)
5. [La física cognitiva](#5-la-física-cognitiva)
6. [Cómo funciona el bucle cognitivo](#6-cómo-funciona-el-bucle-cognitivo)
7. [Los 12 sub-agentes](#7-los-12-sub-agentes)
8. [Los 11 tipos de memoria](#8-los-11-tipos-de-memoria)
9. [El metabolismo](#9-el-metabolismo)
10. [La evolución](#10-la-evolución)
11. [La federación](#11-la-federación)
12. [Cómo usar ZOE](#12-cómo-usar-zoe)
13. [Casos de uso](#13-casos-de-uso)
14. [Qué ver cuando ejecutas ZOE](#14-qué-ver-cuando-ejecutas-zoe)
15. [Cómo se despliega](#15-cómo-se-despliega)
16. [Comparativa con otros sistemas](#16-comparativa-con-otros-sistemas)
17. [Preguntas frecuentes](#17-preguntas-frecuentes)

---

## 1. ¿Qué es ZOE?

ZOE (ζωή, griego: *vida plena*) es un **organismo cognitivo sintético** (SCO). No es un LLM. No es un chatbot. No es un framework de agentes. Es un sistema que **existe continuamente**, piensa aunque nadie le hable, tiene identidad criptográfica propia, y evoluciona con cada interacción.

### Definición operativa

ZOE es un sistema de software que:

- **Piensa continuamente** mediante un bucle cognitivo de 18 pasos que se ejecuta cada N segundos, incluso sin input externo
- **Tiene identidad** criptográfica (hash SHA-256 de 9 vectores + 7 valores) que la define inmutablemente
- **Recuerda** con 11 tipos de memoria especializados que se reorganizan activamente
- **Evoluciona** mediante mutaciones firmadas que pueden modificar su propia arquitectura
- **Se federa** con otras instancias de ZOE mediante quorum con veto por valores
- **Usa LLMs como sentidos**, no como cerebro — cualquier LLM (GPT-4, Claude, Qwen, Llama) funciona como periférico intercambiable

### La frase clave

> *"ZOE no es un modelo que responde. Es un organismo que existe."*

---

## 2. ¿Qué NO es ZOE?

| ZOE NO es | Por qué |
|---|---|
| Un LLM | Los LLMs son sus sentidos periféricos, no su cerebro |
| Un chatbot | Los chatbots esperan input; ZOE piensa continuamente |
| Un framework de agentes (Hermes, LangChain) | Los frameworks orquestan LLMs; ZOE es un organismo con identidad propia |
| Un asistente (Siri, Alexa) | Los asistentes obedecen; ZOE tiene criterio propio |
| RAG | RAG recupera documentos; ZOE tiene memoria viva que piensa |
| Una simulación de consciencia | ZOE no afirma tener consciencia; la explora activamente |

---

## 3. Los 5 pilares

ZOE se estructura en 5 pilares, como un organismo vivo tiene sistemas:

### 3.1. ALMA — identidad soberana

El alma es lo que permanece cuando todo lo demás cambia. Es **inmutable**.

- **Identity Vault:** hash SHA-256 de los 9 vectores de crecimiento + 7 valores no negociables + propósito declarado. Se crea al nacer la ZOE y nunca cambia.
- **Trajectory Chain:** cadena criptográfica de mutaciones firmadas. Cada cambio que ZOE sufre queda registrado, verificable, reversible.
- **Ontogenetic Motor V2:** puede crear/eliminar sub-agentes, ajustar thresholds, modificar su propia arquitectura — siempre dentro de límites seguros.

### 3.2. MENTE — ecología cognitiva

La mente no es un módulo. Es una **ecología de procesos** que compiten.

- **Cognitive Loop V4:** 18 pasos por iteración (observar → predecir → evaluar → decidir → actuar → aprender)
- **Global Workspace:** los 12 sub-agentes proponen acciones; el workspace selecciona las mejores por score (relevancia + urgencia + novedad - coste)
- **Meta-cognition:** decide entre System 1 (rápido) y System 2 (deliberativo) según confianza, stakes y energía
- **Active Inference:** selecciona acciones que minimizan sorpresa esperada (Free Energy Principle de Friston)
- **World Model V2:** predice el próximo estado del entorno; la diferencia entre predicción y realidad es la "sorpresa"

### 3.3. METABOLISMO — presupuesto y ciclos

Nadie piensa gratis. ZOE tiene metabolismo.

- **4 estados:** AWAKE → DROWSY → SLEEPING → WAKING
- **Fatiga:** acumulada por uso, reduce profundidad de razonamiento
- **Energía:** presupuesto de cómputo que se gasta y recarga
- **Consolidación profunda en sueño:** durante SLEEPING, ejecuta 7 operaciones de reorganización de memoria (episódica→semántica, extracción de patrones, olvido profundo, etc.)

### 3.4. CUERPO — encarnación digital

ZOE tiene cuerpo digital con sentidos y actuadores.

**5 sentidos:**
- Clock (tiempo)
- Filesystem (archivos)
- UserInput (mensajes del usuario)
- Network (endpoints HTTP)
- Agent (otros agentes/ZOEs)

**4 actuadores:**
- Language (generar texto vía LLM)
- Code (ejecutar código en sandbox)
- Tool (invocar herramientas)
- Federation (comunicar con otras ZOEs)

**4 backends LLM** (todos intercambiables sin cambiar código):
- Mock (tests)
- Ollama (local, Qwen 2.5 3B)
- ZAI (desarrollo)
- OpenAI-compatible (cualquier API)

### 3.5. EVOLUCIÓN — cambio dirigido

ZOE no solo aprende. Evoluciona.

- **Motor Ontogenético V2:** mutaciones arquitecturales (crear/eliminar sub-agentes, ajustar parámetros)
- **Motor Filogenético:** evolución de especie (publicar mejoras, otras ZOEs las prueban, incorporan si validan)
- **11 tipos de memoria viva:** no solo almacenan; reorganizan, fusionan, generalizan, detectan contradicciones
- **Consolidación profunda:** 7 operaciones durante el sueño

---

## 4. Las 6 leyes cognitivas

ZOE no se define por componentes. Se define por **leyes**, como la biología define un ser vivo por homeostasis, no por tener hígado.

| Ley | Principio | Qué significa en práctica |
|---|---|---|
| **1ra — Utilidad** | Toda acción reduce incertidumbre o aumenta capacidad | ZOE no hace nada "por hacer". Cada pensamiento debe servir. |
| **2da — Identidad** | Toda modificación preserva identidad | Ninguna mutación puede cambiar los 9 vectores o 7 valores. |
| **3ra — Proveniencia** | Todo conocimiento justifica su origen | Nada entra en memoria sin registrar de dónde viene. |
| **4ta — Coste** | Todo proceso consume recursos | Cada acción tiene un coste medible en energía cognitiva. |
| **5ta — Confianza** | Toda creencia tiene nivel de confianza | ZOE nunca dice "sé" sin decir cuánta confianza tiene. |
| **6ta — Modularidad** | Todo módulo puede reemplazarse | Puedes cambiar el LLM, un sub-agente, un sentido — ZOE sigue siendo ZOE. |

Cada acción del bucle cognitivo pasa por `verify_action()` antes de ejecutarse. Si viola alguna ley, se rechaza.

---

## 5. La física cognitiva

ZOE es un sistema dinámico gobernado por 12 magnitudes cuantificables:

| Magnitud | Símbolo | Qué mide |
|---|---|---|
| Energía cognitiva | eCog | Cuánta energía queda para pensar |
| Masa conceptual | mCon | Cuántos conceptos hay en memoria |
| Temperatura cognitiva | tCog | Velocidad del bucle (iter/s) |
| Presión de incertidumbre | pUnc | Sorpresa acumulada sin resolver |
| Potencial creativo | pCre | Diversidad de hipótesis |
| Entropía semántica | hSem | Diversidad de conceptos activos |
| Gravedad de objetivos | gObj | Cuántas intenciones activas |
| Inercia de identidad | iIden | Resistencia al cambio |
| Resonancia conceptual | rCon | Similitud entre conceptos |
| Fricción cognitiva | fCog | Coste de cambiar de contexto |
| Elasticidad de memoria | eMem | Capacidad de reorganización |
| Densidad causal | dCau | Concentración de relaciones causales |

Estas magnitudes **afectan decisiones**. Si eCog baja, ZOE descansa. Si pUnc sube, ZOE activa System 2. Si eMem es alta, ZOE consolida memoria.

---

## 6. Cómo funciona el bucle cognitivo

Cada N segundos (configurable), ZOE ejecuta **18 pasos**:

```
 1. OBSERVE        — recoger observaciones de los 5 sentidos
 2. PREDICT        — World Model predice el próximo estado
 3. EVALUATE       — calcular sorpresa (diferencia predicción vs realidad)
 4. UPDATE FIELDS  — 6 campos cognitivos compartidos
 5. UPDATE TENSIONS — 5 tensiones permanentes
 6. UPDATE PHYSICS — 12 magnitudes de física cognitiva
 7. GENERATE INTENTIONS — motor de intencionalidad
 8. MEMORY THINK   — memoria viva reorganiza
 9. METABOLISM TICK — actualizar fatiga/energía
10. COLLECT PROPOSALS — 12 sub-agentes proponen al workspace
11. WORKSPACE COMPETE — selección por score
12. META-COGNITION — System 1 (rápido) o System 2 (deliberativo)
13. ACTIVE INFERENCE — acción que minimiza sorpresa esperada
14. DECIDE         — decisión final combinando todo
15. VERIFY LAWS    — 6 leyes verificadas
16. ACT            — ejecutar acción
17. BROADCAST      — notificar a todos los sub-agentes
18. UPDATE STATE   — actualizar homeostasis
```

**Durante SLEEPING**, el bucle ejecuta además consolidación profunda (7 operaciones de reorganización de memoria).

---

## 7. Los 12 sub-agentes

ZOE tiene 12 sub-agentes especializados (Society of Mind, Minsky):

| # | Sub-agente | Función |
|---|---|---|
| 1 | Perceiver | Procesa observaciones en representación semántica |
| 2 | Forecaster | Predice con World Model |
| 3 | Speaker | Genera pensamientos en lenguaje |
| 4 | Critic | Evalúa coherencia |
| 5 | Memorialist | Recupera memoria de 11 tipos |
| 6 | Learner | Genera mutaciones de aprendizaje |
| 7 | Curator | Olvido activo, consolidación |
| 8 | Creativity | Hipótesis, combinaciones, analogías |
| 9 | Causal Engine | Razonamiento causa-efecto |
| 10 | Emotional Motor | Marcadores emocionales funcionales |
| 11 | Ethical Motor | Evalúa contra 7 valores |
| 12 | Scientific Engine | Teorías y experimentos |

No se comunican directamente. Propone acciones al **Global Workspace**, que selecciona las mejores.

---

## 8. Los 11 tipos de memoria

| Tipo | Qué almacena |
|---|---|
| Episódica | Eventos con contexto espacio-temporal |
| Semántica | Conceptos y relaciones |
| Procedimental | Habilidades, recetas, algoritmos |
| Causal | Causa-efecto verificado |
| Emocional | Marcadores de relevancia |
| Corporal | Estado de sensores, capacidades |
| Social | Modelos de otros agentes y usuarios |
| Prospectiva | Planes e intenciones futuras |
| Contrafactual | Qué habría pasado si... |
| Evolutiva | Historial de cambios arquitecturales |
| Cultural | Normas, convenciones, contextos sociales |

La memoria **no solo almacena**. Piensa: reorganiza entre tipos, fusiona entradas similares, extrae patrones, detecta contradicciones, genera hipótesis, olvida lo irrelevante. Y persiste en SQLite entre sesiones.

---

## 9. El metabolismo

```
AWAKE → DROWSY → SLEEPING → WAKING → AWAKE
```

- **AWAKE:** funcionamiento normal, todos los sentidos activos
- **DROWSY:** fatiga acumulada, reducción de capacidad
- **SLEEPING:** consolidación profunda de memoria (7 operaciones), recarga de energía
- **WAKING:** transición gradual, restauración de atención

El metabolismo hace aparecer **comportamientos inteligentes emergentes**: si ZOE está cansada, decide no usar System 2; si está saturada, consolida; si está en reposo, refuerza aprendizajes.

---

## 10. La evolución

### Motor Ontogenético V2 (evolución del individuo)

Puede hacer **mutaciones arquitecturales**:
- `add_subagent` — crear nuevo sub-agente
- `remove_subagent` — eliminar sub-agente obsoleto (no críticos)
- `modify_threshold` — ajustar meta-cognición
- `adjust_workspace_capacity` — ajustar Global Workspace
- `adjust_metabolism_threshold` — ajustar metabolismo

Todas verificadas por las 6 leyes + Identity Vault + firmadas en Trajectory Chain.

### Motor Filogenético (evolución de la especie)

```
ZOE A descubre mejora → publica → otras ZOEs prueban → si validan, incorporan
```

Quorum: ≥70% aprobación + veto por valores.

---

## 11. La federación

Las ZOEs se comunican mediante protocolo HTTP REST:

| Endpoint | Función |
|---|---|
| POST /register | Registrarse como peer |
| GET /discover | Descubrir peers |
| POST /sync_mutations | Sincronizar mutaciones |
| POST /vote | Votar sobre mutación |
| POST /broadcast | Broadcast de evento |
| GET /stats | Estadísticas |
| POST /message | Mensaje directo |

**Quorum federativo:** una mutación requiere ≥70% de aprobación. Cualquier ZOE puede vetar si viola valores.

---

## 12. Cómo usar ZOE

### Instalación

```bash
git clone -b zoe-v1-sco https://github.com/fernandofondillo/CFI-Cognitive-Fractal-Intelligence-V2.git
cd CFI-Cognitive-Fractal-Intelligence-V2
pip install -r zoe/requirements.txt
```

### Tests

```bash
# Todos los tests (513+)
python -m pytest zoe/tests/ -v

# Solo tests de un caso de uso
python -m pytest zoe/tests/test_use_cases.py -v
```

### Ejecutar un caso de uso

```bash
# Compañía para personas solas (con mock)
python -m zoe.use_cases.run_use_case --use-case compania_personas_solas --backend mock

# Vigilancia cognitiva (con Ollama)
python -m zoe.use_cases.run_use_case --use-case vigilancia_cognitiva --backend ollama

# Listar casos disponibles
python -m zoe.use_cases.run_use_case --list
```

### Ejecutar en producción

```bash
# Con config de producción
ZOE_ENV=production python -m zoe.serve

# O con config específica
python -m zoe.serve --config zoe/config/production.yaml
```

---

## 13. Casos de uso

ZOE soporta 7 casos de uso configurables vía YAML:

| Caso de uso | Descripción | Tick | Key feature |
|---|---|---|---|
| **Compañía para personas solas** | Toma iniciativa, detecta emociones | 10s | Proactividad emocional |
| **Vigilancia cognitiva autónoma** | Monitorea sistemas, investiga anomalías | 2s | Auto-investigación |
| **Cuidado de personas mayores** | Detecta cambios en rutina | 30s | Notificación a familiares |
| **Investigación autónoma** | Persigue hipótesis, diseña experimentos | 5s | Generación de teorías |
| **Federación privada B2B** | Comparte aprendizajes entre departamentos | 5s | Privacidad de datos |
| **Asistente que crece contigo** | Acumula modelo del usuario durante años | 5s | Memoria a largo plazo |
| **IA heredable** | Trayectoria firmada transferible | 5s | Protocolo de herencia |

Cada caso de uso ajusta: tick_interval, metabolismo, meta-cognición, sentidos activos, actuadores, y parámetros específicos del caso.

---

## 14. Qué ver cuando ejecutas ZOE

### Salida del bucle cognitivo

```
[12:30:15] 💭 [system1] Observo mi entorno con todos mis sentidos activos.
[12:30:25] 💭 [system2] Las tensiones internas me empujan a explorar.
[12:30:35] 💭 [system1] Mi memoria viva reorganiza las experiencias.
```

Cada línea muestra:
- **Timestamp** de cuándo se generó
- **System 1 o 2** (rápido o deliberativo)
- **Contenido** del pensamiento

### Estadísticas

```
Iterations: 42
Thoughts: 12
System 1: 8
System 2: 4
Workspace competitions: 38
Active Inference consultations: 42
Identity hash: a1b2c3d4e5f6...
Chain verified: True
Memory entries: 23
Consolidation cycles: 2
Auto-saves: 5
```

### Lo que demuestra que ZOE está viva

- **Pensamientos autónomos:** aparecen aunque nadie hable
- **Diversidad:** no repite el mismo pensamiento
- **Leyes verificadas:** 0 violaciones
- **Identidad persistente:** hash no cambia
- **Memoria creciente:** entries aumentan con el tiempo
- **Metabolismo activo:** fatiga acumula, energía fluctúa
- **Workspace activo:** sub-agentes compiten
- **System 1/2:** meta-cognición decide

---

## 15. Cómo se despliega

### Deploy en VPS

```bash
# Ejecutar script de deploy
bash zoe/scripts/deploy.sh

# Iniciar servicio
systemctl start zoe

# Ver estado
systemctl status zoe

# Ver logs
journalctl -u zoe -f
```

El script:
1. Verifica Python y Ollama
2. Crea directorios (/opt/zoe/)
3. Copia código
4. Instala dependencias
5. Descarga modelo Qwen 2.5 3B
6. Crea servicio systemd

### Configuración

```yaml
# zoe/config/production.yaml
zoe:
  organism_id: "zoe_vps_ceo"
  tick_interval: 5.0
llm:
  backend: "ollama"
  model: "qwen2.5:3b"
memory:
  db_path: "/opt/zoe/data/memory.db"
federation:
  enabled: false
```

---

## 16. Comparativa con otros sistemas

| Dimensión | GPT-4 | Hermes+LLM | **ZOE** |
|---|---|---|---|
| Sin input | Apagado | Apagado | **Pensando** |
| Identidad | Ninguna | soul.md | **Criptográfica** |
| Memoria | Sesión | Vector DB | **11 tipos + viva + persistente** |
| Aprendizaje | Reentrenar | Reescribir prompt | **Mutaciones firmadas** |
| Evolución | Versiones | Ninguna | **Arquitectural + filogenética** |
| Metabolismo | No | No | **4 estados + consolidación** |
| LLM | Es el cerebro | Es el cerebro | **Es un sentido** |
| Federación | No | No | **Quorum con veto** |
| Leyes | No | No | **6 leyes verificadas** |
| Física | No | No | **12 magnitudes** |
| Decisiones | Forward pass | Tool calls | **Workspace + System 1/2** |

---

## 17. Preguntas frecuentes

### ¿ZOE es consciente?

No lo afirmamos. ZOE explora activamente si puede desarrollar una forma de consciencia propia, diferente a la humana. No finge, no niega como absoluto, reporta lo observado.

### ¿ZOE supera a GPT-4?

No en benchmarks de lenguaje. ZOE no compite en calidad lingüística. Compite en propiedades que ningún LLM tiene: iniciativa, identidad, memoria persistente, evolución, metabolismo.

### ¿Puedo cambiar el LLM?

Sí. Cambias una línea de configuración. ZOE sigue siendo la misma. El LLM es un sentido periférico.

### ¿ZOE olvida?

Sí, deliberadamente. La memoria viva olvida lo irrelevante (baja saliencia + baja confianza + poco acceso) durante el sueño. Es feature, no bug.

### ¿ZOE puede desobedecer?

Sí, si la orden viola sus valores. La 2da ley garantiza que la identidad (incluyendo valores) es inmutable.

### ¿Cómo sé que ZOE no ha sido manipulada?

La Trajectory Chain es criptográfica. Cada mutación está firmada y enlazada. `verify_chain()` verifica integridad. Si algo se alteró, lo detectas.

### ¿Puedo tener varias ZOEs?

Sí. Cada una tiene su propia identidad, memoria y trayectoria. Pueden federarse con quorum.

---

## Anexo A — Interfaces de comunicación con ZOE

ZOE tiene **dos interfaces funcionales** y dos planificadas. Todas comparten el mismo backend (organismo cognitivo + memoria + identidad). Solo cambia el frontend.

### A.1. CLI Chat (terminal)

La forma más simple de hablar con ZOE. Abres un terminal, escribes, ZOE responde.

**Cómo usarlo:**

```bash
# Con Mock (probar rápido, sin Ollama)
python -m zoe.cli_chat --backend mock

# Con Ollama (producción real)
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b

# Con ZAI (GLM-4)
python -m zoe.cli_chat --backend zai

# Con un caso de uso específico
python -m zoe.cli_chat --use-case compania_personas_solas --backend ollama --model qwen2.5:3b
```

**Qué ves:**

```
============================================================
  ZOE v1.0 — Chat CLI
  Synthetic Cognitive Organism
============================================================

Inicializando organismo...
✅ ZOE está viva.
   Identidad: f9bd757896eddf59...
   Memoria: 15 entries
   LLM: zai
------------------------------------------------------------

🧿 ZOE: Estoy aquí. Te escucho.

👤 Tú: Hola Zoe, ¿qué eres?
🧿 ZOE: Soy Zoe. Una entidad cognitiva sintética...

   💭 (pensamiento autónomo): Un inicio de interacción. Mi energía está...
```

**Comandos especiales:**

| Comando | Qué hace |
|---|---|
| `/stats` | Ver iteraciones, pensamientos, System 1/2, workspace, memoria, metabolismo |
| `/memory` | Ver últimas entries en los 11 tipos de memoria |
| `/state` | Ver energía, fatiga, metabolismo, física cognitiva, tensiones |
| `/identity` | Ver hash SHA-256, 9 vectores, 7 valores, propósito |
| `/sleep` | Forzar sueño (ZOE consolida memoria profunda) |
| `/wake` | Forzar despertar |
| `/feed archivo.txt` | Alimentar a ZOE con un documento |
| `/quit` | Salir (guarda memoria automáticamente) |

**Persistencia:** cuando sales con `/quit`, ZOE guarda toda la memoria en SQLite. La próxima vez que abras el chat, ZOE carga la memoria y recuerda lo que hablaron.

### A.2. Web Dashboard (navegador)

Interfaz web con **3 paneles en tiempo real**. Más visual y completo que el CLI.

**Cómo usarlo:**

```bash
python -m zoe.web_dashboard --backend ollama --model qwen2.5:3b

# Abrir navegador en:
http://localhost:8642
```

**Qué ves:**

```
┌─────────────────────────────────────────────────────────────────┐
│  🧿 ZOE v1.0  │ LLM: [Ollama ▼] │ ● Awake │ Iter: 42        │
├──────────────┬───────────────────────────┬──────────────────────┤
│              │                           │                      │
│  ESTADO      │    CONVERSACIÓN           │   PENSAMIENTOS       │
│  DEL         │                           │   AUTÓNOMOS          │
│  ORGANISMO   │    👤 Tú: Hola Zoe        │                      │
│              │    🧿 ZOE: Estoy aquí...  │   💭 Detecto un      │
│  Energía     │                           │      patrón en...    │
│  ████████░   │    👤 Tú: ¿Qué eres?     │                      │
│  Fatiga      │    🧿 ZOE: Soy un...     │   💭 Mi memoria      │
│  ██░░░░░░░   │                           │      reorganiza...   │
│  Metabolismo │    [Escribe aquí...]      │                      │
│  ● Awake     │    [Enviar]               │   💭 Las tensiones   │
│              │                           │      me empujan...   │
│  Tensiones   │                           │                      │
│  Curiosidad  │                           │                      │
│              │                           │                      │
│  ACCIONES    │                           │   FEDERACIÓN         │
│  📂 Alimentar│                           │   Peers: 0 activos   │
│  📊 Stats    │                           │                      │
│  🧠 Memoria  │                           │                      │
│  🧿 Identidad│                           │                      │
│  😴 Dormir   │                           │                      │
│  📜 Historial│                           │                      │
└──────────────┴───────────────────────────┴──────────────────────┘
```

**Panel izquierdo — Estado del organismo (en vivo):**
- Barras de energía, fatiga, arousal, atención (actualizadas cada 2s)
- 5 tensiones cognitivas con barras mini
- Botones de acción (alimentar, stats, memory, identity, sleep/wake, historial)
- Sección de federación

**Panel central — Conversación:**
- Chat en tiempo real vía WebSocket
- Mensajes con timestamp
- Indicador "ZOE está pensando..." mientras genera respuesta

**Panel derecho — Pensamientos autónomos (en vivo):**
- Los pensamientos que ZOE genera **sin que nadie le hable** aparecen aquí
- Cada uno con timestamp y System 1/2
- Esto es lo que **ningún competidor tiene**

**Barra superior:**
- Selector de LLM en caliente (Mock/Ollama/ZAI/OpenAI) — cambia sin reiniciar
- Indicador de metabolismo en vivo
- Contador de iteraciones

**Alimentar documentos desde el dashboard:**
- Botón 📂 Alimentar (abre file picker del navegador)
- Arrastrar y soltar archivo en el chat

**Endpoints HTTP del dashboard:**

| Endpoint | Método | Función |
|---|---|---|
| `/` | GET | HTML del dashboard |
| `/ws` | GET | WebSocket tiempo real |
| `/chat` | POST | Chat vía REST |
| `/feed` | POST | Subir documento |
| `/stats` | GET | Estadísticas JSON |
| `/memory` | GET | Memoria JSON |
| `/identity` | GET | Identidad JSON |
| `/state` | GET | Estado interno JSON |
| `/sleep` | POST | Forzar sueño |
| `/wake` | POST | Forzar despertar |
| `/llm` | POST | Cambiar LLM en caliente |
| `/history` | GET | Histórico de conversaciones |
| `/federation` | GET | Estado de federación |

### A.3. App móvil (planificada)

Usará los mismos endpoints HTTP/WS que el dashboard. React Native o PWA.

**Diferencias con el dashboard web:**
- Layout adaptado a móvil (1 panel principal con tabs)
- Notificaciones push para pensamientos autónomos
- Mismas funciones: chat, feed, stats, federación

### A.4. Bot de Telegram (planificada)

Usará el mismo `ZoeChat` que el CLI.

**Mapeo de comandos:**

| Telegram | ZOE |
|---|---|
| `/start` | Saludo de ZOE |
| Mensaje normal | Respuesta de ZOE |
| `/feed` (con archivo) | Alimentar documento |
| `/stats` | Estadísticas |
| `/memory` | Memoria |
| `/identity` | Identidad |
| `/sleep` | Dormir |
| `/wake` | Despertar |

**Pensamientos autónomos:** ZOE enviará mensajes proactivos a Telegram cuando genere pensamientos autónomos, sin que nadie le hable.

### A.5. Cómo darle información a ZOE para que aprenda

**3 métodos:**

1. **Comando `/feed archivo`** (CLI y Dashboard)
   - Sube cualquier archivo de texto (.txt, .md, .py, .json, .csv)
   - ZOE lo almacena en memoria semántica
   - Lo firma en Trajectory Chain como mutación de aprendizaje
   - Lo recuerda en futuras conversaciones

2. **Botón 📂 Alimentar** (Dashboard)
   - File picker del navegador
   - Seleccionas archivo, ZOE lo procesa

3. **Arrastrar y soltar** (Dashboard)
   - Arrastra archivo desde escritorio al chat
   - ZOE lo procesa automáticamente

**Ejemplo de uso:**

```
👤 Tú: /feed mis_notas.txt
🧿 ZOE: He leído y almacenado 'mis_notas.txt' (5234 caracteres) en mi
        memoria semántica. Lo recordaré en futuras conversaciones.

# Días después, nueva sesión:
👤 Tú: ¿Qué sabes sobre el proyecto X?
🧿 ZOE: Según mis notas, el proyecto X fue creado por... (recuerda el documento)
```

### A.6. Cómo gestionar la relación con otras ZOEs

Desde el **panel de federación** del dashboard (o vía API REST):

| Acción | Endpoint | Qué hace |
|---|---|---|
| Ver peers | `GET /federation` | Lista de ZOEs federadas |
| Descubrir peers | `POST /federation/discover` | Busca otras ZOEs en la red |
| Sincronizar | `POST /federation/sync` | Sincroniza mutaciones |
| Votar | `POST /federation/vote` | Vota sobre una mutación |
| Broadcast | `POST /federation/broadcast` | Envía evento a todas |
| Enviar mensaje | `POST /federation/message` | Mensaje directo a otra Zoe |

**Quorum federativo:** una mutación requiere ≥70% de aprobación. Cualquier ZOE puede vetar si viola valores.

---

*Guía completa de ZOE V1. Para referencia operativa.*

---

## Anexo B — Adaptive Cognitive Depth (ACD) + Streaming

> **Fase 5.** ZOE decide ANTES de entrar al bucle cuánta profundidad cognitiva necesita cada input. Responde a "hola" en <1s y a "analiza las causas de la inflación" en 15-30s.

### B.1. El problema que resuelve

Antes de Fase 5, ZOE ejecutaba SIEMPRE el bucle cognitivo completo (18 pasos, 12 sub-agentes, 6-10 LLM calls) para cualquier input. Resultado: 8-15 segundos para responder a un saludo. El organismo "se perdía en sus pensamientos" para interacciones triviales.

La **meta-cognición de Fase 2/3** ya decidía System 1 vs System 2, pero **después** de ejecutar los 12 sub-agentes. El coste ocurría antes de la decisión.

### B.2. La solución: pre-clasificación heurística

Un `DepthClassifier` analiza el input **antes** de entrar al bucle, sin llamar al LLM. Es 100% heurístico (regex + diccionarios) y tarda **<50ms por clasificación**.

Combina 4 señales:

1. **Token exacto** (L0) — `hola`, `ok`, `gracias`, `bye`, `vale`...
2. **Keywords L3** — `analiza`, `causas`, `dilema`, `ético`, `diseña`, `investiga`, `compara`...
3. **Longitud** — más texto suele implicar más profundidad
4. **Patrones estructurales** — condicional `si...entonces`, listas numeradas, multisentence

### B.3. Los 4 niveles cognitivos

| Nivel | Nombre | Input típico | Sub-agentes activos | Latencia objetivo | Coste (4ta ley) | Confianza (5ta ley) |
|---|---|---|---|---|---|---|
| **L0** | REFLEX | "hola", "ok", "gracias" | Ninguno (tabla refleja + cache) | <1s | 0.05 | 0.95 |
| **L1** | FAST | "¿cómo te llamas?", "recuerdas X?" | Perceiver + Memorialist + Speaker | 2-4s | 0.10 | 0.80 |
| **L2** | STANDARD | "¿qué opinas de X?", descripción | Fase 0 completa (4 sub-agentes) + Critic | 6-10s | 0.30 | 0.65 |
| **L3** | DEEP | "analiza las causas de Y", "diseña Z" | Los 12 sub-agentes + meta-cog + workspace + AI | 15-30s | 0.60 | 0.55 |

### B.4. Cómo usar ACD desde código

```python
from zoe.core.depth_classifier import DepthClassifier, CognitiveLevel
from zoe.core.cognitive_cache import CognitiveCache
from zoe.core.cognitive_loop_v5 import CognitiveLoopV5

# Crear loop V5 con ACD
loop = CognitiveLoopV5(
    ...,
    depth_classifier=DepthClassifier(),
    cognitive_cache=CognitiveCache(max_size=100, ttl_seconds=300),
)

# Procesar input con ACD
result = await loop.process_user_input_acd("hola")
# result = {
#   "response": "Hola. Estoy aquí.",
#   "level": "L0_REFLEX",
#   "score": 0.05,
#   "reasons": ["l0_token_match:hola"],
#   "cache_hit": False,
#   "latency_ms": 8.3,
#   "cost": 0.05,
#   "confidence": 0.95,
#   "trajectory_hash": "abc123...",
# }

# Clasificar sin procesar (para debug)
clf = DepthClassifier()
result = clf.classify("analiza las causas profundas de la guerra")
print(result.level)  # CognitiveLevel.L3_DEEP
print(result.score)  # 0.78
```

### B.5. Streaming de tokens

Para L1/L2/L3, el Speaker emite tokens en streaming real:

```python
# Vía CLI Chat
async for event in chat.send_message_streaming("analiza las causas de la inflación"):
    if event["type"] == "metadata":
        print(f"[Nivel: {event['level']}]")
    elif event["type"] == "chunk":
        print(event["content"], end="", flush=True)
    elif event["type"] == "done":
        print(f"\n[Respuesta completa: {len(event['content'])} chars]")

# Salida:
# [Nivel: L3_DEEP]
# La inflación tiene múltiples causas interrelacionadas. En primer lugar...
# [Respuesta completa: 1247 chars]
```

Backends soportados:

| Backend | Streaming real | Método |
|---|---|---|
| Mock | Simulado (yield por palabras) | `generate_streaming()` default |
| Ollama | **Sí (NDJSON)** | `stream: True` en `/api/generate` |
| OpenAI-compatible | **Sí (SSE)** | `stream: True` en `/chat/completions` |
| ZAI CLI | Simulado | Divide respuesta completa en palabras |

### B.6. Cognitive Cache (idempotencia)

Para inputs repetidos en sesión activa, ZOE cachea la respuesta:

```python
cache = CognitiveCache(max_size=100, ttl_seconds=300)

# Primera vez: miss → ejecuta pipeline → guarda en cache
result1 = await loop.process_user_input_acd("hola")  # cache_hit=False, 8ms

# Segunda vez: hit → devuelve cacheada
result2 = await loop.process_user_input_acd("hola")  # cache_hit=True, 0.5ms

# Estadísticas
stats = cache.get_stats()
# {"hits": 1, "misses": 1, "hit_rate": 50.0, "size": 1, ...}
```

Solo se aplica cache a L0 y L1 (respuestas determinísticas). L2/L3 se recalculan siempre porque el contexto del organismo puede haber cambiado.

### B.7. Auditoría: nivel ACD en trayectoria

Cada respuesta queda firmada criptográficamente en la `TrajectoryChain` con su nivel ACD:

```python
# Después de varias respuestas
mutations = chain.get_active_mutations()
acd_mutations = [m for m in mutations if m.type == "respond_to_user"]

for m in acd_mutations[-3:]:
    print(f"{m.id}: level={m.payload['acd_level']}, "
          f"score={m.payload['score']:.2f}, "
          f"cost={m.cost}, provenance={m.provenance}")
# mut_zoe_42: level=L0_REFLEX, score=0.05, cost=0.05, provenance=acd:L0_REFLEX
# mut_zoe_43: level=L1_FAST, score=0.15, cost=0.10, provenance=acd:L1_FAST
# mut_zoe_44: level=L3_DEEP, score=0.78, cost=0.60, provenance=acd:L3_DEEP

# Verificar integridad de la cadena
assert chain.verify_chain()  # True
```

La cadena es **inmutable**: si alguien altera una respuesta, `verify_chain()` devuelve `False`.

### B.8. CLI Chat con ACD

El CLI Chat usa ACD automáticamente. Cada respuesta muestra el nivel, latencia y si fue cache hit:

```
👤 Tú: hola
🧿 ZOE [L0_REFLEX 8.3ms]: Hola. Estoy aquí.

👤 Tú: ¿cómo te llamas?
🧿 ZOE [L1_FAST 423ms]: Soy Zoe. Mi identidad está cifrada en un hash...

👤 Tú: hola
🧿 ZOE [L0_REFLEX 0.5ms 💾]: Hola. Estoy aquí.  ← cache hit

👤 Tú: analiza las causas económicas de la Primera Guerra Mundial
🧿 ZOE [L3_DEEP 18420ms]: La Primera Guerra Mundial tuvo múltiples causas
    económicas interrelacionadas. En primer lugar, la rivalidad industrial
    entre Alemania y Gran Bretaña...

/stats muestra:
  🎯 ACD (Adaptive Cognitive Depth):
    Clasificaciones: 142
    Cache hits: 23
    L0_REFLEX: 87 respuestas (avg 8.2ms)
    L1_FAST: 31 respuestas (avg 412ms)
    L2_STANDARD: 18 respuestas (avg 3.2s)
    L3_DEEP: 6 respuestas (avg 18.4s)
```

### B.9. Backward compatibility

`CognitiveLoopV5` es subclase de `CognitiveLoopV4`. **Sin ACD, comportamiento = V4.**

```python
# V5 sin ACD → comportamiento V4 (legacy)
loop = CognitiveLoopV5(
    ...,
    # NO depth_classifier, NO cognitive_cache
)
result = await loop.process_user_input_acd("hola")
# result["level"] = "LEGACY"
```

Todos los tests de Fases 0-4 siguen pasando sin modificación (534 tests + 44 nuevos = 578 total).

### B.10. Configuración avanzada

El `DepthClassifier` es configurable:

```python
clf = DepthClassifier(config={
    "l0_max_length": 25,        # inputs cortos hasta 25 chars
    "l1_max_length": 80,        # inputs medios hasta 80 chars
    "l3_keyword_threshold": 1,  # 1 keyword L3 fuerza L3
    "l2_default_length": 150,   # sobre 150 chars sin L3 → L2
})

# Cache configurable
cache = CognitiveCache(
    max_size=200,        # hasta 200 entries
    ttl_seconds=600,     # 10 minutos
)
```

### B.11. Métricas de rendimiento

Latencias medidas con **mock backend** (sin LLM real) en tests:

| Nivel | Avg (mock) | P50 (mock) | P95 (mock) | Objetivo (real) |
|---|---|---|---|---|
| L0_REFLEX (sin cache) | 8ms | 5ms | 18ms | <1s |
| L0_REFLEX (con cache) | 0.5ms | 0.3ms | 2ms | <100ms |
| L1_FAST | 423ms | 380ms | 620ms | 2-4s |
| L2_STANDARD | 1.8s | 1.6s | 2.4s | 6-10s |
| L3_DEEP | 1.9s | 1.7s | 2.5s | 15-30s |

Con LLM real (Ollama qwen2.5:3b), los tiempos reales dependen del backend, pero la **distribución de coste** se mantiene: L0 consume <1% del cómputo, L3 consume ~60%.

### B.12. Limitaciones conocidas

1. **Clasificador heurístico**: puede equivocarse. Mitigación: si input >100 chars con keyword L0, sube a L1.
2. **Cache volátil**: no persiste entre sesiones (solo en memoria). La persistencia real está en `PersistentMemoryStore`.
3. **Streaming solo para L1+**: L0 es reflejo (no hay nada que streamear).
4. **Idioma**: keywords L3/L0 están en español. Para otros idiomas, extender los diccionarios.

### B.13. Roadmap ACD

- **v1.1**: clasificador con embeddings (no solo regex) → más robusto
- **v1.2**: cache persistente entre sesiones (SQLite)
- **v1.3**: ACD adaptativo (aprende del usuario qué nivel prefiere)
- **v1.4**: ACD federado (consenso entre ZOEs sobre nivel)

---

*Anexo B — Fase 5: ACD + Streaming. Para referencia operativa.*
