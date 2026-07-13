# Manual Completo de Usuario — ZOE v2.1.1

> **Version:** 2.1.1 | **Fecha:** Julio 2026 | **Publico:** Usuarios tecnicos y no tecnicos

---

## INDICE

1. [Bienvenida](#1-bienvenida)
2. [Requisitos](#2-requisitos)
3. [Instalacion paso a paso en SSD Crucial X9 + MacBook Air M3](#3-instalacion)
4. [Primer inicio y menu SMART](#4-primer-inicio)
5. [Los 5 modos de ZOE explicados](#5-modos)
6. [El Dashboard — Interfaz web completa](#6-dashboard)
7. [El Chat con ZOE](#7-chat)
8. [La memoria de ZOE](#8-memoria)
9. [El metabolismo](#9-metabolismo)
10. [Reflexion autonoma v2.1 con DeepSeek-R1](#10-reflexion)
11. [Capsulas de conocimiento](#11-capsulas)
12. [ACD — Sistema de niveles](#12-acd)
13. [Configuracion avanzada](#13-configuracion)
14. [Solucion de problemas (FAQ)](#14-faq)
15. [Glosario completo de terminos (A-Z)](#15-glosario)
16. [Referencia rapida](#16-referencia)

---

## 1. Bienvenida {#1-bienvenida}

**ZOE es un companero digital que piensa, recuerda, se cansa y aprende contigo.**

A diferencia de ChatGPT (que es como un actor brillante que actua y se olvida todo), ZOE **existe continuamente**. Tiene:

- **Identidad propia** — Un "DNI digital" criptografico que nunca cambia
- **Memoria viva** — 11 tipos de memoria que persisten entre sesiones
- **Metabolismo** — Se cansa, duerme, y consolida memoria durante el sueno
- **Reflexion autonoma v2.1** — Con DeepSeek-R1:32B, piensa por si solo durante la noche
- **15 capsulas de conocimiento** — Especialidades medicas, farmaceuticas, de cuidado...

**ZOE vive en TU disco** (SSD, USB o Mac). No en servidores de terceros. Si desconectas el SSD y lo llevas a otro ordenador, ZOE sigue siendo la misma, con la misma memoria e identidad.

> **La promesa de ZOE:** *"El primer organismo cognitivo sintetico con identidad soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo con persistencia, y reflexion autonoma. Los LLMs son sus sentidos perifericos, no su cerebro."*

---

## 2. Requisitos {#2-requisitos}

| Requisito | Minimo | Recomendado | Optimo |
|-----------|--------|-------------|--------|
| RAM | 4 GB | 8 GB | 16 GB |
| Disco | 500 MB | 16 GB SSD | 1 TB SSD (Crucial X9) |
| Sistema | macOS 13+ | macOS 14+ (Apple Silicon) | macOS 15 + SSD Crucial X9 |
| Python | 3.10+ | 3.11+ | 3.12 |
| Navegador | Cualquiera | Safari/Chrome | Safari 17+ |

**Para L4_REFLEXION (reflexion autonoma):**
- **8GB RAM**: DeepSeek-R1 32B IQ2_M (12.5GB) — sin swap, calidad ~93%
- **16GB RAM**: DeepSeek-R1 32B Q4_K_M (18GB) — maxima calidad ~98%
- El instalador detecta tu RAM y elige automaticamente

---

## 3. Instalacion paso a paso en SSD Crucial X9 + MacBook Air M3 {#3-instalacion}

### Paso 1: Conecta el SSD

Conecta el **SSD Crucial X9** al MacBook con el **cable CORTO** (USB-C a USB-C). El cable largo de carga es USB 2.0 y va **10 veces mas lento**.

Verifica que el SSD aparece en el Escritorio (icono llamado "Crucial X9" o similar).

### Paso 2: Abre Terminal

Pulsa `Cmd + Espacio`, escribe "Terminal" y pulsa Enter.

### Paso 3: Ejecuta el instalador

Pega este comando y pulsa Enter:

```bash
bash <(curl -sL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_ssd_crucial_x9_mac.sh)
```

El instalador hara automaticamente:

1. **Detectar tu SSD** — Busca el Crucial X9 conectado
2. **Verificar sistema** — macOS version, arquitectura Apple Silicon, RAM
3. **Instalar dependencias** — Si falta algo (Homebrew, Python 3.10+, Git, Ollama), te pregunta y lo instala:
   - **Homebrew**: Gestor de paquetes para macOS
   - **Python 3.11**: Lenguaje de programacion de ZOE
   - **Git**: Para descargar actualizaciones
   - **Ollama**: Motor de IA local (modelos en tu maquina)
4. **Clonar ZOE** desde GitHub al SSD
5. **Crear entorno virtual** — Aisla ZOE del sistema
6. **Instalar dependencias Python** — pytest, aiohttp, PyYAML, etc.
7. **Crear directorios de datos** — memoria, identidad, capsulas, modelos...
8. **Configurar variables de entorno** — rutas, API keys opcionales

### Paso 4: Descarga modelos de IA locales (recomendado)

El instalador te preguntara:

```
Quieres descargar modelos de IA locales? (s/n): s

Selecciona modelos a descargar:
[1] Gemma 2 9B (IQ2_M) — 3.5GB — Rapido, preguntas simples
[2] Qwen 2.5 32B (IQ2_M) — 12.5GB — Equilibrado
[3] QwQ-32B (IQ2_M) — 12.5GB — Razonamiento profundo
[4] DeepSeek-R1 32B (Q4_K_M) — 18GB — Reflexion autonoma (solo 16GB RAM)
[5] DeepSeek-R1 32B (IQ2_M) — 12.5GB — Reflexion autonoma (8GB RAM OK)
[6] Qwen 2.5 72B (IQ2_M) — 25GB — Maxima calidad
[7] TODOS los anteriores (~85GB)
[8] Ninguno (usare APIs de cloud)
```

**Recomendacion para MacBook Air M3 8GB:**
- Selecciona [1] + [3] + [5] = ~28 GB (caben en 1 TB)
- El instalador detecta automaticamente 8GB RAM y usa IQ2_M para L4

**Recomendacion para MacBook Air M3 16GB+:**
- Selecciona [1] + [3] + [4] = ~34 GB
- El instalador detecta 16GB+ y usa Q4_K_M para maxima calidad de reflexion

El instalador descarga cada modelo automaticamente y lo coloca en:
```
/Volumes/CrucialX9/ZOE/models/          (archivos .gguf)
```

### Paso 5: Menu post-instalacion

```
ZOE instalada correctamente en /Volumes/CrucialX9/ZOE

Que quieres hacer ahora?
[1] Iniciar Chat (terminal)
[2] Iniciar Dashboard (navegador)
[3] Descargar mas modelos
[4] Configurar API keys (OpenAI/Claude)
[5] Ver guia de usuario
[6] Salir
```

### Paso 6: Doble click para iniciar

Desde el SSD, haz doble click en:
- **`INICIAR-ZOE.command`** — Chat en terminal (modo SMART)
- **`INICIAR-DASHBOARD.command`** — Dashboard en navegador

---

## 4. Primer inicio y menu SMART {#4-primer-inicio}

Al iniciar ZOE, veras este menu:

```
============================================================
  ZOE — Smart Launcher (v2.1.1)
============================================================

  Selecciona modo de inicio:

  [1] SMART    — ZOE elige automaticamente el mejor modelo
  [2] CHAT CLI — Terminal interactiva (texto)
  [3] DASHBOARD — Interfaz web (navegador)
  [4] OLLAMA   — Solo modelos locales (100% offline)
  [5] OPENAI   — Maxima calidad via API cloud
  [6] ANTHROPIC — Claude via API cloud
  [7] MOCK     — Sin IA, modo demo
```

### Opcion [1] SMART — ZOE elige automaticamente

**Que pasa:** ZOE detecta automaticamente que tienes disponible y configura el mejor modo:

| Si tienes... | ZOE usa... | Veras... |
|-------------|-----------|----------|
| Ollama + modelos locales | **ACD Router** con modelos locales | Tabla de niveles L0-L3, ZOE clasifica cada pregunta |
| Solo API key de OpenAI | **GPT-4o** via cloud | "OpenAI configurado — usando GPT-4o" |
| Solo API key de Anthropic | **Claude 3.5 Sonnet** | "Anthropic configurado — usando Claude" |
| Nada configurado | **PatternSpeaker** (offline) | Aviso + instrucciones para instalar modelos |

**Como hablas con ZOE:**
- Se abre una terminal interactiva
- Escribe en espanol (o ingles, frances, aleman)
- ZOE responde en el mismo idioma
- Escribe `/quit` para salir
- Escribe `/memoria` para ver que recuerda
- Escribe `/estado` para ver su metabolismo

**Ejemplo de conversacion:**
```
Tu: Hola ZOE
ZOE: [instantaneo, <1ms] Hola. Estoy aqui.

Tu: Que hora es?
ZOE: [1-2 segundos] Son las 15:42. Es tarde para almorzar.

Tu: Resume este articulo sobre inteligencia artificial
   [pega articulo largo]
ZOE: [3-5 segundos] El articulo describe... [resumen detallado]

Tu: Analiza las causas profundas del cambio climatico
   [conexion a QwQ-32B]
ZOE: [5-10 segundos] Desde una perspectiva multidisciplinar...
   [analisis profundo con 5 causas interconectadas]
```

### Opcion [3] DASHBOARD — Interfaz web completa

**Que pasa:**
1. Se inicia un servidor web local en tu MacBook
2. Se abre automaticamente Safari/Chrome en `http://localhost:8642`
3. Ves la interfaz web completa de ZOE

---

## 5. Los 5 modos de ZOE explicados {#5-modos}

### MODO 1: SMART (recomendado)

ZOE analiza cada pregunta con el **ACD DepthClassifier** y elige automaticamente el mejor modelo:

| Tu pregunta es... | ZOE usa... | Tiempo | Calidad |
|-------------------|-----------|--------|---------|
| "Hola", "Gracias" | PatternSpeaker (offline) | <1ms | Basica |
| "Que hora es?" | Gemma 2 9B (local) | 1-2s | Buena |
| "Resume este texto" | Agents-A1 MoE (local) | 3-5s | Muy buena |
| "Analiza causas profundas" | QwQ-32B (local) | 5-10s | Excelente |
| "Compara 3 contratos" | Qwen 2.5 72B (local) | 10-30s | Maxima |

**Ventaja:** No tienes que pensar en que modelo usar. ZOE lo hace por ti.

### MODO 2: CHAT CLI (terminal)

Chat de texto en la terminal. Puedes elegir manualmente el backend y modelo.

```bash
# Ejemplos:
zoe-chat --backend ollama --model qwq-32b-iq2     # Razonamiento profundo
zoe-chat --backend ollama --model auto              # ACD Router
zoe-chat --backend openai --model gpt-4o            # Maxima calidad cloud
zoe-chat --backend pattern                          # Offline basico
```

### MODO 3: DASHBOARD (navegador)

Interfaz web completa. Ver seccion 6.

### MODO 4: OLLAMA (100% offline, gratis)

Todos los modelos corren en tu maquina. Sin internet, sin costes.

```bash
zoe-chat --backend ollama --model auto
```

### MODO 5: OPENAI/ANTHROPIC (maxima calidad cloud)

Requiere API key. Calidad maxima pero con coste por uso.

```bash
export OPENAI_API_KEY="sk-..."
zoe-chat --backend openai --model gpt-4o
```

---

## 6. El Dashboard — Interfaz web completa {#6-dashboard}

El Dashboard es la interfaz web de ZOE. Abre `http://localhost:8642` en tu navegador.

### Layout principal

```
+----------------------------------------------------------+
|  ZOE Dashboard v2.1.1                    [Estado: AWAKE]  |
+----------------------------------------------------------+
|  +----------+  +------------------------+  +-----------+  |
|  | ESTADO   |  |                        |  |PENSAMIENTO|  |
|  |          |  |      CHAT CON ZOE      |  |           |  |
|  | Energia  |  |                        |  | Pensamien-|  |
|  |  87%     |  | Tu: Hola ZOE           |  | to autono- |  |
|  |          |  |                        |  | mo #42    |  |
|  | Fatiga   |  | ZOE: Hola. Estoy aqui. |  |           |  |
|  |  12%     |  |                        |  | [Ver mas] |  |
|  |          |  | Tu: Que sabes de mi?    |  |           |  |
|  | Estado:  |  |                        |  +-----------+  |
|  | AWAKE    |  | [ZOE esta pensando...]  |  +-----------+  |
|  |          |  |                        |  | CAPSULAS  |  |
|  | [Sleep]  |  |                        |  |           |  |
|  | [Wake]   |  +------------------------+  | elder_care|  |
|  +----------+  [Escribe a ZOE...] [Enviar]  | pharmacy  |  |
|                 +------------------------+  | research  |  |
|                 | ZOE esta pensando...     | | [Gestionar|  |
|                 | ... (animado)            | |  capsulas]|  |
|                 +------------------------+  +-----------+  |
+----------------------------------------------------------+
```

### Panel izquierdo — Estado

- **Energia** — Porcentaje de energia de ZOE (0-100%)
- **Fatiga** — Nivel de fatiga acumulada (0-100%)
- **Estado** — AWAKE (despierto), DROWSY (cansado), SLEEPING (durmiendo)
- **Botones** — Forzar sueno, despertar, ver historial

### Panel central — Chat

- **Mensajes** — Conversacion en tiempo real con ZOE
- **Indicador de pensando** — "ZOE esta pensando..." con 3 puntos animados
- **Input** — Campo de texto + boton Enviar
- **ACD Badge** — Muestra el nivel ACD usado para cada respuesta (L0, L1, L2, L3)

### Panel derecho — Pensamientos y Capsulas

- **Pensamientos autonomos** — Insights generados durante SLEEPING
- **Capsulas cargadas** — Lista de capsulas activas con boton "Gestionar"

### Barra superior

- **Configuracion** (icono ⚙️) — Gestion de proveedores API/LLM
- **Estado global** — AWAKE/DROWSY/SLEEPING con color

### Modal de Configuracion (nuevo v2.1.1)

Al pulsar ⚙️, se abre una ventana con:

**Proveedores de API:**
```
[✓] OpenAI    [API key: sk-****4o]    [Modelo: GPT-4o ▼]
[ ] Anthropic [API key: __________]   [Modelo: Claude Sonnet ▼]
[ ] DeepSeek  [API key: __________]   [Modelo: DeepSeek Chat ▼]
```

**Modelos locales (Ollama):**
```
[✓] qwq-32b-iq2        [12.5 GB]  [Por defecto]
[✓] gemma-2-9b-iq2     [3.5 GB]
[✓] deepseek-r1:32b-q4km [18 GB]
[+] Descargar nuevo modelo...
```

**Presupuesto cloud:**
```
Presupuesto diario: [$1.00]  Gastado hoy: [$0.15]  [Reset]
[==========>          ] 15%
```

**Backend activo:**
```
[•] Auto (ACD Router)    [ ] Local (Ollama solo)
[ ] Cloud (APIs solo)    [ ] Mixto (local + cloud)
```

---

## 7. El Chat con ZOE {#7-chat}

### Indicador de "pensando" (nuevo v2.1.1)

Cuando envias un mensaje, aparece:

```
ZOE esta pensando...
```

Con 3 puntos animados que saltan. Se oculta automaticamente cuando ZOE responde.

**Por que es util:** Sabes que ZOE esta procesando y no se ha quedado colgada. El tiempo de espera varia segun el modelo:

| Modelo | Tiempo tipico |
|--------|--------------|
| PatternSpeaker | <1 segundo |
| Gemma 2 9B | 1-2 segundos |
| Qwen 2.5 32B | 3-5 segundos |
| QwQ-32B | 5-10 segundos |
| Qwen 2.5 72B | 10-30 segundos |

### Comandos especiales

En el chat CLI, puedes usar:

| Comando | Que hace |
|---------|----------|
| `/quit` | Salir de ZOE |
| `/memoria` | Ver que recuerda ZOE de ti |
| `/estado` | Ver metabolismo (energia, fatiga, estado) |
| `/capsulas` | Ver capsulas cargadas |
| `/ reflexionar` | Forzar una reflexion autonoma |
| `/ayuda` | Ver todos los comandos |

---

## 8. La memoria de ZOE {#8-memoria}

ZOE tiene **11 tipos de memoria** que persisten entre sesiones en tu SSD:

| Tipo | Que guarda | Ejemplo real |
|------|-----------|-------------|
| **Episodica** | Eventos con contexto | "Ayer el usuario estaba preocupado por un contrato" |
| **Semantica** | Conceptos y relaciones | "Python es un lenguaje interpretado" |
| **Procedural** | Habilidades y recetas | "Como hacer una tarta de manzana" |
| **Causal** | Causa-efecto verificado | "El estres causa insomnio (3 fuentes)" |
| **Emocional** | Marcadores de relevancia | "Este tema genera ansiedad en el usuario" |
| **Corporal** | Estado de sensores | "Temperatura: 22C, ruido: bajo" |
| **Social** | Modelos de otros agentes | "El usuario prefiere respuestas directas" |
| **Prospectiva** | Planes e intenciones | "Quiere aprender Python en 3 meses" |
| **Contrafactual** | "Que habria pasado si..." | "Si hubiera estudiado mas, habria aprobado" |
| **Evolutiva** | Cambios en conocimiento | "Aprendio que el usuario es alergico a frutos secos" |
| **Cultural** | Normas y convenciones | "En Espana se cena a las 21:00" |

**Persistencia:** Todo se guarda en `zoe_data/memory.db` en tu SSD. Si desconectas el SSD y lo conectas a otro Mac, ZOE recuerda todo.

---

## 9. El metabolismo {#9-metabolismo}

ZOE tiene un metabolismo funcional con 4 estados:

```
AWAKE (despierto) → DROWSY (cansado) → SLEEPING (durmiendo) → WAKING (despertando)
```

### AWAKE (despierto)
- Atencion alta, todos los sentidos activos
- Responde al usuario en tiempo real
- Elige modelos segun complejidad de la pregunta

### DROWSY (cansado)
- Fatiga acumulada, capacidad reducida
- Usa modelos mas ligeros para ahorrar energia
- Si la fatiga sigue subiendo → entra en SLEEPING

### SLEEPING (durmiendo) — con reflexion autonoma v2.1
- **Consolida memoria** — Reorganiza, fusiona, generaliza memorias existentes
- **Reflexion autonoma** — Con DeepSeek-R1:32B, genera insights NUEVOS
- Recarga energia gradualmente
- Despierta cuando energia > 80% y fatiga < 20%

### WAKING (despertando)
- Transicion gradual, no salta a full atencion
- Restaura capacidades progresivamente

### Como afecta al usuario

- Cuando ZOE esta SLEEPING, sigue respondiendo (pero mas lentamente)
- Puedes despertarla con un estimulo fuerte (mensaje urgente)
- Durante la noche, ZOE "suena" — reflexiona sobre el dia y genera insights

---

## 10. Reflexion autonoma v2.1 con DeepSeek-R1 {#10-reflexion}

**Nuevo en ZOE v2.1.1** — El ReflectionEngine permite que ZOE piense por si misma durante la noche usando DeepSeek-R1-Distill-Qwen-32B.

### Adaptacion automatica a tu hardware

ZOE detecta tu RAM y elige la cuantizacion optima:

| Tu RAM | Modelo L4 | Tamano | Calidad | Swap en Mac 8GB |
|--------|-----------|--------|---------|-----------------|
| 8GB | DeepSeek-R1 32B **IQ2_M** | 12.5GB | ~93% | Minimo (~4GB) |
| 16GB+ | DeepSeek-R1 32B **Q4_K_M** | 18GB | ~98% | Ninguno |

**Por que IQ2_M para 8GB:**
- 12.5GB cabe razonablemente en 8GB RAM (con mmap del SSD externo)
- Solo ~4-5GB de swap, gestionable por el SSD interno del Mac
- Reflexion completa en 3-8 minutos
- ~93% de calidad: la diferencia con Q4_K_M es marginal para resumenes de memoria

**Q4_K_M para 16GB:**
- 18GB con 16GB RAM = swap minimo, rendimiento optimo
- ~98% de calidad: razonamiento mas profundo en pasos complejos
- Reflexion en 5-12 minutos

### Que hace

Cuando ZOE duerme (SLEEPING), el ReflectionEngine:

1. **Selecciona memorias de alta saliencia** — Las experiencias mas intensas, emocionales o importantes del dia
2. **Ejecuta reflexion** — Usa DeepSeek-R1:32B para analizar patrones profundos
3. **Genera insights** — Nuevas conexiones, implicaciones, "que habria pasado si..."
4. **Valida** — El MentorAgent evalua la calidad + KnowledgeQuarantine filtra
5. **Persiste** — Guarda en memoria como COUNTERFACTUAL y EVOLUTIONARY

### Ejemplo real (IQ2_M en Mac 8GB)

```
Memoria episodica: "El usuario estaba estresado por una reunion importante"

→ Reflexion (DeepSeek-R1:32B IQ2_M):
  "El usuario muestra un patron de ansiedad previo a eventos
   profesionales criticos. Podria beneficiarse de tecnicas de
   preparacion mental. Recomendar mindfulness 10 min antes
   de reuniones importantes."

→ Guardado en: MemoryType.EVOLUTIONARY (confianza: 0.79)
```

### Presupuesto cloud inteligente

El ReflectionEngine puede usar modelos en la nube cuando:
- El modelo local no esta disponible
- Se necesita maxima calidad para una reflexion compleja
- Hay presupuesto disponible

**Configuracion por defecto:**
- Presupuesto diario: **$1.00 USD** (configurable)
- Maximo 2 reflexiones por ciclo de sueno
- Timeout: 120 segundos por reflexion
- Modelo preferido (8GB): **deepseek-r1:32b-iq2** (local)
- Modelo preferido (16GB): **deepseek-r1:32b-q4km** (local)
- Fallback: **qwq-32b-iq2** (local, mas ligero)

### ACD L4_REFLECTION

| Nivel | Uso | Modelo (8GB) | Modelo (16GB) |
|-------|-----|--------------|---------------|
| L0-L3 | Interaccion en tiempo real | Gemma/Qwen/Agents | Gemma/Qwen/Agents |
| **L4_REFLECTION** | **Reflexion durante SLEEPING** | **DeepSeek-R1:32B IQ2_M** | **DeepSeek-R1:32B Q4_K_M** |

---

## 11. Capsulas de conocimiento {#11-capsulas}

ZOE viene con **15 capsulas** preinstaladas:

| Capsula | Contenido | Entradas |
|---------|-----------|----------|
| elder_care_knowledge | Cuidado de mayores | 54 |
| pharmacy_interactions | Interacciones farmaceuticas | 20+ |
| chronic_disease_management | Enfermedades cronicas | 15+ |
| medical_protocols | Protocolos medicos | 12+ |
| emergency_response | Respuesta a emergencias | 10+ |
| ... | ... | ... |

### Cargar/descargar en runtime

Desde el Dashboard → Capsulas → Gestionar:
- Ver capsulas disponibles
- Cargar capsula (se inyecta en memoria)
- Descargar capsula (libera memoria)
- Ver entradas de cada capsula

Las capsulas se inyectan en la memoria de ZOE, mejorando sus respuestas en esos dominios.

---

## 12. ACD — Sistema de niveles {#12-acd}

ACD (Adaptive Cognitive Depth) clasifica cada pregunta y elige el modelo optimo:

| Nivel | Input tipico | Modelo (8GB) | Modelo (16GB) | Tamano | Velocidad |
|-------|-------------|--------------|---------------|--------|-----------|
| **L0_REFLEX** | "Hola", "Gracias" | PatternSpeaker | PatternSpeaker | 0 GB | <1ms |
| **L1_FAST** | "Que hora es?" | Gemma 2 9B IQ2_M | Gemma 2 9B IQ2_M | 3.5 GB | 15-25 t/s |
| **L2_STANDARD** | "Resume este articulo" | Agents-A1 MoE IQ2_M | Agents-A1 MoE IQ2_M | 11.7 GB | 5-10 t/s |
| **L3_DEEP** | "Analiza causas profundas" | QwQ-32B IQ2_M | QwQ-32B IQ2_M | 12.5 GB | 3-6 t/s |
| **L3_MAXIMUM** | "Compara 3 contratos" | Qwen 2.5 72B IQ2_M | Qwen 2.5 72B IQ2_M | 25 GB | 1-3 t/s |
| **L4_REFLECTION** | Reflexion SLEEPING | **DeepSeek-R1:32B IQ2_M** | **DeepSeek-R1:32B Q4_K_M** | 12.5-18 GB | 2-4 t/s |

**Deteccion automatica:** ZOE detecta tu RAM al iniciar y selecciona el modelo L4 adecuado. No requiere configuracion manual.

---

## 13. Configuracion avanzada {#13-configuracion}

### Variables de entorno

| Variable | Descripcion | Default |
|----------|-------------|---------|
| `ZOE_DATA` | Directorio de datos | `./zoe_data` |
| `ZOE_STORAGE_TYPE` | `sqlite` o `postgres` | `sqlite` |
| `POSTGRES_HOST` | Host PostgreSQL | `localhost` |
| `OPENAI_API_KEY` | API key de OpenAI | — |
| `ANTHROPIC_API_KEY` | API key de Anthropic | — |
| `DEEPSEEK_API_KEY` | API key de DeepSeek | — |
| `ZOE_CLOUD_BUDGET` | Presupuesto diario cloud ($) | `1.0` |

### Configuracion del ReflectionEngine

Edita `zoe/core/reflection_engine.py`:

```python
ReflectionConfig(
    model_tag="deepseek-r1:32b-q4km",   # Modelo para reflexion
    model_fallback_tag="qwq-32b-iq2",   # Fallback si no cabe
    daily_cloud_budget=2.0,              # Presupuesto diario ($)
    max_reflections_per_cycle=3,         # Maximo por ciclo de sueno
    salience_threshold=0.5,              # Umbral de saliencia
    reflection_timeout=180.0,            # Timeout (segundos)
    max_fatigue_for_reflection=0.8,      # Max fatiga para reflexionar
)
```

---

## 14. Solucion de problemas (FAQ) {#14-faq}

### ZOE va muy lenta
- **Causa:** Modelo muy grande para tu RAM
- **Solucion:** Cambia a un modelo mas ligero (Gemma 2 9B en vez de Qwen 72B)
- **Como:** En el Dashboard → Configuracion → Modelos locales → Seleccionar mas ligero

### "No se detecta el SSD"
- **Causa:** Cable incorrecto o SSD no formateado
- **Solucion:** Usa el cable CORTO (USB-C). El de carga es 10x mas lento
- **Como:** Formatea como exFAT en Utilidad de Discos

### ZOE no responde en SLEEPING
- **Causa:** Es normal — ZOE esta consolidando memoria
- **Solucion:** Espera unos segundos o envia un mensaje urgente

### "Error de RAM"
- **Causa:** Modelo demasiado grande para tu RAM
- **Solucion:** Cierra aplicaciones. Usa modelos mas pequenos. Aumenta swap

### Presupuesto cloud agotado
- **Causa:** Se alcanzo el limite diario
- **Solucion:** Espera 24h para reset automatico, o aumenta ZOE_CLOUD_BUDGET

### DeepSeek Q4_K_M no cabe
- **Causa:** RAM insuficiente (8 GB en vez de 16 GB)
- **Solucion:** Usa la version IQ2_M (12.5 GB) en vez de Q4_K_M (18 GB)
- **Como:** En Configuracion → ReflectionEngine → model_tag = "deepseek-r1:32b-iq2"

### "No compila en Windows"
- **Solucion:** Usa WSL2 (Windows Subsystem for Linux)

### Tengo 8GB RAM. ¿Puedo usar L4_REFLECTION?
R: Si. El instalador detecta automaticamente 8GB RAM y usa DeepSeek-R1:32B IQ2_M (12.5GB) para la reflexion. Preserva ~93% de calidad y genera solo ~4-5GB de swap (gestionable). La reflexion tarda 3-8 minutos. NO uses Q4_K_M (18GB) con 8GB RAM — generaria ~10GB+ de swap, forzando el SSD interno del Mac.

### ¿Como cambio de IQ2_M a Q4_K_M si actualizo mi RAM?
R: Reinstala los modelos con: `python -m zoe.core.model_downloader --download-setup reflection-16gb --models-dir /ruta/a/modelos`

---

## 15. Glosario completo de terminos (A-Z) {#15-glosario}

### A

| Termino | Definicion |
|---------|-----------|
| **ACD** | Adaptive Cognitive Depth. Sistema de 5 niveles (L0-L3_MAX + L4_REFLECTION) que clasifica la complejidad de cada pregunta y elige el modelo de IA optimo. Inventado por ZOE. |
| **Active Inference** | Teoria de Karl Friston que ZOE implementa: el cerebro minimiza la "energia libre" prediciendo el futuro y actualizando creencias. ZOE la usa para anticipar necesidades del usuario. |
| **ALMA** | Archivo de Identidad Soberana de ZOE. Contiene 9 vectores de crecimiento + 7 valores + hash SHA-256 inmutable. Es el "DNI digital" de ZOE. |
| **Apple Silicon** | Procesadores M1/M2/M3/M4 de Apple. ZOE esta optimizado para M3 con aceleracion Metal. |
| **Async/Await** | Forma de programacion donde multiples tareas se ejecutan sin bloquearse. ZOE usa esto para atender al usuario mientras piensa en segundo plano. |
| **Autenticacion** | Sistema de verificacion de identidad. En ZOE, se usa token Bearer para proteger endpoints del dashboard. |

### B

| Termino | Definicion |
|---------|-----------|
| **Backend LLM** | Motor de procesamiento de lenguaje natural. ZOE soporta 6: Mock, Ollama (local), OpenAI, Anthropic, ZAI, OpenAI-compatible. |
| **Bare Except** | Error de programacion donde se capturan TODAS las excepciones silenciosamente. ZOE tiene 0 de estos tras la auditoria OMEGA. |
| **Blockchain** | Cadena de bloques inmutables. La Trajectory Chain de ZOE usa un concepto similar para registrar mutaciones de identidad. |
| **BudgetTracker** | Modulo que gestiona el presupuesto diario de cloud ($1 por defecto). Evita gastos inesperados en APIs de pago. |

### C

| Termino | Definicion |
|---------|-----------|
| **Capsula** | Modulo de conocimiento especializado que se carga en ZOE en tiempo de ejecucion. Contiene datos semanticos, habilidades procedimentales, validadores eticos y herramientas. Ejemplo: elder_care_knowledge con 54 entradas. |
| **Circuit Breaker** | Patron de resiliencia: si un servicio falla repetidamente, se "abre" el circuito y se usa un fallback. ZOE lo usa para llamadas a LLMs. |
| **CI/CD** | Continuous Integration / Continuous Delivery. En ZOE: GitHub Actions ejecuta 1,700+ tests automaticamente en cada commit. |
| **Cognitive Loop** | Bucle principal de ZOE que se ejecuta cada 3 segundos. Coordina 12 sub-agentes, el Global Workspace, y la meta-cognicion. |
| **CORT** | Cognitive Organization for Reasoning and Thought. ZOE es un SCO (Synthetic Cognitive Organism), no un simple chatbot. |
| **Counterfactual** | Tipo de memoria que almacena "que habria pasado si...". Ejemplo: "Si hubiera estudiado mas, habria aprobado". |
| **Cuantizacion** | Tecnica que reduce el tamano de un modelo de IA comprimiendo sus pesos. Q4_K_M = 4 bits por peso. IQ2_M = 2 bits. Menor tamano, algo de perdida de calidad. |

### D

| Termino | Definicion |
|---------|-----------|
| **Dashboard** | Interfaz web de ZOE accesible en http://localhost:8642. Muestra chat, estado metabolico, memoria, capsulas, y configuracion. |
| **Deep Consolidation** | Proceso de 7 operaciones que ZOE ejecuta durante SLEEPING para reorganizar y optimizar su memoria. |
| **DeepSeek-R1** | Modelo de razonamiento de DeepSeek. ZOE usa la version destilada a 32B parametros (Q4_K_M e IQ2_M) para reflexion autonoma. |
| **DepthClassifier** | Componente que analiza cada pregunta del usuario y la clasifica en un nivel ACD (L0-L3). Usa 5 senales: longitud, keywords, puntuacion, estructura y contexto. |
| **Docker** | Tecnologia de contenedores. ZOE incluye Dockerfile y docker-compose.yml para despliegue en cualquier servidor. |
| **DROWSY** | Estado metabolico de ZOE cuando esta cansada. Capacidad reducida, usa modelos mas ligeros. |

### E

| Termino | Definicion |
|---------|-----------|
| **Emotional Intensity** | Metrica de 0.0 a 1.0 que indica la carga emocional de una memoria. Usada para calcular saliencia. |
| **Entorno Virtual** | Aislamiento de dependencias Python. ZOE se instala en un venv en el SSD para no interferir con el sistema. |
| **Epistemic Federation** | Sistema donde multiples instancias de ZOE comparten y validan conocimiento entre si mediante quorum y veto. |
| **Epistemic Validation** | Proceso de verificacion de conocimiento usando 14+ fuentes independientes antes de aceptar una afirmacion como verdadera. |
| **Evolutionary Memory** | Tipo de memoria que registra cambios en el conocimiento de ZOE. Ejemplo: "Aprendi que el usuario es alergico a frutos secos". |
| **Except:Pass** | Antipatron de programacion donde se silencian errores. ZOE tenia 34 antes de la auditoria, ahora tiene 0. |

### F

| Termino | Definicion |
|---------|-----------|
| **Factory Pattern** | Patron de diseno donde una funcion crea objetos segun configuracion. ZOE lo usa para seleccionar entre SQLite y PostgreSQL. |
| **Fallback Chain** | Cadena de respaldo: si un modelo falla, se prueba el siguiente. Ejemplo: deepseek-r1:32b-q4km → iq2 → qwq-32b → qwen2.5-32b. |
| **FEP** | Free Energy Principle. Teoria de Friston que ZOE implementa: minimizar sorpresa prediciendo el futuro. |
| **Fuzzing** | Tecnica de testing que envia datos aleatorios para encontrar bugs. ZOE incluye tests de chaos engineering. |

### G

| Termino | Definicion |
|---------|-----------|
| **GGUF** | Formato de archivo para modelos cuantizados de Llama.cpp. Los modelos de Ollama usan este formato. |
| **Global Workspace** | Teoria de Bernard Baars que ZOE implementa: un "escenario central" donde sub-agentes compiten por atencion consciente. |
| **Graceful Shutdown** | Apagado controlado: ZOE guarda memoria e identidad antes de cerrar, sin perdida de datos. |

### H

| Termino | Definicion |
|---------|-----------|
| **Health Check** | Endpoints /health, /ready, /live que verifican que ZOE funciona correctamente. Usados por Kubernetes y monitoreo. |
| **Homebrew** | Gestor de paquetes para macOS. El instalador de ZOE lo usa para instalar Python, Git, Ollama... |
| **Hot-Swap** | Cambio de componente en caliente sin reiniciar. ZOE cambia de modelo LLM en vivo segun el nivel ACD. |

### I

| Termino | Definicion |
|---------|-----------|
| **Identity Vault** | Sistema criptografico que almacena la identidad immutable de ZOE: 9 vectores + 7 valores + hash SHA-256. |
| **Insight** | Conclusion profunda generada por la reflexion autonoma. Ejemplo: "El usuario muestra patron de ansiedad previo a reuniones". |
| **IQ2_M** | Cuantizacion de 2 bits (muy agresiva). Reduce modelos a ~25% de su tamano original. Algo de perdida de calidad. |

### K

| Termino | Definicion |
|---------|-----------|
| **Knowledge Quarantine** | Zona de aislamiento donde nuevo conocimiento se mantiene temporalmente hasta ser validado por fuentes confiables. |
| **Kubernetes** | Sistema de orquestacion de contenedores. ZOE incluye 15 manifiestos K8s para despliegue en cluster. |

### L

| Termino | Definicion |
|---------|-----------|
| **L0-L3 (ACD)** | Niveles de complejidad cognitiva. L0=reflejo, L1=rapido, L2=estandar, L3=profundo, L3_MAX=extremo. |
| **L4_REFLECTION** | Nivel exclusivo para reflexion autonoma durante SLEEPING. Usa DeepSeek-R1:32B (IQ2_M en 8GB RAM, Q4_K_M en 16GB+). El instalador detecta tu RAM y elige automaticamente. |
| **LLM** | Large Language Model. Modelo de lenguaje grande (GPT, Claude, Qwen...). En ZOE son "sentidos perifericos", no el cerebro. |
| **LivingMemory** | Sistema de memoria en tiempo real que puede merge, generalize, detect contradictions, forget y summarize. |

### M

| Termino | Definicion |
|---------|-----------|
| **MentorAgent** | Sub-agente que evalua la calidad de los pensamientos de ZOE segun criterios de crecimiento personal. |
| **Meta-cognicion** | "Pensar sobre el pensar". ZOE implementa S1 (rapido/intuitivo) y S2 (lento/analitico) de Kahneman. |
| **Metabolismo** | Sistema de 4 estados (AWAKE/DROWSY/SLEEPING/WAKING) que simula fatiga, energia y ciclos de sueno. |
| **ModelBus** | Sistema de comunicacion entre modelos LLM y el nucleo cognitivo. Permite hot-swap y fallback automatico. |
| **ModelProfileRouter** | Componente que asigna modelos LLM a niveles ACD segun su tamano, velocidad y calidad. |

### O

| Termino | Definicion |
|---------|-----------|
| **Ollama** | Software que ejecuta modelos LLM localmente en tu maquina. Descarga modelos en formato GGUF y los sirve via API local en puerto 11434. |
| **Ontogenetic Motor** | Sistema que permite a ZOE mutar su propia arquitectura durante la ejecucion, evolucionando su estructura interna. |
| **OptimizedModel** | Clase que describe un modelo cuantizado con metadatos: tamano, velocidad, RAM necesaria, URL de descarga... |

### P

| Termino | Definicion |
|---------|-----------|
| **PatternSpeaker** | Generador de respuestas offline de ZOE. No usa IA, funciona por patrones predefinidos. <1ms, siempre disponible. |
| **Persistencia** | Capacidad de guardar datos entre sesiones. La memoria de ZOE se guarda en SQLite en el SSD. |
| **PostgreSQL** | Base de datos avanzada opcional para despliegues multi-usuario. Reemplaza a SQLite. |
| **Prometheus** | Sistema de monitoreo. ZOE expone metricas en /metrics para integracion con Grafana. |
| **Prompt Injection** | Ataque donde un usuario intenta manipular el comportamiento de la IA mediante el input. ZOE tiene proteccion contra esto. |
| **psutil** | Libreria Python para monitorear recursos del sistema (CPU, RAM, disco). ZOE la usa para adaptarse al hardware. |

### Q

| Termino | Definicion |
|---------|-----------|
| **Q4_K_M** | Cuantizacion de 4 bits (moderada). Balance entre calidad y tamano. DeepSeek-R1:32B Q4_K_M = ~18 GB. |
| **IQ2_M** | Cuantizacion ultra-agresiva de 2 bits. Reduce tamano ~70% con ~93% de calidad. Ideal para Mac 8GB RAM. DeepSeek-R1:32B IQ2_M = ~12.5 GB. |
| **QwQ-32B** | Modelo de razonamiento de Qwen (Alibaba). 32B parametros, especializado en razonamiento paso a paso. |
| **Qwen 2.5** | Familia de modelos de Alibaba. ZOE usa versiones de 14B, 32B y 72B parametros. |

### R

| Termino | Definicion |
|---------|-----------|
| **Race Condition** | Error de concurrencia donde dos procesos compiten por el mismo recurso. ZOE evita esto usando asyncio.Lock. |
| **Rate Limiting** | Limite de 60 peticiones/minuto para proteger el dashboard contra abuso. |
| **ReflectionEngine** | Motor de reflexion autonoma v2.1.1 que usa DeepSeek-R1:32B para generar insights durante SLEEPING. |
| **ReflectionHook** | Conector que integra el ReflectionEngine con el metabolismo de ZOE (se activa durante SLEEPING). |
| **RLS** | Row Level Security. Proteccion de datos a nivel de fila en PostgreSQL. |

### S

| Termino | Definicion |
|---------|-----------|
| **Saliencia** | Metrica que mide cuanto deberia preocupar/destacar una memoria. Se calcula por recencia + emocion + confianza inversa + conexiones. |
| **Satiety** | Metrica de saciedad de informacion (0-1). Indica si ZOE esta "satisfecha" con el conocimiento recibido. |
| **SCO** | Synthetic Cognitive Organism. Lo que ZOE es: un organismo cognitivo sintetico, no un simple chatbot. |
| **Seed Mode** | Modo de inicializacion de ZOE. Genera una identidad unica a partir de valores proporcionados por el usuario. |
| **SHA-256** | Algoritmo de hash criptografico. ZOE lo usa para la identidad, federacion y verificacion de integridad. |
| **SMART** | Modo de ZOE que elige automaticamente el mejor modelo para cada pregunta usando el ACD Router. |
| **Society of Mind** | Teoria de Marvin Minsky: la mente es una sociedad de agentes especializados. ZOE implementa 12 sub-agentes. |
| **SQLite** | Base de datos ligera embebida. ZOE la usa por defecto para persistencia de memoria. |
| **SSL/TLS** | Protocolo de cifrado para conexiones seguras. El dashboard de ZOE lo usa para proteger comunicaciones. |
| **Sub-agente** | Agente especializado dentro del Society of Mind de ZOE. Hay 12: Perceiver, Forecaster, Speaker, Critic, Memorialist, Learner, Curator, Creativity, CausalEngine, EmotionalMotor, EthicalMotor, ScientificEngine. |
| **SLEEPING** | Estado metabolico donde ZOE consolida memoria y ejecuta reflexion autonoma. |

### T

| Termino | Definicion |
|---------|-----------|
| **Thinking Indicator** | Indicador visual "ZOE esta pensando..." con 3 puntos animados que aparece en el chat mientras ZOE procesa una respuesta. |
| **Timeout** | Limite de tiempo para una operacion. El ReflectionEngine tiene 120 segundos de timeout por reflexion. |
| **Token** | Unidad basica de texto para modelos LLM. ~4 caracteres = 1 token. Las APIs cobran por token, no por palabra. |
| **Trajectory Chain** | Cadena inmutable de mutaciones de la identidad de ZOE, similar a un blockchain. Cada cambio se firma con SHA-256. |
| **TTFT** | Time To First Token. Tiempo hasta el primer token de respuesta. ZOE lo optimiza segun el hardware. |

### U

| Termino | Definicion |
|---------|-----------|
| **Universal Model Bus** | Sistema que permite a ZOE comunicarse con multiples backends LLM de forma uniforme, con hot-swap y fallback. |
| **UTF-8** | Codificacion de caracteres que soporta todos los idiomas. ZOE la usa para espanol, ingles, frances y aleman. |

### V

| Termino | Definicion |
|---------|-----------|
| **Validacion Epistemica** | Proceso de verificacion de conocimiento mediante multiples fuentes independientes antes de aceptarlo como verdadero. |
| **Vector de crecimiento** | Una de las 9 dimensiones que definen la identidad de ZOE. Ejemplo: autonomia, creatividad, empatia... |

### W

| Termino | Definicion |
|---------|-----------|
| **WAL Mode** | Write-Ahead Logging. Modo de SQLite que mejora la concurrencia y previene corrupcion de datos. |
| **WebSocket** | Protocolo de comunicacion en tiempo real bidireccional. El chat del dashboard lo usa para conversacion instantanea. |
| **Waking** | Estado metabolico de transicion entre SLEEPING y AWAKE. ZOE restaura capacidades progresivamente. |

### Z

| Termino | Definicion |
|---------|-----------|
| **ZoePackager** | Herramienta que empaqueta una instancia de ZOE completa en un archivo .zoe portatil (identidad + memoria + capsulas). |
| **ZoeRuntime** | Entorno de ejecucion que coordina todos los componentes de ZOE en tiempo real. |
| **.zoe** | Formato de archivo portatil que contiene una instancia completa de ZOE (identidad + memoria + capsulas + configuracion). |

---

## 16. Referencia rapida {#16-referencia}

### Tabla de comandos

| Comando | Descripcion |
|---------|-------------|
| `zoe-chat --backend ollama --model auto` | Chat con ACD Router |
| `zoe-chat --backend openai --model gpt-4o` | Chat con OpenAI |
| `zoe-dashboard --backend ollama` | Iniciar dashboard |
| `python -m zoe.core.model_downloader --model qwq-32b-iq2` | Descargar modelo |
| `pytest zoe/tests/ -q` | Ejecutar tests |

### Tabla de variables de entorno

| Variable | Ejemplo |
|----------|---------|
| `ZOE_DATA` | `/Volumes/CrucialX9/ZOE/data` |
| `OPENAI_API_KEY` | `sk-abc123...` |
| `ZOE_CLOUD_BUDGET` | `2.0` |

### Tabla de modelos

| Modelo | Tamano | Velocidad | Uso | Requiere |
|--------|--------|-----------|-----|----------|
| gemma-2-9b-iq2 | 3.5 GB | 15-25 t/s | Preguntas simples | 4GB RAM |
| qwen2.5:32b-iq2 | 12.5 GB | 5-10 t/s | Equilibrado | 8GB RAM |
| qwq-32b-iq2 | 12.5 GB | 3-6 t/s | Razonamiento | 8GB RAM |
| deepseek-r1:32b-iq2 | 12.5 GB | 2-4 t/s | Reflexion (8GB) | 8GB RAM |
| deepseek-r1:32b-q4km | 18 GB | 2-4 t/s | Reflexion (16GB) | 16GB RAM |
| qwen2.5:72b-iq2 | 25 GB | 1-3 t/s | Maxima calidad | 8GB RAM |

### Tabla de endpoints del dashboard

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/health` | GET | Estado del sistema |
| `/api/reflections` | GET | Reflexiones recientes |
| `/api/providers/config` | GET/POST | Configuracion proveedores |
| `/api/providers/status` | GET | Estado de proveedores |
| `/ws` | WebSocket | Chat en tiempo real |

### Tabla de atajos de teclado (Dashboard)

| Atajo | Accion |
|-------|--------|
| `Enter` | Enviar mensaje |
| `Esc` | Cerrar modal |
| `Ctrl+K` | Enfocar campo de chat |

---

<p align="center">
  <b>ZOE v2.1.1 — Synthetic Cognitive Organism</b><br>
  1,700+ tests · 210 archivos Python · 15 capsulas · 84 endpoints · 6 backends LLM · 4 idiomas<br>
  DeepSeek-R1:32B IQ2_M/Q4_K_M · Reflexion autonoma adaptativa · SMART con ACD Router<br>
  <i>"ZOE no es un modelo que responde. Es un organismo que existe."</i>
</p>
