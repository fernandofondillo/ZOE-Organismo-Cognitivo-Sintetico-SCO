# ZOE — Manual de Instalación Multiplataforma
### Para usuarios no técnicos

> **Versión**: 1.0 — Julio 2026 (Sprint 5.23)
> **Proyecto**: ZOE — Synthetic Cognitive Organism
> **Repo**: github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO

---

## ¿Qué es ZOE?

ZOE es un **organismo cognitivo sintético**: un asistente de IA que **recuerda**
lo que hablas con él, tiene **identidad propia** (un hash criptográfico que lo
hace único), **reflexiona cuando está solo** y **aprende nuevos temas cargando
cápsulas de conocimiento**.

A diferencia de ChatGPT o Claude (que cada vez que abres empiezan desde cero),
ZOE **persiste entre sesiones**: cierras hoy, abres dentro de un mes, y recuerda
literalmente lo que hablaron.

ZOE funciona con modelos LLM locales (Ollama) o cloud (MiniMax, OpenAI,
Anthropic, DeepSeek). Tú eliges cuál usar.

---

## Tabla de plataformas soportadas

| Plataforma | Soporte | Dificultad | Recomendado para |
|---|---|---|---|
| **macOS** (Intel/Apple Silicon) | ✅ Oficial | Fácil | Usuario final |
| **SSD USB-C portátil** | ✅ Oficial | Fácil | Movilidad |
| **Linux** (Ubuntu/Debian) | ✅ Oficial | Media | VPS / servidor |
| **Windows 10/11** (con Git Bash) | ⚠️ Parcial | Media | Usuario técnico |
| **VPS** (DigitalOcean/Hetzner/AWS) | ✅ Oficial | Media | Producción 24/7 |
| **iPhone** | ⚠️ Vía web | Fácil | Consumo remoto |
| **Android** | ⚠️ Vía web | Fácil | Consumo remoto |
| **iPad** | ⚠️ Vía web | Fácil | Consumo remoto |

> **Nota**: iPhone/iPad/Android **no ejecutan ZOE nativamente**. Consumen ZOE
> vía navegador web apuntando a un VPS o Mac donde ZOE está corriendo.

---

# PARTE 1 — Instalación en macOS (recomendado)

## 1.1 Requisitos previos

Antes de empezar necesitas:

1. **Mac con macOS 12+** (Monterey, Ventura, Sonoma, Sequoia).
2. **8 GB de RAM mínimo** (recomendado 16 GB).
3. **20 GB libres en disco** (para ZOE + 1 modelo local).
4. **Conexión a internet** durante la instalación.
5. **Terminal** (viene preinstalada en macOS, en `Aplicaciones > Utilidades`).

## 1.2 Instalación con SSD portátil (recomendado)

Esta opción instala ZOE en un SSD USB-C para que puedas llevarlo contigo
y arrancarlo en cualquier Mac.

### Paso 1 — Conectar el SSD

1. Conecta tu SSD USB-C al Mac.
2. Abre el Finder y verifica que el SSD aparece en la barra lateral.
3. Anota el nombre del SSD (ej: `Crucial X9`).

### Paso 2 — Abrir Terminal

1. Abre `Aplicaciones > Utilidades > Terminal`.
2. Verás una ventana negra con texto. Eso es normal.

### Paso 3 — Descargar el script de instalación

Copia y pega este comando en la Terminal y pulsa Enter:

```bash
curl -fsSL https://raw.githubusercontent.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/main/zoe/scripts/install_ssd_crucial_x9_mac.sh -o /tmp/install_zoe.sh
```

Si ves texto moviéndose, está bien. Espera a que termine.

### Paso 4 — Ejecutar el instalador

```bash
bash /tmp/install_zoe.sh
```

El instalador te preguntará:

1. **¿En qué SSD instalar ZOE?** — Te muestra una lista. Escribe el número
   correspondiente a tu SSD.
2. **¿Qué set de modelos descargar?** — Recomendado: `balanced` (1 modelo,
   ~5 GB). Si tienes 16 GB de RAM, puedes elegir `complete`.
3. **¿Tienes API key de OpenAI?** — Si tienes una, pégala. Si no, pulsa Enter.
4. **¿Tienes API key de Anthropic o MiniMax?** — Si tienes una (especialmente
   de MiniMax), pégala. Si no, pulsa Enter.

El instalador descargará todo lo necesario. **Tarda entre 10 y 30 minutos**
dependiendo de tu conexión.

### Paso 5 — Verificar la instalación

Cuando termine, verás un mensaje como:

```
✅ ZOE instalado correctamente en /Volumes/Crucial X9/ZOE
```

Abre el Finder, navega a tu SSD, y verás una carpeta `ZOE` con estos archivos:

- `INICIAR-DASHBOARD.command` — **Doble-click para arrancar ZOE**
- `INICIAR-ZOE.command` — Doble-click para arrancar en modo terminal
- `zoe/` — Código del proyecto
- `data/` — Tu memoria, identidad, configuración
- `venv/` — Entorno Python (no tocar)
- `models/` — Modelos IA locales (si descargaste alguno)

### Paso 6 — Arrancar ZOE por primera vez

1. **Doble-click** en `INICIAR-DASHBOARD.command`.
2. Se abrirá Terminal automáticamente con texto moviéndose.
3. Espera a ver: `✅ Dashboard iniciado en http://localhost:8642`.
4. Tu navegador se abrirá automáticamente con ZOE.
5. **Escribe "hola"** en el chat y pulsa Enter.
6. ZOE te responderá. ¡Felicidades, está funcionando!

### Paso 7 — Cerrar ZOE

1. Ve a la Terminal donde está corriendo ZOE.
2. Pulsa `Ctrl + C` (las dos teclas a la vez).
3. Verás `💾 Memoria guardada: XXX entries` — eso significa que tu conversación
   quedó guardada.
4. Cierra la Terminal.

## 1.3 Instalación SIN SSD (en el Mac directamente)

Si no tienes SSD, puedes instalar ZOE en tu carpeta de usuario:

### Paso 1 — Instalar Python

macOS ya trinda Python, pero conviene tener la última versión:

1. Ve a https://www.python.org/downloads/
2. Descarga el instalador de Python 3.12+.
3. Doble-click en el `.pkg` descargado y sigue los pasos.

### Paso 2 — Instalar Git

1. Abre Terminal.
2. Escribe `git --version` y pulsa Enter.
3. Si te pide instalar "Command Line Tools", di que sí.

### Paso 3 — Clonar el repositorio

```bash
cd ~
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git ZOE
cd ZOE
```

### Paso 4 — Crear entorno virtual e instalar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Paso 5 — Arrancar

```bash
python -m zoe.web_dashboard --backend pattern --port 8642
```

Abre `http://localhost:8642` en tu navegador.

## 1.4 Configurar MiniMax (recomendado para España)

MiniMax-M3 es un modelo cloud muy capaz y económico. Para usarlo:

### Paso 1 — Obtener API key de MiniMax

1. Ve a https://platform.minimaxi.com/
2. Regístrate con tu email.
3. Entra en tu dashboard.
4. Crea una API key (botón "Create API Key").
5. **Copia el token** (empieza con `eyJ...`). Guárdalo en un lugar seguro.

### Paso 2 — Crear archivo .env

1. Abre Terminal.
2. Navega a tu carpeta ZOE: `cd ~/ZOE` (o donde lo hayas instalado).
3. Crea la carpeta data: `mkdir -p data`.
4. Crea el archivo .env:

```bash
nano data/.env
```

5. Pega este contenido (sustituye `TU_TOKEN_AQUI`):

```
ANTHROPIC_API_KEY=TU_TOKEN_AQUI
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_MODEL=MiniMax-M3
```

6. Pulsa `Ctrl + O` para guardar, `Ctrl + X` para salir.
7. Protege el archivo: `chmod 600 data/.env`.

### Paso 3 — Arrancar ZOE con MiniMax

```bash
bash zoe/scripts/INICIAR-DASHBOARD.command
```

O si lo arrancas manualmente:

```bash
python -m zoe.web_dashboard \
    --backend anthropic \
    --model MiniMax-M3 \
    --base-url https://api.minimax.io/anthropic \
    --port 8642
```

Verás en la consola: `Anthropic-compat -- MiniMax-M3 @ https://api.minimax.io/anthropic`.

¡Listo! ZOE usará MiniMax-M3 para responder.

---

# PARTE 2 — Instalación en SSD portátil (multi-Mac)

Esta sección es para usuarios que ya instalaron ZOE en un SSD y quieren
usarlo en **cualquier Mac**.

## 2.1 Llevar el SSD a otra Mac

1. Expulsa el SSD en la Mac original (`Cmd + E` en Finder).
2. Conecta el SSD a la nueva Mac.
3. Si te pregunta "¿Confiar en este dispositivo?", di que sí.

## 2.2 Arrancar ZOE en la nueva Mac

1. Abre el Finder.
2. Navega al SSD (aparece en la barra lateral con el nombre que le diste).
3. Abre la carpeta `ZOE`.
4. **Doble-click en `INICIAR-DASHBOARD.command`**.
5. Si macOS dice "No se puede abrir porque no es de un desarrollador
   identificado":
   - Botón derecho sobre el archivo.
   - Selecciona "Abrir".
   - En el diálogo, pulsa "Abrir".
6. ZOE arrancará usando el backend configurado en `.env`.

> **Importante**: Tu memoria, identidad y trayectoria persisten en el SSD.
> Es la **misma ZOE** en cualquier Mac donde la conectes.

## 2.3 Actualizar ZOE en el SSD

Cuando salga una nueva versión de ZOE:

1. Conecta el SSD a una Mac con internet.
2. Doble-click en `ACTUALIZAR-ZOE.command` (en la carpeta `ZOE`).
3. El script hará backup automático de tus datos.
4. Verificará si hay actualizaciones en GitHub.
5. Si las hay, te preguntará si quieres instalarlas.
6. Tras instalar, ejecutará smoke tests para asegurar que nada se rompió.
7. Si los tests pasan: tu ZOE está actualizado y tus datos intactos.
8. Si los tests fallan: restaura automáticamente la versión anterior.

> **Esto es seguro**: nunca perderás tu memoria, identidad o configuración.

---

# PARTE 3 — Instalación en VPS (producción 24/7)

Recomendado si quieres acceder a ZOE desde cualquier dispositivo (iPhone,
Android, iPad) vía navegador web.

## 3.1 Crear un VPS

### Opción A — DigitalOcean (más fácil)

1. Ve a https://digitalocean.com/.
2. Crea una cuenta con tu tarjeta.
3. Crea un Droplet:
   - **Imagen**: Ubuntu 22.04 LTS.
   - **Plan**: Basic Premium Intel con **4 GB RAM / 80 GB SSD** ($24/mes).
   - **Datacenter**: Frankfurt (si estás en España).
   - **SSH keys**: añade tu clave pública SSH (busca tutorial si no sabes).
4. Pulsa "Create Droplet".
5. Anota la IP pública (ej: `164.90.200.50`).

### Opción B — Hetzner (más barato)

1. Ve a https://hetzner.cloud/.
2. Crea una cuenta.
3. Crea un servidor:
   - **Ubicación**: Falkenstein (Alemania).
   - **Imagen**: Ubuntu 22.04.
   - **Tipo**: CPX31 (4 vCPU, 8 GB RAM, 160 GB) — ~€15/mes.
4. Añade tu clave SSH.
5. Crea y anota la IP.

### Opción C — AWS EC2 (avanzado)

1. Ve a https://aws.amazon.com/ec2/.
2. Lanza instancia `t3.medium` (4 GB RAM) o `t3.large` (8 GB RAM).
3. AMI: Ubuntu Server 22.04 LTS.
4. Configura security group con puertos 22 (SSH), 80 (HTTP), 443 (HTTPS),
   y 8642 (ZOE dashboard).
5. Crea key pair y descarga el `.pem`.

## 3.2 Conectarse al VPS por SSH

En tu Mac o Linux:

```bash
ssh root@TU_IP_DEL_VPS
```

Sustituye `TU_IP_DEL_VPS` por la IP real. La primera vez, escribe `yes` cuando
pregunte por la fingerprint.

## 3.3 Instalar Docker

```bash
apt update
apt install -y docker.io docker-compose git
systemctl enable docker
systemctl start docker
```

Verifica: `docker --version` debe mostrar `Docker version 24.x.x` o superior.

## 3.4 Clonar ZOE y configurar

```bash
cd /opt
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git zoe
cd zoe
```

Crea el archivo `.env` con tu API key:

```bash
mkdir -p data
cat > data/.env <<EOF
ANTHROPIC_API_KEY=TU_TOKEN_DE_MINIMAX_AQUI
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_MODEL=MiniMax-M3
EOF
chmod 600 data/.env
```

## 3.5 Arrancar ZOE con Docker Compose

```bash
docker-compose up -d
```

Esto arrancará ZOE + Ollama + Postgres en contenedores. Tarda 2-3 minutos
la primera vez (descarga imágenes).

Verifica que está corriendo:

```bash
docker-compose ps
```

Debes ver 3 contenedores con estado `Up`.

## 3.6 Configurar Nginx + HTTPS (para acceso web)

```bash
apt install -y nginx certbot python3-certbot-nginx
```

Crea configuración de Nginx:

```bash
cat > /etc/nginx/sites-available/zoe <<'EOF'
server {
    listen 80;
    server_name zoe.tudominio.com;  # CAMBIA esto

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8642;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

ln -s /etc/nginx/sites-available/zoe /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Configura tu dominio para apuntar a la IP del VPS (registro A en tu proveedor
de dominio). Luego pide certificado HTTPS:

```bash
certbot --nginx -d zoe.tudominio.com
```

Sigue las instrucciones. Cuando termine, podrás acceder a ZOE en:

```
https://zoe.tudominio.com
```

## 3.7 Asegurar el dashboard con token

Por defecto, ZOE en VPS requiere un token de autenticación. Para verlo:

```bash
cat /opt/zoe/data/dashboard_token.txt
```

Ese token te lo pedirá el navegador al abrir la URL. Guárdalo en un gestor
de contraseñas (Bitwarden, 1Password, etc.).

Para regenerar el token:

```bash
rm /opt/zoe/data/dashboard_token.txt
docker-compose restart zoe
cat /opt/zoe/data/dashboard_token.txt
```

## 3.8 Actualizar ZOE en el VPS

```bash
cd /opt/zoe
git pull
docker-compose build
docker-compose up -d
```

Tus datos (memoria, identidad) persisten en el volumen Docker `zoe_data`.

---

# PARTE 4 — Acceder a ZOE desde iPhone, iPad o Android

Una vez que ZOE está corriendo en un VPS (sección 3), puedes acceder desde
tu móvil.

## 4.1 Acceso vía navegador (todas las plataformas)

1. Abre el navegador (Safari en iOS, Chrome en Android).
2. Ve a `https://zoe.tudominio.com` (tu dominio del VPS).
3. Te pedirá usuario/contraseña o token. Pega el token de
   `dashboard_token.txt`.
4. Verás el dashboard de ZOE. ¡Funciona igual que en el Mac!

## 4.2 Añadir a pantalla de inicio (PWA)

Para que ZOE se abra como una app nativa:

### iPhone/iPad (Safari)

1. Abre Safari.
2. Ve a tu URL de ZOE.
3. Pulsa el botón **Compartir** (cuadrado con flecha hacia arriba).
4. Selecciona **"Añadir a pantalla de inicio"**.
5. Ponle nombre "ZOE" y pulsa **Añadir**.
6. Ahora tendrás un icono de ZOE en tu pantalla de inicio.

### Android (Chrome)

1. Abre Chrome.
2. Ve a tu URL de ZOE.
3. Pulsa el botón de **menú** (3 puntos arriba a la derecha).
4. Selecciona **"Añadir a pantalla de inicio"**.
5. Confirma.

## 4.3 Activar voz (si quieres hablar con ZOE)

1. En el dashboard, pulsa el icono de **micrófono** (arriba a la derecha).
2. El navegador te pedirá permiso para usar el micrófono. Acepta.
3. Ahora puedes hablar con ZOE. Di "hola ZOE" para despertarla.
4. ZOE responderá con voz.

> **Nota**: la función de voz requiere conexión estable. En 4G funciona
> pero puede tener latencia. Recomendado WiFi.

## 4.4 Recibir notificaciones (próximamente)

En una próxima versión de ZOE podrás recibir notificaciones push cuando ZOE
tenga un insight o quiera compartir un pensamiento autónomo contigo.

---

# PARTE 5 — Instalación en Windows

## 5.1 Requisitos

- Windows 10 o Windows 11.
- 8 GB RAM mínimo.
- 20 GB libres en disco.
- Conexión a internet.

## 5.2 Instalar WSL2 (recomendado)

La forma más fácil de ejecutar ZOE en Windows es con WSL2 (Windows Subsystem
for Linux):

1. Abre PowerShell como administrador (botón derecho sobre Inicio).
2. Ejecuta:

```powershell
wsl --install
```

3. Reinicia el equipo cuando termine.
4. Al reiniciar, se abrirá Ubuntu automáticamente. Configura tu usuario y
   contraseña.

A partir de aquí, **sigue las instrucciones de Linux** (sección 6) dentro
de Ubuntu WSL.

## 5.3 Instalación nativa en Windows (avanzado)

Si no quieres usar WSL2:

### Paso 1 — Instalar Python

1. Ve a https://www.python.org/downloads/
2. Descarga Python 3.12+ para Windows.
3. **Importante**: durante la instalación, marca "Add Python to PATH".
4. Completa la instalación.

### Paso 2 — Instalar Git

1. Ve a https://git-scm.com/download/win
2. Descarga e instala con opciones por defecto.

### Paso 3 — Abrir Git Bash

1. Busca "Git Bash" en el menú Inicio.
2. Ábrelo. Verás una terminal tipo Linux.

### Paso 4 — Clonar ZOE

```bash
cd ~
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git ZOE
cd ZOE
```

### Paso 5 — Crear entorno virtual e instalar

```bash
python -m venv venv
source venv/Scripts/activate
pip install -e .
```

### Paso 6 — Configurar API key

```bash
mkdir -p data
echo "ANTHROPIC_API_KEY=TU_TOKEN_AQUI" > data/.env
echo "ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic" >> data/.env
echo "ANTHROPIC_MODEL=MiniMax-M3" >> data/.env
```

### Paso 7 — Arrancar

```bash
python -m zoe.web_dashboard --backend anthropic --model MiniMax-M3 --base-url https://api.minimax.io/anthropic --port 8642
```

Abre `http://localhost:8642` en tu navegador.

> **Nota**: algunas features de ZOE (señales de sistema, voice-first)
> pueden no funcionar en Windows nativo. Recomendado WSL2.

---

# PARTE 6 — Instalación en Linux (Ubuntu/Debian)

## 6.1 Requisitos

- Ubuntu 20.04, 22.04 o 24.04 LTS (o Debian 11/12).
- 4 GB RAM mínimo (recomendado 8 GB).
- 20 GB libres en disco.
- Acceso `sudo`.

## 6.2 Instalar dependencias

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

## 6.3 Clonar ZOE

```bash
cd ~
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git ZOE
cd ZOE
```

## 6.4 Crear entorno virtual e instalar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## 6.5 Configurar API key (MiniMax)

```bash
mkdir -p data
cat > data/.env <<EOF
ANTHROPIC_API_KEY=TU_TOKEN_DE_MINIMAX_AQUI
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_MODEL=MiniMax-M3
EOF
chmod 600 data/.env
```

## 6.6 Arrancar ZOE

```bash
source venv/bin/activate
set -a; source data/.env; set +a
python -m zoe.web_dashboard --backend anthropic --model MiniMax-M3 --base-url https://api.minimax.io/anthropic --port 8642
```

Abre `http://localhost:8642` en tu navegador.

## 6.7 Como servicio systemd (para arranque automático)

Crea el archivo `/etc/systemd/system/zoe.service`:

```bash
sudo nano /etc/systemd/system/zoe.service
```

Pega este contenido (sustituye `TU_USUARIO`):

```ini
[Unit]
Description=ZOE Synthetic Cognitive Organism
After=network.target

[Service]
Type=simple
User=TU_USUARIO
WorkingDirectory=/home/TU_USUARIO/ZOE
EnvironmentFile=/home/TU_USUARIO/ZOE/data/.env
ExecStart=/home/TU_USUARIO/ZOE/venv/bin/python -m zoe.serve --env production
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Habilita y arranca:

```bash
sudo systemctl daemon-reload
sudo systemctl enable zoe
sudo systemctl start zoe
sudo systemctl status zoe
```

Para ver los logs:

```bash
sudo journalctl -u zoe -f
```

---

# PARTE 7 — Solución de problemas

## 7.1 ZOE no arranca

### Síntoma: `ModuleNotFoundError: No module named 'zoe'`

**Causa**: no activaste el venv o falta `pip install -e .`.

**Solución**:

```bash
cd ~/ZOE
source venv/bin/activate
pip install -e .
```

### Síntoma: `Permission denied` al ejecutar `.command`

**Causa**: macOS no marca el archivo como ejecutable.

**Solución**:

```bash
chmod +x ~/ZOE/zoe/scripts/INICIAR-DASHBOARD.command
```

### Síntoma: "No se puede abrir porque no es de un desarrollador identificado"

**Causa**: macOS Gatekeeper bloquea scripts de terceros.

**Solución**:
1. Botón derecho sobre el `.command`.
2. Selecciona "Abrir".
3. En el diálogo, pulsa "Abrir".

## 7.2 ZOE arranca pero no responde

### Síntoma: el chat muestra "Estoy aquí. Te escucho." siempre

**Causa**: estás usando `--backend pattern` (sin LLM). Necesitas configurar
una API key o instalar Ollama.

**Solución**: ver sección 1.4 (MiniMax) o instalar Ollama desde
https://ollama.com.

### Síntoma: `Anthropic error 401: Unauthorized`

**Causa**: API key incorrecta o sin saldo.

**Solución**:
1. Verifica tu API key en https://platform.minimaxi.com/.
2. Verifica que tienes saldo en tu cuenta.
3. Asegúrate de que `data/.env` tiene las 3 líneas correctas:

```
ANTHROPIC_API_KEY=tu_token_real
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_MODEL=MiniMax-M3
```

### Síntoma: `Connection refused` al abrir localhost:8642

**Causa**: ZOE no está corriendo o el puerto está ocupado.

**Solución**:
1. Verifica que la Terminal muestra `Dashboard iniciado`.
2. Si el puerto 8642 está ocupado, ZOE buscará otro automáticamente
   (8643, 8644...). Mira el log para ver qué puerto usó.
3. Para matar procesos en el puerto 8642:

```bash
lsof -ti:8642 | xargs kill -9
```

## 7.3 ZOE olvidó lo que hablamos

### Síntoma: abro ZOE y no recuerda conversaciones previas

**Causa**: la memoria SQLite se borró o el path cambió.

**Solución**:
1. Verifica que existe `data/dashboard_memory.db`:

```bash
ls -la ~/ZOE/data/
```

2. Si no existe, ZOE creará una nueva al arrancar (memoria vacía).
3. Si lo cambiaste de sitio, restaura desde el backup:

```bash
cd ~/ZOE
tar -xzf backups/zoe_data_backup_YYYYMMDD_HHMMSS.tar.gz
```

## 7.4 Voice-first no funciona

### Síntoma: "No se detecta el micrófono"

**Causa**: el navegador no tiene permiso, o no tienes Whisper/Piper instalados.

**Solución**:
1. En el navegador, ve a la configuración de permisos del sitio.
2. Permite el acceso al micrófono.
3. Instala Whisper: `pip install openai-whisper`.
4. Instala Piper desde https://github.com/rhasspy/piper.

## 7.5 Dashboard no se actualiza en tiempo real

### Síntoma: los pensamientos autónomos no aparecen

**Causa**: bug del mentor arreglado en Sprint 5.23.

**Solución**:

```bash
cd ~/ZOE
bash zoe/scripts/ACTUALIZAR-ZOE.command
```

## 7.6 Obtener ayuda

Si tienes problemas:

1. **Revisa el log**:

```bash
cat ~/ZOE/data/zoe.log | tail -50
```

2. **Busca en el dossier técnico**: en `zoe/docs/ZOE_DOSSIER_CERTIFICACION_RECUPERACION.md`
   está el catálogo completo de 50 bugs y sus fixes.
3. **Abre un issue en GitHub**: https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/issues
4. **Incluye en tu reporte**:
   - Tu sistema operativo.
   - Versión de ZOE (`git rev-parse HEAD` en `~/ZOE/zoe`).
   - Mensaje de error completo.
   - Log completo (`cat data/zoe.log`).

---

# PARTE 8 — Comandos útiles

## 8.1 Ver estado de ZOE

```bash
# En terminal, con ZOE corriendo:
/stats
/memory
/state
/identity
```

## 8.2 Forzar sueño/despertar

```bash
# En el chat de ZOE:
/sleep   # forzar SLEEPING (ZOE reflexiona)
/wake    # forzar AWAKE
```

## 8.3 Cargar cápsula de conocimiento

```bash
# En el chat:
/capsules              # lista cápsulas disponibles
/capsule elder_care_knowledge    # cargar cápsula
/uncapsule elder_care_knowledge  # descargar cápsula
```

## 8.4 Alimentar documento a ZOE

```bash
# En el chat:
/feed /ruta/a/mi/documento.txt
```

ZOE leerá el documento y lo recordará como memoria semántica.

## 8.5 Ver historial de conversación

```bash
# En el chat:
/history
```

## 8.6 Backup manual

```bash
cd ~/ZOE
tar -czf backups/manual_$(date +%Y%m%d).tar.gz data/
```

## 8.7 Restaurar backup

```bash
cd ~/ZOE
tar -xzf backups/zoe_data_backup_YYYYMMDD_HHMMSS.tar.gz
```

---

# PARTE 9 — Preguntas frecuentes (FAQ)

## Q: ¿ZOE envía mis datos a terceros?

**No**, si usas un modelo local (Ollama). Toda la memoria e identidad viven
en tu SSD.

Si usas un cloud provider (MiniMax, OpenAI, Anthropic), **las preguntas que
haces se envían a ese provider** para que genere la respuesta. Tu memoria
episódica persiste localmente; solo las peticiones HTTP van fuera.

## Q: ¿Puedo usar ZOE sin internet?

**Sí**, si instalaste Ollama con un modelo local. Funciona 100% offline.

Si usas MiniMax/OpenAI, necesitas internet para cada mensaje.

## Q: ¿ZOE es gratis?

El software ZOE es open-source (MIT license). Los costes son:

- **MiniMax**: pago por token (~$0.001 por mensaje corto).
- **OpenAI GPT-4o**: ~$0.01-0.05 por mensaje.
- **Anthropic Claude**: ~$0.005-0.03 por mensaje.
- **Ollama local**: gratis (solo consume tu electricidad).

## Q: ¿Puedo tener varias ZOE?

**Sí**. Cada carpeta ZOE en tu SSD es una ZOE distinta con su propia
identidad, memoria y trayectoria. Puedes tener `~/ZOE-trabajo`,
`~/ZOE-personal`, etc.

## Q: ¿Cómo cambio el nombre de mi ZOE?

Por ahora no se puede desde el dashboard. Tienes que editar el código:

```bash
nano ~/ZOE/zoe/alma/identity_vault.py
# Busca NINE_VECTORS y SEVEN_VALUES, modifica los valores
# Borra data/identity_vault.json para que se regenere
rm ~/ZOE/data/identity_vault.json
```

> **Nota**: esto creará una ZOE nueva (hash distinto). Tu memoria y
> trayectoria se conservan, pero la identidad criptográfica cambia.

## Q: ¿Puedo mover ZOE entre Mac y Linux?

**Sí**. ZOE es multiplataforma. Solo necesitas:
1. Copiar la carpeta `ZOE/` (incluyendo `data/`) al otro sistema.
2. Crear un nuevo venv en el destino (`python3 -m venv venv`).
3. `pip install -e .`
4. Arrancar con `python -m zoe.web_dashboard ...`.

Tu memoria, identidad y trayectoria persisten porque están en `data/`.

## Q: ¿ZOE aprende de lo que hablo?

**Sí, lentamente**. Cada conversación se almacena como memoria episódica.
Durante los ciclos de SLEEPING (cuando ZOE está en reposo), consolida
memorias episódicas en semánticas, extrae patrones y detecta
contradicciones.

Para forzar reflexión: `/sleep`, espera 30 segundos, `/wake`, y revisa
`/api/reflections` en el dashboard.

## Q: ¿Puedo borrar memorias específicas?

Por ahora no desde el dashboard. Tienes que editar SQLite directamente:

```bash
sqlite3 ~/ZOE/data/dashboard_memory.db "DELETE FROM memory_entries WHERE id='mem_XYZ';"
```

(En una próxima versión habrá un endpoint `/api/memory/{id}/delete`.)

---

# PARTE 10 — Glosario para no técnicos

| Término | Qué significa |
|---|---|
| **ACD** | Adaptive Cognitive Depth. Sistema que decide si tu pregunta es fácil (L0) o difícil (L3) y usa el modelo adecuado. |
| **Backend** | El "cerebro" de IA que ZOE usa. Puede ser MiniMax, OpenAI, Anthropic u Ollama. |
| **Cápsula** | Paquete de conocimiento que ZOE carga para aprender un tema (ej: farmacología). |
| **CSP** | Content Security Policy. Cabecera HTTP que protege contra ataques web. |
| **Dashboard** | La interfaz web de ZOE (http://localhost:8642). |
| **Embeddings** | Vectores numéricos que representan el significado de un texto. Permiten búsqueda semántica. |
| **Identidad criptográfica** | Hash SHA-256 único que identifica a tu ZOE. Si alguien modifica tus vectores de identidad, el hash cambia. |
| **LLM** | Large Language Model. El modelo de IA que genera las respuestas (GPT-4, Claude, MiniMax-M3, etc.). |
| **Memoria episódica** | Recuerdos de eventos específicos (lo que hablaron ayer). |
| **Memoria semántica** | Conocimiento general (la tierra es redonda, el cielo es azul). |
| **Metabolismo** | Sistema que alterna entre AWAKE (despierto) y SLEEPING (durmiendo para consolidar memoria). |
| **MiniMax-M3** | Modelo de IA chino, barato y capaz. Recomendado para España. |
| **Ollama** | Software para ejecutar modelos de IA localmente en tu Mac/Linux. |
| **PatternSpeaker** | Modo sin IA que responde con plantillas prefabricadas. Útil si no tienes API key. |
| **PWA** | Progressive Web App. Web que se instala como app nativa en tu móvil. |
| **Reflexión** | Cuando ZOE está en SLEEPING, piensa sobre memorias recientes y genera insights. |
| **SSD** | Solid State Drive. Disco duro portátil USB-C. |
| **Token** | Unidad de texto (~4 caracteres). Los cloud providers cobran por token. |
| **Trayectoria** | Cadena de mutaciones firmadas. Como una blockchain de la vida de ZOE. |
| **VPS** | Virtual Private Server. Ordenador remoto que alquilas en la nube. |
| **Whisper** | Modelo de transcripción de voz a texto de OpenAI. |
| **WSL2** | Windows Subsystem for Linux 2. Permite correr Linux dentro de Windows. |

---

# PARTE 11 — Recursos adicionales

## Documentación técnica

- **Dossier Técnico Maestro** (auditoría completa):
  `zoe/docs/ZOE_DOSSIER_CERTIFICACION_RECUPERACION.md`
- **README del proyecto**: https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO
- **Wiki**: próximamente

## Comunidad

- **Issues (bugs, preguntas)**: https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/issues
- **Discusiones**: https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO/discussions

## Proveedores cloud compatibles

- **MiniMax**: https://platform.minimaxi.com/ (recomendado para España)
- **OpenAI**: https://platform.openai.com/
- **Anthropic Claude**: https://console.anthropic.com/
- **DeepSeek**: https://platform.deepseek.com/
- **Groq**: https://console.groq.com/
- **Moonshot/Kimi**: https://platform.moonshot.cn/

## Modelos locales (Ollama)

- **Web**: https://ollama.com
- **Modelos recomendados**:
  - `gemma2:9b` (rápido, 5 GB RAM)
  - `qwen2.5:3b` (muy rápido, 2 GB RAM)
  - `deepseek-r1:32b` (potente, 16 GB RAM)

---

**Fin del Manual de Instalación Multiplataforma.**

> Si tienes dudas, abre un issue en GitHub con tu pregunta. El equipo
> responde en 24-48 horas.

> **Última actualización**: Julio 2026 (Sprint 5.23)
