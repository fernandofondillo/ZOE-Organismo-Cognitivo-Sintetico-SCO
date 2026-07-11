# Guía de Instalación y Uso de ZOE para No Técnicos

> **No necesitas saber programar.** Esta guía te lleva paso a paso desde "no tengo nada" hasta "estoy hablando con ZOE".
> **Versión:** V1.8.0 — Julio 2026

---

## ¿Qué es ZOE en palabras simples?

ZOE es un **organismo digital que piensa**. No es un chatbot más como ChatGPT. Es diferente porque:

1. **Recuerda todo** — si le cuentas algo hoy, lo recordará dentro de meses
2. **Tiene identidad propia** — no depende de OpenAI ni de Google
3. **Se cansa y descansa** — como un ser vivo, no se cuelga
4. **Sabe qué sabe y qué no sabe** — no inventa con seguridad
5. **Aprende de cápsulas** — paquetes de conocimiento experto que cargas en segundos
6. **Funciona sin internet** — puede vivir 100% en tu ordenador
7. **Viaja en un pendrive** — tu ZOE va contigo a cualquier Mac o PC

---

## ¿Qué necesito instalar?

Depende de dónde quieras usar ZOE. Aquí está la **tabla definitiva**:

### En tu Mac o Linux (lo más fácil)

| Necesitas instalar | Ya lo tienes | Hay que instalar | Dónde |
|---|---|---|---|
| **Python 3.10+** | Probablemente no | ✅ Sí | https://python.org |
| **pip** (gestor de paquetes) | Viene con Python | ✅ Sí (automático) | — |
| **Git** (para descargar ZOE) | En Mac viene con Xcode | 🟡 Opcional | https://git-scm.com |
| **Ollama** (IA local gratis) | No | 🟡 Opcional | https://ollama.com |
| **API key de OpenAI** | No | 🟡 Opcional | https://platform.openai.com |

**Lo mínimo:** Python + pip. Con eso, ZOE funciona con PatternSpeaker (sin IA, pero responde).

**Lo recomendado:** Python + Ollama. Con eso, ZOE tiene IA local gratis.

### En un pendrive USB o SSD (portátil)

| En el Mac | En el pendrive/SSD |
|---|---|
| Python 3.10+ | ZOE (código) |
| Git | venv (entorno virtual) |
| (Opcional) Ollama | Memoria de ZOE |
| | (Opcional) Modelos de IA |

**El Mac solo necesita Python y Git.** Todo lo demás vive en el pendrive.

### En un VPS Linux (servidor remoto)

| Necesitas instalar |
|---|
| Python 3.10+ |
| Git |
| Ollama (recomendado) |
| ZOE (vía deploy.sh) |
| Nginx (para HTTPS, recomendado) |

### En Windows

| Necesitas instalar |
|---|
| Python 3.10+ (desde python.org) |
| Git (desde git-scm.com) |
| (Opcional) Ollama |

ZOE trae un installer PowerShell (`install_windows.ps1`) que lo hace todo automático.

### Con un archivo .zoe (máxima portabilidad)

| Necesitas instalar |
|---|
| **Solo Python 3.10+** |

Un archivo `.zoe` contiene TODO: ZOE + memoria + cápsulas + patrones. No necesitas instalar nada más.

---

## Instalación paso a paso — Elige tu escenario

### Escenario A: SSD/Pendrive con instalación automática (recomendado, 5 minutos)

**Un solo comando** configura ZOE completo en tu SSD. No necesitas saber programar.

```bash
# PASO 1: Conecta el SSD al Mac (usa el cable CORTO de la caja del SSD)
# PASO 2: Abre Terminal y ejecuta:
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh | bash
```

El instalador hace TODO automáticamente:
1. Detecta tu SSD
2. Verifica Python y Git
3. Instala ZOE + entorno virtual EN EL SSD (no carga tu Mac)
4. Te pregunta si instalar Ollama (IA local gratis)
5. Te pregunta qué modelos descargar (Gemma, Qwen, etc.)
6. Configura API keys opcionales
7. Crea scripts de doble clic (.command)
8. Arranca el Dashboard

**Cuando termine, ve al SSD en Finder y doble clic en ZOE-Dashboard.command**

### Escenario B: Mac o Linux (5 minutos, sin SSD)

```bash
# PASO 1: Descargar ZOE
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# PASO 2: Instalar
pip install -e .

# PASO 3: Hablar con ZOE (sin IA, funciona ya)
zoe-chat --backend pattern

# ¡Ya está! ZOE responde.
```

**¿Quieres IA de verdad?** Instala Ollama:
```bash
# Descargar desde https://ollama.com e instalar
ollama pull qwen2.5:3b     # 2GB, gratis
zoe-chat --backend ollama --model qwen2.5:3b
```

### Escenario B: Pendrive USB / SSD en Mac (10 minutos)

```bash
# PASO 1: Conecta el SSD al Mac (usa el cable CORTO de la caja)
# PASO 2: Abre Terminal y ejecuta:
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_pendrive_macos.sh | bash

# PASO 3: El instalador te pregunta:
#   - ¿Qué disco? → Elige tu SSD
#   - ¿API key de OpenAI? → No (si no tienes)
#   - ¿Instalar Ollama? → Sí (si quieres IA local)

# PASO 4: Cuando termine, ve al SSD en Finder
# Doble clic en ZOE-Chat.command → ¡ZOE responde!
# Doble clic en ZOE-Dashboard.command → Dashboard web
```

### Escenario C: Pendrive USB / SSD en Windows (10 minutos)

```powershell
# PASO 1: Conecta el SSD al PC
# PASO 2: Abre PowerShell y ejecuta:
.\install_windows.ps1

# PASO 3: El instalador te pregunta qué disco usar
# PASO 4: Cuando termine, ve al SSD
# Doble clic en ZOE-Chat.bat → ¡ZOE responde!
```

### Escenario D: VPS Linux (servidor, 15 minutos)

```bash
# PASO 1: Conectarse al VPS por SSH
ssh root@IP-DEL-VPS

# PASO 2: Instalar dependencias
apt update && apt install -y python3.12 git
curl -fsSL https://ollama.com/install.sh | sh

# PASO 3: Clonar ZOE
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git /opt/zoe
cd /opt/zoe
pip install -e .

# PASO 4: Ejecutar el script de deploy
sudo bash zoe/scripts/deploy.sh

# PASO 5: ZOE corre como servicio
sudo systemctl start zoe

# Acceder desde navegador: http://IP-DEL-VPS:8642
```

### Escenario E: Archivo .zoe portátil (2 minutos)

```bash
# Si ya tienes un archivo .zoe (descargado o compartido):
python -c "from zoe.core.zoe_packager import ZoePackager; ZoePackager().unpackage('mi_zoe.zoe', './ZOE')"
cd ZOE
python zoe_runtime.py
# ¡ZOE despierta con su memoria y cápsulas intactas!
```

### Escenario F: Telegram (móvil, 5 minutos)

```bash
# Requiere ZOE corriendo en un Mac, Linux o VPS
pip install python-telegram-bot

# Crear bot en Telegram (hablar con @BotFather, obtener token)
python -m zoe.peripherals.telegram_bridge --token TU_TOKEN --zoe-url http://localhost:8642

# Ahora habla con ZOE desde Telegram en tu móvil
```

### Escenario G: Voice-first (voz natural, 5 minutos)

```bash
# Requiere micrófono y altavoz
pip install openai-whisper sounddevice numpy

python -m zoe.peripherals.voice_first --zoe-url http://localhost:8642

# Di "Hey ZOE" y conversa por voz
```

---

## Configuración automática con `zoe-setup`

ZOE incluye un asistente que detecta qué tienes y te guía:

```bash
python zoe/scripts/zoe_setup.py
```

Este comando:
1. Detecta tu sistema (Mac, Linux, Windows)
2. Verifica Python, Git, Ollama, API keys
3. Te dice qué te falta y cómo instalarlo
4. Te recomienda el mejor modo para tu hardware
5. Te da el comando exacto para empezar

**Si no sabes por dónde empezar, ejecuta `zoe-setup` y sigue las instrucciones.**

---

## ¿Qué hace ZOE cuando la arrancas?

Cuando ejecutas `zoe-chat` o `zoe-dashboard`, ZOE hace esto automáticamente:

1. **Carga su identidad** — su ADN criptográfico (hash SHA-256 único)
2. **Carga su memoria** — todo lo que recuerda de sesiones anteriores (SQLite)
3. **Carga la cápsula basal** — conocimiento fundamental sobre sí misma
4. **Detecta qué tienes** — busca Ollama, API keys, modelos disponibles
5. **Elige el mejor modo** — si hay Ollama, lo usa; si no, PatternSpeaker; si hay API key, cloud
6. **Empieza a pensar** — el bucle cognitivo arranca (observar, predecir, decidir, actuar)
7. **Si nadie habla, piensa sola** — consolida memoria, detecta patrones, genera ideas

**Tú no configuras nada.** ZOE detecta y se adapta.

---

## Cómo usar ZOE — primeros pasos

### En CLI (terminal)

```bash
zoe-chat --backend pattern
```

```
zoe> Hola, ¿quién eres?
ZOE: Soy ZOE, un organismo cognitivo sintético. No soy un modelo
     de lenguaje, soy un organismo que existe continuamente.

zoe> ¿Qué puedes hacer?
ZOE: Puedo conversar, recordar lo que me dices, aprender de cápsulas
     de conocimiento, pensar autónomamente, y adaptarme a tu hardware.

zoe> Mi madre tiene 78 años y vive sola.
ZOE: Entiendo tu preocupación. Cuéntame más sobre su situación.

zoe> /stats
  Organism ID: zoe_default
  Iterations: 47
  Energy: 0.82  Fatigue: 0.15
  Memory entries: 12
  Capsules loaded: 2

zoe> /capsules
  Available capsules (15):
    📦 base_ethics — Ética general
    📦 zoe_basal_knowledge — Conocimiento basal
    📦 basic_psychology — Psicología general
    📦 elder_care_knowledge — Cuidado geriátrico
    ...

zoe> /capsule elder_care_knowledge
  ✅ Loaded: 54 entries injected

zoe> /quit
  Saving memory... ✅ 12 entries saved.
  Goodbye.
```

### En Dashboard web

```bash
zoe-dashboard --backend pattern
# → abre http://localhost:8642
```

El Dashboard tiene 3 paneles:
- **Izquierda:** estado del organismo (energía, fatiga, atención)
- **Centro:** chat en tiempo real
- **Derecha:** memoria viva + pensamientos autónomos

Botones:
- 📦 **Cápsulas** — ver y cargar cápsulas de conocimiento
- 🔒 **Cuarentena** — conocimiento en validación
- 🏪 **Marketplace** — comprar/descargar cápsulas
- 👨‍🏫 **Mentor** — configurar el tutor mentor de ZOE

---

## Cápsulas de conocimiento — qué son y cómo usarlas

### ¿Qué son?

Las cápsulas son **paquetes de conocimiento experto** que ZOE carga para aprender un dominio. Como libros que ZOE lee en segundos.

### Las 15 cápsulas que vienen por defecto

| Cápsula | Para qué sirve | Cuándo cargarla |
|---|---|---|
| `zoe_basal_knowledge` | Conocimiento fundamental de ZOE | Siempre (se carga sola) |
| `base_ethics` | Ética general | Siempre (recomendada) |
| `basic_psychology` | Psicología general | Cuando hablas de emociones |
| `communication_skills` | Comunicación empática | Cuando necesitas conversación profunda |
| `elder_care_knowledge` | Cuidado geriátrico | Para cuidado de mayores |
| `elder_care_skills` | Herramientas de cuidado | Para cuidado activo de mayores |
| `pharmacy_interactions` | Interacciones de medicamentos | Para consultas de medicación |
| `company_loneliness_knowledge` | Soledad y duelo | Para acompañar a personas solas |
| `vigilance_devops_knowledge` | Sistemas y monitoring | Para vigilancia de servidores |
| `research_methodology` | Método científico | Para investigación |
| `federation_b2b_skills` | Federación entre empresas | Para federación B2B |
| `b2c_assistant_growth` | Asistente personal | Para asistente a largo plazo |
| `ia_heredable_legal` | IA heredable | Para herencia digital |
| `multimodal_perception` | Visión y voz | Para imágenes y audio |
| `language_patterns` | Patrones de lenguaje | Para funcionar sin LLM |

### Cómo cargar una cápsula

```
zoe> /capsule elder_care_knowledge
✅ Loaded: 54 entries injected
```

O desde el Dashboard: botón 📦 Cápsulas → elegir → Cargar.

### Qué pasa cuando cargas una cápsula

ZOE "aprende" ese conocimiento en segundos:
1. Los hechos se inyectan en memoria semántica
2. Los procedimientos en memoria procedural
3. Los modelos causales en el CausalEngine
4. Las directrices éticas en el EthicalMotor
5. Los validadores en el Speaker y el Learner
6. Todo se firma en la Trajectory Chain (auditable)

**Sin reentrenar. Sin fine-tuning. Sin esperar.** ZOE ya sabe del dominio.

---

## Ventajas de ZOE — para qué sirve cada cosa

| Característica | Para qué sirve | Ventaja real |
|---|---|---|
| **Memoria persistente (11 tipos)** | Recuerda todo entre sesiones | No tienes que repetirle cosas |
| **Metabolismo (4 estados)** | Se cansa y descansa | No se cuelga por agotamiento |
| **Validación epistémica** | Sabe qué sabe y qué no | No te da información falsa con seguridad |
| **12 sub-agentes** | Piensa desde múltiples perspectivas | Respuestas más ricas y matizadas |
| **Cápsulas de conocimiento** | Aprende dominios en segundos | Sin reentrenar, sin esperar |
| **ACD (4 niveles)** | Piensa más en lo difícil, menos en lo simple | Ahorra tiempo y dinero |
| **PatternSpeaker** | Funciona sin LLM | Gratis, offline, sin instalar nada |
| **Multi-idioma** | Detecta tu idioma automáticamente | ES, EN, FR, DE |
| **Multi-modal** | Ve imágenes, escucha voz | No solo texto |
| **Voice-first** | Conversa por voz natural | Como hablar con una persona |
| **Formato .zoe** | Organismo completo en un archivo | Portátil, heredable |
| **Pendrive USB/SSD** | Viaja contigo | Tu ZOE en cualquier Mac/PC |
| **Telegram** | Usa ZOE desde el móvil | Sin app nativa |
| **Federación B2B** | Múltiples ZOEs colaboran | Conocimiento compartido con control |
| **Cognitive Optimization Layer** | Optimiza inferencia | Más rápido, más barato, más inteligente |

---

## ¿Por qué ZOE hace lo que hace?

### ACD (Adaptive Cognitive Depth) — por qué a veces responde rápido y a veces lento

ZOE tiene 4 niveles de profundidad de pensamiento:

| Nivel | Cuándo | Tiempo | Coste | Ejemplo |
|---|---|---|---|---|
| L0 Reflejo | "Hola", "Gracias" | <1s | 0€ | PatternSpeaker |
| L1 Rápido | Pregunta sencilla | 1-3s | 0€ | PatternSpeaker u Ollama 3B |
| L2 Estándar | Conversación normal | 3-10s | ~0.01€ | Ollama 7B o cloud |
| L3 Profundo | Análisis complejo | 10-60s | ~0.05€ | Cloud GPT-4o/Claude |

**ZOE decide automáticamente** qué nivel usar según tu mensaje. No configuras nada.

### Cognitive Optimization Layer — por qué ZOE es más eficiente

Antes de llamar al LLM, ZOE ya sabe:
- Qué tipo de pregunta es (ACD)
- Qué memoria tiene relevante
- Qué cápsulas están cargadas
- Qué energía le queda

Usa esa información para:
- **L0/L1:** responder con PatternSpeaker (no toca el LLM, instantáneo)
- **L2/L3:** pre-cargar el modelo y preparar contexto (ahorra 3-10s de espera)
- **Sin LLM:** responder con patrones + conocimiento de cápsulas

### Metabolismo — por qué a veces ZOE está "cansada"

ZOE tiene 4 estados como un ser vivo:
- **AWAKE:** estado normal, atención alta
- **DROWSY:** fatiga acumulada, respuestas más lentas
- **SLEEPING:** consolida memoria (reorganiza, fusiona, generaliza)
- **WAKING:** transición gradual

Cuando ZOE está cansada, duerme. Al despertar, tiene más energía y mejor memoria. **No se cuelga nunca.**

---

## Solución de problemas rápida

| Problema | Solución |
|---|---|
| ZOE va muy lento | Usa `--backend pattern` (sin LLM, instantáneo) |
| No tengo Ollama | ZOE funciona con PatternSpeaker. O instala Ollama desde ollama.com |
| No tengo API key | ZOE funciona con PatternSpeaker u Ollama. No necesitas API key |
| ZOE no recuerda nada | Ejecuta `/quit` para salir bien (guarda memoria). Verifica `zoe_data/` existe |
| Cable USB muy lento | Usa el cable CORTO de la caja del SSD (no el de carga del Mac) |
| Python no encontrado | Instala Python 3.10+ desde python.org |
| No sé qué backend usar | Ejecuta `python zoe/scripts/zoe_setup.py` — te lo dice |

---

## Resumen — cómo empezar en 30 segundos

```bash
# 1. Descargar
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO

# 2. Instalar
pip install -e .

# 3. Hablar con ZOE (sin IA, funciona ya)
zoe-chat --backend pattern

# ¿Quieres IA? Instala Ollama y:
zoe-chat --backend ollama --model qwen2.5:3b

# ¿Prefieres Dashboard web?
zoe-dashboard --backend pattern
# → http://localhost:8642

# ¿No sabes qué hacer? Ejecuta el asistente:
python zoe/scripts/zoe_setup.py
```

---

*ZOE V1.8.0 — Guía de Instalación y Uso para No Técnicos*
*Julio 2026*
