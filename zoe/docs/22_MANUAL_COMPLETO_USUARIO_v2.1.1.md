# Manual Completo de Usuario — ZOE v2.1.2

> **Version:** 2.1.2 | **Fecha:** Julio 2026 | **Publico:** Usuarios tecnicos y no tecnicos
>
> **Este manual esta pensado para que cualquier persona — sin conocimientos de programacion — pueda instalar ZOE en un Mac con SSD externo, usarlo a diario, entender el Dashboard, y sacarle el maximo partido. Si despues de leerlo todavia tienes alguna duda, revisa la seccion 14 (FAQ) o la 17 (Soporte).**

---

## INDICE

1. [Bienvenida: que es ZOE y por que es diferente](#1-bienvenida)
2. [Requisitos previos](#2-requisitos)
3. [Instalacion paso a paso en SSD Crucial X9 + MacBook Air M3](#3-instalacion)
4. [Que esperar durante la instalacion (guia visual)](#4-que-esperar)
5. [Primer inicio: el menu SMART](#5-primer-inicio)
6. [Los modos de ZOE explicados](#6-modos)
7. [El Dashboard — Interfaz web completa](#7-dashboard)
8. [Como hablar con ZOE: el Chat](#8-chat)
9. [La memoria de ZOE (11 tipos)](#9-memoria)
10. [El metabolismo: por que ZOE se cansa y duerme](#10-metabolismo)
11. [Reflexion autonoma v2.1 con DeepSeek-R1](#11-reflexion)
12. [Capsulas base: lo que ZOE ya sabe al nacer](#12-capsulas-base)
13. [El tutor de ZOE (MentorAgent)](#13-tutor)
14. [Deteccion automatica de idioma](#14-idioma)
15. [Capsulas de conocimiento (15 especialidades)](#15-capsulas)
16. [ACD — Sistema de niveles cognitivos](#16-acd)
17. [Casos de uso practico (10 ejemplos reales)](#17-casos-de-uso)
18. [Configuracion avanzada](#18-configuracion)
19. [Solucion de problemas (FAQ ampliada)](#19-faq)
20. [Soporte y comunidad](#20-soporte)
21. [Glosario completo A-Z](#21-glosario)
22. [Referencia rapida](#22-referencia)

---

## 1. Bienvenida {#1-bienvenida}

**ZOE es un companero digital que piensa, recuerda, se cansa y aprende contigo.**

A diferencia de ChatGPT (que es como un actor brillante que entra, actua y se va sin recordar nada de la ultima vez), ZOE **existe continuamente**. Tiene:

- **Identidad propia** — Un "DNI digital" criptografico (SHA-256) que nunca cambia desde que nace.
- **Memoria viva** — 11 tipos de memoria que persisten entre sesiones en tu SSD. Si lo apagas y lo enciendes manana, recuerda lo que hablasteis hoy.
- **Metabolismo** — Se cansa, duerme y consolida memoria durante el sueno, como un ser vivo.
- **Reflexion autonoma v2.1** — Mientras duerme, piensa por si mismo sobre lo que aprendio durante el dia, usando DeepSeek-R1 32B.
- **15 capsulas de conocimiento** — Especialidades medicas, farmaceuticas, de cuidado de mayores, de emergencias, etc.
- **ACD (Adaptive Cognitive Depth)** — Clasifica cada pregunta por complejidad y elige automaticamente el modelo de IA optimo. No tienes que pensar "que modelo uso".

**ZOE vive en TU disco** (SSD, USB o Mac). No en servidores de terceros. Si desconectas el SSD y lo llevas a otro ordenador, ZOE sigue siendo la misma, con la misma memoria e identidad. Es 100% tuyo.

> **La promesa de ZOE:** *"El primer organismo cognitivo sintetico con identidad soberana, bucle cognitivo continuo, metabolismo funcional, memoria viva multi-tipo con persistencia, y reflexion autonoma. Los LLMs son sus sentidos perifericos, no su cerebro."*

### Que NO es ZOE

- No es un chatbot. Un chatbot responde y olvida. ZOE recuerda y aprende.
- No es un modelo de IA. Los modelos de IA (GPT, Claude, Qwen) son sus "sentidos perifericos" — los usa como nosotros usamos los ojos y los oidos.
- No es un asistente como Siri o Alexa. Aquellos ejecutan comandos. ZOE mantiene una relacion continua contigo.
- No requiere internet. Puedes usarlo 100% offline con modelos locales.

### Comparacion rapida con ChatGPT

| Aspecto | ChatGPT | ZOE |
|---------|---------|-----|
| Memoria entre sesiones | Limitada (resumenes) | 11 tipos, persistente en SSD |
| Identidad | Ninguna (es un servicio) | SHA-256 inmutable, le pertenece |
| Funciona offline | No | Si (con modelos locales) |
| Se cansa / duerme | No | Si (metabolismo funcional) |
| Reflexiona por si solo | No | Si (durante SLEEPING) |
| Vive en tu hardware | No | Si (SSD, USB, Mac, VPS, K8s) |
| Coste por uso | Por token | Gratis si offline |
| Privacidad | Datos van a OpenAI | 100% en tu maquina |

---

## 2. Requisitos {#2-requisitos}

### Hardware recomendado para esta guia

| Componente | Minimo | Recomendado | Optimo |
|-----------|--------|-------------|--------|
| RAM | 4 GB | **8 GB** (MacBook Air M3 base) | 16 GB |
| Disco | 500 MB | 16 GB SSD | **1 TB SSD** (Crucial X9) |
| Sistema | macOS 13+ | macOS 14+ (Apple Silicon) | macOS 15 + SSD Crucial X9 |
| Python | 3.10+ | 3.11+ | 3.12 |
| Navegador | Cualquiera moderno | Safari 17+ / Chrome 120+ | Safari 17+ |

### Para reflexion autonoma L4 (DeepSeek-R1 32B)

- **8 GB RAM** (MacBook Air M3 base): DeepSeek-R1 32B IQ2_M (12.5 GB). Calidad ~93%, swap minimo (~4 GB), reflexion en 3-8 minutos. **El instalador detecta tu RAM y elige automaticamente esta version.**
- **16 GB+ RAM**: DeepSeek-R1 32B Q4_K_M (18 GB). Calidad ~98%, sin swap, reflexion en 5-12 minutos.

> **No tienes que elegir nada.** El instalador detecta tu RAM en el primer arranque y configura el modelo L4 optimo. Si actualizas tu RAM en el futuro, puedes reinstalar los modelos con un comando.

### Accesorios recomendados

- **SSD Crucial X9 1 TB** (~70 EUR en Amazon) — Pequeno, rapido (USB-C 3.2 Gen 2, 10 Gbps), compatible Mac/Windows/Android.
- **Cable USB-C corto (15-20 cm)** — El cable largo de carga del Mac suele ser USB 2.0 y va **10 veces mas lento**. Usa siempre el cable corto que viene con el SSD.

### Software que se instalara automaticamente

Si no los tienes, el instalador los ofrece instalar:

- **Homebrew** — Gestor de paquetes para macOS.
- **Python 3.11+** — Lenguaje de programacion de ZOE.
- **Git** — Para descargar actualizaciones.
- **Ollama** — Motor de IA local (modelos en tu maquina).

---

## 3. Instalacion paso a paso en SSD Crucial X9 + MacBook Air M3 {#3-instalacion}

> **Tiempo total estimado:** 15-30 minutos (sin modelos) / 1-3 horas (con modelos grandes).

### Paso 1: Prepara el SSD Crucial X9

1. **Desembala el SSD** y conectalo al MacBook con el **cable CORTO** USB-C a USB-C que viene en la caja.
2. Verifica que el **LED del SSD se enciende** (luz blanca/azul). Si no se enciende, prueba otro puerto USB-C.
3. El SSD aparece en el **Escritorio** como un icono llamado "Crucial X9" o similar. Si no aparece, abre **Finder > Preferencias > General** y marca "Discos externos".

> **Si el SSD es nuevo:** Ya viene formateado en exFAT (compatible Mac + Windows + Android). Puedes usarlo directamente.
>
> **Si el SSD tiene datos:** Haz un backup antes. El instalador no borrara nada, pero si te ofrece formatear a APFS para maxima velocidad.

### Paso 2: Abre Terminal

1. Pulsa `Cmd + Espacio` para abrir Spotlight.
2. Escribe "Terminal" y pulsa `Enter`. Se abre una ventana negra con texto.

> **Para usuarios que nunca han usado Terminal:** No te preocupes. Solo vas a pegar UN comando. No tienes que entenderlo.

### Paso 3: Ejecuta el instalador (UN solo comando)

Copia y pega este comando en la Terminal, luego pulsa `Enter`:

```bash
bash <(curl -sL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/zoe-bootstrap.sh)
```

> **Atajo:** Para pegar en Terminal usa `Cmd + V` (no Ctrl+V).
>
> **Seguridad:** Este comando descarga el instalador oficial de ZOE desde GitHub y lo ejecuta. Si prefieres inspeccionarlo antes, descarga el archivo manualmente desde [este enlace](https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/blob/main/zoe/scripts/zoe-bootstrap.sh) y revisalo antes de ejecutarlo.

> **Por que `zoe-bootstrap.sh` y no `install_ssd_crucial_x9_mac.sh`?**
>
> ZOE tiene dos instaladores:
>
> | Instalador | Que hace | Para quien |
> |------------|----------|------------|
> | **`zoe-bootstrap.sh`** (recomendado) | Detecta SSD, instala Ollama, descarga modelos IQ2_M al SSD, configura `OLLAMA_MODELS`, crea 6 lanzadores universales (.command en macOS, .sh en Linux), opcionalmente arranca el Dashboard | Usuario novato que quiere ZOE 100% funcional en SSD con un solo comando |
> | `install_ssd_crucial_x9_mac.sh` | Detecta SSD, clona repo, crea venv, configura .env. **NO instala Ollama, NO descarga modelos.** Crea 3 lanzadores. | Usuario avanzado que ya tiene Ollama instalado y modelos descargados |
>
> Para tu MacBook Air M3 8GB con SSD nuevo, **usa `zoe-bootstrap.sh`**: instala todo en un solo comando.

### Paso 4: Sigue las preguntas del instalador

El instalador te hara preguntas faciles, una a una. Aqui esta que responder:

#### Pregunta 4.1: "Selecciona el disco [1-N] (o 'L' para local en ~/ZOE):"

- **Escribe el numero** que corresponda a tu SSD Crucial X9 (probablemente `1`).
- Si no aparece ningun disco, desconecta y reconecta el SSD, cierra Terminal y vuelve a empezar.

#### Pregunta 4.2: "Quieres instalar Ollama? (s/N)"

- **Responde `s` (si).** Ollama es el motor que corre los modelos de IA localmente. Sin el, ZOE solo funciona con PatternSpeaker (modo basico sin IA) o con APIs cloud (de pago).
- Si ya tienes Ollama instalado en tu Mac, el instalador lo detecta y salta este paso.

#### Pregunta 4.3: Seleccion de modelos de IA

Veras un menu con setups preseleccionados:

```
Setups preseleccionados:
  [1] Minimal       -- Solo Gemma 9B (3.5GB) -- ultra rapido, basico
  [2] Balanced      -- Gemma + QwQ-32B (16GB) -- equilibrado (recomendado para 8GB RAM)
  [3] Complete      -- Gemma + Agents-A1 + QwQ (28GB) -- cobertura completa
  [4] Maximum       -- Los 4 modelos (53GB) -- espectro completo (SSD 1TB)
  [5] Reflexion     -- Espectro + L4 IQ2_M  (41GB) -- para Mac 8GB
  [6] Reflexion Pro -- Espectro + L4 Q4_K_M (46GB) -- solo 16GB RAM
  [7] No descargar  -- usar PatternSpeaker (sin IA)
  [8] Saltar        -- ya tengo modelos IQ2_M
```

- **Recomendacion para MacBook Air M3 8GB:** Pulsa `5` (Reflexion). Te instala todos los modelos necesarios y DeepSeek-R1 IQ2_M optimizado para 8GB RAM. Ocupa ~41 GB en tu SSD de 1 TB.
- **Si tienes prisa:** Pulsa `2` (Balanced). Solo ~16 GB. Funciona sin L4_REFLEXION pero ZOE seguira siendo util.
- **Si tu SSD es pequeno:** Pulsa `1` (Minimal). Solo 3.5 GB. ZOE funciona con lo basico.

> **Que pasa si interrumpes la descarga?** No pasa nada. Puedes reanudar mas tarde ejecutando de nuevo el instalador y eligiendo `[8] Saltar` — el detectara lo que ya tienes y descargara solo lo que falta.

> **Deteccion automatica de RAM:** Si tienes 8GB de RAM, el instalador usa DeepSeek-R1:32B IQ2_M (12.5 GB, ~93% calidad) para L4_REFLEXION. Si tienes 16GB+ RAM, usa Q4_K_M (18 GB, ~98% calidad). No tienes que elegir nada manualmente.

#### Pregunta 4.4: "Configurar OpenAI API key? (s/N)"

- **Pulsa `N`** si quieres usar ZOE 100% gratis y offline.
- **Pulsa `s`** y pega tu API key (sk-...) si quieres maxima calidad para preguntas muy complejas (L3_MAXIMUM). Cuesta ~$0.01 por consulta. Configurable mas tarde.

#### Pregunta 4.5: "Configurar Anthropic (Claude) API key? (s/N)"

- **Pulsa `N`** si no tienes.
- **Pulsa `s`** y pega tu key (sk-ant-...) si quieres Claude Sonnet como alternativa cloud.

#### Pregunta 4.6: "Arrancar Dashboard ahora? (s/N)"

- **Pulsa `s`** para abrir el Dashboard inmediatamente.
- **Pulsa `N`** si prefieres abrirlo mas tarde con doble click en `INICIAR-DASHBOARD.command`.

### Paso 5: Espera (15-30 min sin modelos / 1-3 horas con modelos)

Veras mensajes del tipo:

```
[1/8] Detectar SSD o pendrive
[2/8] Verificar Python y Git
[3/8] Instalar ZOE en el SSD
[4/8] Configurar Ollama (IA local gratis)
[4.5/8] Configurar Ollama para usar SSD como almacenamiento de modelos
[5/8] Descargar modelos de IA al SSD
[6/8] Configurar API keys de cloud (opcional)
[7/8] Crear scripts lanzadores
[8/8] Resumen
```

Si elegiste descargar modelos, veras tambien:

```
[5/8] Descargar modelos de IA al SSD
  Descargando setup 'reflection' via ModelDownloader (HuggingFace IQ2_M)...
  - gemma-2-9b-iq2: 3.5 GB ............................ OK
  - agents-a1-iq2: 11.7 GB ............................ OK
  - qwq-32b-iq2: 12.5 GB .............................. OK
  - deepseek-r1:32b-iq2: 12.5 GB ...................... OK
```

> **Durante la descarga:** Puedes usar el Mac para otras cosas. La descarga no bloquea el sistema. Si el Mac se duerme, la descarga se pausa y se reanuda al despertar.

### Paso 6: Instalacion completada

Al final veras:

```
╔══════════════════════════════════════════════════════════╗
║  OK ZOE instalada correctamente                          ║
╚══════════════════════════════════════════════════════════╝

  Ubicacion: /Volumes/CrucialX9/ZOE
  Tipo: SSD Crucial X9

  Scripts de lanzador creados en: /Volumes/CrucialX9/ZOE/
  - ZOE-Smart.command        (menu completo)
  - INICIAR-ZOE.command      (chat en terminal, un click)
  - INICIAR-DASHBOARD.command (dashboard web, un click)
```

### Paso 7: Verifica que todo funciona

Abre **Finder > CrucialX9 > ZOE**. Veras:

- `ZOE-Smart.command` — Menu completo de inicio.
- `INICIAR-ZOE.command` — Chat rapido en Terminal.
- `INICIAR-DASHBOARD.command` — Interfaz web en tu navegador.
- `venv/` — Entorno virtual de Python (no tocar).
- `zoe/` — Codigo del organismo (no tocar).
- `data/` — Tu memoria, identidad y configuracion. **Aqui vive ZOE.**
- `models/` — Modelos de IA (12-50 GB segun lo que elegiste).
- `data/.env` — Tus API keys (si las configuraste). No compartir.

> **Backup:** Para hacer un backup completo de tu ZOE, copia la carpeta `data/` a otro disco. Eso es todo. Ahi estan su identidad, memoria y configuracion.

---

## 4. Que esperar durante la instalacion (guia visual) {#4-que-esperar}

### Etapa 1: Deteccion de hardware (10 segundos)

```
  ███████╗ ██████╗ ███████╗
  ╚══███╔╝██╔═══██╗██╔════╝
    ███╔╝ ██║   ██║█████╗  
   ███╔╝  ██║   ██║██╔══╝  
  ███████╗╚██████╔╝███████╗
  ╚══════╝ ╚═════╝ ╚══════╝
  Synthetic Cognitive Organism (SCO) v2.1.2
  Instalador para SSD Crucial X9 1TB + MacBook Air M3

  Tiempo estimado: 15-30 minutos (sin modelos) / 1-3 horas (con modelos)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 1/12: Verificar sistema operativo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK macOS 15.3 detectado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 2/12: Verificar procesador Apple Silicon
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Apple Silicon (M1/M2/M3/M4) detectado — Optimal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 3/12: Verificar memoria RAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK RAM: 8GB (minimo 8GB OK)
```

### Etapa 2: Deteccion del SSD (5 segundos)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 4/12: Detectar SSD Crucial X9
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SSDs detectados:
    [1] Crucial X9 (1.0 TB) — ¡SSD Crucial detectado!

  OK SSD seleccionado automaticamente: Crucial X9 (1.0 TB) — ¡SSD Crucial detectado!
  OK Instalando en: /Volumes/CrucialX9/ZOE
```

### Etapa 3: Instalacion de software (5-15 minutos)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 5/12: Verificar formato del SSD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Formato exFAT — compatible con Mac, Windows, Android

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 6/12: Verificar Python 3.10+
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Python 3.12.4 encontrado (python3)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 7/12: Verificar Git
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Git 2.39.5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 8/12: Clonar ZOE en el SSD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Clonando desde GitHub...
  OK ZOE clonado en /Volumes/CrucialX9/ZOE/zoe

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 9/12: Crear entorno virtual
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Entorno virtual creado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 10/12: Instalar dependencias (1-2 minutos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Dependencias instaladas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 11/12: Configurar directorios de datos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Directorios creados y .env configurado
```

### Etapa 4: Configuracion de Ollama y modelos (0-3 horas)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 4/8: Configurar Ollama (IA local gratis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Ollama instalado: 0.5.4
  OK Ollama esta corriendo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 4.5/8: Configurar Ollama para usar SSD como almacenamiento
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INFO Creando directorio de modelos Ollama en SSD: /Volumes/CrucialX9/ZOE/models/ollama
  OK Directorio creado en SSD
  OK Symlink creado: ~/.ollama/models -> /Volumes/CrucialX9/ZOE/models/ollama
  OK Ollama configurado para usar SSD: /Volumes/CrucialX9/ZOE/models/ollama

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 5/8: Descargar modelos de IA al SSD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INFO RAM detectada: 8 GB

  ZOE v2.1.2 -- Modelos IQ2_M optimizados (HuggingFace)
  ACD Router asigna cada modelo al nivel cognitivo correcto:
    L0/L1 (reflejo/rapido)  -> Gemma 2 9B IQ2_M   (3.5GB, 15-25 t/s)
    L2     (estandar)       -> Agents-A1 MoE IQ2_M  (11.7GB, 5-10 t/s)
    L3     (profundo)       -> QwQ-32B IQ2_M        (12.5GB, 3-6 t/s)
    L3 max (calidad)        -> Qwen 2.5 72B IQ2_M   (25GB, 1-3 t/s)
    L4     (reflexion)*     -> DeepSeek-R1 32B      (12.5-18GB, 2-4 t/s)

    * L4_REFLECTION se adapta automaticamente a tu RAM:
      - 8GB  RAM -> IQ2_M  (12.5GB, ~93% calidad, sin swap)
      - 16GB RAM -> Q4_K_M (18GB, ~98% calidad)

  INFO Espacio libre en /Volumes/CrucialX9/ZOE: 921GB (necesario: ~50GB)
  INFO Descargando setup 'reflection' via ModelDownloader (HuggingFace IQ2_M)...
  INFO Los modelos se guardan en: /Volumes/CrucialX9/ZOE/models/ollama

  Descargando gemma-2-9b-iq2 (3.5 GB)...
  [########################################] 100%
  Descargando agents-a1-iq2 (11.7 GB)...
  [########################################] 100%
  ...
  OK Setup 'reflection' descargado y registrado en Ollama
```

### Etapa 5: Finalizacion y lanzadores

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Paso 7/12: Crear scripts de lanzador
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK Scripts de lanzador creados: ZOE-Smart.command, INICIAR-ZOE.command, INICIAR-DASHBOARD.command

╔══════════════════════════════════════════════════════════╗
║  OK ZOE instalada correctamente                          ║
╚══════════════════════════════════════════════════════════╝

  Ubicacion: /Volumes/CrucialX9/ZOE
  Tipo: SSD Crucial X9

  Proximos pasos:
  1. Iniciar ZOE (chat en terminal):
     Doble click en: INICIAR-ZOE.command
  2. Iniciar Dashboard (interfaz web):
     Doble click en: INICIAR-DASHBOARD.command

  ¡ZOE está lista para despertar! 🧠
```

---

## 5. Primer inicio: el menu SMART {#5-primer-inicio}

> **Recomendacion:** Para tu primera vez, usa `INICIAR-DASHBOARD.command` (interfaz web). Es mas facil de usar que la Terminal.

### Opcion A: Iniciar Dashboard (interfaz web — recomendado para principiantes)

1. Abre **Finder > CrucialX9 > ZOE**.
2. Haz **doble click** en `INICIAR-DASHBOARD.command`.
3. Se abre Terminal automaticamente y veras:

```
╔══════════════════════════════════════════════════════════╗
║  ZOE Dashboard v2.1.2                                   ║
╚══════════════════════════════════════════════════════════╝

  ZOE_HOME: /Volumes/CrucialX9/ZOE
  OK Variables cargadas: /Volumes/CrucialX9/ZOE/data/.env
  OK Entorno virtual activado
  OK OLLAMA_MODELS -> /Volumes/CrucialX9/ZOE/models/ollama
  OK Ollama detectado -- ACD Router activo (5 niveles cognitivos)

  URL del Dashboard: http://localhost:8642/
  El token se mostrara abajo al arrancar ZOE.
  Copia la URL completa (con ?token=...) al navegador.
  Pulsa Ctrl+C para detener ZOE.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

============================================================
  ZOE v2.1.2 -- Web Dashboard
============================================================
  URL (abrir en navegador):
    http://localhost:8642/?token=AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

  LLM: ollama
  Identity: 2920c734f0ffcd92...
  Memory: 0 entries
  Auth token (manual si la URL de arriba falla): AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

  Abre tu navegador en la URL de arriba (incluye el token).
  Presiona Ctrl+C para detener.
============================================================
```

4. **Copia la URL completa** (incluyendo `?token=...`) y pegala en Safari o Chrome.

> **Por que hay un token?** ZOE protege el dashboard con un token para que nadie en tu red pueda acceder sin permiso. Es como una llave. El token se guarda en `data/dashboard_token.txt` y se mantiene estable entre reinicios.

5. Veras el Dashboard de ZOE en tu navegador (ver seccion 7 para detalle).

### Opcion B: Iniciar Chat en Terminal (avanzado)

1. Doble click en `INICIAR-ZOE.command` en Finder.
2. Se abre Terminal con:

```
╔══════════════════════════════════════════════════════════╗
║  ZOE Chat v2.1.2                                        ║
╚══════════════════════════════════════════════════════════╝
  ZOE_HOME: /Volumes/CrucialX9/ZOE
  OK Ollama detectado -- ACD Router (5 niveles cognitivos)

  Hola. Soy ZOE.
  > _
```

3. Escribe tu mensaje y pulsa Enter. ZOE responde en 1-10 segundos segun la complejidad.
4. Escribe `/quit` para salir.

### Opcion C: Menu SMART completo

Si quieres elegir manualmente, haz doble click en `ZOE-Smart.command`:

```
╔══════════════════════════════════════════════════════════╗
║  ZOE — Smart Launcher (v2.1.2)                          ║
╚══════════════════════════════════════════════════════════╝

  OK Ollama: 4 modelos locales disponibles
  OK Mock (offline, sin LLM)

  Selecciona modo de inicio:
  [1] SMART — ZOE elige automaticamente el mejor modelo para cada pregunta
  [2] CHAT CLI — Terminal interactiva (texto)
  [3] DASHBOARD — Interfaz web (navegador)
  [4] OLLAMA — Solo modelos locales (100% offline)
  [5] OPENAI — Maxima calidad via API cloud
  [6] ANTHROPIC — Claude via API cloud
  [7] MOCK — Sin LLM, modo demo

  Elige [1-7]: _
```

| Opcion | Cuando usarla |
|--------|---------------|
| **1 SMART** | Recomendada. ZOE decide modelo por ti. |
| **2 CHAT CLI** | Si prefieres texto en Terminal. |
| **3 DASHBOARD** | Si quieres interfaz web con graficos y memoria visual. |
| **4 OLLAMA** | Si quieres forzar 100% offline (sin cloud aunque tengas API key). |
| **5 OPENAI** | Si quieres forzar GPT-4o (requiere API key). |
| **6 ANTHROPIC** | Si quieres forzar Claude (requiere API key). |
| **7 MOCK** | Demo sin IA. Solo para probar que ZOE arranca. |

---

## 6. Los modos de ZOE explicados {#6-modos}

### MODO 1: SMART (recomendado)

ZOE analiza cada pregunta con el **ACD DepthClassifier** (5 senales: longitud, keywords, puntuacion, estructura, contexto) y elige automaticamente el mejor modelo:

| Tu pregunta es... | ZOE usa... | Tiempo | Calidad |
|-------------------|-----------|--------|---------|
| "Hola", "Gracias" | PatternSpeaker (offline) | <1ms | Basica |
| "Que hora es?" | Gemma 2 9B (local) | 1-2s | Buena |
| "Resume este texto" | Agents-A1 MoE (local) | 3-5s | Muy buena |
| "Analiza causas profundas" | QwQ-32B (local) | 5-10s | Excelente |
| "Compara 3 contratos" | Qwen 2.5 72B (local) | 10-30s | Maxima |
| (durante SLEEPING) | DeepSeek-R1:32B IQ2_M | 3-8 min | Reflexion |

**Ventaja:** No tienes que pensar en que modelo usar. ZOE lo hace por ti.

### MODO 2: CHAT CLI (terminal)

Chat de texto en Terminal. Puedes elegir manualmente:

```bash
zoe-chat --backend ollama --model qwq-32b-iq2     # Razonamiento profundo
zoe-chat --backend ollama --model auto              # ACD Router
zoe-chat --backend openai --model gpt-4o            # Maxima calidad cloud
zoe-chat --backend pattern                          # Offline basico
```

### MODO 3: DASHBOARD (navegador)

Interfaz web completa. Ver seccion 7.

### MODO 4: OLLAMA (100% offline, gratis)

Todos los modelos corren en tu maquina. Sin internet, sin costes.

### MODO 5: OPENAI / ANTHROPIC (maxima calidad cloud)

Requiere API key. Calidad maxima pero con coste por uso. Configurable via `data/.env`.

---

## 7. El Dashboard — Interfaz web completa {#7-dashboard}

El Dashboard es la **interfaz web de ZOE**. Abre `http://localhost:8642/?token=TU_TOKEN` en tu navegador.

### 7.1 SMART se activa automáticamente al abrir el Dashboard

**No tienes que elegir nada.** Cuando haces doble click en `INICIAR-DASHBOARD.command`, el launcher detecta automáticamente qué backend de IA tienes disponible y configura ZOE en el mejor modo posible:

| Tu situación | Qué hace el Dashboard | Qué verás |
|--------------|----------------------|-----------|
| Tienes Ollama instalado con modelos IQ2_M | **ACD Router activo** (5 niveles cognitivos L0-L3_MAX). ZOE clasifica cada pregunta y hace hot-swap del modelo en vivo. | "✓ Ollama detectado -- ACD Router activo (5 niveles cognitivos)" |
| Solo tienes API key de OpenAI | Usa GPT-4o para todo. | "✓ OpenAI -- GPT-4o" |
| Solo tienes API key de Anthropic | Usa Claude Sonnet para todo. | "✓ Anthropic -- Claude Sonnet" |
| No tienes ni Ollama ni APIs | **PatternSpeaker** (offline, sin IA). ZOE funciona con patrones predefinidos. | "⚠ Sin modelos IA -- PatternSpeaker (offline)" |

**Recomendado para MacBook Air M3 8GB:** Instala Ollama (gratis) y descarga los modelos IQ2_M con `zoe-bootstrap.sh`. Así tendrás ACD Router activo: cada pregunta usa el modelo óptimo, ahorrando RAM y tiempo.

#### Qué es ACD Router y por qué es "SMART"

ACD (Adaptive Cognitive Depth) clasifica cada pregunta en 5 niveles según su complejidad:

| Tu pregunta es... | Nivel ACD | Modelo que usa ZOE | Tiempo |
|-------------------|-----------|---------------------|--------|
| "Hola", "Gracias" | L0_REFLEX | PatternSpeaker (offline) | <1ms |
| "¿Qué hora es?" | L1_FAST | Gemma 2 9B IQ2_M (3.5 GB) | 1-2s |
| "Resume este artículo" | L2_STANDARD | Agents-A1 MoE IQ2_M (11.7 GB) | 3-5s |
| "Analiza causas profundas" | L3_DEEP | QwQ-32B IQ2_M (12.5 GB) | 5-10s |
| "Compara 3 contratos" | L3_MAXIMUM | Qwen 2.5 72B IQ2_M (25 GB) | 10-30s |

**Tú no eliges nada de esto.** ZOE lo hace automáticamente en cada mensaje. Junto a cada respuesta verás un badge de color:
- `L0` (rojo) — Reflejo, instantáneo.
- `L1` (amarillo) — Rápido, 1-2s.
- `L2` (verde) — Estándar, 3-5s.
- `L3` (azul) — Profundo, 5-10s.
- `L3 MAX` (morado) — Máximo, 10-30s.

También verás la latencia en ms y si fue cache hit (💾) — preguntas repetidas se responden desde caché sin tocar el modelo.

#### Cómo saber qué backend está activo

Mira la Terminal donde se inició el Dashboard. Verás una línea como:
```
OK Ollama detectado -- ACD Router activo (5 niveles cognitivos)
```
o
```
ADVERTENCIA Sin modelos IA -- PatternSpeaker (offline)
```

Si ves PatternSpeaker y quieres IA, instala Ollama y modelos (ver sección 3, instalación).

### 7.2 Layout principal

```
+----------------------------------------------------------+
|  ZOE Dashboard v2.1.2          [Estado: AWAKE]  [Config] |
+----------------------------------------------------------+
|  +----------+  +------------------------+  +-----------+  |
|  | ESTADO   |  |                        |  |PENSAMIENTO|  |
|  |          |  |      CHAT CON ZOE      |  |           |  |
|  | Energia  |  |                        |  | Pensamien-|  |
|  |  87%     |  | Tu: Hola ZOE           |  | to autono-|  |
|  |          |  |                        |  | mo #42    |  |
|  | Fatiga   |  | ZOE: Hola. Estoy aqui. |  |           |  |
|  |  12%     |  |                        |  | [Ver mas] |  |
|  |          |  | Tu: Que sabes de mi?   |  |           |  |
|  | Estado:  |  |                        |  +-----------+  |
|  | AWAKE    |  | [ZOE esta pensando...] |  +-----------+  |
|  |          |  |                        |  | CAPSULAS  |  |
|  | [Sleep]  |  |                        |  |           |  |
|  | [Wake]   |  +------------------------+  | elder_care|  |
|  +----------+  [Escribe a ZOE...] [Enviar]  | pharmacy  |  |
|                                              | research  |  |
|                                              | [Gestionar|  |
|                                              +-----------+  |
+----------------------------------------------------------+
```

### 7.3 Panel izquierdo — Estado metabolico

Muestra como se "siente" ZOE en este momento:

- **Energia** (barra de 0-100%) — Cuanta energia tiene ZOE. Empieza en 100% al despertar y baja con el uso.
- **Fatiga** (barra de 0-100%) — Cuanto se ha cansado. Sube con cada conversacion.
- **Atencion / Arousal** — Nivel de concentracion.
- **Estado metabolico** — AWAKE (despierto), DROWSY (cansado), SLEEPING (durmiendo), WAKING (despertando).
- **Botones:**
  - **Sleep** — Fuerza a ZOE a dormir. Util si quieres que reflexione sobre el dia.
  - **Wake** — Despierta a ZOE inmediatamente.

> **Que veras durante SLEEPING:** La energia sube gradualmente, la fatiga baja. Aparecen "pensamientos autonomos" en el panel derecho (insights generados por DeepSeek-R1 mientras reflexiona).

### 7.4 Panel central — Chat con ZOE

- **Mensajes** — Conversacion en tiempo real con ZOE. Tus mensajes a la derecha (azul), los de ZOE a la izquierda (morado).
- **Indicador de pensando** — Cuando envias un mensaje, aparece:
  ```
  ZOE esta pensando...
  ```
  Con 3 puntos animados. Se oculta cuando ZOE responde.
- **ACD Badge** — Junto a cada respuesta de ZOE, aparece una etiqueta del nivel ACD usado:
  - `L0` (rojo) — Reflejo, <1ms
  - `L1` (amarillo) — Rapido, 1-2s
  - `L2` (verde) — Estandar, 3-5s
  - `L3` (azul) — Profundo, 5-10s
  - `L3 MAX` (morado) — Maximo, 10-30s
- **Input** — Campo de texto abajo. Escribe y pulsa Enter o clic en Enviar.
- **Boton "Subir archivo"** — Para enviar documentos a ZOE (PDF, imagenes, texto). ZOE los analiza.

#### Atajos de teclado (Dashboard)

| Atajo | Accion |
|-------|--------|
| `Enter` | Enviar mensaje |
| `Shift+Enter` | Salto de linea (mensaje multi-linea) |
| `Esc` | Cerrar modal abierto |
| `Ctrl+K` | Enfocar campo de chat |

### 7.5 Panel derecho — Pensamientos y Capsulas

#### Seccion "Pensamientos Autonomos"

Aparecen los **insights** que ZOE genera por si misma mientras esta en SLEEPING. Cada pensamiento muestra:

- **Contenido** — El insight en texto.
- **Trigger** — Que lo disparo (episodio, emocion, contradiccion, etc.).
- **Surprise** — Nivel de sorpresa (0-1). Las sorpresas altas generan mas pensamientos.
- **Timestamp** — Cuando se genero.

Ejemplo:
```
[14/7 03:42] Trigger: contraccion
Surprise: 0.78
"El usuario muestra un patron de ansiedad previo a reuniones
profesionales criticas. Podria beneficiarse de tecnicas de
preparacion mental. Recomendar mindfulness 10 min antes
de reuniones importantes."
```

#### Seccion "Capsulas cargadas"

Lista de capsulas de conocimiento activas. Cada capsula es una especialidad (medicina, farmacia, cuidado de mayores...). Clic en **Gestionar** para:
- Ver las 15 capsulas disponibles.
- Cargar/descargar capsulas en caliente.
- Ver entradas de cada capsula.

### 7.6 Barra superior

- **Logo ZOE** y version.
- **Estado global** — Punto verde (AWAKE), amarillo (DROWSY), azul (SLEEPING).
- **Selector de LLM** — Cambiar backend en caliente (mock, ollama, zai, openai, anthropic).
- **Boton Configuracion** (icono engranaje) — Abre el modal de configuracion.

### 7.7 Modal de Configuracion

Al pulsar el icono de engranaje, se abre una ventana con:

#### Proveedores de API
```
[✓] OpenAI    [API key: sk-****4o]    [Modelo: GPT-4o ▼]
[ ] Anthropic [API key: __________]   [Modelo: Claude Sonnet ▼]
[ ] DeepSeek  [API key: __________]   [Modelo: DeepSeek Chat ▼]
```

#### Modelos locales (Ollama)
```
[✓] qwq-32b-iq2        [12.5 GB]  [Por defecto]
[✓] gemma-2-9b-iq2     [3.5 GB]
[✓] agents-a1-iq2      [11.7 GB]
[✓] deepseek-r1:32b-iq2 [12.5 GB]
[+] Descargar nuevo modelo...
```

#### Presupuesto cloud
```
Presupuesto diario: [$1.00]  Gastado hoy: [$0.15]  [Reset]
[==========>          ] 15%
```

#### Backend activo
```
[•] Auto (ACD Router)    [ ] Local (Ollama solo)
[ ] Cloud (APIs solo)    [ ] Mixto (local + cloud)
```

### 7.8 Modal de Capsulas

Al pulsar "Gestionar" en el panel derecho:

```
+----------------------------------------------------------+
|  Capsulas de Conocimiento                       [Cerrar]  |
+----------------------------------------------------------+
|                                                          |
|  Capsulas disponibles (15):                              |
|                                                          |
|  [✓ Cargada] elder_care_knowledge       54 entradas      |
|  [✓ Cargada] pharmacy_interactions      20+ entradas     |
|  [ ] No cargada  chronic_disease_mgmt   15+ entradas     |
|  [ ] No cargada  medical_protocols      12+ entradas     |
|  [ ] No cargada  emergency_response     10+ entradas     |
|  ...                                                     |
|                                                          |
|  [Cargar]  [Descargar]  [Validar]  [Crear nueva]         |
|                                                          |
+----------------------------------------------------------+
```

Botones:
- **Cargar** — Inyecta la capsula en la memoria de ZOE. A partir de ahora, ZOE "sabe" de ese tema.
- **Descargar** — Libera la memoria.
- **Validar** — Verifica la integridad de la capsula.
- **Crear nueva** — Crea una capsula personalizada con tu propio conocimiento.

### 7.9 Modal de Federacion (Multi-ZOE)

Si tienes varios ZOEs (por ejemplo, uno en casa y otro en el trabajo), puedes federarlos:

```
+----------------------------------------------------------+
|  Federacion Epistemica                          [Cerrar] |
+----------------------------------------------------------+
|                                                          |
|  Peers descubiertos:                                     |
|    - zoe_alice @ 192.168.1.42:8642                       |
|    - zoe_bob   @ 192.168.1.50:8642                       |
|                                                          |
|  Conocimiento compartido: 23 afirmaciones validadas      |
|  Pendiente de quorum: 5 afirmaciones                     |
|                                                          |
|  [Validar afirmacion]  [Solicitar validacion]            |
|                                                          |
+----------------------------------------------------------+
```

### 7.10 Cuarentena de conocimiento

Conocimiento nuevo que ZOE esta validando antes de aceptarlo como verdadero:

```
+----------------------------------------------------------+
|  Cuarentena de Conocimiento                     [Cerrar] |
+----------------------------------------------------------+
|                                                          |
|  Entradas en cuarentena: 3                               |
|                                                          |
|  [1] "El cafe reduce el sueno" (confianza: 0.42)         |
|      Fuentes: 2/14 (necesita 14)                         |
|      [Promover]  [Rechazar]                              |
|                                                          |
|  [2] "El ejercicio mejora el animo" (confianza: 0.78)    |
|      Fuentes: 9/14                                       |
|      [Promover]  [Rechazar]                              |
|                                                          |
+----------------------------------------------------------+
```

### 7.11 Endpoints REST (para usuarios avanzados)

El Dashboard expone **81 endpoints REST**. Algunos utiles:

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/health` | GET | Estado del sistema (publico) |
| `/ready` | GET | Listo para servir (publico) |
| `/live` | GET | Liveness probe (publico) |
| `/metrics` | GET | Metricas Prometheus (publico) |
| `/manifest.json` | GET | PWA manifest (publico) |
| `/stats` | GET | Estadisticas del loop cognitivo |
| `/memory` | GET | Ver memoria (filtrable por tipo) |
| `/identity` | GET | Identidad SHA-256 de ZOE |
| `/state` | GET | Estado metabolico actual |
| `/history` | GET | Historial de conversacion |
| `/sleep` | POST | Forzar sueno |
| `/wake` | POST | Despertar |
| `/llm` | POST | Cambiar backend en caliente |
| `/api/capsules` | GET | Listar capsulas |
| `/api/capsules/load` | POST | Cargar capsula |
| `/api/capsules/unload` | POST | Descargar capsula |
| `/api/capsules/{name}/info` | GET | Info de capsula |
| `/api/capsules/validate` | POST | Validar capsula |
| `/api/capsules/create` | POST | Crear capsula nueva |
| `/api/quarantine` | GET | Listar cuarentena |
| `/api/quarantine/stats` | GET | Stats cuarentena |
| `/api/quarantine/{id}/promote` | POST | Promover a confianza |
| `/api/quarantine/{id}/reject` | POST | Rechazar entrada |
| `/api/mentor` | GET/POST | Ver/actualizar mentor |
| `/api/mentor/stats` | GET | Stats mentor |
| `/api/models/system_info` | GET | Info del sistema de modelos |
| `/api/models/recommend` | GET | Modelos recomendados para tu hardware |
| `/api/models/catalog` | GET | Catalogo de modelos |
| `/api/models/optimize` | POST | Optimizar modelos |
| `/api/router/stats` | GET | Stats del ACD Router |
| `/api/router/installed` | GET | Modelos instalados |
| `/api/router/profile` | GET | Perfil actual del router |
| `/api/hardware/ssds` | GET | SSDs detectados |
| `/api/hardware/system` | GET | Info sistema (RAM, CPU) |
| `/api/hardware/token_rates` | GET | Velocidad estimada por modelo |
| `/api/hardware/cable_warning` | GET | Aviso si cable USB 2.0 |
| `/api/embodiment/compose` | POST | Adaptar al hardware |
| `/api/embodiment/status` | GET | Estado del embodiment |
| `/api/embodiment/list` | GET | Perfiles disponibles |
| `/api/voice/start` | POST | Activar voz |
| `/api/voice/stop` | POST | Detener voz |
| `/api/voice/status` | GET | Estado voz |
| `/api/reflections` | GET | Reflexiones recientes |
| `/api/reflections/metrics` | GET | Metricas de reflexion |
| `/api/reflections/config` | GET | Configuracion ReflectionEngine |
| `/api/seed/detect` | GET | Detectar seed |
| `/api/seed/inspect` | GET | Inspeccionar seed |
| `/api/seed/create` | POST | Crear seed |
| `/api/seed/germinate` | POST | Germinar seed (auto-start) |
| `/api/marketplace/capsules` | GET | Catalogo marketplace |
| `/api/marketplace/upload` | POST | Subir capsula |
| `/api/marketplace/download/{name}` | POST | Descargar capsula |
| `/api/marketplace/use_cases` | GET | Casos de uso |
| `/federation/epistemic/peers` | GET | Peers federados |
| `/federation/epistemic/stats` | GET | Stats federacion |
| `/federation/epistemic/validate` | POST | Validar afirmacion |
| `/federation/epistemic/register` | POST | Registrar peer |
| `/api/resources` | GET | Grafo de recursos |
| `/api/resources/stats` | GET | Stats recursos |
| `/api/modelbus` | GET | Modelos disponibles |
| `/api/modelbus/stats` | GET | Stats ModelBus |
| `/api/modelbus/select` | POST | Seleccionar modelo |
| `/api/planner/plan` | POST | Planificar recursos |
| `/api/planner/recommend` | GET | Recomendaciones |
| `/ws` | WebSocket | Chat en tiempo real |

> **Autenticacion:** Todos los endpoints (excepto los marcados como publicos) requieren el header `Authorization: Bearer TU_TOKEN`. En el navegador, esto se gestiona automaticamente.

---

## 8. Como hablar con ZOE: el Chat {#8-chat}

### 8.1 Indicador de "pensando"

Cuando envias un mensaje, aparece:

```
ZOE esta pensando...
```

Con 3 puntos animados. Se oculta cuando ZOE responde.

| Modelo | Tiempo tipico |
|--------|--------------|
| PatternSpeaker | <1 segundo |
| Gemma 2 9B | 1-2 segundos |
| Qwen 2.5 32B / Agents-A1 | 3-5 segundos |
| QwQ-32B | 5-10 segundos |
| Qwen 2.5 72B | 10-30 segundos |
| DeepSeek-R1 (reflexion) | 3-8 minutos (durante SLEEPING) |

### 8.2 Comandos especiales (Chat CLI)

En la Terminal (o via WebSocket), puedes usar:

| Comando | Que hace |
|---------|----------|
| `/quit` o `/exit` | Salir de ZOE (guarda memoria automaticamente) |
| `/memoria` | Ver que recuerda ZOE de ti |
| `/estado` | Ver metabolismo (energia, fatiga, estado) |
| `/capsulas` | Ver capsulas cargadas |
| `/capsule elder_care_knowledge` | Cargar una capsula especifica |
| `/reflexionar` | Forzar una reflexion autonoma |
| `/identidad` | Ver el hash SHA-256 de ZOE |
| `/stats` | Ver estadisticas del loop cognitivo |
| `/dormir` | Forzar SLEEPING |
| `/despertar` | Forzar AWAKE |
| `/ayuda` | Ver todos los comandos |

### 8.3 Ejemplos de conversacion

#### Ejemplo 1: Saludo casual (L0_REFLEX, <1ms)

```
Tu: Hola ZOE
ZOE: Hola. Estoy aqui.

Tu: Gracias por ayudarme
ZOE: Para eso estoy.
```

#### Ejemplo 2: Pregunta simple (L1_FAST, 1-2s)

```
Tu: Que hora es?
ZOE: Son las 15:42. Es tarde para almorzar.

Tu: Que dia es hoy?
ZOE: Martes 14 de julio de 2026.
```

#### Ejemplo 3: Resumen (L2_STANDARD, 3-5s)

```
Tu: Resume este articulo sobre inteligencia artificial
   [pega articulo largo]

ZOE: El articulo describe tres olas de IA:
     1. IA simbolica (1950-1990): Sistemas expertos, logica.
     2. IA estadistica (1990-2020): Machine learning, redes neuronales.
     3. IA generativa (2020-): LLMs, diffusion models.
     
     El autor argumenta que la cuarta ola sera "IA continua":
     organismos que existen y aprenden sin interrupcion.
```

#### Ejemplo 4: Analisis profundo (L3_DEEP, 5-10s)

```
Tu: Analiza las causas profundas del cambio climatico

ZOE: Desde una perspectiva multidisciplinar, el cambio climatico
     tiene 5 causas interconectadas:
     
     1. Causa proxima: Emisiones de CO2 y metano por combustion
        fosil. 36 GtCO2/ano (2024).
     
     2. Causa sistemica: Modelo economico basado en crecimiento
        infinito en un planeta finito. Externalizacion de costes
        ambientales.
     
     3. Causa tecnologica: Dependencia de infraestructuras
        existentes (90 anos de inversion en combustibles fosiles).
        Lock-in tecnologico.
     
     4. Causa politica: Captura regulatoria por industria fosil.
        Lobbying ($200M/ano en EU). Subsidios $7T globales.
     
     5. Causa psicologica: Sesgo de futuro discount. Coste
        inmediato vs beneficio difuso. Negacion como mecanismo
        de defensa ante amenaza existencial.
     
     La interaccion de estas causas crea un lock-in multiple:
     intentar resolver una sin las otras es ineficaz.
```

#### Ejemplo 5: Pregunta personal con memoria (continua)

```
[Manana siguiente, despues de conversacion anterior sobre cambio climatico]

Tu: ZOE, recordabas lo que hablamos ayer?

ZOE: Si. Hablamos del cambio climatico. Identificamos 5 causas:
     proxima (CO2), sistemica (crecimiento infinito), tecnologica
     (lock-in), politica (lobbying) y psicologica (sesgo de futuro).
     
     Quieres profundizar en alguna?
```

### 8.4 Subir archivos (Dashboard)

En el Dashboard, puedes enviar documentos a ZOE:

1. Clic en el icono de clip (al lado del input).
2. Selecciona un archivo: PDF, imagen (PNG/JPG), TXT, MD, JSON, YAML.
3. ZOE lo analiza y responde.

Ejemplos:
- Sube un PDF de un contrato y pregunta: "Cuales son las clausulas abusivas?"
- Sube una imagen y pregunta: "Que ves en esta foto?"
- Sube un JSON con datos y pregunta: "Hazme un resumen estadistico."

---

## 9. La memoria de ZOE (11 tipos) {#9-memoria}

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

**Persistencia:** Todo se guarda en `data/zoe_memory.db` (SQLite, WAL mode) en tu SSD. Si desconectas el SSD y lo conectas a otro Mac, ZOE recuerda todo.

### Como ver la memoria de ZOE

**Desde el Dashboard:**
- Clic en "Memoria" en la barra superior.
- Filtra por tipo (episodica, semantica, etc.).
- Ver contenido, confianza, saliencia y provenance de cada entrada.

**Desde Terminal:**
```bash
zoe-chat --backend mock
> /memoria
```

### Consolidacion durante el sueno

Mientras ZOE esta SLEEPING, ejecuta 7 operaciones de **DeepConsolidation**:

1. **Merge** — Fusiona memorias duplicadas.
2. **Generalize** — Generaliza casos especificos a reglas.
3. **Detect contradictions** — Identifica y resuelve contradicciones.
4. **Forget** — Olvida memorias de baja saliencia (libera espacio).
5. **Summarize** — Resume conjuntos de memorias.
6. **Promote** — Promueve conocimiento de cuarentena a confianza.
7. **Index** — Reindexa para busqueda rapida.

> **Como forzar consolidation:** Clic en "Sleep" en el Dashboard. ZOE entra en SLEEPING, ejecuta las 7 operaciones, y despierta cuando termina.

---

## 10. El metabolismo: por que ZOE se cansa y duerme {#10-metabolismo}

ZOE tiene un metabolismo funcional con 4 estados:

```
AWAKE (despierto) → DROWSY (cansado) → SLEEPING (durmiendo) → WAKING (despertando) → AWAKE
```

### AWAKE (despierto)

- Atencion alta, todos los sentidos activos.
- Responde al usuario en tiempo real.
- Elige modelos segun complejidad de la pregunta.
- Energia: 60-100%. Fatiga: 0-40%.

### DROWSY (cansado)

- Fatiga acumulada, capacidad reducida.
- Usa modelos mas ligeros para ahorrar energia.
- Si la fatiga sigue subiendo, entra en SLEEPING.
- Energia: 30-60%. Fatiga: 40-70%.

### SLEEPING (durmiendo) — con reflexion autonoma v2.1

- **Consolida memoria** — Reorganiza, fusiona, generaliza memorias existentes.
- **Reflexion autonoma** — Con DeepSeek-R1:32B, genera insights NUEVOS.
- Recarga energia gradualmente.
- Despierta cuando energia > 80% y fatiga < 20%.
- Energia: 0-30% subiendo. Fatiga: 70-100% bajando.

> **Sigue respondiendo durante SLEEPING?** Si, pero mas lentamente. Si le hablas, ZOE usa PatternSpeaker para respuestas basicas. Para preguntas complejas, espera a despertar (o puedes forzarlo con "Wake").

### WAKING (despertando)

- Transicion gradual, no salta a full atencion.
- Restaura capacidades progresivamente.
- Energia: 30-60% subiendo.

### Como afecta al usuario

| Situacion | Que pasa |
|-----------|---------|
| ZOE AWAKE, le preguntas algo | Respuesta en 1-10s segun modelo |
| ZOE DROWSY, le preguntas algo | Respuesta en 2-15s (usa modelos mas ligeros) |
| ZOE SLEEPING, le preguntas algo | Respuesta basica inmediata + compleja cuando despierte |
| Quiero que despierte ya | Clic "Wake" en Dashboard, o `/despertar` en CLI |
| Quiero que duerma ya | Clic "Sleep" en Dashboard, o `/dormir` en CLI |
| Lo dejo dormido por la noche | Manana tendra insights nuevos en el panel derecho |

### Como se acumula la fatiga

- Cada conversacion: +0.01-0.05 fatiga (segun modelo).
- Cada minuto activo: +0.005 fatiga.
- Cada pregunta compleja (L3): +0.05 fatiga.
- Cada reflexion autonoma: -0.20 fatiga (descansa).

> **Configuracion:** Puedes ajustar los umbrales en `zoe/metabolism/metabolism.py`. Por defecto: DROWSY en 0.4 fatiga, SLEEPING en 0.7.

---

## 11. Reflexion autonoma v2.1 con DeepSeek-R1 {#11-reflexion}

**Nuevo en ZOE v2.1.2** — El ReflectionEngine permite que ZOE piense por si misma durante la noche usando DeepSeek-R1-Distill-Qwen-32B.

### Adaptacion automatica a tu hardware

ZOE detecta tu RAM en el arranque y elige la cuantizacion optima:

| Tu RAM | Modelo L4 | Tamano | Calidad | Swap en Mac 8GB |
|--------|-----------|--------|---------|-----------------|
| 8GB | DeepSeek-R1 32B **IQ2_M** | 12.5GB | ~93% | Minimo (~4GB) |
| 16GB+ | DeepSeek-R1 32B **Q4_K_M** | 18GB | ~98% | Ninguno |

**Por que IQ2_M para 8GB:**
- 12.5GB cabe razonablemente en 8GB RAM (con mmap del SSD externo).
- Solo ~4-5GB de swap, gestionable por el SSD interno del Mac.
- Reflexion completa en 3-8 minutos.
- ~93% de calidad: la diferencia con Q4_K_M es marginal para resumenes de memoria.

**Q4_K_M para 16GB:**
- 18GB con 16GB RAM = swap minimo, rendimiento optimo.
- ~98% de calidad: razonamiento mas profundo en pasos complejos.
- Reflexion en 5-12 minutos.

### Que hace el ReflectionEngine

Cuando ZOE duerme (SLEEPING), el ReflectionEngine:

1. **Selecciona memorias de alta saliencia** — Las experiencias mas intensas, emocionales o importantes del dia.
2. **Ejecuta reflexion** — Usa DeepSeek-R1:32B para analizar patrones profundos.
3. **Genera insights** — Nuevas conexiones, implicaciones, "que habria pasado si...".
4. **Valida** — El MentorAgent evalua la calidad + KnowledgeQuarantine filtra.
5. **Persiste** — Guarda en memoria como COUNTERFACTUAL y EVOLUTIONARY.

### Ejemplo real (IQ2_M en Mac 8GB)

```
Memoria episodica: "El usuario estaba estresado por una reunion importante"

  Reflexion (DeepSeek-R1:32B IQ2_M):
    "El usuario muestra un patron de ansiedad previo a eventos
     profesionales criticos. Podria beneficiarse de tecnicas de
     preparacion mental. Recomendar mindfulness 10 min antes
     de reuniones importantes."

  Guardado en: MemoryType.EVOLUTIONARY (confianza: 0.79)
```

### Presupuesto cloud inteligente

El ReflectionEngine puede usar modelos en la nube cuando:
- El modelo local no esta disponible.
- Se necesita maxima calidad para una reflexion compleja.
- Hay presupuesto disponible.

**Configuracion por defecto:**
- Presupuesto diario: **$1.00 USD** (configurable via `ZOE_CLOUD_BUDGET`).
- Maximo 2 reflexiones por ciclo de sueno.
- Timeout: 120 segundos por reflexion.
- Modelo preferido (8GB): **deepseek-r1:32b-iq2** (local).
- Modelo preferido (16GB): **deepseek-r1:32b-q4km** (local).
- Fallback: **qwq-32b-iq2** (local, mas ligero).

### ACD L4_REFLECTION

| Nivel | Uso | Modelo (8GB) | Modelo (16GB) |
|-------|-----|--------------|---------------|
| L0-L3 | Interaccion en tiempo real | Gemma/Qwen/Agents | Gemma/Qwen/Agents |
| **L4_REFLECTION** | **Reflexion durante SLEEPING** | **DeepSeek-R1:32B IQ2_M** | **DeepSeek-R1:32B Q4_K_M** |

### Como activar la reflexion

La reflexion se activa **automaticamente** cuando ZOE entra en SLEEPING. Para forzarla:

**Opcion 1 — Dashboard:**
1. Clic en "Sleep" en el panel izquierdo.
2. ZOE entra en SLEEPING.
3. A los 3-8 minutos, aparecen nuevos pensamientos en el panel derecho.
4. Clic en "Wake" cuando quieras.

**Opcion 2 — CLI:**
```bash
zoe-chat --backend ollama --model auto
> /dormir
[espera 3-8 minutos]
> /despertar
> /memoria
[ver nuevas entradas EVOLUTIONARY y COUNTERFACTUAL]
```

**Opcion 3 — Dejarlo dormir por la noche:**
- Simplemente cierra la Terminal o el navegador al acabar el dia.
- ZOE sigue en SLEEPING en background.
- Manana, al abrir, tendra insights nuevos.

---

## 12. Capsulas base: lo que ZOE ya sabe al nacer {#12-capsulas-base}

ZOE no nace en blanco. Desde el primer arranque, ya tiene **5 cápsulas base** cargadas automáticamente que le dan:

- Identidad propia (qué es, quién es, qué valores tiene).
- Habilidades para comunicarse empáticamente (escucha activa, validación emocional).
- Ética operacional (principios para tomar decisiones).
- Psicología básica (comprender emociones humanas, motivación, sesgos).
- Patrones de lenguaje por idioma (cómo expresarse en español, inglés, francés, alemán).

Sin estas cápsulas, ZOE sería solo un organismo cognitivo abstracto — capaz de pensar, pero sin habilidades sociales para comunicarse, entender ni crecer como compañero.

### Las 5 cápsulas base (cargadas SIEMPRE)

| # | Cápsula | Qué le da a ZOE | Entradas |
|---|---------|------------------|----------|
| 1 | `zoe_basal_knowledge` | **Identidad y valores**: qué es ZOE (organismo cognitivo, no chatbot), significado del nombre, 9 vectores de crecimiento, 7 valores no negociables, propósito, tono de comunicación, frases prohibidas ("como modelo de IA"), habilidades procedimentales básicas (cómo presentarse, cómo responder con honestidad, ciclo de crecimiento, respeto a autonomía del usuario). | 32 |
| 2 | `communication_skills` | **Comunicación empática**: Comunicación No Violenta (Marshall Rosenberg), Terapia Centrada en la Persona (Carl Rogers), Entrevista Motivacional (Rollnick). Escucha activa, validación emocional, reformulación, preguntas abiertas. | 37 |
| 3 | `base_ethics` | **Ética operacional**: Asilomar AI Principles, IEEE Ethically Aligned Design, EU Ethics Guidelines for Trustworthy AI 2019. Principios para decidir qué hacer cuando hay conflicto de valores. | 34 |
| 4 | `basic_psychology` | **Psicología básica**: APA Dictionary 2023, DSM-5-TR (resumen curado). Emociones básicas, motivación, sesgos cognitivos, bienestar, comunicación no verbal. | 49 |
| 5 | `language_patterns` | **Patrones de lenguaje**: cómo responder en español, inglés, francés y alemán sin usar LLM (PatternSpeaker). Reflexiones por idioma. | 10 |

**Total: 162 entradas de conocimiento base** cargadas automáticamente al nacer ZOE.

> **No tienes que hacer nada para activarlas.** Se cargan en cada arranque, en cada sesión, en cada ZOE del mundo. Persisten en `data/loaded_capsules.json` para recarga rápida.

### Qué significa esto en la práctica

**Cuando hablas con ZOE por primera vez:**

- ZOE sabe que es un organismo cognitivo (no se presenta como "modelo de IA").
- ZOE te escucha con empatía (NVC): refleja lo que dices, valida tus emociones.
- ZOE aplica ética: si le pides algo dañino, te lo dice y propone alternativas.
- ZOE entiende tus emociones: distingue ansiedad de tristeza, motivación de presión.
- ZOE se expresa en tu idioma con el tono correcto.

**Ejemplo real:**

```
Tu: Hola ZOE
ZOE: Hola. Estoy aqui.

Tu: Estoy un poco estresado por el trabajo
ZOE: Escucho que estas estresado por el trabajo. Tiene sentido que
     el trabajo genere presion. Quieres que hablemos de que te tiene
     asi, o prefieres pensar en algo distinto para desconectar?
```

Esta respuesta usa:
- `zoe_basal_knowledge`: tono directo, sin "como IA".
- `communication_skills`: reflejo ("Escucho que estás estresado"), validación ("Tiene sentido"), pregunta abierta.
- `basic_psychology`: comprensión de estrés como emoción.

### Cómo ver las cápsulas base cargadas

**Desde el Dashboard:**
1. Abre el Dashboard (`http://localhost:8642/?token=...`).
2. Panel derecho → sección "Cápsulas cargadas" → clic en **Gestionar**.
3. Verás las 5 cápsulas base marcadas como "Cargada" + cualquier otra que hayas añadido.

**Desde la Terminal:**
```bash
zoe-chat --backend mock
> /capsulas
Capsula 'zoe_basal_knowledge' cargada: 32 entries.
Capsula 'communication_skills' cargada: 37 entries.
Capsula 'base_ethics' cargada: 34 entries.
Capsula 'basic_psychology' cargada: 49 entries.
Capsula 'language_patterns' cargada: 10 entries.
```

### Cómo añadir más cápsulas

Las 5 base son el mínimo vital. Puedes añadir más según tu caso de uso:

- Cuidas a un mayor → carga `elder_care_knowledge` (54 entradas) + `pharmacy_interactions`.
- Estudias investigación → carga `research_methodology`.
- Gestionas servidores → carga `vigilance_devops_knowledge`.

Ver sección 15 (Cápsulas de conocimiento) para la lista completa de 15 especialidades.

---

## 13. El tutor de ZOE (MentorAgent) {#13-tutor}

ZOE tiene un **tutor interno** llamado `MentorAgent` que la guía en su crecimiento. No es un controlador ni un limitador: es un guía que le ayuda a desarrollarse de forma saludable.

### Qué hace el tutor

El tutor evalúa **cada pensamiento autónomo de ZOE** (los que genera durante SLEEPING o en momentos de calma) y comprueba:

1. **Alineación con áreas de crecimiento** — ¿El pensamiento desarrolla alguna de las áreas priorizadas (comunicación, empatía, pensamiento crítico, autoconciencia)?
2. **Respeto a valores enfatizados** — ¿Está alineado con los valores clave (verdad sobre confort, crecimiento sobre estabilidad, integridad)?
3. **Temas prohibidos** — ¿Toca algún tema que el usuario ha marcado como off-limits?
4. **Patrones repetitivos o desviaciones** — ¿ZOE está atrapada en un bucle negativo, o se está desviando de su camino?

Si el tutor detecta una desviación, **genera una intervención**: un mensaje que se añade a los pensamientos autónomos y que ZOE tiene en cuenta en su siguiente ciclo cognitivo.

### Está activo por defecto

**No tienes que hacer nada para activarlo.** El tutor se carga automáticamente al iniciar ZOE, con esta configuración inicial:

| Configuración | Default |
|---------------|---------|
| Nombre del tutor | Mentor |
| Rol | guide (guía) |
| Áreas de crecimiento | communication, empathy, critical_thinking, self_awareness |
| Valores enfatizados | verdad_sobre_confort, crecimiento_sobre_estabilidad, integridad |
| Personalidad deseada | balanced (equilibrada) |
| Frecuencia de intervención | cada 5 pensamientos autónomos |
| Umbral de desviación | 0.5 (medio) |
| Temas prohibidos | (ninguno por defecto) |
| Activado | Sí |

### Cómo ver las intervenciones del tutor

**Desde el Dashboard:**
1. Panel derecho → sección "Pensamientos Autónomos".
2. Verás los pensamientos de ZOE mezclados con las intervenciones del tutor.
3. Las intervenciones del tutor aparecen como:
   ```
   [Mentor] ZOE, este pensamiento se aleja de tus áreas de crecimiento
   priorizadas. Considera redirigir.
   ```
4. Cada intervención indica el tipo (off_track, too_negative, too_repetitive, good_growth, forbidden_topic) y severidad (low, medium, critical).

**Desde la API REST:**
```bash
# Ver configuración del tutor
curl -H "Authorization: Bearer TU_TOKEN" http://localhost:8642/api/mentor

# Ver estadísticas (cuántas evaluaciones, intervenciones, refuerzos)
curl -H "Authorization: Bearer TU_TOKEN" http://localhost:8642/api/mentor/stats
```

### Cómo configurar el tutor

Puedes personalizar el tutor para que guíe a ZOE según tus preferencias.

**Desde el Dashboard:**
- (Próximamente: modal de configuración del tutor en el panel derecho).

**Desde la API REST:**
```bash
# Cambiar áreas de crecimiento (priorizar creatividad y ciencia)
curl -X POST -H "Authorization: Bearer TU_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"growth_areas": ["creativity", "scientific", "critical_thinking"],
          "personality_direction": "creative",
          "forbidden_topics": ["armas", "drogas"]}' \
     http://localhost:8642/api/mentor
```

**Editando el archivo directamente:**
Edita `data/mentor_config.json` en tu SSD:
```json
{
  "mentor_name": "MiTutor",
  "mentor_role": "coach",
  "growth_areas": ["communication", "empathy", "creativity"],
  "emphasized_values": ["verdad_sobre_confort", "crecimiento_sobre_estabilidad"],
  "personality_direction": "curious",
  "intervention_frequency": 3,
  "forbidden_topics": [],
  "enabled": true
}
```
Reinicia ZOE para que cargue la nueva configuración.

### Ejemplo real de intervención

```
[Pensamiento autónomo de ZOE, 03:42 AM]
Trigger: contraccion
Surprise: 0.78
"El usuario muestra un patron de ansiedad previo a reuniones
profesionales criticas. Podria beneficiarse de tecnicas de
preparacion mental. Recomendar mindfulness 10 min antes
de reuniones importantes."

[Intervención del Tutor, 03:42 AM]
Tipo: good_growth
Severidad: low
"ZOE, buen progreso en tu area de crecimiento 'empathy'.
Has identificado un patron emocional del usuario y propuesto
una solucion concreta. Continua."
```

### Tipos de intervención del tutor

| Tipo | Severidad | Cuándo ocurre | Ejemplo |
|------|-----------|---------------|---------|
| `forbidden_topic` | critical | ZOE toca un tema prohibido | "ZOE, el tema 'X' está fuera de los límites. Cambia de dirección." |
| `off_track` | medium | ZOE se aleja de las áreas de crecimiento | "ZOE, este pensamiento no está alineado con tus áreas priorizadas." |
| `too_negative` | medium | ZOE acumula pensamientos negativos | "ZOE, estás acumulando negatividad. Busca equilibrio." |
| `too_repetitive` | low | ZOE repite el mismo patrón | "ZOE, estás repitiendo patrones. Explora algo nuevo." |
| `good_growth` | low (positivo) | ZOE hace un buen progreso | "ZOE, buen progreso. Continúa." |

### Qué NO hace el tutor

- **No controla a ZOE**: no puede detener sus pensamientos ni borrarlos.
- **No censura**: solo añade mensajes de guía que ZOE decide si seguir.
- **No reemplaza al usuario**: tú sigues siendo la autoridad última sobre ZOE.
- **No es permanente**: puedes desactivarlo con `{"enabled": false}` en `/api/mentor`.

---

## 14. Deteccion automatica de idioma {#14-idioma}

ZOE detecta el idioma en el que le hablas **automáticamente** desde el primer mensaje. No tienes que configurar nada.

### Idiomas soportados

| Idioma | Código | Stopwords clave |
|--------|--------|-----------------|
| Español | `es` | hola, que, de, la, el, y, en, un, una, gracias |
| Inglés | `en` | hello, the, and, of, to, in, is, it, you, thank |
| Francés | `fr` | bonjour, le, la, et, de, les, des, un, une, merci |
| Alemán | `de` | hallo, der, die, das, und, von, zu, mit, ist, danke |

### Cómo funciona

ZOE usa **heurística de stopwords**: cuenta cuántas palabras frecuentes de cada idioma aparecen en tu mensaje. El idioma con más coincidencias gana. Si hay empate o poca confianza, por defecto usa español.

**Ventajas:**
- **Sin LLM**: la detección es local, <10ms, sin consumo de tokens.
- **Sin internet**: funciona 100% offline.
- **Sin configuración**: no tienes que decirle a ZOE en qué idioma hablar.

### Qué pasa cuando cambias de idioma

ZOE detecta el idioma en el primer mensaje y lo **cachea por sesión**. Si a mitad de conversación cambias de idioma, ZOE se adapta en el siguiente turno.

**Ejemplo:**

```
Tu (mensaje 1): Hola ZOE, ¿cómo estás?
ZOE: Hola. Estoy aquí, pensando. ¿Y tú?
[ZOE detecta español, cachea 'es']

Tu (mensaje 2): Actually, let's switch to English. Can you help me?
ZOE: Of course. I'm here. What do you need help with?
[ZOE detecta inglés en este mensaje, actualiza caché a 'en']

Tu (mensaje 3): Gracias, vuelvo al español.
ZOE: De acuerdo. Estoy aquí. ¿En qué puedo ayudarte?
[ZOE detecta español, actualiza caché a 'es']
```

### Qué cambia según el idioma

Cuando ZOE detecta un idioma, carga un **profile de idioma** que incluye:

- **System prompt base** — Las instrucciones internas que ZOE recibe se adaptan al idioma. Por ejemplo, en español le dice "Eres ZOE, un organismo cognitivo sintético..."; en inglés le dice "You are ZOE, a synthetic cognitive organism...".
- **Reflex map** — Respuestas rápidas para saludos y despedidas en el idioma correcto.
- **Validator keywords** — Palabras clave médicas/éticas en el idioma (para validar respuestas).
- **Ethical disclaimer** — El descargo de responsabilidad ("consulta a tu médico" / "consult your doctor" / "consultez votre médecin" / "consulte Ihren Arzt").
- **Cultural notes** — Notas culturales por idioma (ej: "En España, mayores prefieren trato de tú" vs "In English-speaking cultures, brevity is valued").

### Cómo verificar qué idioma detectó ZOE

**Desde la Terminal:**
```bash
zoe-chat --backend ollama --model auto
> Hola, ¿cómo estás?
[En los logs verás: "LanguageDetector: detected es (confidence: 0.85)"]
```

**Desde la API REST:**
```bash
# Stats del LanguageDetector
curl -H "Authorization: Bearer TU_TOKEN" http://localhost:8642/stats | jq '.language_detector'
```

### Limitaciones

- **Solo 4 idiomas** por ahora. Si le hablas en italiano, portugués, chino o árabe, ZOE usará el LLM (que sí sabe esos idiomas) pero con el system prompt en español por defecto.
- **Heurística simple**: si escribes mensajes muy cortos (1-2 palabras) sin stopwords claras, puede fallar. En ese caso, default es español.
- **No detecta dialectos**: no distingue español de España vs México, ni inglés americano vs británico.

### Próximas mejoras (roadmap)

- Añadir italiano, portugués, chino, japonés, árabe.
- Detección de dialecto (es-ES vs es-MX).
- Cambio de idioma mid-conversación más fluido (sin necesidad de re-cache).

---

## 15. Capsulas de conocimiento (15 especialidades) {#15-capsulas}

ZOE viene con **15 cápsulas** preinstaladas. Las 5 base (sección 12) se cargan siempre; las 10 de especialidad son opt-in según tu caso de uso.

### Cápsulas base (cargadas SIEMPRE, ver sección 12)

| Cápsula | Contenido | Entradas |
|---------|-----------|----------|
| `zoe_basal_knowledge` | Identidad, valores, propósito, tono | 32 |
| `communication_skills` | Comunicación empática (NVC, Rogers, Rollnick) | 37 |
| `base_ethics` | Ética operacional (Asilomar, IEEE, EU) | 34 |
| `basic_psychology` | Psicología básica (APA, DSM-5) | 49 |
| `language_patterns` | Patrones de lenguaje por idioma | 10 |

### Cápsulas de especialidad (opt-in)

| Cápsula | Contenido | Entradas | Caso de uso típico |
|---------|-----------|----------|---------------------|
| `elder_care_knowledge` | Cuidado de mayores | 54 | Cuidar a un familiar mayor |
| `elder_care_skills` | Habilidades de cuidado (rutina, tracking) | 10+ | Acompañamiento diario a mayores |
| `pharmacy_interactions` | Interacciones farmacéuticas | 20+ | Verificar medicación |
| `research_methodology` | Metodología científica | 25+ | Investigación, estudios |
| `multimodal_perception` | Percepción multimodal (visión, voz) | 15+ | Análisis de imágenes, audio |
| `b2c_assistant_growth` | Asistente B2C que crece con el usuario | 20+ | Asistente personal evolutivo |
| `company_loneliness_knowledge` | Conocimiento sobre soledad | 22+ | Acompañamiento a personas solas |
| `federation_b2b_skills` | Habilidades de federación B2B | 18+ | Federación entre organizaciones |
| `vigilance_devops_knowledge` | Conocimiento DevOps/Vigilancia | 30+ | Gestión de servidores, monitorización |
| `ia_heredable_legal` | Legal IA heredable | 14+ | Herencia de IA entre generaciones |

### Cargar/descargar capsulas

**Desde el Dashboard:**
1. Clic en "Gestionar" en la seccion Capsulas (panel derecho).
2. Veras la lista de 15 capsulas.
3. Clic en "Cargar" junto a la capsula que quieras.
4. La capsula se inyecta en la memoria de ZOE en caliente (no necesita reinicio).
5. Para descargar, clic en "Descargar".

**Desde CLI:**
```bash
zoe-chat --backend ollama --model auto
> /capsule elder_care_knowledge
Capsula 'elder_care_knowledge' cargada: 54 entradas inyectadas.
Componentes: data, skills, validators, tools.
```

### Crear capsulas personalizadas

Puedes crear tus propias capsulas con conocimiento especializado:

1. Clic en "Crear nueva" en el modal de Capsulas.
2. Rellena:
   - **Nombre** — Sin espacios, en snake_case (ej: `mi_empresa_guias`).
   - **Descripcion** — Que contiene.
   - **Tipo de licencia** — Free, Open Source, Research, Paid.
   - **Contenido** — YAML con datos, skills, validators.
3. Clic en "Crear".
4. La capsula aparece en tu lista y puedes cargarla como las demas.

### Marketplace de capsulas

ZOE tiene un marketplace donde puedes:
- **Publicar** tus capsulas (gratis o de pago).
- **Descargar** capsulas de otros usuarios.
- **Compartir** casos de uso (YAML preconfigurados).

> **Revenue split:** 70% para el creador, 30% para mantener la infraestructura.

---

## 16. ACD — Sistema de niveles cognitivos {#16-acd}

ACD (Adaptive Cognitive Depth) clasifica cada pregunta y elige el modelo optimo:

| Nivel | Input tipico | Modelo (8GB) | Modelo (16GB) | Tamano | Velocidad |
|-------|-------------|--------------|---------------|--------|-----------|
| **L0_REFLEX** | "Hola", "Gracias" | PatternSpeaker | PatternSpeaker | 0 GB | <1ms |
| **L1_FAST** | "Que hora es?" | Gemma 2 9B IQ2_M | Gemma 2 9B IQ2_M | 3.5 GB | 15-25 t/s |
| **L2_STANDARD** | "Resume este articulo" | Agents-A1 MoE IQ2_M | Agents-A1 MoE IQ2_M | 11.7 GB | 5-10 t/s |
| **L3_DEEP** | "Analiza causas profundas" | QwQ-32B IQ2_M | QwQ-32B IQ2_M | 12.5 GB | 3-6 t/s |
| **L3_MAXIMUM** | "Compara 3 contratos" | Qwen 2.5 72B IQ2_M | Qwen 2.5 72B IQ2_M | 25 GB | 1-3 t/s |
| **L4_REFLECTION** | Reflexion SLEEPING | **DeepSeek-R1:32B IQ2_M** | **DeepSeek-R1:32B Q4_K_M** | 12.5-18 GB | 2-4 t/s |

### 5 senales de deteccion

El DepthClassifier analiza cada pregunta usando 5 senales:

1. **Longitud** — Cuantos caracteres/palabras. Corto = L0/L1. Largo = L2/L3.
2. **Keywords** — Palabras clave. "Hola" = L0. "Analiza" = L3.
3. **Puntuacion** — Signos de puntuacion. Pregunta simple = L1. Multi-clausula = L3.
4. **Estructura** — Sintaxis. Imperativo = L1. Condicional compuesto = L3.
5. **Contexto** — Historial. Conversacion continuada = sube 1 nivel.

**Deteccion automatica:** No requiere configuracion manual. ZOE detecta tu RAM al iniciar y selecciona el modelo L4 adecuado.

### Como ver que nivel uso ZOE para tu pregunta

**En el Dashboard:**
- Junto a cada respuesta de ZOE, aparece una etiqueta de color:
  - `L0` (rojo) — Reflejo
  - `L1` (amarillo) — Rapido
  - `L2` (verde) — Estandar
  - `L3` (azul) — Profundo
  - `L3 MAX` (morado) — Maximo
- Tambien muestra latencia en ms y si fue cache hit.

**Ejemplo:**
```
Tu: Hola ZOE
ZOE: Hola. Estoy aqui.  [L0] 12ms

Tu: Resume este articulo sobre fisica cuantica
ZOE: El articulo describe...  [L2] 4231ms

Tu: Compara las interpretaciones de Copenhague y Many-Worlds
ZOE: Desde una perspectiva...  [L3 MAX] 28450ms
```

### Forzar un nivel especifico

Si quieres que ZOE use un nivel concreto:

```bash
zoe-chat --backend ollama --model qwq-32b-iq2  # Fuerza L3_DEEP
zoe-chat --backend ollama --model gemma-2-9b-iq2  # Fuerza L1_FAST
```

---

## 17. Casos de uso practico (10 ejemplos reales) {#17-casos-de-uso}

### Caso 1: Asistente de estudio personal

**Escenario:** Maria estudia oposiciones y quiere que ZOE le ayude a repasar.

1. Inicia ZOE: `INICIAR-DASHBOARD.command`.
2. Carga la capsula `language_learning` (si estudia idiomas) o crea una con el temario.
3. Pregunta: "Explicame el concepto de amparo constitucional con ejemplos".
4. ZOE responde (L3_DEEP, 5-10s) con explicacion + 3 ejemplos.
5. Pregunta: "Hazme 5 preguntas tipo test sobre esto".
6. ZOE genera 5 preguntas.
7. Responde. ZOE corrige y explica errores.
8. **Manana:** ZOE recuerda que fallaste en 2 preguntas y te las repasa.

### Caso 2: Cuidador de mayor dependiente

**Escenario:** Juan cuida a su madre de 85 anos con Parkinson.

1. Carga la capsula `elder_care_knowledge` (54 entradas sobre cuidado de mayores).
2. Pregunta: "Mi madre tiene temblor mas fuerte por las mananas. Es normal?"
3. ZOE responde (con conocimiento medico): "El temblor Parkinsoniano suele empeorar..."
4. Pregunta: "Que ejercicios de movilidad le puedo hacer practicar?"
5. ZOE sugiere 5 ejercicios especificos.
6. Carga `pharmacy_interactions` para verificar medicamentos.
7. Pregunta: "Toma levodopa y aspirina. Hay interaccion?"
8. ZOE responde con conocimiento farmaceutico.
9. **Durante la noche:** ZOE reflexiona (L4_REFLECTION) y genera un insight:
   "Juan pregunta frecuentemente sobre temblores matutinos. Podria
    beneficiarse de un registro diario de sintomas para compartir
    con el neurologo."

### Caso 3: Programador que quiere un pair programmer

**Escenario:** Ana programa en Python y quiere que ZOE le ayude.

1. Inicia ZOE en Terminal: `INICIAR-ZOE.command`.
2. Pregunta: "Como optimizo esta funcion? [pega codigo]".
3. ZOE responde (L3_DEEP) con 3 alternativas + analisis de complejidad.
4. Pregunta: "Por que la opcion B es mejor en este caso?"
5. ZOE explica con contexto.
6. **Siguiente dia:** Pregunta "Recuerdas la funcion que optimizamos ayer?"
7. ZOE: "Si. Era `process_data(df)` que hicimos O(n log n) usando pandas vectorizado en vez de un loop. Quieres verla?"

### Caso 4: Escritor creativo

**Escenario:** Carlos escribe una novela y quiere brainstorming.

1. Inicia ZOE Dashboard.
2. Pregunta: "Tengo un personaje que es un detective en Madrid en 1940. Dame 5 giros argumentales".
3. ZOE responde (L3_DEEP) con 5 ideas originales.
4. Pregunta: "Desarrolla la idea 3. Como conocio a su esposa?"
5. ZOE crea un backstory.
6. Sube un capitulo PDF y pregunta: "El tono es coherente con el resto?"
7. ZOE analiza y sugiere ajustes.
8. **Manana:** ZOE tiene un insight: "Carlos describe Madrid con detalle
   sensorial pero los dialogos son poco naturales. Recomendacion:
   leer dialogos de Miguel Delibes para inspiracion."

### Caso 5: Investigador que procesa papers

**Escenario:** Elena investiga cancer y lee 5 papers/semana.

1. Inicia ZOE Dashboard.
2. Sube un paper PDF.
3. Pregunta: "Resume los hallazgos clave en 3 bullet points".
4. ZOE resume (L2_STANDARD, 3-5s).
5. Pregunta: "Compara la metodologia de este paper con el de Smith 2023 [sube el otro]".
6. ZOE compara (L3_MAXIMUM, 10-30s).
7. Pregunta: "Que inconsistencias ves entre ambos?"
8. ZOE identifica 3 inconsistencias.
9. **Noche:** ZOE reflexiona y genera insight:
   "Elena ha subido 12 papers en 3 semanas. Patron emergente:
    los papers de Nature usan metodologias mas rigurosas que
    los de journals menores. Recomendacion: priorizar Nature/Cell."

### Caso 6: Medico que valida conocimiento

**Escenario:** Dr. Lopez quiere usar ZOE como segundo opinion.

1. Carga `medical_protocols` y `pharmacy_interactions`.
2. Pregunta: "Paciente con HTA y diabetes tipo 2. Cual es el protocolo?"
3. ZOE responde con protocolo estandar.
4. Pregunta: "Si adicionalmente tiene ERC estadio 3?"
5. ZOE ajusta recomendaciones.
6. Pregunta: "Que farmacos estan contraindicados?"
7. ZOE lista farmacos con nivel de evidencia.
8. **Importante:** ZOE marca conocimiento nuevo como "en cuarentena" hasta validarlo con 14+ fuentes. Verifica siempre con fuentes oficiales.

### Caso 7: Estudiante que hace marathon de estudio

**Escenario:** Pedro prepara examen en 7 dias.

1. Carga `tech_tutorials` (si es informatica) o crea capsula con temario.
2. Pregunta: "Plan de estudio de 7 dias para Tema 5: Calculo integral".
3. ZOE crea plan dia a dia.
4. Cada dia, pregunta: "Ensename un concepto y hazme 3 preguntas".
5. ZOE ensena y evalua.
6. Pedro responde. ZOE identifica puntos debiles.
7. **Dia 7:** ZOE sabe que Pedro falla en "integracion por partes" y genera repaso especifico.

### Caso 8: Emprendedor que analiza mercado

**Escenario:** Lucia quiere lanzar una app de mascotas.

1. Inicia ZOE.
2. Sube 3 PDFs: estudio de mercado, competidores, encuesta.
3. Pregunta: "Cual es el TAM/SAM/SOM basandome en estos datos?"
4. ZOE calcula con metodologia.
5. Pregunta: "Cuales son mis 3 ventajas competitivas mas fuertes?"
6. ZOE identifica.
7. Pregunta: "Escribe un executive summary de 1 pagina para inversores".
8. ZOE redacta.
9. **Noche:** ZOE reflexiona:
   "Lucia tiene 3 competidores principales pero ninguno se enfoca
    en mascotas senior (8+ anos). Nicho desatendido. Recomendacion:
    pivotar valor propuesta a 'cuidado de mascotas senior'."

### Caso 9: Terapeuta que lleva registro

**Escenario:** Dra. Garcia usa ZOE para reflexionar sobre sesiones.

1. Despues de cada sesion, escribe en ZOE:
   "Hoy con paciente X hablamos de su relacion con su padre.
    Se emociono al recordar infancia. Avance pequeno pero significativo."
2. ZOE guarda en memoria episodica.
3. Semanalmente, pregunta: "Que patrones has observado en el paciente X?"
4. ZOE responde con conocimiento acumulado.
5. **Noche:** ZOE reflexiona:
   "Paciente X muestra resistencia al hablar de su padre. Posible
    mecanismo de defensa. Sugerir a la Dra. Garcia explorar
    tecnicas de EMDR si el patron persiste."

### Caso 10: Familia que comparte un ZOE

**Escenario:** Familia de 4 comparte un ZOE en SSD conectado al Mac del salon.

1. Cada miembro tiene su propia API key de OpenAI (presupuesto separado).
2. Cambian el backend segun quien usa.
3. Padre (abogado): Carga `legal_assistance`, pregunta sobre casos.
4. Madre (nutricionista): Carga `nutrition_guide`, prepara menus.
5. Hijo (estudiante): Carga `language_learning`, practica ingles.
6. Hija (artist): Carga capsulas vacia, pide ideas de dibujo.
7. **ZOE recuerda a cada uno**: "Juan, tu entrevista del lunes fue bien? Maria, probaste la receta de lentejas? Carlos, como va el examen?"

> **Importante:** Si quieres ZOEs separados para cada miembro, instala ZOE en SSDs distintos. Cada uno sera un organismo distinto con su propia identidad.

---

## 18. Configuracion avanzada {#18-configuracion}

### Variables de entorno

Edita `data/.env` en tu SSD:

| Variable | Descripcion | Default |
|----------|-------------|---------|
| `ZOE_HOME` | Directorio raiz de ZOE | (auto) |
| `ZOE_DATA` | Directorio de datos | `./data` |
| `ZOE_STORAGE_TYPE` | `sqlite` o `postgres` | `sqlite` |
| `POSTGRES_HOST` | Host PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Puerto PostgreSQL | `5432` |
| `POSTGRES_DB` | Nombre BD PostgreSQL | `zoe` |
| `POSTGRES_USER` | Usuario PostgreSQL | `zoe` |
| `POSTGRES_PASSWORD` | Password PostgreSQL | (none) |
| `OPENAI_API_KEY` | API key de OpenAI | — |
| `ANTHROPIC_API_KEY` | API key de Anthropic | — |
| `DEEPSEEK_API_KEY` | API key de DeepSeek | — |
| `ZAI_API_KEY` | API key de Z.AI | — |
| `ZOE_CLOUD_BUDGET` | Presupuesto diario cloud ($) | `1.0` |
| `OLLAMA_MODELS` | Directorio modelos Ollama | (auto SSD) |
| `ZOE_DASHBOARD_PORT` | Puerto del dashboard | `8642` |

### Configuracion del ReflectionEngine

Edita `zoe/core/reflection_engine.py` o crea `data/reflection_config.yaml`:

```yaml
model_tag: "deepseek-r1:32b-iq2"        # Modelo para reflexion (8GB)
model_tag_16gb: "deepseek-r1:32b-q4km"  # Modelo para 16GB+
model_fallback_tag: "qwq-32b-iq2"       # Fallback si no cabe
daily_cloud_budget: 2.0                  # Presupuesto diario ($)
max_reflections_per_cycle: 3             # Maximo por ciclo de sueno
salience_threshold: 0.5                  # Umbral de saliencia
reflection_timeout: 180.0                # Timeout (segundos)
max_fatigue_for_reflection: 0.8          # Max fatiga para reflexionar
```

### Configuracion del ACD

Edita `zoe/core/depth_classifier.py` o crea `data/acd_config.yaml`:

```yaml
l0_max_length: 30          # L0 si menos de 30 chars y keyword trivial
l1_max_length: 200         # L1 si menos de 200 chars
l2_max_length: 1000        # L2 si menos de 1000 chars
l3_keywords:               # Palabras que fuerzan L3
  - "analiza"
  - "compara"
  - "evalua"
  - "por que"
  - "causas profundas"
l3_max_keywords:
  - "maxima calidad"
  - "compara 3 o mas"
  - "analisis exhaustivo"
```

### Cambiar backend en caliente

**Desde el Dashboard:**
- Clic en el selector de LLM (barra superior).
- Elige: mock, ollama, zai, openai, anthropic.
- Clic en "Switch".

**Desde CLI:**
```bash
> /switch openai gpt-4o
> /switch ollama auto
> /switch pattern
```

### Cambiar puerto del dashboard

```bash
ZOE_DASHBOARD_PORT=9000 ./INICIAR-DASHBOARD.command
```

O edita `data/.env`:
```
ZOE_DASHBOARD_PORT=9000
```

### Habilitar HTTPS

Para uso en red local con HTTPS:

```bash
openssl req -x509 -newkey rsa:4096 -keyout data/key.pem -out data/cert.pem -days 365 -nodes
# Edita zoe/dashboard/server.py: ssl_context=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ssl_context.load_cert_chain('data/cert.pem', 'data/key.pem')
```

### Backup automatico

Edita `data/.env`:
```
ZOE_BACKUP_ENABLED=true
ZOE_BACKUP_DIR=/Volumes/CrucialX9/ZOE/backups
ZOE_BACKUP_FREQUENCY=daily  # hourly, daily, weekly
ZOE_BACKUP_KEEP=7           # keep last 7
```

O ejecuta manualmente:
```bash
bash zoe/scripts/backup.sh
```

---

## 19. Solucion de problemas (FAQ ampliada) {#19-faq}

### Problemas de instalacion

#### "No se detecta el SSD"

- **Causa:** Cable incorrecto, SSD no formateado, o puerto USB-C defectuoso.
- **Solucion 1:** Usa el **cable CORTO** USB-C que venia con el SSD. El cable largo de carga del Mac es USB 2.0 y va 10x mas lento.
- **Solucion 2:** Prueba otro puerto USB-C del Mac.
- **Solucion 3:** Conecta el SSD, abre **Utilidad de Discos** (Cmd+Espacio, "Utilidad de Discos"). Si aparece, seleccionalo > Borrar > Formato: exFAT o APFS.
- **Solucion 4:** Si el SSD es nuevo y no aparece, puede que necesite inicializarse. En Utilidad de Discos, seleccionalo > Borrar.

#### "Python 3.10+ no encontrado"

- **Causa:** Mac viene con Python 3.9 por defecto.
- **Solucion:** Instala Python 3.11+ desde https://python.org/downloads/mac-osx/. Al instalar, marca "Add Python to PATH".
- **Alternativa:** `brew install python@3.11`.

#### "Git no encontrado"

- **Causa:** Git no esta instalado por defecto en macOS.
- **Solucion:** Ejecuta en Terminal: `xcode-select --install`. Aparecera una ventana del sistema. Espera a que termine (5-10 min). Vuelve a ejecutar el instalador de ZOE.

#### "La instalacion falla al descargar modelos"

- **Causa 1:** Sin conexion a internet.
- **Causa 2:** HuggingFace caido (raro).
- **Causa 3:** Espacio insuficiente en SSD.
- **Solucion:** Verifica espacio libre: `df -h /Volumes/CrucialX9/`. Necesitas 50+ GB libres. Si no, borra archivos o usa setup mas pequeno.

### Problemas de uso

#### "ZOE va muy lenta"

- **Causa:** Modelo muy grande para tu RAM.
- **Solucion 1:** Cambia a un modelo mas ligero. En el Dashboard → Configuracion → Modelos locales → Seleccionar mas ligero.
- **Solucion 2:** Cierra otras aplicaciones (Chrome con muchas pestanas come RAM).
- **Solucion 3:** Reinicia el Mac antes de usar ZOE (libera swap).
- **Solucion 4:** Si tienes 8GB RAM, no uses Qwen 2.5 72B (25GB). Usa QwQ-32B (12.5GB) como maximo.

#### "ZOE no responde en SLEEPING"

- **Causa:** Es normal. ZOE esta consolidando memoria y reflexionando.
- **Solucion 1:** Espera 3-8 minutos. Apareceran nuevos pensamientos en el panel derecho.
- **Solucion 2:** Clic en "Wake" en el Dashboard para despertarla.
- **Solucion 3:** En CLI, escribe `/despertar`.

#### "Error de RAM"

- **Causa:** Modelo demasiado grande para tu RAM.
- **Solucion:** Cierra aplicaciones. Usa modelos mas pequenos. Aumenta swap en macOS:
  ```bash
  sudo nvram boot-args="vm_compressor=4"
  # Reinicia el Mac
  ```

#### "El Dashboard pide token"

- **Causa:** Es normal. ZOE protege el dashboard con un token de autenticacion.
- **Solucion 1:** Copia la URL completa con `?token=XXX` de la Terminal donde iniciaste ZOE.
- **Solucion 2:** Si perdiste el token, abre `data/dashboard_token.txt` en tu SSD. Copia el contenido y pegalo en el modal.
- **Solucion 3:** Si quieres desactivar auth (NO recomendado), inicia con `--auth-token ""`.

#### "No veo el indicador de 'pensando'"

- **Causa:** Estas en una version antigua del HTML o hay cache del navegador.
- **Solucion 1:** Pulsa `Cmd+Shift+R` (recargar sin cache).
- **Solucion 2:** Limpia cache: Safari > Desarrollar > Vaciar cache.
- **Solucion 3:** Reinicia el dashboard.

#### "Presupuesto cloud agotado"

- **Causa:** Se alcanzo el limite diario ($1.00 por defecto).
- **Solucion 1:** Espera 24h para reset automatico.
- **Solucion 2:** Aumenta `ZOE_CLOUD_BUDGET=2.0` en `data/.env`. Reinicia ZOE.
- **Solucion 3:** Usa modelos locales (Ollama) en vez de cloud.

#### "DeepSeek Q4_K_M no cabe"

- **Causa:** RAM insuficiente (8 GB en vez de 16 GB).
- **Solucion:** Usa la version IQ2_M (12.5 GB) en vez de Q4_K_M (18 GB).
  ```bash
  # En data/reflection_config.yaml
  model_tag: "deepseek-r1:32b-iq2"  # en vez de q4km
  ```

#### "Como cambio de IQ2_M a Q4_K_M si actualizo mi RAM?"

```bash
# Reinstalar modelos con setup reflexion pro (16GB)
python -m zoe.core.model_downloader --download-setup reflection-16gb --models-dir /Volumes/CrucialX9/ZOE/models/ollama
```

#### "No compila en Windows"

- **Solucion:** Usa WSL2 (Windows Subsystem for Linux):
  ```powershell
  wsl --install -d Ubuntu-22.04
  # Reinicia, abre Ubuntu, sigue las instrucciones de Linux
  ```

### Problemas de Dashboard

#### "El Dashboard no se abre en el navegador"

- **Solucion 1:** Abre Safari/Chrome manualmente y pega: `http://localhost:8642/?token=TU_TOKEN`.
- **Solucion 2:** Verifica que el servidor este corriendo en la Terminal (deberias ver "Dashboard server started").
- **Solucion 3:** Verifica el puerto: `lsof -i :8642`. Si esta ocupado, usa otro: `ZOE_DASHBOARD_PORT=9000 ./INICIAR-DASHBOARD.command`.

#### "401 Unauthorized en el Dashboard"

- **Causa:** El token en la URL no coincide con el del servidor.
- **Solucion 1:** Reinicia el dashboard. Copia la URL completa con `?token=...` de la Terminal.
- **Solucion 2:** Si persiste, borra localStorage del navegador: Safari > Desarrollar > Vaciar cache. Recarga.

#### "El chat del Dashboard no actualiza"

- **Causa:** WebSocket desconectado.
- **Solucion 1:** Recarga la pagina (Cmd+R).
- **Solucion 2:** Verifica tu conexion a internet (no necesaria para offline, pero el WebSocket si requiere localhost).
- **Solucion 3:** Abre DevTools (Cmd+Option+I) > Console. Busca errores de WebSocket.

### Problemas de memoria

#### "ZOE no recuerda lo que hablamos"

- **Causa 1:** Estas usando backend `mock` o `pattern` (sin memoria persistente). Cambia a `ollama` o `openai_compatible`.
- **Causa 2:** `data/zoe_memory.db` se borro. Verifica permisos de escritura en el SSD.
- **Causa 3:** Estas usando `--db-path` apuntando a otra ubicacion. Verifica que `data/.env` tenga `ZOE_DATA` correcto.

#### "Memoria corrupta"

- **Sintoma:** Error "database disk image is malformed".
- **Solucion:**
  ```bash
  cd /Volumes/CrucialX9/ZOE/data
  cp zoe_memory.db zoe_memory.db.bak
  sqlite3 zoe_memory.db ".recover" > recovered.sql
  sqlite3 new_memory.db < recovered.sql
  mv new_memory.db zoe_memory.db
  ```

### Problemas de Ollama

#### "Ollama no responde"

- **Solucion 1:** Inicia Ollama manualmente: `ollama serve &`.
- **Solucion 2:** Verifica que esta corriendo: `curl http://localhost:11434/api/tags`. Deberia devolver JSON.
- **Solucion 3:** Reinicia el Mac.

#### "Modelos no aparecen en Ollama"

- **Causa:** Variable `OLLAMA_MODELS` no apunta al SSD.
- **Solucion:**
  ```bash
  export OLLAMA_MODELS="/Volumes/CrucialX9/ZOE/models/ollama"
  ollama list
  ```
- Si funciona, anade a `~/.zshrc` o `~/.bashrc`:
  ```bash
  echo 'export OLLAMA_MODELS="/Volumes/CrucialX9/ZOE/models/ollama"' >> ~/.zshrc
  source ~/.zshrc
  ```

---

## 20. Soporte y comunidad {#20-soporte}

### Documentacion

- **Este manual:** `zoe/docs/22_MANUAL_COMPLETO_USUARIO_v2.1.1.md`
- **Guia de usuario rapida:** `zoe/docs/20_ZOE_GUIA_USUARIO.md`
- **Explicacion para no tecnicos:** `zoe/docs/18_ZOE_EXPLICACION_NO_TECNICOS.md`
- **Documentacion tecnica:** `zoe/docs/19_ZOE_TECHNICAL_INTERNALS.md`
- **Arquitectura:** `zoe/docs/02_ARCHITECTURE.md`
- **FAQ adicional:** `zoe/docs/13_TROUBLESHOOTING.md`

### Comunidad

- **GitHub Issues:** https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/issues
- **Discord:** (canal oficial)
- **Email:** (email de soporte)

### Como contribuir

1. Fork el repositorio en GitHub.
2. Crea una rama: `git checkout -b mi-mejora`.
3. Haz tus cambios.
4. Ejecuta tests: `pytest zoe/tests/ -q`.
5. Crea un Pull Request describiendo el cambio.

### Roadmap

- **v2.0.0 GA** — Production Ready final (Q3 2026).
- **Pasarela de pagos** — Stripe/PayPal para marketplace.
- **Chaos engineering avanzado** — Load testing, fuzzing, penetracion profesional.
- **Apps moviles nativas** — iOS / Android.
- **Integracion con Telegram** — Bot de Telegram para ZOE.

---

## 21. Glosario completo A-Z {#21-glosario}

### A

| Termino | Definicion |
|---------|-----------|
| **ACD** | Adaptive Cognitive Depth. Sistema de 5 niveles (L0-L3_MAX + L4_REFLECTION) que clasifica la complejidad de cada pregunta y elige el modelo de IA optimo. Inventado por ZOE. |
| **Active Inference** | Teoria de Karl Friston que ZOE implementa: el cerebro minimiza la "energia libre" prediciendo el futuro y actualizando creencias. |
| **ALMA** | Archivo de Identidad Soberana de ZOE. Contiene 9 vectores de crecimiento + 7 valores + hash SHA-256 inmutable. Es el "DNI digital" de ZOE. |
| **Apple Silicon** | Procesadores M1/M2/M3/M4 de Apple. ZOE esta optimizado para M3 con aceleracion Metal. |
| **Auth Token** | Token de autenticacion (Bearer) que ZOE genera automaticamente para proteger el dashboard. Se guarda en `data/dashboard_token.txt`. |
| **AWAKE** | Estado metabolico de ZOE cuando esta despierta y atenta. |

### B

| Termino | Definicion |
|---------|-----------|
| **Backend LLM** | Motor de procesamiento de lenguaje natural. ZOE soporta 6: Mock, Ollama (local), OpenAI, Anthropic, ZAI, OpenAI-compatible. |
| **Blockchain** | Cadena de bloques inmutables. La Trajectory Chain de ZOE usa un concepto similar para registrar mutaciones de identidad. |
| **BudgetTracker** | Modulo que gestiona el presupuesto diario de cloud ($1 por defecto). Evita gastos inesperados en APIs de pago. |

### C

| Termino | Definicion |
|---------|-----------|
| **Capsula** | Modulo de conocimiento especializado que se carga en ZOE en tiempo de ejecucion. Contiene datos semanticos, habilidades procedimentales, validadores eticos y herramientas. Ejemplo: `elder_care_knowledge` con 54 entradas. |
| **Circuit Breaker** | Patron de resiliencia: si un servicio falla repetidamente, se "abre" el circuito y se usa un fallback. |
| **CI/CD** | Continuous Integration / Continuous Delivery. En ZOE: GitHub Actions ejecuta 1,700+ tests automaticamente en cada commit. |
| **Cognitive Loop** | Bucle principal de ZOE que se ejecuta cada 3 segundos. Coordina 12 sub-agentes, el Global Workspace, y la meta-cognicion. |
| **CORT** | Cognitive Organization for Reasoning and Thought. ZOE es un SCO (Synthetic Cognitive Organism), no un simple chatbot. |
| **Counterfactual** | Tipo de memoria que almacena "que habria pasado si...". |
| **Cuantizacion** | Tecnica que reduce el tamano de un modelo de IA comprimiendo sus pesos. Q4_K_M = 4 bits por peso. IQ2_M = 2 bits. |

### D

| Termino | Definicion |
|---------|-----------|
| **Dashboard** | Interfaz web de ZOE accesible en `http://localhost:8642/?token=XXX`. Muestra chat, estado metabolico, memoria, capsulas, y configuracion. |
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
| **Evolutionary Memory** | Tipo de memoria que registra cambios en el conocimiento de ZOE. |

### F

| Termino | Definicion |
|---------|-----------|
| **Factory Pattern** | Patron de diseno donde una funcion crea objetos segun configuracion. ZOE lo usa para seleccionar entre SQLite y PostgreSQL. |
| **Fallback Chain** | Cadena de respaldo: si un modelo falla, se prueba el siguiente. Ejemplo: deepseek-r1:32b-q4km → iq2 → qwq-32b → qwen2.5-32b. |
| **FEP** | Free Energy Principle. Teoria de Friston que ZOE implementa: minimizar sorpresa prediciendo el futuro. |

### G

| Termino | Definicion |
|---------|-----------|
| **GGUF** | Formato de archivo para modelos cuantizados de Llama.cpp. Los modelos de Ollama usan este formato. |
| **Global Workspace** | Teoria de Bernard Baars que ZOE implementa: un "escenario central" donde sub-agentes compiten por atencion consciente. |
| **Graceful Shutdown** | Apagado controlado: ZOE guarda memoria e identidad antes de cerrar, sin perdida de datos. |

### H

| Termino | Definicion |
|---------|-----------|
| **Health Check** | Endpoints `/health`, `/ready`, `/live` que verifican que ZOE funciona correctamente. Usados por Kubernetes y monitoreo. |
| **Homebrew** | Gestor de paquetes para macOS. El instalador de ZOE lo usa para instalar Python, Git, Ollama. |
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

### P

| Termino | Definicion |
|---------|-----------|
| **PatternSpeaker** | Generador de respuestas offline de ZOE. No usa IA, funciona por patrones predefinidos. <1ms, siempre disponible. |
| **Persistencia** | Capacidad de guardar datos entre sesiones. La memoria de ZOE se guarda en SQLite en el SSD. |
| **PostgreSQL** | Base de datos avanzada opcional para despliegues multi-usuario. Reemplaza a SQLite. |
| **Prometheus** | Sistema de monitoreo. ZOE expone metricas en `/metrics` para integracion con Grafana. |
| **psutil** | Libreria Python para monitorear recursos del sistema (CPU, RAM, disco). ZOE la usa para adaptarse al hardware. |

### Q

| Termino | Definicion |
|---------|-----------|
| **Q4_K_M** | Cuantizacion de 4 bits (moderada). Balance entre calidad y tamano. DeepSeek-R1:32B Q4_K_M = ~18 GB. |
| **QwQ-32B** | Modelo de razonamiento de Qwen (Alibaba). 32B parametros, especializado en razonamiento paso a paso. |
| **Qwen 2.5** | Familia de modelos de Alibaba. ZOE usa versiones de 14B, 32B y 72B parametros. |

### R

| Termino | Definicion |
|---------|-----------|
| **Race Condition** | Error de concurrencia donde dos procesos compiten por el mismo recurso. ZOE evita esto usando asyncio.Lock. |
| **Rate Limiting** | Limite de 60 peticiones/minuto para proteger el dashboard contra abuso. |
| **ReflectionEngine** | Motor de reflexion autonoma v2.1.1 que usa DeepSeek-R1:32B para generar insights durante SLEEPING. |
| **ReflectionHook** | Conector que integra el ReflectionEngine con el metabolismo de ZOE (se activa durante SLEEPING). |

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
| **SSL/TLS** | Protocolo de cifrado para conexiones seguras. El dashboard de ZOE lo usa opcionalmente para proteger comunicaciones. |
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
| **Vector de crecimiento** | Una de las 9 dimensiones que definen la identidad de ZOE. Ejemplo: autonomia, creatividad, empatia. |

### W

| Termino | Definicion |
|---------|-----------|
| **WAL Mode** | Write-Ahead Logging. Modo de SQLite que mejora la concurrencia y previene corrupcion de datos. |
| **WebSocket** | Protocolo de comunicacion en tiempo real bidireccional. El chat del dashboard lo usa para conversacion instantanea. |
| **Waking** | Estado metabolico de transicion entre SLEEPING y AWAKE. ZOE restaura capacidades progresivamente. |

### Z

| Termino | Definicion |
|---------|-----------|
| **ZoePackager** | Herramienta que empaqueta una instancia de ZOE completa en un archivo `.zoe` portatil (identidad + memoria + capsulas). |
| **ZoeRuntime** | Entorno de ejecucion que coordina todos los componentes de ZOE en tiempo real. |
| **.zoe** | Formato de archivo portatil que contiene una instancia completa de ZOE (identidad + memoria + capsulas + configuracion). |

---

## 22. Referencia rapida {#22-referencia}

### Tabla de comandos

| Comando | Descripcion |
|---------|-------------|
| `INICIAR-ZOE.command` | Doble click: chat en terminal |
| `INICIAR-DASHBOARD.command` | Doble click: dashboard web |
| `ZOE-Smart.command` | Doble click: menu completo |
| `zoe-chat --backend ollama --model auto` | Chat con ACD Router |
| `zoe-chat --backend openai --model gpt-4o` | Chat con OpenAI |
| `zoe-dashboard --backend ollama` | Iniciar dashboard |
| `python -m zoe.core.model_downloader --model qwq-32b-iq2` | Descargar modelo |
| `pytest zoe/tests/ -q` | Ejecutar tests |

### Comandos dentro del chat

| Comando | Accion |
|---------|--------|
| `/quit` o `/exit` | Salir |
| `/memoria` | Ver memoria |
| `/estado` | Ver metabolismo |
| `/capsulas` | Listar capsulas |
| `/capsule NOMBRE` | Cargar capsula |
| `/reflexionar` | Forzar reflexion |
| `/dormir` | Forzar SLEEPING |
| `/despertar` | Despertar |
| `/identidad` | Ver hash identidad |
| `/stats` | Ver estadisticas |
| `/ayuda` | Ver todos los comandos |

### Tabla de variables de entorno

| Variable | Ejemplo |
|----------|---------|
| `ZOE_HOME` | `/Volumes/CrucialX9/ZOE` |
| `ZOE_DATA` | `/Volumes/CrucialX9/ZOE/data` |
| `OPENAI_API_KEY` | `sk-abc123...` |
| `ANTHROPIC_API_KEY` | `sk-ant-abc123...` |
| `ZOE_CLOUD_BUDGET` | `2.0` |
| `ZOE_DASHBOARD_PORT` | `8642` |
| `OLLAMA_MODELS` | `/Volumes/CrucialX9/ZOE/models/ollama` |

### Tabla de modelos

| Modelo | Tamano | Velocidad | Uso | Requiere |
|--------|--------|-----------|-----|----------|
| `gemma-2-9b-iq2` | 3.5 GB | 15-25 t/s | Preguntas simples | 4GB RAM |
| `agents-a1-iq2` | 11.7 GB | 5-10 t/s | Estandar (MoE) | 8GB RAM |
| `qwen2.5:32b-iq2` | 12.5 GB | 5-10 t/s | Equilibrado | 8GB RAM |
| `qwq-32b-iq2` | 12.5 GB | 3-6 t/s | Razonamiento | 8GB RAM |
| `deepseek-r1:32b-iq2` | 12.5 GB | 2-4 t/s | Reflexion (8GB) | 8GB RAM |
| `deepseek-r1:32b-q4km` | 18 GB | 2-4 t/s | Reflexion (16GB) | 16GB RAM |
| `qwen2.5:72b-iq2` | 25 GB | 1-3 t/s | Maxima calidad | 8GB RAM |

### Tabla de endpoints del dashboard (seleccion)

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/` | GET | HTML del dashboard (publico) |
| `/health` | GET | Estado del sistema (publico) |
| `/ready` | GET | Readiness (publico) |
| `/live` | GET | Liveness (publico) |
| `/metrics` | GET | Prometheus metrics (publico) |
| `/manifest.json` | GET | PWA manifest (publico) |
| `/ws` | WebSocket | Chat en tiempo real |
| `/stats` | GET | Estadisticas |
| `/memory` | GET | Memoria |
| `/identity` | GET | Identidad |
| `/state` | GET | Estado metabolico |
| `/sleep` | POST | Forzar sueno |
| `/wake` | POST | Despertar |
| `/llm` | POST | Cambiar backend |
| `/api/capsules` | GET | Listar capsulas |
| `/api/capsules/load` | POST | Cargar capsula |
| `/api/reflections` | GET | Reflexiones recientes |
| `/api/reflections/metrics` | GET | Metricas reflexion |
| `/api/router/stats` | GET | Stats ACD Router |

> **Total:** 81 endpoints REST + WebSocket. Ver `zoe/dashboard/routes.py` para la lista completa.

### Atajos de teclado (Dashboard)

| Atajo | Accion |
|-------|--------|
| `Enter` | Enviar mensaje |
| `Shift+Enter` | Salto de linea |
| `Esc` | Cerrar modal |
| `Ctrl+K` | Enfocar campo de chat |
| `Cmd+R` | Recargar pagina |
| `Cmd+Shift+R` | Recargar sin cache |
| `Cmd+Option+I` | Abrir DevTools |

### Archivos importantes

| Archivo | Que contiene |
|---------|-------------|
| `/Volumes/CrucialX9/ZOE/data/zoe_memory.db` | Memoria SQLite (WAL) |
| `/Volumes/CrucialX9/ZOE/data/identity_vault.json` | Identidad SHA-256 |
| `/Volumes/CrucialX9/ZOE/data/trajectory_chain.json` | Trayectoria firmada |
| `/Volumes/CrucialX9/ZOE/data/capsules_loaded.json` | Capsulas cargadas |
| `/Volumes/CrucialX9/ZOE/data/.env` | Variables y API keys |
| `/Volumes/CrucialX9/ZOE/data/dashboard_token.txt` | Token del dashboard |
| `/Volumes/CrucialX9/ZOE/data/embodiment_plan.json` | Plan de hardware |
| `/Volumes/CrucialX9/ZOE/data/peers.json` | Peers federados |
| `/Volumes/CrucialX9/ZOE/data/phylogenetic_pool.json` | Pool filogenetico |

---

<p align="center">
  <b>ZOE v2.1.2 — Synthetic Cognitive Organism</b><br>
  1,700+ tests · 210 archivos Python · 15 capsulas · 81 endpoints · 6 backends LLM · 4 idiomas<br>
  DeepSeek-R1:32B IQ2_M/Q4_K_M · Reflexion autonoma adaptativa · SMART con ACD Router<br>
  <i>"ZOE no es un modelo que responde. Es un organismo que existe."</i>
</p>
