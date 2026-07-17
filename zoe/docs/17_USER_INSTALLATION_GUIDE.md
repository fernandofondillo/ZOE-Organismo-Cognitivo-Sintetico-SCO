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

ZOE trae un installer PowerShell (`install_windows.ps1`) que lo hace todo automático, **incluyendo detección de formato del SSD** (avisa si está en FAT32 antes de descargar modelos grandes).

### En Android

| Necesitas instalar | Para qué |
|---|---|
| Telegram (app gratuita) | Hablar con ZOE desde un bot (recomendado) |
| Chrome | Instalar el Dashboard como PWA en pantalla de inicio |
| (Avanzado) Termux desde F-Droid | Ejecutar ZOE dentro del propio móvil |

**Android no ejecuta ZOE de forma nativa.** Se usa a través de Telegram, PWA o (avanzado) Termux. Ver **Escenario H** más abajo.

### En iPhone / iPad

| Necesitas instalar | Para qué |
|---|---|
| Telegram (App Store, gratis) | Hablar con ZOE desde un bot (recomendado) |
| Safari (preinstalado) | Instalar el Dashboard como PWA en pantalla de inicio |
| (Hardware) Adaptador USB-C / Lightning | Conectar SSD externo a iPhone 15+ o iPad |

**iOS no ejecuta ZOE de forma nativa.** Se usa a través de Telegram, PWA en Safari o SSD externo (solo lectura). Ver **Escenario I** más abajo.

### Con un archivo .zoe (máxima portabilidad)

| Necesitas instalar |
|---|
| **Solo Python 3.10+** |

Un archivo `.zoe` contiene TODO: ZOE + memoria + cápsulas + patrones. No necesitas instalar nada más.

---

## Instalación paso a paso — Elige tu escenario

### Escenario A: SSD/Pendrive con instalación automática (recomendado, 5 minutos)

**Un solo comando** configura ZOE completo en tu SSD. No necesitas saber programar.

> ⚠️ **ANTES DE EMPEZAR — Formato del SSD**
>
> El formato del SSD es crítico. Los modelos de IA pesan entre 3.5 GB y 25 GB.
>
> | Formato | Compatible con | Ideal para | Limitación |
> |---|---|---|---|
> | **APFS** | Mac, iPhone, iPad | Solo Apple — máxima velocidad mmap | Windows/Android no lo leen |
> | **exFAT** | Mac, iPhone, Android, Windows | Multiplataforma — universal | Ninguna |
> | ~~FAT32~~ | ~~Todos~~ | ~~Dispositivos antiguos~~ | ❌ No permite archivos >4GB (inútil para modelos) |
>
> **¿Cómo formatear?**
> 1. Abre "Utilidad de Discos" en tu Mac
> 2. Selecciona tu SSD
> 3. Clic en "Borrar"
> 4. Formato: **APFS** (solo Mac) o **exFAT** (Mac + Windows + Android)
> 5. ⚠️ Esto borrará todo el contenido del SSD
>
> El instalador de ZOE detecta automáticamente el formato y te avisa si es incompatible.

```bash
# PASO 1: Conecta el SSD al Mac (usa el cable CORTO de la caja del SSD)
# PASO 2: Abre Terminal y ejecuta:
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh | bash
```

El instalador hace TODO automáticamente:
1. Detecta tu SSD y **verifica el formato** (avisa si es FAT32)
2. Verifica Python y Git
3. Instala ZOE + entorno virtual EN EL SSD (no carga tu Mac)
4. Te pregunta si instalar Ollama (IA local gratis)
5. Te pregunta qué setup de modelos IQ2_M descargar (minimal/balanced/complete/maximum)
6. Configura API keys opcionales
7. Crea scripts de doble clic (.command) con `--model auto` (ACD Router activo)
8. **Elimina el atributo quarantine** de macOS (los .command arrancan sin warning)
9. Arranca el Dashboard

### ¿Qué hace el ACD Router? (Sprint 5.7)

Cuando ejecutas `ZOE-Chat-Ollama.command`, el script lanza `zoe-chat --backend ollama --model auto`. Esto activa el **ACD Model Router**: ZOE detecta el tipo de pregunta y usa **el modelo óptimo** para cada una.

| Input del usuario | Nivel ACD | Modelo usado | Velocidad |
|---|---|---|---|
| "Hola" | L0_REFLEX | (sin LLM — tabla refleja) | <1ms |
| "¿Qué hora es?" | L1_FAST | Gemma 2 9B IQ2_M (3.5GB) | 15-25 t/s ⚡ |
| "Resume este artículo" | L2_STANDARD | Agents-A1 MoE IQ2_M (11.7GB) | 5-10 t/s ✅ |
| "Analiza las causas de esta depresión" | L3_DEEP | QwQ-32B IQ2_M (12.5GB) | 3-6 t/s 🧠 |
| "Compara 3 contratos jurídicamente" | L3_MAXIMUM | Qwen 2.5 72B IQ2_M (25GB) | 1-3 t/s 🎯 |

**Tú no configuras nada.** ZOE detecta qué modelos hay en el SSD y asigna cada uno al nivel cognitivo donde es mejor.

### Setups preseleccionados IQ2_M (Sprint 5.7)

Cuando el instalador te pregunte qué setup descargar, puedes elegir:

| Setup | Modelos | Tamaño | Cobertura | SSD mínimo |
|---|---|---|---|---|
| `minimal` | Solo Gemma 9B | 3.5 GB | L0/L1/L2 (Gemma para todo) | 16 GB |
| `balanced` ⭐ | Gemma + QwQ-32B | 16 GB | L0/L1 rápido + L3 profundo | 32 GB |
| `complete` | Gemma + MoE + QwQ | 28 GB | L0/L1 + L2 + L3 | 64 GB |
| `maximum` | Los 4 modelos | 53 GB | Todo el espectro (incluye Qwen 72B para L3_MAXIMUM) | 128 GB |

**Recomendación para SSD de 1TB:** setup `maximum` (53GB) — sobra 947GB para cápsulas, memoria y archivos `.zoe`.

**Recomendación para MacBook Air 8GB RAM:** setup `balanced` (16GB) — los modelos IQ2_M caben en RAM vía mmap y responden en tiempos razonables.

### Instalación manual de modelos IQ2_M (sin ejecutar el bootstrap)

Si ya tienes ZOE instalado pero quieres añadir los modelos IQ2_M:

```bash
# Ver qué modelos hay disponibles
python -m zoe.core.model_downloader --list

# Descargar un setup completo
python -m zoe.core.model_downloader --download-setup balanced
# (cambia 'balanced' por: minimal, complete, o maximum)

# O usar el asistente que detecta tu RAM y recomienda
python zoe/scripts/zoe_setup.py --check
python zoe/scripts/zoe_setup.py --install-iq2-models balanced
```

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

**¿Quieres IA de verdad?** Instala Ollama y los modelos IQ2_M:
```bash
# Descargar Ollama desde https://ollama.com e instalar

# Descargar los 4 modelos IQ2_M optimizados (recomendado: balanced, 16GB)
python -m zoe.core.model_downloader --download-setup balanced

# Lanzar ZOE con routing automático por nivel cognitivo
zoe-chat --backend ollama --model auto
# ZOE usará Gemma 9B para "Hola", QwQ-32B para análisis, Qwen 72B para comparativas
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

ZOE funciona nativamente en Windows 10/11 sin necesidad de WSL ni máquinas virtuales. El instalador de PowerShell configura todo en el SSD y crea lanzadores `.bat` para arrancar con doble clic.

> ⚠️ **ANTES DE EMPEZAR — Formato del SSD en Windows**
>
> Windows soporta tres formatos principales. La elección del formato es **crítica** si piensas mover el SSD entre dispositivos:
>
> | Formato | Compatible con | Ideal para | Limitación |
> |---|---|---|---|
> | **NTFS** | Solo Windows | Máxima velocidad en Windows | Mac lo lee pero no escribe sin drivers de terceros |
> | **exFAT** | Windows, Mac, Android, iPhone | Multiplataforma — universal | Ninguna (recomendado si usas varios dispositivos) |
> | ~~FAT32~~ | ~~Todos~~ | ~~Dispositivos antiguos~~ | ❌ No permite archivos >4GB (inútil para modelos de IA) |
>
> **¿Cómo formatear en Windows?**
> 1. Conecta el SSD
> 2. Abre el menú Inicio y escribe `diskmgmt.msc` → Enter (abre "Crear y formatear particiones del disco duro")
> 3. Click derecho sobre el volumen del SSD → "Formatear…"
> 4. Sistema de archivos: **NTFS** (solo Windows) o **exFAT** (multiplataforma)
> 5. ⚠️ Esto borrará todo el contenido del SSD
>
> El instalador `install_windows.ps1` detecta automáticamente el formato y te avisa si es FAT32 antes de iniciar la descarga de modelos grandes.

```powershell
# PASO 1: Instala Python 3.10+ desde https://python.org
#         (marca la casilla "Add Python to PATH" durante la instalación)

# PASO 2: Instala Git desde https://git-scm.com

# PASO 3: Conecta el SSD al PC

# PASO 4: Abre PowerShell (busca "PowerShell" en el menú Inicio)
#         Si nunca ejecutaste scripts, habilita permisos una vez:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# PASO 5: Descarga y ejecuta el instalador
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_windows.ps1" -OutFile "install_zoe.ps1"
.\install_zoe.ps1

# PASO 6: El instalador te pregunta:
#   - ¿Qué disco? → Elige la letra de tu SSD (D:, E:, etc.)
#   - ¿Sobrescribir si ya existe? → Normalmente "N"
#   - ¿Configurar OpenAI API key? → No (si no tienes)

# PASO 7: Cuando termine, ve al SSD en el Explorador
#   Doble clic en ZOE-Chat.bat            → ZOE responde (sin IA)
#   Doble clic en ZOE-Chat-Ollama.bat     → ZOE con IA local
#   Doble clic en ZOE-Dashboard.bat       → Dashboard web en http://localhost:8642
```

**Notas importantes para Windows:**
- Si PowerShell bloquea la ejecución del script, ejecuta `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (solo se hace una vez en la vida).
- Para usar IA local (Ollama), descarga e instala Ollama desde https://ollama.com antes de ejecutar `install_windows.ps1`. El instalador lo detecta automáticamente.
- Si tu SSD está en **exFAT**, puedes desconectarlo del PC, conectarlo a un Mac o un Android (con cable OTG) y ZOE funcionará allí también (siempre que el dispositivo tenga Python instalado).
- El entorno virtual (`venv\`) creado en Windows **no es portable a Mac/Linux**. Si quieres usar el mismo SSD en varias plataformas, usa el formato `.zoe` (ver Escenario E) o crea un `venv` por plataforma en subcarpetas separadas (`venv-win/`, `venv-mac/`).

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

### Escenario H: Android (móvil o tablet, 5-10 minutos)

Android **no puede ejecutar ZOE de forma nativa** porque ZOE requiere Python 3.10+ y Android no lo incluye por defecto. Tienes **tres opciones** para usar ZOE desde Android, ordenadas de más fácil a más avanzada:

#### Opción H1 — Telegram (la más fácil, recomendada para la mayoría)

Conversa con ZOE a través de un bot de Telegram. ZOE vive en tu Mac/PC/VPS y tú le hablas desde Telegram en cualquier sitio con internet.

```bash
# 1. En tu Mac/PC/VPS (donde ya tienes ZOE corriendo):
pip install python-telegram-bot

# 2. Habla con @BotFather en Telegram desde tu móvil:
#    - /newbot
#    - Elige nombre (ej: "Mi ZOE Personal")
#    - Elige username (ej: "mi_zoe_bot")
#    - BotFather te da un token (formato: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)

# 3. Lanza el bridge en tu Mac/PC:
python -m zoe.peripherals.telegram_bridge --token TU_TOKEN --zoe-url http://localhost:8642

# 4. Desde tu Android, abre Telegram, busca tu bot y empieza a hablar
```

**Ventajas:** no necesitas instalar nada en el móvil, funciona con datos móviles o WiFi, y la memoria de ZOE vive en tu Mac/PC (no se pierde si pierdes el móvil).
**Inconvenientes:** requiere que tu Mac/PC esté encendido y accesible (o uses un VPS).

#### Opción H2 — PWA (instalable como app nativa)

Si tienes ZOE Dashboard corriendo en tu red local (o en un VPS), puedes instalar el Dashboard como una app más en Android:

1. Arranca ZOE Dashboard en tu Mac/PC: `zoe-dashboard --backend pattern`
2. En tu Android, abre Chrome y ve a `http://IP-DE-TU-MAC:8642` (la IP la encuentras en Preferencias de Red del Mac)
3. Menú de Chrome (⋮) → **"Añadir a pantalla de inicio"**
4. Ahora ZOE aparece como un icono de app más en tu Android. Ábrela y conversa.

**Ventajas:** interfaz nativa, pantalla completa, sin barra de navegador.
**Inconvenientes:** solo funciona en tu red WiFi local (a menos que uses un VPS o un túnel).

#### Opción H3 — Termux (ZOE corriendo dentro del Android, avanzado)

Para usuarios técnicos que quieren ZOE 100% offline dentro del propio móvil:

```bash
# 1. Instala Termux desde F-Droid (NO uses la versión de Google Play, está obsoleta)
#    https://f-droid.org/packages/com.termux/

# 2. Dentro de Termux:
pkg update && pkg upgrade
pkg install python git
termux-setup-storage    # permite acceder al almacenamiento del móvil

# 3. Clona e instala ZOE:
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git
cd ZOE-Organismo-Cognitivo-Sintetico-SCO
pip install -e .

# 4. Arranca:
python -m zoe.cli_chat --backend pattern

# 5. (Opcional) Instala Ollama en Android vía Termux:
#    NOTA: Ollama no tiene build oficial para ARM Android.
#    Alternativa: usa ZOE con PatternSpeaker + cloud API key para L3.
```

**Ventajas:** ZOE funciona 100% offline dentro del móvil, sin depender de un ordenador.
**Inconvenientes:** sin Ollama (los móviles ARM no ejecutan modelos grandes razonablemente), solo PatternSpeaker + API cloud para L3. Requiere conocimientos técnicos.

#### SSD externo en Android (avanzado)

Si tienes un SSD en **exFAT** con ZOE instalado, puedes conectarlo a Android mediante un cable **USB OTG** (On-The-Go) o una hub USB-C:

1. Formatea el SSD como **exFAT** en tu Mac/PC (ver tabla anterior)
2. Instala ZOE en el SSD desde tu Mac/PC (Escenario A o C)
3. En Android, instala **Termux** + `pkg install python`
4. Conecta el SSD con cable OTG/USB-C
5. Android lo monta en `/storage/USB_DRIVE/`
6. En Termux: `cd /storage/USB_DRIVE/ZOE/zoe && python -m zoe.cli_chat --backend pattern`

**⚠️ Advertencias:** Android solo lee SSDs en **exFAT** o **FAT32** (no NTFS ni APFS). La velocidad por USB OTG suele ser lenta (~30-50 MB/s), así que los modelos grandes pueden no cargar bien en memoria. Recomendado solo para PatternSpeaker y memoria, no para ejecutar Ollama.

### Escenario I: iPhone o iPad (5 minutos)

iOS/iPadOS **tampoco ejecuta ZOE de forma nativa** por las mismas restricciones de Python. Tienes **tres opciones**:

#### Opción I1 — Telegram (la más fácil)

Idéntica a la opción H1 de Android. Habla con @BotFather desde tu iPhone, crea un bot, lanza el bridge en tu Mac/PC, y conversa con ZOE desde Telegram en iOS. Funciona igual de bien en iPhone, iPad y Mac.

#### Opción I2 — PWA en Safari (instalable como app)

Apple permite instalar PWAs desde Safari en iOS/iPadOS 16.4+:

1. Arranca ZOE Dashboard en tu Mac: `zoe-dashboard --backend pattern`
2. En tu iPhone/iPad, abre **Safari** y ve a `http://IP-DE-TU-MAC:8642`
3. Toca el botón **Compartir** (cuadrado con flecha hacia arriba)
4. Selecciona **"Añadir a pantalla de inicio"**
5. Ahora ZOE aparece como una app más en tu iPhone. Ábrela y conversa.

**⚠️ Notas iOS:**
- Debes usar **Safari** (Chrome y Firefox en iOS no soportan instalación de PWA correctamente).
- Para que ZOE sea accesible fuera de casa, necesitas un VPS o un túnel (Tailscale, Cloudflare Tunnel, etc.).
- Las notificaciones push de la PWA funcionan en iOS 16.4+ solo si sirves ZOE sobre HTTPS.

#### Opción I3 — SSD externo en iPhone/iPad (hardware)

Los iPhone 15 y posteriores (con puerto USB-C) y los iPad Pro/Air modernos **pueden leer SSDs externos** directamente con el adaptador correcto:

1. **Formato del SSD:** debe ser **exFAT** o **APFS** (iOS no lee NTFS)
   - APFS: máxima velocidad, pero solo Apple (no se puede usar en Windows/Android)
   - exFAT: universal, recomendado si también usarás el SSD en otros dispositivos
2. **Conexión física:**
   - iPhone 15+ / iPad USB-C: conecta el SSD directamente con cable USB-C
   - iPhone 14 o anterior (Lightning): necesitas el adaptador "Lightning a USB 3 Camera Adapter" (Apple, ~39€)
3. **App para acceder:** abre la app **"Archivos"** de iOS → busca tu SSD en "Ubicaciones"
4. **Uso de ZOE:** iOS no puede ejecutar Python, así que solo puedes **ver y copiar** el contenido del SSD (memoria, cápsulas, archivo .zoe). Para ejecutar ZOE necesitarás otro dispositivo (Mac/PC).

**El escenario ideal para iPhone + SSD externo** es:
1. Tienes ZOE instalada en un SSD exFAT (creado desde Mac o Windows)
2. Conectas el SSD a tu iPhone para revisar/copia tu memoria
3. Para conversar con ZOE desde el iPhone, usas Telegram (Opción I1) o PWA (Opción I2), conectándote a un Mac/VPS donde el SSD está enchufado

#### Archivo .zoe en iPhone (lo más portable)

El formato `.zoe` es la opción más elegante para iPhone:
1. Genera un archivo `mi_zoe.zoe` desde tu Mac/PC (ver Escenario E)
2. Envíatelo por AirDrop, Telegram o iCloud Drive al iPhone
3. Guárdalo en la app **Archivos** de iOS
4. Cuando quieras revivir esa ZOE, pásalo a un Mac/PC y ejecuta `python zoe_runtime.py`

Esto te permite llevar **múltiples ZOEs en el bolsillo** dentro del iPhone, cada una con su propia memoria e identidad, listas para despertar en cualquier ordenador.

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

# ¿Quieres IA real con 4 modelos IQ2_M y routing automático?
# (Sprint 5.7 — ACD Model Router)
# Instala Ollama desde https://ollama.com y luego:
python -m zoe.core.model_downloader --download-setup balanced  # 16GB, recomendado
zoe-chat --backend ollama --model auto
# ZOE usará Gemma/QwQ-32B/Qwen 72B según el tipo de pregunta automáticamente

# ¿SSD de 1TB? Setup maximum (los 4 modelos, 53GB):
python -m zoe.core.model_downloader --download-setup maximum
zoe-chat --backend ollama --model auto

# ¿Prefieres Dashboard web?
zoe-dashboard --backend pattern       # sin IA
zoe-dashboard --backend ollama --model auto  # con ACD Router
# → http://localhost:8642

# ¿No sabes qué hacer? Ejecuta el asistente (detecta tu RAM y recomienda setup):
python zoe/scripts/zoe_setup.py --check
python zoe/scripts/zoe_setup.py --install-iq2-models balanced
```

---

*ZOE V1.8.0 — Guía de Instalación y Uso para No Técnicos*
*Julio 2026 — Sprint 5.7: ACD Model Router + L3_MAXIMUM + 4 modelos IQ2_M*
