# Guía de Usuario Completa — ZOE v2.1

> **Versión:** 2.1.0 | **Fecha:** Julio 2026 | **Público:** Usuarios técnicos y no técnicos

---

## Índice

1. [Qué es ZOE](#qué-es-zoe)
2. [Instalación paso a paso](#instalación)
3. [Primer uso](#primer-uso)
4. [Los 5 modos de ZOE](#modos)
5. [El Dashboard](#dashboard)
6. [La memoria de ZOE](#memoria)
7. [El metabolismo](#metabolismo)
8. [Reflexión autónoma v2.1](#reflexión)
9. [Cápsulas de conocimiento](#cápsulas)
10. [ACD — El sistema de niveles](#acd)
11. [Configuración avanzada](#avanzado)
12. [Preguntas frecuentes (FAQ)](#faq)
13. [Solución de problemas](#problemas)

---

## 1. Qué es ZOE {#qué-es-zoe}

**ZOE es un compañero digital que piensa, recuerda, se cansa y aprende contigo.**

A diferencia de ChatGPT (que es como un actor brillante que actúa y se olvida todo), ZOE **existe continuamente**. Tiene:

- **Identidad propia** — Un "DNI digital" criptográfico que nunca cambia
- **Memoria viva** — 11 tipos de memoria que persisten entre sesiones
- **Metabolismo** — Se cansa, duerme, y consolida memoria durante el sueño
- **Reflexión autónoma v2.1** — Piensa por sí solo durante la noche, generando insights nuevos
- **15 cápsulas de conocimiento** — Especialidades médicas, farmacéuticas, de cuidado...

**ZOE vive en TU disco** (SSD, USB o Mac). No en servidores de terceros. Si desconectas el SSD y lo llevas a otro ordenador, ZOE sigue siendo la misma, con la misma memoria e identidad.

### Los LLMs son sus sentidos, no su cerebro

ZOE puede usar 6 "sentidos" (backends de IA):
- **PatternSpeaker** — Respuestas instantáneas (<1ms), sin IA, 100% offline
- **Ollama** — Modelos locales (Gemma, Qwen, DeepSeek) que corren en TU máquina
- **OpenAI** — GPT-4o (máxima calidad, requiere API key)
- **Anthropic** — Claude 3.5 Sonnet (alternativa de calidad)
- **ZAI** — Backend experimental
- **Mock** — Modo demo sin IA

ZOE elige automáticamente el mejor "sentido" según lo que le preguntes.

---

## 2. Instalación paso a paso {#instalación}

### Requisitos mínimos

| Requisito | Mínimo | Recomendado | Óptimo |
|-----------|--------|-------------|--------|
| RAM | 4 GB | 8 GB | 16 GB |
| Disco | 500 MB | 16 GB SSD | 128 GB SSD |
| Sistema | macOS/Linux | macOS 14+ | macOS + SSD Crucial X9 |
| Python | 3.10+ | 3.11+ | 3.12 |

### Opción A — SSD Crucial X9 + MacBook Air M3 (recomendado)

**Paso 1:** Conecta el SSD al Mac con el **cable CORTO** (el largo de carga es 10x más lento)

**Paso 2:** Abre Terminal (Cmd+Espacio, escribe "Terminal")

**Paso 3:** Ejecuta:

```bash
bash <(curl -sL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_ssd_crucial_x9_mac.sh)
```

El instalador hará:
1. Detectar tu SSD automáticamente
2. Verificar Python, RAM y sistema
3. Descargar ZOE desde GitHub
4. Crear un entorno virtual Python en el SSD
5. Instalar dependencias automáticamente
6. Crear lanzadores de doble click

**Paso 4:** Doble click en `INICIAR-ZOE.command` en tu SSD

### Opción B — Docker (producción)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
docker-compose up -d
```

### Opción C — Desarrollo (más rápido, sin IA)

```bash
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .
zoe-chat --backend pattern
```

---

## 3. Primer uso {#primer-uso}

Al iniciar ZOE por primera vez, verás un menú:

```
╔══════════════════════════════════════════════════════════╗
║  ZOE — Smart Launcher (v2.1.0)                          ║
╚══════════════════════════════════════════════════════════╝

  Selecciona modo de inicio:

  [1] SMART — ZOE elige automáticamente el mejor modelo
  [2] CHAT CLI — Terminal interactiva (texto)
  [3] DASHBOARD — Interfaz web (navegador)
  [4] OLLAMA — Solo modelos locales (100% offline)
  [5] OPENAI — Máxima calidad vía API cloud
  [6] ANTHROPIC — Claude vía API cloud
  [7] MOCK — Sin IA, modo demo
```

### Modo SMART (recomendado)

ZOE detecta automáticamente la complejidad de cada pregunta y elige el modelo óptimo:

| Si preguntas... | ZOE usa... | Tiempo |
|----------------|-----------|--------|
| "Hola" | PatternSpeaker (offline) | <1ms |
| "¿Qué hora es?" | Gemma 2 9B (local) | 1-2s |
| "Resume este artículo" | Agents-A1 MoE (local) | 3-5s |
| "Analiza causas profundas" | QwQ-32B (local) | 5-10s |
| "Compara 3 contratos legales" | Qwen 2.5 72B (local) | 10-30s |

### Primer mensaje

ZOE habla español por defecto. Puedes escribirle en español, inglés, francés o alemán.

```
Tú: Hola ZOE, ¿quién eres?
ZOE: [responde con su identidad, valores y propósito]

Tú: ¿Recuerdas quién soy?
ZOE: [responde basándose en su memoria episódica]
```

---

## 4. Los 5 modos de ZOE {#modos}

### Modo 1: SMART (elige automáticamente)

ZOE analiza cada pregunta y elige el mejor modelo. No tienes que pensar en nada.

```bash
zoe-chat --backend auto
```

### Modo 2: OLLAMA (100% offline, gratis)

Todos los modelos corren en tu máquina. No necesitas internet ni API keys.

```bash
# Descargar modelos optimizados
python -m zoe.core.model_downloader --download-setup balanced

# Iniciar
zoe-chat --backend ollama --model auto
```

**Modelos disponibles:**
- `gemma-2-9b-iq2` — Rápido, bueno para preguntas simples (~3.5GB)
- `qwen2.5:32b-iq2` — Equilibrado calidad/velocidad (~12.5GB)
- `qwq-32b-iq2` — Razonamiento profundo (~12.5GB)
- `deepseek-r1:32b-iq2` — Reflexión autónoma v2.1 (~18GB)
- `qwen2.5:72b-iq2` — Máxima calidad offline (~25GB)

### Modo 3: OPENAI/ANTHROPIC (máxima calidad)

Requiere API key pero ofrece la mejor calidad de respuesta.

```bash
export OPENAI_API_KEY="sk-..."
zoe-chat --backend openai_compatible --model gpt-4o
```

### Modo 4: DASHBOARD (interfaz web)

Abre tu navegador en `http://localhost:8642`:

```bash
zoe-dashboard --backend ollama
```

### Modo 5: MOCK (demo sin IA)

Para probar la interfaz sin consumir recursos.

```bash
zoe-chat --backend mock
```

---

## 5. El Dashboard {#dashboard}

El dashboard es la interfaz web de ZOE. Abre `http://localhost:8642` en tu navegador.

### Secciones principales

| Sección | Qué muestra |
|---------|-------------|
| **Chat** | Conversación en tiempo real con ZOE |
| **Estado** | Estado metabólico (AWAKE/DROWSY/SLEEPING), energía, fatiga |
| **Memoria** | Entradas de memoria por tipo (episódica, semántica, etc.) |
| **Identidad** | Hash SHA-256, 9 vectores de crecimiento, 7 valores |
| **Cápsulas** | 15 cápsulas cargadas, estado, validación |
| **Reflexiones v2.1** | Insights autogenerados durante SLEEPING, métricas, presupuesto cloud |
| **Mentor** | Evaluación de pensamientos, criterios de crecimiento |
| **Hardware** | SSDs detectados, velocidad de cable, uso de recursos |
| **Federación** | Validación epistémica, peers conectados |

### Nuevos endpoints v2.1 — Reflexión

```
GET /api/reflections         → Lista reflexiones recientes autogeneradas
GET /api/reflections/metrics → Métricas: insights generados, coste, presupuesto restante
GET /api/reflections/config  → Configuración: modelo usado, presupuesto diario, umbrales
```

---

## 6. La memoria de ZOE {#memoria}

ZOE tiene **11 tipos de memoria** que persisten entre sesiones:

| Tipo | Qué guarda | Ejemplo |
|------|-----------|---------|
| **Episódica** | Eventos con contexto temporal | "Ayer el usuario estaba preocupado por un contrato" |
| **Semántica** | Conceptos y relaciones | "Python es un lenguaje de programación interpretado" |
| **Procedural** | Habilidades y recetas | "Cómo hacer una tarta de manzana" |
| **Causal** | Causa-efecto verificado | "El estrés causa insomnio (validado por 3 fuentes)" |
| **Emocional** | Marcadores de relevancia | "Este tema genera ansiedad en el usuario" |
| **Corporal** | Estado de sensores | "Temperatura ambiente: 22°C, ruido: bajo" |
| **Social** | Modelos de otros agentes | "El usuario prefiere respuestas directas" |
| **Prospectiva** | Planes e intenciones | "El usuario quiere aprender Python en 3 meses" |
| **Contrafactual** | "Qué habría pasado si..." | "Si hubiera estudiado más, habría aprobado" |
| **Evolutiva** | Cambios en el conocimiento | "ZOE aprendió que el usuario es alérgico a los frutos secos" |
| **Cultural** | Normas y convenciones | "En España se cena a las 21:00" |

### Persistencia

- **SQLite** (por defecto) — Base de datos local en `zoe_data/memory.db`
- **PostgreSQL** (opcional) — Para despliegues multi-usuario
- **Backup automático** — Script en `zoe/scripts/backup.sh`

---

## 7. El metabolismo {#metabolismo}

ZOE tiene un metabolismo funcional con 4 estados:

```
AWAKE (despierto) → DROWSY (cansado) → SLEEPING (durmiendo) → WAKING (despertando)
```

### AWAKE (despierto)
- Atención alta, todos los sentidos activos
- Responde al usuario en tiempo real
- Elige modelos según complejidad de la pregunta

### DROWSY (cansado)
- Fatiga acumulada, capacidad reducida
- Usa modelos más ligeros para ahorrar energía
- Si la fatiga sigue subiendo → entra en SLEEPING

### SLEEPING (durmiendo) — v2.1: Ahora con reflexión autónoma
- **Consolida memoria** — Reorganiza, fusiona, generaliza memorias existentes
- **Reflexión autónoma v2.1** — Genera insights NUEVOS (ver sección 8)
- Recarga energía gradualmente
- Despierta cuando energía > 80% y fatiga < 20%

### WAKING (despertando)
- Transición gradual, no salta a full atención
- Restaura capacidades progresivamente

### Cómo afecta al usuario

- Cuando ZOE está SLEEPING, sigue respondiendo (pero más lentamente)
- Puedes despertarla con un estímulo fuerte (mensaje urgente)
- Durante la noche, ZOE "sueña" — reflexiona sobre el día y genera insights

---

## 8. Reflexión autónoma v2.1 {#reflexión}

**Nuevo en ZOE v2.1** — El ReflectionEngine permite que ZOE piense por sí misma durante la noche.

### Qué hace

Cuando ZOE duerme (SLEEPING), el ReflectionEngine:

1. **Selecciona memorias de alta saliencia** — Las experiencias más intensas, emocionales o importantes del día
2. **Ejecuta reflexión** — Usa un modelo de IA (DeepSeek-R1, QwQ-32B, etc.) para analizar patrones profundos
3. **Genera insights** — Nuevas conexiones, implicaciones, "qué habría pasado si..."
4. **Valida** — El MentorAgent evalúa la calidad + KnowledgeQuarantine filtra
5. **Persiste** — Guarda en memoria como COUNTERFACTUAL (simulaciones) y EVOLUTIONARY (evolución)

### Ejemplo real

```
Memoria episódica: "El usuario estaba estresado por una reunión importante"

→ Reflexión: "El usuario muestra un patrón de ansiedad previo a eventos
   profesionales críticos. Podría beneficiarse de técnicas de preparación
   mental. Recomendar mindfulness 10 min antes de reuniones importantes."

→ Guardado en: MemoryType.EVOLUTIONARY (confianza: 0.82)
```

### Presupuesto cloud inteligente

El ReflectionEngine puede usar modelos en la nube (OpenAI, Anthropic) cuando:
- El modelo local no está disponible
- Se necesita máxima calidad para una reflexión compleja
- Hay presupuesto disponible

**Configuración por defecto (segura para todos):**
- Presupuesto diario: **$1.00 USD** (configurable)
- Máximo 2 reflexiones por ciclo de sueño
- Timeout: 120 segundos por reflexión
- Modelo preferido: qwq-32b-iq2 (local)
- Fallback: qwen2.5:14b-iq2 (local, más ligero)

### Endpoints del dashboard

```
GET /api/reflections         → Ver insights generados
GET /api/reflections/metrics → Presupuesto restante, total insights, costes
GET /api/reflections/config  → Ver/modificar configuración
```

### ACD L4_REFLECTION

El sistema ACD (Adaptive Cognitive Depth) ahora incluye un nivel adicional:

| Nivel | Uso | Modelo |
|-------|-----|--------|
| L0-L3 | Interacción en tiempo real con el usuario | Gemma/Qwen/Agents |
| **L4_REFLECTION** | **Reflexión profunda durante SLEEPING** | **DeepSeek-R1:32b-iq2** |

---

## 9. Cápsulas de conocimiento {#cápsulas}

ZOE viene con **15 cápsulas** preinstaladas:

| Cápsula | Contenido | Entradas |
|---------|-----------|----------|
| elder_care_knowledge | Cuidado de mayores | 54 |
| pharmacy_interactions | Interacciones farmacéuticas | 20+ |
| chronic_disease_management | Gestión de enfermedades crónicas | 15+ |
| medical_protocols | Protocolos médicos | 12+ |
| emergency_response | Respuesta a emergencias | 10+ |
| ... | ... | ... |

### Cargar/descargar en runtime

```
Dashboard → Cápsulas → Load/Unload
```

Las cápsulas se inyectan en la memoria de ZOE, mejorando sus respuestas en esos dominios.

---

## 10. ACD — El sistema de niveles {#acd}

ACD (Adaptive Cognitive Depth) clasifica cada pregunta y elige el modelo óptimo:

| Nivel | Input típico | Modelo | Tamaño | Velocidad |
|-------|-------------|--------|--------|-----------|
| **L0_REFLEX** | "Hola", "Gracias" | PatternSpeaker | 0 GB | <1ms |
| **L1_FAST** | "¿Qué hora es?" | Gemma 2 9B IQ2_M | 3.5 GB | 15-25 t/s |
| **L2_STANDARD** | "Resume este artículo" | Agents-A1 MoE IQ2_M | 11.7 GB | 5-10 t/s |
| **L3_DEEP** | "Analiza causas profundas" | QwQ-32B IQ2_M | 12.5 GB | 3-6 t/s |
| **L3_MAXIMUM** | "Compara 3 contratos" | Qwen 2.5 72B IQ2_M | 25 GB | 1-3 t/s |
| **L4_REFLECTION** | Reflexión autónoma SLEEPING | DeepSeek-R1:32b-iq2 | 18 GB | 2-4 t/s |

**Hot-swap:** ZOE cambia de modelo en vivo, sin reiniciar.

---

## 11. Configuración avanzada {#avanzado}

### Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `ZOE_DATA` | Directorio de datos | `./zoe_data` |
| `ZOE_STORAGE_TYPE` | `sqlite` o `postgres` | `sqlite` |
| `POSTGRES_HOST` | Host PostgreSQL | `localhost` |
| `OPENAI_API_KEY` | API key de OpenAI | — |
| `ANTHROPIC_API_KEY` | API key de Anthropic | — |
| `ZOE_CLOUD_BUDGET` | Presupuesto diario cloud ($) | `1.0` |

### Configuración del ReflectionEngine

Edita `zoe/core/reflection_engine.py` o usa variables de entorno:

```python
ReflectionConfig(
    model_tag="deepseek-r1:32b-iq2",      # Modelo para reflexión
    daily_cloud_budget=2.0,                 # Presupuesto diario ($)
    max_reflections_per_cycle=3,            # Máximo por ciclo de sueño
    salience_threshold=0.5,                 # Umbral de saliencia
    reflection_timeout=180.0,               # Timeout (segundos)
)
```

---

## 12. Preguntas frecuentes (FAQ) {#faq}

### ¿ZOE funciona sin internet?
**Sí.** Con el modo Ollama, todos los modelos corren localmente. Solo necesitas internet para la instalación inicial.

### ¿Cuánto cuesta usar ZOE?
**Gratis** si usas modelos locales (Ollama). Si usas OpenAI/Anthropic, pagas por uso. El ReflectionEngine tiene un presupuesto diario configurable (default: $1/día).

### ¿Puedo llevar ZOE en un pendrive?
**Sí.** ZOE está diseñada para SSDs portátiles. Instala en el SSD, ejecútalo en cualquier Mac/PC/Linux.

### ¿ZOE recuerda conversaciones anteriores?
**Sí.** La memoria episódica persiste entre sesiones. ZOE recuerda lo que hablasteis ayer, la semana pasada, etc.

### ¿Es seguro?
**Sí.** Auditoría ZOE OMEGA confirmó 0 vulnerabilidades críticas. Auth obligatoria, rate limiting, headers de seguridad. Todo el código es open source.

### ¿Qué pasa si ZOE "sueña" mal?
El ReflectionEngine valida cada insight: MentorAgent evalúa calidad + KnowledgeQuarantine filtra. Solo insights con confianza > 0.5 se persisten. Puedes revisar y eliminar reflexiones desde el dashboard.

---

## 13. Solución de problemas {#problemas}

| Problema | Solución |
|----------|----------|
| "No se detecta el SSD" | Usa el cable CORTO (USB 3.2). El cable de carga es USB 2.0 (10x más lento) |
| "ZOE va muy lenta" | Reduce modelos cargados. Usa Gemma 2 9B en vez de Qwen 72B |
| "Error de RAM" | Cierra aplicaciones. Usa modelos más pequeños. Aumenta swap |
| "No responde en SLEEPING" | Normal — ZOE consolida memoria. Espera o envía estímulo fuerte |
| "Presupuesto cloud agotado" | Espera 24h para reset, o aumenta ZOE_CLOUD_BUDGET |
| "No compila en Windows" | Usa WSL2 (Windows Subsystem for Linux) |

### Dónde pedir ayuda

- **GitHub Issues:** https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/issues
- **Documentación técnica:** `zoe/docs/19_ZOE_TECHNICAL_INTERNALS.md`
- **Explicación para no técnicos:** `zoe/docs/18_ZOE_EXPLICACION_NO_TECNICOS.md`

---

<p align="center">
  <b>ZOE v2.1.0 — Synthetic Cognitive Organism</b><br>
  1,668+ tests · 205 archivos Python · 15 cápsulas · 81 endpoints · 6 backends LLM · 4 idiomas<br>
  Docker · Kubernetes · SSD portátil · 100% offline · Reflexión autónoma v2.1<br>
  <i>"ZOE no es un modelo que responde. Es un organismo que existe."</i>
</p>
