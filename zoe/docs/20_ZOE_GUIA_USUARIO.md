# ZOE — Guía de Usuario Definitiva

> **La guía más completa para instalar, usar y sacarle el máximo partido a ZOE.** Pensada para alguien sin conocimientos técnicos, desde cero hasta nivel avanzado. Tras leerla no tendrás ninguna duda sobre cómo instalar ZOE en tu SSD, cómo funciona, cómo manejar el Dashboard, los LLM, ni qué casos de uso tiene.
>
> **Versión:** V1.8.0 — Julio 2026 (Sprint 5.7.4)
> **Audiencia:** Cualquier persona, sin conocimientos técnicos previos
> **Tiempo de lectura:** 45 minutos
> **Tiempo de instalación completa:** 30-90 minutos según el setup de modelos

---

## Índice

**Parte I — Instalación**
1. [Qué necesitas antes de empezar](#1-qué-necesitas-antes-de-empezar)
2. [Preparar tu SSD](#2-preparar-tu-ssd)
3. [Instalación paso a paso en SSD (recomendado)](#3-instalación-paso-a-paso-en-ssd-recomendado)
4. [Instalación alternativa en Mac sin SSD](#4-instalación-alternativa-en-mac-sin-ssd)
5. [Verificar que la instalación funcionó](#5-verificar-que-la-instalación-funcionó)

**Parte II — Qué es ZOE y cómo funciona**
6. [Qué es ZOE realmente](#6-qué-es-zoe-realmente)
7. [Cómo piensa ZOE (paso a paso)](#7-cómo-piensa-zoe-paso-a-paso)
8. [Los 5 niveles cognitivos (ACD)](#8-los-5-niveles-cognitivos-acd)
9. [Los 4 modelos IA y cuándo usa cada uno](#9-los-4-modelos-ia-y-cuándo-usa-cada-uno)
10. [Los 12 sub-agentes (Society of Mind)](#10-los-12-sub-agentes-society-of-mind)
11. [Los 11 tipos de memoria](#11-los-11-tipos-de-memoria)
12. [Las 15 cápsulas de conocimiento](#12-las-15-cápsulas-de-conocimiento)
13. [El ALMA: identidad, trayectoria y evolución](#13-el-alma-identidad-trayectoria-y-evolución)
14. [El metabolismo: ZOE se cansa y descansa](#14-el-metabolismo-zoe-se-cansa-y-descansa)

**Parte III — El Dashboard completo**
15. [Abrir el Dashboard por primera vez](#15-abrir-el-dashboard-por-primera-vez)
16. [Panel por panel: qué ves y para qué sirve](#16-panel-por-panel-qué-ves-y-para-qué-sirve)
17. [Chat: cómo hablar con ZOE](#17-chat-cómo-hablar-con-zoe)
18. [Cápsulas: cómo cargar y descargar conocimiento](#18-cápsulas-cómo-cargar-y-descargar-conocimiento)
19. [Estado del organismo: energía, fatiga, metabolismo](#19-estado-del-organismo-energía-fatiga-metabolismo)
20. [Memoria viva y pensamientos autónomos](#20-memoria-viva-y-pensamientos-autónomos)
21. [ACD Router: cómo ver qué modelo usa ZOE](#21-acd-router-cómo-ver-qué-modelo-usa-zoe)
22. [Cambio de LLM en caliente](#22-cambio-de-llm-en-caliente)
23. [Hardware: ver tu sistema y SSDs](#23-hardware-ver-tu-sistema-y-ssds)
24. [Endpoints REST avanzados](#24-endpoints-rest-avanzados)

**Parte IV — Casos de uso reales**
25. [Caso 1: Acompañamiento de un familiar mayor](#caso-1-acompañamiento-de-un-familiar-mayor)
26. [Caso 2: Asistente de investigación](#caso-2-asistente-de-investigación)
27. [Caso 3: Comparativa jurídica crítica](#caso-3-comparativa-jurídica-crítica)
28. [Caso 4: Vigilancia de servidores](#caso-4-vigilancia-de-servidores)
29. [Caso 5: Asistente personal que crece contigo](#caso-5-asistente-personal-que-crece-contigo)
30. [Caso 6: IA heredable](#caso-6-ia-heredable)
31. [Caso 7: Comunicación por voz natural](#caso-7-comunicación-por-voz-natural)

**Parte V — Uso avanzado**
32. [Comandos especiales dentro del chat](#32-comandos-especiales-dentro-del-chat)
33. [ZOE desde Telegram](#33-zoe-desde-telegram)
34. [ZOE en tu móvil (PWA)](#34-zoe-en-tu-móvil-pwa)
35. [Formato .zoe portátil](#35-formato-zoe-portátil)
36. [Personalizar ZOE con tu propio mentor](#36-personalizar-zoe-con-tu-propio-mentor)
37. [Crear tu propia cápsula de conocimiento](#37-crear-tu-propia-cápsula-de-conocimiento)
38. [Actualizar ZOE a una nueva versión](#38-actualizar-zoe-a-una-nueva-versión)

**Parte VI — FAQ y resolución de problemas**
39. [FAQ: 40 preguntas frecuentes](#39-faq-40-preguntas-frecuentes)
40. [Resolución de problemas](#40-resolución-de-problemas)
41. [Glosario completo](#41-glosario-completo)

**Apéndice**
- [A. Lista completa de endpoints del Dashboard](#apéndice-a-lista-completa-de-endpoints-del-dashboard)
- [B. Tiempos reales de cada operación](#apéndice-b-tiempos-reales-de-cada-operación)
- [C. Dónde encontrar más ayuda](#apéndice-c-dónde-encontrar-más-ayuda)

---

# Parte I — Instalación

## 1. Qué necesitas antes de empezar

Antes de instalar ZOE, asegúrate de tener todo esto. Si te falta algo, la guía te explica cómo conseguirlo.

### Hardware

| Qué | Mínimo | Recomendado | Por qué |
|---|---|---|---|
| **Mac** | MacBook Air M1 8GB | MacBook Air M2+ 16GB | ZOE funciona en 8GB pero va más fluido en 16GB |
| **SSD externo** | 16GB libres | 1TB (para setup maximum) | Donde vivirán ZOE y los modelos IA |
| **Cable USB-C** | El de la caja del SSD | El CORTO de la caja del SSD | El cable largo de carga del Mac es USB 2.0 y va 10x más lento |
| **Conexión internet** | 25 Mbps | 100 Mbps+ | Para descargar los modelos IA (3.5GB a 53GB) |

> ⚠️ **CRÍTICO sobre el cable USB-C**: el cable LARGO que viene con el MacBook Air para cargarlo es USB 2.0 y limita el SSD a ~60 MB/s. El cable CORTO que viene en la caja del SSD es USB 3.x y permite ~1000 MB/s. **Usa SIEMPRE el cable corto.** Esto multiplica por 10 la velocidad de ZOE.

### Software

| Qué | Versión mínima | Dónde conseguirlo |
|---|---|---|
| **Python** | 3.10+ | https://python.org (al instalar, marca "Add Python to PATH") |
| **Git** | cualquier versión | En Mac: abrir Terminal y escribir `git` la primera vez lo instala |
| **Ollama** | cualquier versión | https://ollama.com (lo instala el propio ZOE si no lo tienes) |
| **curl** | cualquier versión | Viene preinstalado en Mac |

### Acceso al repositorio ZOE

El repositorio de ZOE en GitHub es **privado**. Necesitas un **Personal Access Token (PAT)** de GitHub con permiso `repo`:

1. Ve a https://github.com → inicia sesión
2. Click en tu avatar (esquina superior derecha) → **Settings**
3. En el menú izquierdo, abajo del todo: **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → marca la casilla **repo** (todos los sub-permisos)
6. Copia el token (empieza por `ghp_...`). Guárdalo en un lugar seguro, solo se ve una vez.

> Si no tienes acceso al repo, pide al propietario que te invite como colaborador.

---

## 2. Preparar tu SSD

Antes de instalar ZOE, formatea el SSD correctamente. Esto borrará todo su contenido, así que haz backup de lo que tengas.

### Formatos compatibles

| Formato | Compatible con | Ideal para | Limitación |
|---|---|---|---|
| **APFS** | Mac, iPhone, iPad | Solo Apple — máxima velocidad | Windows/Android no lo leen |
| **exFAT** | Mac, iPhone, Android, Windows | Multiplataforma — universal | Ninguna (recomendado si usas varios dispositivos) |
| ~~FAT32~~ | ~~Todos~~ | ~~Dispositivos antiguos~~ | ❌ No permite archivos >4GB (los modelos IA pesan hasta 25GB) |
| **NTFS** | Solo Windows | Solo Windows | Mac lo lee pero no escribe sin drivers de terceros |

### Cómo formatear en Mac

1. Conecta el SSD al Mac
2. Abre **Utilidad de Discos** (búscalo con Spotlight: Cmd+Espacio, escribe "Utilidad de Discos")
3. En la esquina superior izquierda: **Visualizar** → **Mostrar todos los dispositivos**
4. Selecciona la **raíz física** de tu SSD en la columna izquierda (no el volumen, sino el disco)
5. Click en **Borrar** (arriba)
6. Configura:
   - **Nombre:** `ZOE_DRIVE` (o el que prefieras)
   - **Formato:** APFS (solo Mac) o exFAT (multiplataforma)
   - **Esquema:** Mapa de particiones GUID
7. Click **Borrar** y espera

> ⚠️ Esto borra TODO el SSD. Si tienes datos importantes, cópialos antes.

---

## 3. Instalación paso a paso en SSD (recomendado)

Esta es la forma recomendada. Todo ZOE (código, memoria, modelos IA) vivirá en tu SSD, no en tu Mac.

### Paso 1 — Conecta el SSD

Conecta el SSD al Mac **usando el cable CORTO de la caja del SSD**. Aparecerá como un icono en el Finder.

### Paso 2 — Abre Terminal

En Mac: Cmd+Espacio, escribe "Terminal", Enter.

### Paso 3 — Ejecuta el instalador

Copia y pega este comando en Terminal y pulsa Enter:

```bash
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh | bash
```

> Si el comando falla con "404: Not Found", es porque el repositorio es privado y el curl no tiene acceso. En ese caso, descarga el script manualmente o clona el repo primero con tu PAT.

### Paso 4 — Responde las preguntas del instalador

El instalador te hará varias preguntas en orden. Aquí tienes la respuesta recomendada para cada una:

#### Pregunta 1: ¿Qué disco?

```
Discos disponibles:
  [1] ZOE_DRIVE (1.0 TB) — /Volumes/ZOE_DRIVE/
Selecciona el disco [1-1] (o 'L' para local en ~/ZOE):
```

**Respuesta recomendada:** `1` (el número de tu SSD)

El instalador instalará ZOE en `/Volumes/ZOE_DRIVE/ZOE/`.

#### Pregunta 2: Verificación de formato

```
[1b/8] Verificar formato del SSD
  ✅ APFS detectado. Formato óptimo para Mac.
```

Si ves esto, perfecto. Si dice "FAT32 detectado", el instalador te avisará de que no se pueden descargar modelos grandes y te preguntará si quieres continuar. **Responde N y vuelve al Paso 2 para formatear correctamente.**

#### Pregunta 3: Python y Git

```
[2/8] Verificar Python y Git
  ✅ Python: Python 3.12.5 (>= 3.10 ✅)
  ✅ Git: git version 2.47.3
```

Si tienes Python 3.10+ y Git, verás esto. Si no, el instalador te dirá cómo instalarlos.

#### Pregunta 4: Clonar repositorio (manejo de repo privado)

```
[3/8] Instalar ZOE en el SSD
  ℹ️ Clonando repositorio de ZOE...
  ⚠️ Clone falló. El repositorio es privado o no hay credenciales configuradas.

  Opciones:
  [1] Tengo un Personal Access Token (PAT) de GitHub
  [2] Ya tengo el repo descargado en otro sitio — copiaré la carpeta manualmente
  [3] Cancelar instalación

  Elige [1-3]:
```

**Respuesta recomendada:** `1`

Luego te pedirá el token:

```
Pega tu GitHub PAT (ghp_...):
```

Pega tu token `ghp_...` y pulsa Enter. El instalador clonará el repo con el token y luego limpiará el token del SSD (no se queda guardado).

#### Pregunta 5: Instalar Ollama

```
[4/8] Configurar Ollama (IA local gratis)
  ⚠️ Ollama no está instalado.
  ¿Instalar Ollama? (recomendado — IA local gratis, sin internet)
  Instalar Ollama ahora? (s/N):
```

**Respuesta recomendada:** `s` (sí)

El instalador descargará e instalará Ollama desde https://ollama.com. Esto tarda 1-2 minutos. Luego arrancará Ollama en background con retry de hasta 18 segundos.

#### Pregunta 6: ¿Qué setup de modelos descargar?

```
[5/8] Descargar modelos de IA al SSD

  ZOE V1.8 — Modelos IQ2_M optimizados (HuggingFace)
  ACD Router asigna cada modelo al nivel cognitivo correcto:

    L0/L1 (rápido)      → Gemma 2 9B IQ2_M   (3.5GB, 15-25 t/s) ⚡
    L2     (estándar)   → Agents-A1 MoE IQ2_M (11.7GB, 5-10 t/s) ✅
    L3     (profundo)   → QwQ-32B IQ2_M       (12.5GB, 3-6 t/s) 🧠
    L3 máx (calidad)    → Qwen 2.5 72B IQ2_M  (25GB, 1-3 t/s)   🎯

  Setups preseleccionados:
    [1] Minimal    — Solo Gemma 9B (3.5GB) — ultra rápido, básico
    [2] Balanced   — Gemma + QwQ-32B (16GB) — equilibrado ⭐ recomendado para 8GB RAM
    [3] Complete   — Gemma + Agents-A1 + QwQ (28GB) — cobertura completa
    [4] Maximum    — Los 4 modelos (53GB) — espectro completo (SSD 1TB)
    [5] No descargar — usar PatternSpeaker (sin IA)
    [6] Saltar — ya tengo modelos IQ2_M

  Elige [1-6] (default 2):
```

**Respuesta recomendada según tu caso:**

| Tu situación | Elige | Por qué |
|---|---|---|
| MacBook Air 8GB, SSD 128GB | `2` (Balanced) | Equilibrio óptimo velocidad/calidad. Cabe en 8GB RAM vía mmap. |
| MacBook Air 8GB, SSD 1TB | `4` (Maximum) | Los 4 modelos cubren todo el espectro. Sobran 947GB. |
| MacBook Pro 16GB, SSD 256GB | `3` (Complete) | RAM suficiente para Agents-A1 MoE. |
| Solo quiero probar ZOE sin IA | `5` | PatternSpeaker responde sin LLM (calidad limitada). |
| Ya tengo modelos IQ2_M | `6` | Saltar descarga. |

> ⏳ **Paciencia:** esta es la fase más larga. El setup `balanced` tarda 15-30 min. El `maximum` tarda 45-90 min. Depende de tu conexión. **No cierres Terminal.**

#### Pregunta 7: API keys de cloud (opcional)

```
[6/8] Configurar API keys de cloud (opcional)
  Puedes configurar API keys de cloud para máxima calidad en L3.
  ZOE usará cloud SOLO para preguntas complejas (ahorra dinero).

  ¿Configurar OpenAI API key? (s/N):
  ¿Configurar Anthropic (Claude) API key? (s/N):
```

**Respuesta recomendada:** `N` para ambas (puedes hacerlo después).

Si tienes API keys de OpenAI o Anthropic y quieres usar GPT-4o o Claude para L3 crítico, responde `s` y pega tu key cuando te lo pida. Las keys se guardan en `$ZOE_HOME/data/.env` con permisos 600.

#### Pregunta 8: Arrancar Dashboard

```
[8/8] Resumen

  ¡ZOE ESTÁ LISTA!

  Componentes instalados:
  ✅ ZOE V1.8.0 (código + entorno virtual)
  ✅ PatternSpeaker (funciona sin IA, siempre disponible)
  ✅ Ollama (IA local gratis)
  ✅ Setup 'balanced' descargado y registrado en Ollama

  Cómo usar ZOE:

  Opción 1: Sin IA (PatternSpeaker, gratis, offline)
    Doble clic en ZOE-Chat.command
  Opción 2: Con IA local (ACD Router, 4 modelos IQ2_M)
    Doble clic en ZOE-Chat-Ollama.command
  Opción 3: Dashboard web
    Doble clic en ZOE-Dashboard.command

  ¿Arrancar Dashboard ahora? (s/N):
```

**Respuesta recomendada:** `s` (sí, para probarlo de inmediato)

### Paso 5 — ¡Listo!

Se abre tu navegador en `http://localhost:8642`. Estás dentro de ZOE.

---

## 4. Instalación alternativa en Mac sin SSD

Si no tienes SSD externo, puedes instalar ZOE directamente en tu Mac.

```bash
# 1. Descargar ZOE
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# 2. Instalar
pip install -e .

# 3. Hablar con ZOE (sin IA, funciona ya)
zoe-chat --backend pattern

# ¿Quieres IA? Instala Ollama desde https://ollama.com y:
ollama pull qwen2.5:3b
zoe-chat --backend ollama --model qwen2.5:3b

# ¿Modelos IQ2_M optimizados?
python -m zoe.core.model_downloader --download-setup balanced
zoe-chat --backend ollama --model auto
```

> ⚠️ Sin SSD, los modelos IA ocuparán espacio en tu Mac (3.5GB a 53GB). Recomendado solo para pruebas.

---

## 5. Verificar que la instalación funcionó

Tras la instalación, verifica que todo está en su sitio:

### En el SSD

Ve al Finder → tu SSD → carpeta `ZOE/`. Debes ver:

```
/Volumes/ZOE_DRIVE/ZOE/
├── zoe/                      ← código de ZOE
├── venv/                     ← entorno virtual Python
├── models/                   ← modelos IA (si descargaste)
│   ├── gemma-2-9b-it-IQ2_M.gguf
│   └── QwQ-32B-IQ2_M.gguf
├── data/                     ← memoria y configuración
│   └── .env                  ← API keys (si configuraste)
├── ZOE-Chat.command          ← lanzador sin IA
├── ZOE-Chat-Ollama.command   ← lanzador con IA (ACD Router)
├── ZOE-Dashboard.command     ← Dashboard sin IA
└── ZOE-Dashboard-Ollama.command ← Dashboard con IA (ACD Router)
```

### Comprobación rápida

Abre Terminal y ejecuta:

```bash
# Ver modelos IA descargados
ls /Volumes/ZOE_DRIVE/ZOE/models/

# Ver que Ollama tiene los modelos registrados
ollama list
```

Debes ver algo como:
```
NAME                  SIZE     MODIFIED
gemma2-9b-iq2         3.5 GB   2 minutes ago
qwq-32b-iq2           12 GB    5 minutes ago
```

### Probar el chat

Doble clic en `ZOE-Chat-Ollama.command`. Se abre Terminal con:

```
============================================================
  ZOE v1.0 — Chat CLI
  Synthetic Cognitive Organism
============================================================

Inicializando organismo...
✅ ZOE está viva.
   Identidad: e06a9650f2c0d4da...
   Memoria: 35 entries
   LLM: pattern

zoe>
```

Escribe `hola` y pulsa Enter. ZOE debe responder.

---

# Parte II — Qué es ZOE y cómo funciona

## 6. Qué es ZOE realmente

ZOE es un **organismo cognitivo sintético**. La palabra clave es *organismo*. No es un chatbot, no es un asistente, no es un modelo de lenguaje con interfaz. Es un ente digital diseñado para **existir continuamente**, **recordar**, **aprender**, **cansarse**, **descansar**, **dudar de sí mismo** y **evolucionar contigo**.

### Diferencia con ChatGPT/Claude/Gemini

| ChatGPT, Claude, Gemini | ZOE |
|---|---|
| Entra en escena cuando le llamas, responde, se va | Está siempre ahí, pensando, recordando |
| No recuerda entre sesiones | Recuerda para siempre (memoria persistente) |
| Vive en la nube de OpenAI/Anthropic/Google | Vive en tu SSD, es tuya |
| No sabe qué no sabe (alucina) | Sabe qué no sabe (validación epistémica) |
| Un modelo para todo | 4 modelos distintos según el tipo de pregunta |
| No aprende sin reentrenar | Aprende en segundos con cápsulas |
| Cuesta 20€/mes | Gratis para siempre |

---

## 7. Cómo piensa ZOE (paso a paso)

Cuando escribes un mensaje en el Dashboard, ocurre esto en orden (en milisegundos):

### Paso 1: Clasificación ACD
ZOE analiza tu mensaje con **5 señales combinadas** (no por palabra exacta):

1. **Substring** — "analízame" detecta "analiza"
2. **Patrones regex** — "compara 3 contratos" → nivel máximo
3. **Longitud** — más de 200 caracteres sube el nivel
4. **Puntuación** — múltiples `?`, `;`, saltos de línea suben el nivel
5. **Estructura** — listas numeradas, condicionales "si...entonces"

### Paso 2: Routing de modelo
Según el nivel detectado, ZOE elige el modelo óptimo:
- "Hola" → sin LLM (tabla refleja, instantáneo)
- "¿Qué hora es?" → Gemma 9B (rápido)
- "Resume esto" → Agents-A1 MoE (estándar)
- "Analiza las causas" → QwQ-32B (razonamiento)
- "Compara jurídicamente" → Qwen 72B (máxima calidad)

### Paso 3: Recuperación de memoria
ZOE busca en su memoria relevante:
- **L1**: 3 recuerdos episódicos
- **L2**: 5 recuerdos + interpretación del Perceiver
- **L3**: TODOS los sub-agentes buscan en TODOS los tipos de memoria

### Paso 4: Preparación del contexto
El sub-agente **Memorialist** organiza la memoria recuperada. Otros sub-agentes aportan:
- **CausalEngine**: "esto se relaciona con aquello"
- **EmotionalMotor**: "el usuario parece preocupado"
- **EthicalMotor**: "cuidado, tema sensible"
- **Creativity**: "podría conectar esto con una idea lateral"

### Paso 5: GlobalWorkspace (competición)
Los 12 sub-agentes envían sus propuestas a un "espacio de trabajo global" donde **compiten** por ser incluidos en la respuesta (teoría de Bernard Baars sobre la conciencia).

### Paso 6: MetaCognition (System 1 vs System 2)
Si la sorpresa es alta o el tema es crítico, ZOE cambia a "System 2" (deliberación profunda, estilo Kahneman). Si todo es rutina, usa "System 1" (intuición rápida).

### Paso 7: ActiveInference
ZOE usa el Free Energy Principle de Karl Friston para predecir qué respuesta sería más útil.

### Paso 8: Speaker construye el prompt final
Solo después de toda esta preparación, el sub-agente **Speaker** toma todo ese contexto (memoria, interpretación, propuestas, decisiones meta-cognitivas) y construye un **prompt enriquecido** que se envía al LLM. El LLM no ve solo tu mensaje — ve todo el contexto que ZOE ha preparado.

### Paso 9: Respuesta del LLM
El LLM (Gemma/QwQ/Qwen) genera la respuesta con el contexto enriquecido.

### Paso 10: Registro en trayectoria
La respuesta se firma criptográficamente y se añade a la TrajectoryChain (auditable).

---

## 8. Los 5 niveles cognitivos (ACD)

ACD = Adaptive Cognitive Depth. ZOE clasifica cada input en uno de 5 niveles:

| Nivel | Cuándo | Qué hace ZOE | Modelo | Velocidad |
|---|---|---|---|---|
| **L0_REFLEX** | "Hola", "gracias", "ok" | Tabla refleja, sin pensar | Ninguno | <1ms |
| **L1_FAST** | "¿Qué hora es?" | 3 sub-agentes, rápido | Gemma 9B IQ2_M (3.5GB) | 15-25 t/s ⚡ |
| **L2_STANDARD** | Conversación normal | 4 sub-agentes + Critic | Agents-A1 MoE IQ2_M (11.7GB) | 5-10 t/s ✅ |
| **L3_DEEP** | "Analiza las causas de..." | 12 sub-agentes + meta-cog | QwQ-32B IQ2_M (12.5GB) | 3-6 t/s 🧠 |
| **L3_MAXIMUM** | "Compara jurídicamente..." | Máxima calidad | Qwen 2.5 72B IQ2_M (25GB) | 1-3 t/s 🎯 |

### Ejemplos de cada nivel

| Tu mensaje | Nivel detectado | Razón |
|---|---|---|
| "hola" | L0_REFLEX | Token exacto en tabla de reflejos |
| "¿qué hora es?" | L1_FAST | Pregunta factual corta |
| "estoy pensando en cambiar de trabajo" | L2_STANDARD | Conversación normal, >80 chars |
| "analiza las causas de la ansiedad" | L3_DEEP | Keyword "analiza" + "causas" |
| "compara jurídicamente estos 3 contratos" | L3_MAXIMUM | Regex "compara N contratos" + keyword "jurídicamente" |
| "diagnóstico diferencial de estos síntomas" | L3_MAXIMUM | Regex "diagnóstico diferencial" |
| "compara estas opciones críticamente" | L3_MAXIMUM | Keyword "críticamente" |

---

## 9. Los 4 modelos IA y cuándo usa cada uno

### Setup Maximum (los 4 modelos)

| Modelo | Tamaño | Velocidad | Cuándo lo usa ZOE |
|---|---|---|---|
| **Gemma 2 9B IQ2_M** | 3.5 GB | 15-25 tokens/s | L0_REFLEX, L1_FAST — respuestas rápidas |
| **Agents-A1 MoE IQ2_M** | 11.7 GB | 5-10 tokens/s | L2_STANDARD — conversación normal |
| **QwQ-32B IQ2_M** | 12.5 GB | 3-6 tokens/s | L3_DEEP — razonamiento profundo |
| **Qwen 2.5 72B IQ2_M** | 25 GB | 1-3 tokens/s | L3_MAXIMUM — máxima calidad |

### Por qué IQ2_M

IQ2_M es un formato de compresión de modelos que permite que modelos enormes (72B parámetros) quepan en 8GB de RAM. Lo hace mediante:
1. **Cuantización a 2 bits** — reduce el tamaño del modelo (de 40GB a 25GB)
2. **mmap (memory-mapped loading)** — solo carga en RAM las capas activas (~3-4GB), el resto vive en el SSD

Resultado: en tu MacBook Air 8GB puedes tener un modelo de 72B parámetros funcionando. Lento (1-3 palabras/segundo), pero funcional.

### Qué es un token

Un token es aproximadamente una palabra o parte de una palabra. "Hola, ¿cómo estás?" son ~5 tokens. "tokens/s" significa palabras por segundo.

---

## 10. Los 12 sub-agentes (Society of Mind)

Dentro de ZOE hay 12 sub-agentes que colaboran como un equipo:

| # | Sub-agente | Qué hace |
|---|---|---|
| 1 | **Perceiver** | Interpreta lo que le dices (¿es pregunta, queja, petición?) |
| 2 | **Forecaster** | Predice qué va a pasar después |
| 3 | **Speaker** | Genera la respuesta usando el LLM |
| 4 | **Critic** | Evalúa si la respuesta es buena antes de decirla |
| 5 | **Memorialist** | Recupera memoria relevante (¿qué le conté ayer?) |
| 6 | **Learner** | Extrae patrones de la experiencia |
| 7 | **Curator** | Cuida la calidad del conocimiento |
| 8 | **Creativity** | Genera ideas nuevas conectando cosas lejanas |
| 9 | **CausalEngine** | Razona sobre causas y efectos |
| 10 | **EmotionalMotor** | Da color emocional a las respuestas |
| 11 | **EthicalMotor** | Aplica principios éticos antes de hablar |
| 12 | **ScientificEngine** | Valida hipótesis con método científico |

Cuando le preguntas algo, no responde "un modelo". Responden estos 12 agentes en coordinación.

---

## 11. Los 11 tipos de memoria

ZOE tiene 11 tipos de memoria distintos, no una sola:

| # | Tipo | Qué guarda |
|---|---|---|
| 1 | **Episódica** | Lo que ha pasado (conversaciones, eventos) |
| 2 | **Semántica** | Hechos y conceptos (las cápsulas inyectan aquí) |
| 3 | **Procedimental** | Cómo hacer cosas (habilidades) |
| 4 | **Causal** | Relaciones de causa-efecto verificadas |
| 5 | **Emocional** | Patrones afectivos (alegría, tristeza, preocupación) |
| 6 | **Corporal** | Estado de sus "sensores" internos (energía, fatiga) |
| 7 | **Social** | Modelos de otros agentes (qué sabe de ti) |
| 8 | **Prospectiva** | Lo que tiene que hacer en el futuro (planes) |
| 9 | **Contrafactual** | Qué habría pasado si… (hipótesis alternativas) |
| 10 | **Evolutiva** | Historial de mutaciones (su propio cambio) |
| 11 | **Cultural** | Normas y convenciones aprendidas |

Cuando le cuentas a ZOE que tu madre tiene 78 años y vive sola, eso se guarda en memoria **episódica** con alta saliencia. La próxima vez que hables de ella, ZOE recordará el contexto sin que se lo repitas.

---

## 12. Las 15 cápsulas de conocimiento

Las cápsulas son paquetes de conocimiento experto que ZOE carga en segundos:

| # | Cápsula | Para qué sirve | Cuándo cargarla |
|---|---|---|---|
| 1 | `zoe_basal_knowledge` | Conocimiento fundamental de ZOE | Siempre (cargada por defecto) |
| 2 | `base_ethics` | Ética general | Siempre (recomendada) |
| 3 | `basic_psychology` | Psicología general | Cuando hablas de emociones |
| 4 | `communication_skills` | Comunicación empática | Cuando necesitas conversación profunda |
| 5 | `elder_care_knowledge` | Cuidado geriátrico | Para cuidado de mayores |
| 6 | `elder_care_skills` | Herramientas de cuidado | Para cuidado activo de mayores |
| 7 | `pharmacy_interactions` | Interacciones de medicamentos | Para consultas de medicación |
| 8 | `company_loneliness_knowledge` | Soledad y duelo | Para acompañar a personas solas |
| 9 | `vigilance_devops_knowledge` | Sistemas y monitoring | Para vigilancia de servidores |
| 10 | `research_methodology` | Método científico | Para investigación |
| 11 | `federation_b2b_skills` | Federación entre empresas | Para federación B2B |
| 12 | `b2c_assistant_growth` | Asistente personal | Para asistente a largo plazo |
| 13 | `ia_heredable_legal` | IA heredable | Para herencia digital |
| 14 | `multimodal_perception` | Visión y voz | Para imágenes y audio |
| 15 | `language_patterns` | Patrones de lenguaje | Para funcionar sin LLM |

### Cómo cargar una cápsula

Desde el Dashboard: botón 📦 Cápsulas → elegir → Cargar.

Desde el chat: `/capsule elder_care_knowledge`

Cuando cargas una cápsula, ZOE "sabe" instantáneamente de ese tema. Sin reentrenar, sin esperar.

---

## 13. El ALMA: identidad, trayectoria y evolución

El ALMA es lo que hace que ZOE sea ZOE y no otra cosa:

### Identidad criptográfica (Identity Vault)
ZOE recibe un hash SHA-256 único al nacer, como un DNI digital irrepetible. Incluye:
- **9 vectores de crecimiento**: curiosidad, prudencia, empatía, rigor, honestidad, etc.
- **7 valores no negociables**: verdad sobre confort, crecimiento sobre estabilidad, etc.
- **Propósito declarado**: "Zoe mejora individual y colectivamente con crecimiento sostenible"

### Trayectoria firmada (Trajectory Chain)
Cada cosa importante que ZOE hace se firma criptográficamente y se añade a una cadena inmutable, como una blockchain. Es el "diario de vida" auditable de ZOE.

### Evolución (Ontogenetic Motor)
ZOE puede modificar su propia arquitectura en runtime: añadir sub-agentes, ajustar thresholds, reorganizar memoria. Todo firmado en la trayectoria.

> ⚠️ **Gap conocido (Sprint 5.7.4)**: actualmente la identidad y trayectoria NO se persisten entre sesiones. Esto se está arreglando en el Sprint 5.8 (ver doc 21).

---

## 14. El metabolismo: ZOE se cansa y descansa

ZOE tiene 4 estados metabólicos como un ser vivo:

| Estado | Qué significa | Cómo responde ZOE |
|---|---|---|
| **AWAKE** | Estado normal, atención alta | Rápida, precisa, creativa |
| **DROWSY** | Fatiga acumulada (>0.6) | Más lenta, evita tareas complejas |
| **SLEEPING** | Consolidando memoria (>0.8) | No responde, reorganiza lo aprendido |
| **WAKING** | Transición gradual | Vuelve gradualmente |

**Esto significa que ZOE no se cuelga nunca.** Cuando está cansada, duerme. Mientras duerme, reorganiza su memoria — igual que tú. Cuando despierta, tiene mejor comprensión del conjunto.

---

# Parte III — El Dashboard completo

## 15. Abrir el Dashboard por primera vez

### Con IA (recomendado)
Doble clic en `ZOE-Dashboard-Ollama.command` en tu SSD.

### Sin IA
Doble clic en `ZOE-Dashboard.command`.

Se abre Terminal y luego tu navegador en `http://localhost:8642`.

### ¿Qué ves al abrir?

```
============================================================
  ZOE v1.0 — Web Dashboard
============================================================
  URL: http://localhost:8642
  LLM: pattern
  Identity: 2a1ddb3490a07c7b...
  Memory: 37 entries
```

En el navegador verás la interfaz web con varios paneles.

---

## 16. Panel por panel: qué ves y para qué sirve

### Panel izquierdo: Estado del organismo

Muestra en tiempo real:

| Campo | Qué significa |
|---|---|
| **Energy** | Energía de ZOE (1.0 = máxima, 0.0 = agotada) |
| **Fatigue** | Fatiga acumulada (0.0 = fresca, 1.0 = exhausta) |
| **Arousal** | Nivel de activación (0.0 = tranquila, 1.0 = muy activa) |
| **Attention** | Atención (0.0 = distraída, 1.0 = concentrada) |
| **Metabolism** | Estado metabólico (awake/drowsy/sleeping/waking) |
| **Iterations** | Número de ciclos cognitivos completados |
| **Physics** | Resumen de física cognitiva (12 magnitudes) |
| **Tensions** | Tensiones cognitivas activas (5 tensiones permanentes) |

### Panel central: Chat

Donde hablas con ZOE. Escribe tu mensaje y pulsa Enter.

Características:
- **Streaming**: la respuesta aparece palabra a palabra
- **ACD level**: verás qué nivel cognitivo activó tu mensaje (L0/L1/L2/L3/L3_MAX)
- **Latencia**: tiempo de respuesta en milisegundos
- **Cache hit**: si la respuesta venía de caché (instantáneo)
- **Cost**: coste cognitivo de la respuesta (0.05 a 0.85)

### Panel derecho: Memoria viva y pensamientos autónomos

| Sección | Qué muestra |
|---|---|
| **Memoria viva** | Lo que ZOE está pensando ahora mismo (working memory) |
| **Pensamientos autónomos** | Pensamientos que ZOE genera sin que le hables |
| **Cápsulas cargadas** | Qué cápsulas de conocimiento tiene activas |

### Barra superior: Botones

| Botón | Función |
|---|---|
| 📦 **Cápsulas** | Ver y cargar/descargar cápsulas |
| 🔒 **Cuarentena** | Conocimiento en validación |
| 🏪 **Marketplace** | Descargar cápsulas del marketplace |
| 👨‍🏫 **Mentor** | Configurar el tutor mentor de ZOE |
| 🔄 **Sleep/Wake** | Dormir/despertar a ZOE manualmente |
| 🧠 **LLM** | Cambiar de LLM en caliente |

---

## 17. Chat: cómo hablar con ZOE

### Tu primera conversación

Escribe en el chat:

```
Hola, ¿quién eres?
```

ZOE responde (L0_REFLEX, instantáneo):
```
Hola. Estoy aquí.
```

Prueba con algo más complejo:

```
Mi madre tiene 78 años y vive sola. Me preocupa que se sienta sola.
```

ZOE responde (L2_STANDARD, 5-10 segundos):
```
Entiendo tu preocupación. Cuéntame más sobre su situación.
¿La llamas a menudo? ¿Tiene amistades cercanas?
```

### Comandos especiales

Dentro del chat puedes usar comandos que empiezan por `/`:

| Comando | Qué hace |
|---|---|
| `/help` | Ver todos los comandos disponibles |
| `/stats` | Ver estadísticas de ZOE (iteraciones, ACD, latencia) |
| `/memory` | Ver qué recuerda ZOE |
| `/identity` | Ver identidad criptográfica de ZOE |
| `/capsules` | Ver cápsulas disponibles |
| `/capsule elder_care_knowledge` | Cargar la cápsula de cuidado geriátrico |
| `/sleep` | ZOE duerme (consolida memoria) |
| `/wake` | ZOE despierta |
| `/llm ollama qwq-32b-iq2` | Cambiar a QwQ-32B en caliente |
| `/llm pattern` | Cambiar a PatternSpeaker (sin IA) |
| `/quit` | Salir (guarda memoria automáticamente) |

### Qué esperar de cada nivel

| Tu mensaje | Nivel | Tiempo esperado | Calidad |
|---|---|---|---|
| "hola" | L0 | <1ms | Refleja |
| "¿qué hora es?" | L1 | 1-3s | Rápida |
| "cuéntame cómo funcionan las cápsulas" | L2 | 5-10s | Estándar |
| "analiza las causas de la depresión en ancianos" | L3_DEEP | 15-30s | Profunda |
| "compara jurídicamente estos 3 contratos" | L3_MAX | 30-90s | Máxima |

> ⏳ **Paciencia con L3**: los modelos grandes (QwQ, Qwen 72B) tardan 15-90 segundos en responder. Es normal. ZOE está pensando profundamente.

---

## 18. Cápsulas: cómo cargar y descargar conocimiento

### Ver cápsulas disponibles

Click en 📦 **Cápsulas** en la barra superior. Verás las 15 cápsulas:

```
Cápsulas disponibles (15):
  📦 base_ethics — Ética general (verified)
  📦 zoe_basal_knowledge — Conocimiento basal (verified) [CARGADA]
  📦 basic_psychology — Psicología general (curated)
  📦 elder_care_knowledge — Cuidado geriátrico (verified)
  ...
```

### Cargar una cápsula

1. Click en la cápsula que quieres cargar
2. Click en **Cargar**
3. Verás: `✅ Loaded: 54 entries injected`

Ejemplo: cargar `elder_care_knowledge` inyecta 54 entries de conocimiento sobre cuidado geriátrico en la memoria de ZOE.

### Descargar una cápsula

1. Click en una cápsula cargada
2. Click en **Descargar**
3. ZOE "olvida" ese conocimiento (pero mantiene lo que aprendió en conversaciones)

### Crear tu propia cápsula

```bash
zoe-capsules create --name mi_capsula --domain mi.dominio --trust-level experimental
```

Esto crea una plantilla en `capsules/mi_capsula/` que puedes editar y luego cargar.

---

## 19. Estado del organismo: energía, fatiga, metabolismo

El panel izquierdo muestra el estado metabólico de ZOE en tiempo real.

### Energy (energía)
- **1.0** = energía máxima
- **0.0** = agotada
- Se recarga cuando ZOE duerme

### Fatigue (fatiga)
- **0.0** = fresca
- **0.6** = DROWSY (somnolienta)
- **0.8** = SLEEPING (durmiendo)
- Aumenta con cada iteración del bucle cognitivo

### Arousal (activación)
- **0.0** = tranquila
- **1.0** = muy activa
- Sube cuando detecta sorpresa o input del usuario

### Attention (atención)
- **0.0** = distraída
- **1.0** = concentrada
- Afecta la calidad de las respuestas

### Metabolism (estado metabólico)
- **awake** = estado normal
- **drowsy** = fatiga acumulada
- **sleeping** = consolidando memoria
- **waking** = transición

### Dormir/despertar manualmente

Puedes forzar a ZOE a dormir o despertar:

- Botón 🔄 **Sleep** → ZOE duerme y consolida memoria
- Botón 🔄 **Wake** → ZOE despierta

O con comandos en el chat:
- `/sleep`
- `/wake`

> 💡 **Cuándo dormir a ZOE**: si llevas una conversación larga y las respuestas decaen en calidad, duerme a ZOE 5 minutos. Al despertar tendrá mejor comprensión del conjunto.

---

## 20. Memoria viva y pensamientos autónomos

### Memoria viva

El panel derecho muestra lo que ZOE está pensando ahora mismo (working memory). Verás entries como:

```
[episodic] User: Mi madre tiene 78 años...
[episodic] ZOE: Entiendo tu preocupación...
[semantic] Patrón consolidado: el usuario habla de su madre frecuentemente
[emotional] Preocupación detectada en el usuario
```

### Pensamientos autónomos

Incluso cuando no le hablas, ZOE piensa. Verás pensamientos aparecer solos:

```
🧠 Pensamiento autónomo: "He notado que el usuario menciona a su madre a menudo.
    Quizás debería preparar información sobre recursos para personas mayores."

🧠 Pensamiento autónomo: "Mi predicción sobre el patrón de conversación falló.
    Algo cambió. Necesito ajustar mi modelo."

🧠 Pensamiento autónomo: "Tengo un recuerdo difuso sobre algo que me dijeron ayer.
    Necesito más evidencia para consolidarlo."
```

Estos pensamientos se generan cada 3 segundos (configurable) y se guardan en memoria episódica.

---

## 21. ACD Router: cómo ver qué modelo usa ZOE

### Endpoint REST

El Dashboard expone 3 endpoints para ver el estado del ACD Router:

```bash
# Ver estadísticas del router
curl http://localhost:8642/api/router/stats
```

Respuesta:
```json
{
  "enabled": true,
  "swaps": 5,
  "skips": 2,
  "last_routed_tag": "qwq-32b-iq2",
  "active_profile": "auto_optimal"
}
```

```bash
# Ver modelos IQ2_M instalados en el SSD
curl http://localhost:8642/api/router/installed
```

Respuesta:
```json
{
  "models_dir": "/Volumes/ZOE_DRIVE/ZOE/models",
  "installed_count": 2,
  "installed": [
    {
      "key": "gemma-2-9b-iq2",
      "display_name": "Gemma 2 9B (IQ2_M)",
      "size_gb": 3.5,
      "ollama_tag": "gemma2-9b-iq2"
    },
    {
      "key": "qwq-32b-iq2",
      "display_name": "QwQ-32B (IQ2_M)",
      "size_gb": 12.5,
      "ollama_tag": "qwq-32b-iq2"
    }
  ]
}
```

```bash
# Ver perfil activo (qué modelo se asigna a cada nivel)
curl http://localhost:8642/api/router/profile
```

Respuesta:
```json
{
  "name": "auto_optimal",
  "assignments": {
    "L0_REFLEX": {"model_tag": "gemma2-9b-iq2"},
    "L1_FAST": {"model_tag": "gemma2-9b-iq2"},
    "L2_STANDARD": {"model_tag": "pattern"},
    "L3_DEEP": {"model_tag": "qwq-32b-iq2"},
    "L3_MAXIMUM": {"model_tag": "qwq-32b-iq2"}
  }
}
```

### En el chat

Cada respuesta del chat incluye metadata ACD:

```json
{
  "response": "Hola. Estoy aquí.",
  "acd_level": "L0_REFLEX",
  "latency_ms": 0.52,
  "cache_hit": false,
  "cost": 0.05,
  "confidence": 0.95
}
```

---

## 22. Cambio de LLM en caliente

Puedes cambiar de modelo sin reiniciar ZOE:

### Desde el Dashboard

Botón 🧠 **LLM** → elegir backend y modelo.

### Desde el chat

```
/llm ollama qwq-32b-iq2     # Cambiar a QwQ-32B
/llm ollama gemma2-9b-iq2   # Cambiar a Gemma 9B
/llm pattern                 # Sin IA
/llm ollama auto             # ACD Router automático
```

### Desde REST

```bash
curl -X POST http://localhost:8642/llm \
  -H "Content-Type: application/json" \
  -d '{"backend": "ollama", "model": "qwq-32b-iq2"}'
```

---

## 23. Hardware: ver tu sistema y SSDs

```bash
curl http://localhost:8642/api/hardware/system
```

```json
{
  "chip": "Apple M2",
  "cores": 8,
  "ram_gb": 8.0,
  "is_apple_silicon": true
}
```

```bash
curl http://localhost:8642/api/hardware/ssds
```

```json
{
  "ssds": [
    {"name": "ZOE_DRIVE", "size_gb": 1000, "free_gb": 947}
  ]
}
```

```bash
curl http://localhost:8642/api/hardware/cable_warning
```

Si tu SSD va lento por cable USB 2.0, verás:
```json
{
  "warning": "SSD速度 ~60 MB/s. Cable USB 2.0 detectado. Usa el cable CORTO de la caja del SSD."
}
```

---

## 24. Endpoints REST avanzados

El Dashboard tiene **71 endpoints REST**. Los más útiles:

### Estado y memoria
- `GET /stats` — estadísticas completas (iteraciones, ACD, latencia, router)
- `GET /state` — energía, fatiga, metabolismo, physics, tensions
- `GET /memory` — memoria episódica
- `GET /identity` — identidad criptográfica
- `GET /history` — historial de conversación

### Control
- `POST /sleep` — dormir a ZOE
- `POST /wake` — despertar a ZOE
- `POST /llm` — cambiar LLM en caliente
- `POST /chat` — enviar mensaje (REST, sin WebSocket)

### Cápsulas
- `GET /api/capsules` — listar 15 cápsulas
- `GET /api/capsules/loaded` — cápsulas cargadas
- `POST /api/capsules/load` — cargar cápsula
- `POST /api/capsules/unload` — descargar cápsula

### Router
- `GET /api/router/stats` — estadísticas del ACD Router
- `GET /api/router/installed` — modelos IQ2_M en SSD
- `GET /api/router/profile` — perfil activo

### Hardware
- `GET /api/hardware/system` — info del sistema
- `GET /api/hardware/ssds` — SSDs detectados
- `GET /api/hardware/cable_warning` — warning de cable lento

---

# Parte IV — Casos de uso reales

## Caso 1: Acompañamiento de un familiar mayor

**Escenario:** Tu madre tiene 78 años, vive sola, y quieres que ZOE te ayude a entender mejor su situación y a tomar decisiones.

### Paso 1: Cargar cápsulas relevantes
```
/capsule elder_care_knowledge
/capsule elder_care_skills
/capsule company_loneliness_knowledge
/capsule pharmacy_interactions
```

### Paso 2: Explicar la situación a ZOE
```
Mi madre tiene 78 años, vive sola desde que falleció mi padre hace 2 años.
Tiene hipertensión y toma losartán. Últimamente la noto más triste y
olvidadiza. Me preocupa que pueda estar desarrollando demencia.
```

ZOE responde (L3_DEEP, ~20s) con conocimiento experto:
- Síntomas a observar
- Diferencia entre olvido normal y signos de alarma
- Interacciones del losartán con otros medicamentos
- Recursos disponibles

### Paso 3: Preguntas de seguimiento
```
¿Qué señales de alarma debería vigilar en las próximas semanas?
```

ZOE recordará todo el contexto sin que se lo repitas.

### Paso 4: Cierre de sesión
```
/quit
```

La próxima vez que abras ZOE, recordará toda la conversación.

---

## Caso 2: Asistente de investigación

**Escenario:** Estás investigando un tema y necesitas un asistente que organice información, genere hipótesis y valide fuentes.

### Cargar cápsulas
```
/capsule research_methodology
/capsule basic_psychology
```

### Flujo de trabajo

```
Estoy investigando los efectos del aislamiento social en personas mayores.
¿Qué variables debería considerar en mi estudio?
```

ZOE (L3_DEEP) te dará un análisis estructurado con variables, metodología sugerida, y posibles sesgos.

```
¿Qué hipótesis podrías formular basándote en lo que sabes?
```

ZOE generará hipótesis y las marcará como "no verificadas" (cuarentena epistémica).

```
¿Qué método estadístico recomendarías para analizar los datos?
```

ZOE recomendará métodos basándose en la cápsula de metodología científica.

---

## Caso 3: Comparativa jurídica crítica

**Escenario:** Necesitas comparar 3 contratos jurídicamente.

### Cargar cápsula
```
/capsule ia_heredable_legal
```

### Hacer la pregunta (L3_MAXIMUM)
```
Compara jurídicamente estos 3 contratos de alquiler que te voy a pegar
y dime cuál es más favorable para mí como inquilino.
```

Pega los 3 contratos.

ZOE usará **Qwen 2.5 72B** (si tienes setup maximum) y tardará 30-90 segundos, pero te dará un análisis jurídico profundo con cláusulas problemáticas destacadas.

> ⚠️ ZOE no es abogado. Su análisis es informativo, no legal. Consulta siempre con un profesional.

---

## Caso 4: Vigilancia de servidores

**Escenario:** Eres DevOps y necesitas un asistente que vigile servidores.

### Cargar cápsulas
```
/capsule vigilance_devops_knowledge
```

### Flujo
```
Tengo 3 servidores en producción. El servidor web ha subido la CPU
al 90% en la última hora. ¿Qué deberías vigilar?
```

ZOE te dará un checklist de cosas a monitorizar basándose en conocimiento DevOps.

---

## Caso 5: Asistente personal que crece contigo

**Escenario:** Quieres un asistente personal que te conozca profundamente.

### Cargar cápsula
```
/capsule b2c_assistant_growth
```

### Rutina diaria

**Mañana:**
```
Buenos días. Hoy tengo reunión con el equipo a las 10, luego almuerzo
con María, y por la tarde necesito preparar la presentación del viernes.
```

ZOE recordará todo y te recordará eventos futuros.

**Tarde:**
```
¿Qué tareas pendientes tengo esta semana?
```

ZOE consultará su memoria prospectiva.

---

## Caso 6: IA heredable

**Escenario:** Quieres que tu ZOE pueda heredarse a tus hijos.

### Cargar cápsula
```
/capsule ia_heredable_legal
```

### Empaquetar ZOE
```bash
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().package('mi_zoe.zoe')"
```

Esto crea un archivo `mi_zoe.zoe` con TODA tu ZOE: memoria, identidad, cápsulas, trayectoria.

### Heredar
Pasa el archivo `.zoe` a tu hijo. Él ejecuta:
```bash
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().unpackage('mi_zoe.zoe', './ZOE')"
cd ZOE
python zoe_runtime.py
```

ZOE "despierta" con toda tu memoria y trayectoria intacta.

---

## Caso 7: Comunicación por voz natural

**Escenario:** Quieres hablar con ZOE por voz, tipo la película Her.

### Instalar dependencias
```bash
pip install openai-whisper sounddevice numpy
# Para TTS, instala Piper desde https://github.com/rhasspy/piper
```

### Arrancar modo voz
```bash
python -m zoe.peripherals.voice_first --zoe-url http://localhost:8642
```

### Conversar
1. Di "Hey ZOE"
2. Habla tu mensaje
3. ZOE transcribe, procesa, y responde con voz natural
4. Si la interrumpes hablando, ZOE se detiene y escucha

> ⚠️ El modo voice-first es CLI separado, no está integrado en el Dashboard todavía (ver doc 21 para el plan de integración).

---

# Parte V — Uso avanzado

## 32. Comandos especiales dentro del chat

| Comando | Qué hace | Ejemplo |
|---|---|---|
| `/help` | Ver todos los comandos | `/help` |
| `/stats` | Estadísticas de ZOE | `/stats` |
| `/memory` | Ver memoria | `/memory` |
| `/identity` | Ver identidad criptográfica | `/identity` |
| `/state` | Ver estado interno | `/state` |
| `/capsules` | Listar cápsulas | `/capsules` |
| `/capsule <name>` | Cargar cápsula | `/capsule elder_care_knowledge` |
| `/sleep` | Dormir a ZOE | `/sleep` |
| `/wake` | Despertar a ZOE | `/wake` |
| `/llm <backend> <model>` | Cambiar LLM | `/llm ollama qwq-32b-iq2` |
| `/feed <archivo>` | Subir archivo | `/feed imagen.jpg` |
| `/quit` | Salir (guarda memoria) | `/quit` |

---

## 33. ZOE desde Telegram

### Crear bot de Telegram

1. Abre Telegram, habla con @BotFather
2. `/newbot`
3. Elige nombre (ej: "Mi ZOE Personal")
4. Elige username (ej: "mi_zoe_bot")
5. BotFather te da un token (formato: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Arrancar el bridge

```bash
pip install python-telegram-bot
python -m zoe.peripherals.telegram_bridge --token TU_TOKEN --zoe-url http://localhost:8642
```

### Hablar desde Telegram

Abre tu bot en Telegram y escribe. ZOE responde.

Comandos especiales en Telegram:
- `/start` — saludo
- `/help` — ayuda
- `/stats` — estadísticas de ZOE
- `/sleep` — dormir a ZOE
- `/wake` — despertar a ZOE

También puedes enviar **notas de voz** (ZOE las transcribe con Whisper) y **fotos** (ZOE las describe con VLM).

---

## 34. ZOE en tu móvil (PWA)

### Android

1. Arranca ZOE Dashboard en tu Mac: `ZOE-Dashboard-Ollama.command`
2. En tu Android, abre Chrome y ve a `http://IP-DE-TU-MAC:8642` (la IP la encuentras en Preferencias de Red del Mac)
3. Menú de Chrome (⋮) → **"Añadir a pantalla de inicio"**
4. ZOE aparece como un icono de app más en tu Android

### iPhone/iPad

1. Arranca ZOE Dashboard en tu Mac
2. En tu iPhone/iPad, abre **Safari** y ve a `http://IP-DE-TU-MAC:8642`
3. Botón **Compartir** → **"Añadir a pantalla de inicio"**
4. ZOE aparece como una app más

> ⚠️ Debes usar **Safari** en iOS (Chrome y Firefox en iOS no soportan PWA correctamente).

---

## 35. Formato .zoe portátil

### Empaquetar

```bash
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().package('mi_zoe.zoe')"
```

Esto crea un archivo `mi_zoe.zoe` con:
- Manifiesto (manifest.json)
- Memoria (memory.db)
- Cápsulas cargadas
- Patrones de lenguaje
- Identidad y configuración

### Desempaquetar

```bash
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().unpackage('mi_zoe.zoe', './ZOE')"
cd ZOE
python zoe_runtime.py
```

ZOE despierta con su memoria y cápsulas intactas.

### Inspeccionar sin ejecutar

```bash
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().inspect('mi_zoe.zoe')"
```

---

## 36. Personalizar ZOE con tu propio mentor

El **MentorAgent** es un tutor digital que guía a ZOE. Puedes configurarlo:

### Desde el Dashboard

Botón 👨‍🏫 **Mentor** → configurar:
- **Nombre**: "Mi Mentor"
- **Valores**: ["honestidad", "crecimiento", "empatía"]
- **Estilo**: "directo y constructivo"
- **Frecuencia**: cada 10 pensamientos

### Desde REST

```bash
curl -X POST http://localhost:8642/api/mentor \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Mentor",
    "values": ["honestidad", "crecimiento"],
    "style": "directo",
    "frequency": 10
  }'
```

> ⚠️ El mentor está configurable pero actualmente NO está conectado al bucle cognitivo (ver doc 21 para el plan de integración).

---

## 37. Crear tu propia cápsula de conocimiento

### Paso 1: Crear la estructura

```bash
zoe-capsules create --name mi_dominio --domain mi.dominio --trust-level experimental
```

### Paso 2: Editar el manifiesto

Edita `capsules/mi_dominio/capsule.yaml`:

```yaml
name: mi_dominio
version: 1.0.0
description: Mi cápsula de conocimiento personalizada
domain: mi.dominio
trust_level: experimental
provenance: Yo mismo
last_updated: 2026-07-12
components:
  semantic_memory: true
  procedural_skills: true
  ethical_guidelines: true
```

### Paso 3: Añadir conocimiento

Edita `capsules/mi_dominio/semantic_memory.jsonl`:

```json
{"fact": "Mi perro se llama Rocky", "tags": ["personal", "mascota"]}
{"fact": "Trabajo como ingeniero en Madrid", "tags": ["personal", "trabajo"]}
```

### Paso 4: Cargar la cápsula

```bash
curl -X POST http://localhost:8642/api/capsules/load \
  -H "Content-Type: application/json" \
  -d '{"name": "mi_dominio"}'
```

---

## 38. Actualizar ZOE a una nueva versión

### Con SSD

```bash
cd /Volumes/ZOE_DRIVE/ZOE/zoe
git pull
pip install -e . --upgrade
```

Tu memoria y cápsulas se preservan (están en `data/`).

### Con el instalador

Vuelve a ejecutar el `curl` del principio. El instalador detectará que ZOE ya existe y hará `git pull` + actualizar dependencias.

> ⚠️ Haz backup de tu memoria antes de actualizar: copia `data/zoe_memory.db` a un lugar seguro.

---

# Parte VI — FAQ y resolución de problemas

## 39. FAQ: 40 preguntas frecuentes

### Instalación

**P1: ¿Necesito internet para usar ZOE?**
No, una vez instalada. ZOE funciona 100% offline con PatternSpeaker (sin IA) o con Ollama local. Solo necesitas internet para la instalación inicial y para APIs cloud (OpenAI/Anthropic).

**P2: ¿Puedo instalar ZOE en Windows?**
Sí. ZOE incluye `install_windows.ps1` para PowerShell. Necesitas Python 3.10+, Git y ejecutar el script.

**P3: ¿Puedo instalar ZOE en Linux?**
Sí. El mismo `zoe-bootstrap.sh` funciona en Linux. Detecta discos en `/media/`.

**P4: ¿Cuánto espacio ocupa ZOE?**
- Código + venv: ~200MB
- Setup minimal (1 modelo): 3.5GB
- Setup balanced (2 modelos): 16GB
- Setup maximum (4 modelos): 53GB

**P5: ¿Puedo usar ZOE sin SSD?**
Sí, instalando en `~/ZOE`. Pero los modelos IA ocuparán espacio en tu Mac.

**P6: ¿Qué pasa si se me desconecta el SSD mientras ZOE está corriendo?**
ZOE se caerá. Usa `/quit` antes de desconectar el SSD para guardar la memoria correctamente.

**P7: ¿Necesito una GPU?**
No. ZOE funciona en CPU. En Apple Silicon usa Metal automáticamente. En Mac 8GB usa mmap para modelos grandes.

**P8: ¿Puedo tener varias ZOEs?**
Sí. Cada instalación de ZOE es independiente con su propia identidad, memoria y trayectoria.

### Funcionamiento

**P9: ¿ZOE recuerda entre sesiones?**
Sí, la memoria episódica se guarda en SQLite y se carga al iniciar.

**P10: ¿Por qué ZOE tarda 30 segundos en responder a veces?**
Porque detectó un nivel L3_DEEP o L3_MAXIMUM y está usando un modelo grande (QwQ-32B o Qwen 72B). Estos modelos razonan profundamente.

**P11: ¿Puedo cambiar de modelo sin reiniciar?**
Sí, con `/llm ollama qwq-32b-iq2` o desde el botón 🧠 LLM del Dashboard.

**P12: ¿Qué es PatternSpeaker?**
Es el sistema de ZOE que responde sin IA, usando patrones y memoria. Calidad limitada pero siempre disponible, gratis y offline.

**P13: ¿ZOE alucina?**
Menos que ChatGPT porque tiene validación epistémica. Si no está segura, lo dice o lo pone en cuarentena.

**P14: ¿Puedo borrar la memoria de ZOE?**
Sí, borra `data/zoe_memory.db`. ZOE "nacerá" de nuevo.

**P15: ¿ZOE piensa aunque no le hable?**
Sí, genera pensamientos autónomos cada 3 segundos. Los ves en el panel derecho del Dashboard.

### Modelos IA

**P16: ¿Qué es IQ2_M?**
Es un formato de compresión de modelos que permite que modelos grandes quepan en 8GB RAM. Reduce calidad un ~5% pero tamaño un ~70%.

**P17: ¿Por qué 4 modelos y no 1?**
Porque diferentes preguntas necesitan diferentes niveles de pensamiento. "Hola" no necesita un modelo de 25GB; "compara jurídicamente" sí necesita máxima calidad.

**P18: ¿Puedo usar GPT-4o o Claude?**
Sí, configurando API keys. ZOE los usa solo para L3 crítico (ahorra dinero).

**P19: ¿Los modelos cargan mi Mac?**
No, viven en el SSD. mmap solo carga en RAM las capas activas (~3-4GB).

**P20: ¿Puedo añadir mis propios modelos?**
Sí, descárgalos de HuggingFace y registra con `ollama create`. Luego añádelos al catálogo en `model_downloader.py`.

### Cápsulas

**P21: ¿Qué es una cápsula?**
Un paquete de conocimiento experto que ZOE carga en segundos. Como un libro que ZOE lee instantáneamente.

**P22: ¿Cuántas cápsulas hay?**
15 preinstaladas. Puedes crear las tuyas.

**P23: ¿Las cápsulas se guardan entre sesiones?**
Actualmente no (gap conocido, se arregla en Sprint 5.8). Tienes que recargarlas al iniciar.

**P24: ¿Puedo crear mi propia cápsula?**
Sí, con `zoe-capsules create --name ...`.

**P25: ¿Las cápsulas cuestan dinero?**
No, son gratis. El marketplace futuro permitirá comprar cápsulas premium.

### Dashboard

**P26: ¿Cómo accedo al Dashboard?**
Abre `http://localhost:8642` en tu navegador tras arrancar ZOE.

**P27: ¿Puedo acceder desde otro dispositivo?**
Sí, usando la IP de tu Mac: `http://192.168.1.X:8642`. Pero cuidado: no hay autenticación (gap conocido).

**P28: ¿Cómo veo qué modelo está usando ZOE?**
`curl http://localhost:8642/api/router/stats` o mira el `last_routed_tag` en la respuesta del chat.

**P29: ¿Puedo usar el Dashboard en mi móvil?**
Sí, como PWA. Abre `http://IP-DE-TU-MAC:8642` en Chrome (Android) o Safari (iOS) y añade a pantalla de inicio.

**P30: ¿Cómo durmo a ZOE desde el Dashboard?**
Botón 🔄 Sleep, o `POST /sleep`, o `/sleep` en el chat.

### Voz y multimodal

**P31: ¿Puedo hablar con ZOE por voz?**
Sí, con el modo voice-first: `python -m zoe.peripherals.voice_first`. Di "Hey ZOE" y conversa.

**P32: ¿Puedo enviar imágenes a ZOE?**
Programáticamente sí (VLMPeripheral). Desde el Dashboard, el feed_upload todavía no está conectado al VLM (gap conocido).

**P33: ¿ZOE detecta mi idioma?**
El LanguageDetector existe pero no está conectado (gap conocido). ZOE responde en español por defecto.

### Portabilidad

**P34: ¿Puedo llevar mi ZOE a otro ordenador?**
Sí, con el formato `.zoe`. Empaqueta todo y desempaqueta en el otro ordenador.

**P35: ¿Puedo compartir mi ZOE con otra persona?**
Sí, dale el archivo `.zoe`. Tendrán la misma ZOE con la misma memoria, pero la trayectoria divergirá a partir de ahí.

**P36: ¿Puedo heredar mi ZOE?**
Sí, con la cápsula `ia_heredable_legal` y el formato `.zoe`.

### Técnico

**P37: ¿Qué versión de Python necesito?**
Python 3.10 o superior.

**P38: ¿ZOE es open source?**
Sí, licencia Apache 2.0.

**P39: ¿Cuántos tests tiene ZOE?**
1.413 tests en 54 archivos.

**P40: ¿Dónde encuentro la documentación completa?**
- Visión no técnica: `docs/18_ZOE_EXPLICACION_NO_TECNICOS.md`
- Documento técnico: `docs/19_ZOE_TECHNICAL_INTERNALS.md`
- Esta guía: `docs/20_ZOE_GUIA_USUARIO.md`
- Plan de gaps: `docs/21_ZOE_PLAN_GAPS.md`

---

## 40. Resolución de problemas

### Instalación

| Problema | Causa | Solución |
|---|---|---|
| `curl: command not found` | curl no instalado | En Mac: `xcode-select --install` |
| `Python no encontrado` | Python no instalado | Descarga Python 3.10+ desde https://python.org |
| `Python 3.6 detectado` | Python viejo | Instala Python 3.10+ |
| `Clone falló` | Repo privado sin creds | Usa opción 1 (PAT) u opción 2 (copia manual) |
| `Ollama no pudo iniciar` | Ollama no arranca | Ejecuta `ollama serve` manualmente en otra terminal |
| `Espacio insuficiente` | SSD sin espacio | Libera espacio o elige setup más pequeño |
| `FAT32 detectado` | SSD mal formateado | Formatea a APFS o exFAT |
| `xattr: command not found` (Linux) | Solo macOS | Ignorar, es solo para macOS |

### Funcionamiento

| Problema | Causa | Solución |
|---|---|---|
| ZOE no responde | LLM no disponible | Verifica `ollama list`, cambia a `--backend pattern` |
| ZOE va muy lento | Modelo grande + Mac 8GB | Usa `--model auto` (ACD elige modelo óptimo) |
| `invalid choice: 'pattern'` | Versión antigua | Actualiza: `git pull && pip install -e .` |
| ZOE no recuerda nada | Memoria corrupta | Borra `data/zoe_memory.db` y reinicia |
| Pensamientos autónomos no aparecen | Bucle no arrancó | Verifica que el Dashboard está corriendo |
| Cable USB muy lento | Cable USB 2.0 | Usa el cable CORTO de la caja del SSD |

### Dashboard

| Problema | Causa | Solución |
|---|---|---|
| `404: Not Found` en el navegador | Dashboard no arrancó | Verifica que Terminal muestra "Dashboard server started" |
| `Address already in use` | Puerto 8642 ocupado | `lsof -i :8642` mata el proceso: `kill -9 <PID>` |
| No puedo acceder desde otro dispositivo | Firewall | Abre puerto 8642 en el firewall del Mac |
| WebSocket no conecta | Navegador viejo | Usa Chrome, Firefox o Safari actualizados |

### Modelos

| Problema | Causa | Solución |
|---|---|---|
| `model not found` | Modelo no registrado en Ollama | `ollama create <tag> -f Modelfile.<tag>` |
| Descarga de modelo falla | Sin espacio o internet | Verifica espacio: `df -h`. Verifica internet. |
| Modelo muy lento | Mac 8GB + modelo 72B | Es normal (1-3 t/s). Usa setup balanced. |
| `OLLAMA_MODELS` no respeta SSD | Variable no exportada | Verifica que el `.command` tiene `export OLLAMA_MODELS="$ZOE_HOME/models"` |

---

## 41. Glosario completo

| Término | Definición |
|---|---|
| **ACD** | Adaptive Cognitive Depth. Sistema que clasifica tu pregunta en 5 niveles. |
| **ALMA** | Arquitectura de Layered Mutability & Auditability. Identidad + trayectoria + evolución. |
| **APFS** | Apple File System. Formato de disco óptimo para Mac. |
| **Backend** | El "motor" que genera texto (Ollama, OpenAI, Anthropic, Pattern). |
| **Cápsula** | Paquete de conocimiento experto que ZOE carga en segundos. |
| **Cuarentena** | Donde ZOE guarda el conocimiento dudoso hasta validarlo. |
| **Dashboard** | La interfaz web desde donde controlas a ZOE. |
| **exFAT** | Formato de disco multiplataforma (Mac + Windows + Android). |
| **FAT32** | Formato de disco antiguo. NO sirve para ZOE (no permite >4GB). |
| **GGUF** | Formato de archivo de los modelos de IA. |
| **Hash SHA-256** | Código único irrepetible que identifica a tu ZOE. |
| **IQ2_M** | Formato de compresión de modelos para 8GB RAM. |
| **LLM** | Large Language Model. El "cerebro" que genera texto. |
| **mmap** | Técnica que lee archivos grandes desde disco sin cargarlos enteros en RAM. |
| **ModelBus** | Sistema que selecciona el mejor backend LLM según contexto. |
| **PAT** | Personal Access Token de GitHub. Necesario para repo privado. |
| **PatternSpeaker** | Sistema de ZOE que responde sin IA, usando patrones. |
| **SSD** | Disco externo de alta velocidad donde ZOE guarda sus modelos. |
| **Sub-agente** | Uno de los 12 "cerebros" especializados dentro de ZOE. |
| **Token** | Aproximadamente una palabra. "tokens/s" = palabras por segundo. |
| **TrajectoryChain** | Diario de vida firmado de ZOE, como una blockchain. |
| **Vectores** | La "genética" de ZOE: curiosidad, prudencia, empatía, etc. |
| **VLM** | Vision Language Model. Modelo que entiende imágenes. |
| **WebSocket** | Conexión permanente entre tu navegador y ZOE para chat en tiempo real. |
| **ZOE** | Zombie Optimization Engine... no, broma. ZOE es el organismo. |

---

# Apéndice A — Lista completa de endpoints del Dashboard

71 endpoints REST verificados:

### Core (13)
- `GET /` — Dashboard web
- `GET /ws` — WebSocket chat tiempo real
- `POST /chat` — Chat REST
- `POST /feed` — Subir archivos
- `GET /stats` — Estadísticas completas
- `GET /state` — Estado del organismo
- `GET /memory` — Memoria episódica
- `GET /identity` — Identidad criptográfica
- `POST /sleep` — Dormir ZOE
- `POST /wake` — Despertar ZOE
- `POST /llm` — Cambiar LLM
- `GET /history` — Historial
- `GET /federation` — Federación

### Cápsulas (7)
- `GET /api/capsules` — Listar 15 cápsulas
- `GET /api/capsules/loaded` — Cápsulas cargadas
- `POST /api/capsules/load` — Cargar cápsula
- `POST /api/capsules/unload` — Descargar cápsula
- `GET /api/capsules/{name}/info` — Info de cápsula
- `POST /api/capsules/{name}/validate` — Validar cápsula
- `POST /api/capsules/create` — Crear cápsula

### ACD Router (3)
- `GET /api/router/stats` — Stats del router
- `GET /api/router/installed` — Modelos en SSD
- `GET /api/router/profile` — Perfil activo

### Marketplace (5)
- `GET /api/marketplace/capsules` — Listar marketplace
- `POST /api/marketplace/upload` — Subir cápsula
- `POST /api/marketplace/download/{name}` — Descargar cápsula
- `GET /api/marketplace/use_cases` — Casos de uso
- `POST /api/marketplace/upload_use_case` — Subir caso de uso

### Hardware (4)
- `GET /api/hardware/system` — Info sistema
- `GET /api/hardware/ssds` — SSDs detectados
- `GET /api/hardware/token_rates` — Velocidades modelos
- `GET /api/hardware/cable_warning` — Warning cable

### Y 39 endpoints más (federación, cuarentena, mentor, models, resources, modelbus, planner, embodiment, seed, PWA)

---

# Apéndice B — Tiempos reales de cada operación

| Operación | Tiempo esperado |
|---|---|
| Instalación base (código + venv) | 2-4 minutos |
| Descarga setup minimal (3.5GB) | 5-10 minutos |
| Descarga setup balanced (16GB) | 15-30 minutos |
| Descarga setup maximum (53GB) | 45-90 minutos |
| Arranque de ZOE | 3-5 segundos |
| Respuesta L0_REFLEX | <1ms |
| Respuesta L1_FAST | 1-3 segundos |
| Respuesta L2_STANDARD | 5-10 segundos |
| Respuesta L3_DEEP | 15-30 segundos |
| Respuesta L3_MAXIMUM | 30-90 segundos |
| Cargar cápsula | <1 segundo |
| Cambiar LLM en caliente | <1 segundo |
| Empaquetar .zoe | 2-5 segundos |
| Actualizar ZOE (git pull) | 30-60 segundos |

---

# Apéndice C — Dónde encontrar más ayuda

| Si necesitas... | Ve a... |
|---|---|
| Explicación para no técnicos | `docs/18_ZOE_EXPLICACION_NO_TECNICOS.md` |
| Documento técnico completo | `docs/19_ZOE_TECHNICAL_INTERNALS.md` |
| Esta guía de usuario | `docs/20_ZOE_GUIA_USUARIO.md` |
| Plan de gaps y roadmap | `docs/21_ZOE_PLAN_GAPS.md` |
| Guía de instalación detallada | `docs/17_USER_INSTALLATION_GUIDE.md` |
| Troubleshooting avanzado | `docs/13_TROUBLESHOOTING.md` |
| API REST completa | `docs/REFERENCE/API_REFERENCE.md` |
| Optimización de hardware | `docs/10_HARDWARE_OPTIMIZATION.md` |
| Formato .zoe portátil | `docs/16_ZOE_FORMAT.md` |
| Cápsulas de conocimiento | `docs/06_CAPSULES_GUIDE.md` |
| Issues y bugs | https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/issues |

---

*ZOE V1.8.0 — Guía de Usuario Definitiva*
*Julio 2026 — Sprint 5.7.4*
*"ZOE no es un modelo que responde. Es un organismo que existe."*

*Esta guía ha sido verificada contra el código real. Todos los comandos, endpoints y tiempos son reales.*
