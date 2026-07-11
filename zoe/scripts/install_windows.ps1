<#
.SYNOPSIS
    ZOE v1.7 — Instalador para Windows (PowerShell)
.DESCRIPTION
    Instala ZOE en un SSD portátil o disco local en Windows.
    Todo (código, entorno virtual, memoria, datos) vive en el dispositivo.
.NOTES
    Requiere: Python 3.10+, Git
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ZOE v1.7 — Instalador para Windows" -ForegroundColor Cyan
Write-Host "  Synthetic Cognitive Organism (SCO)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# --- 1. Verificar Python ---
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -notmatch "3\.(10|11|12|13)") {
        Write-Host "  ADVERTENCIA: Python 3.10+ recomendado. Version detectada: $pythonVersion" -ForegroundColor Orange
    }
    Write-Host "  OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python no encontrado. Instalar desde https://python.org" -ForegroundColor Red
    exit 1
}

# --- 2. Verificar Git ---
Write-Host ""
Write-Host "[2/6] Verificando Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "  OK: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Git no encontrado. Instalar desde https://git-scm.com" -ForegroundColor Red
    exit 1
}

# --- 3. Seleccionar disco ---
Write-Host ""
Write-Host "[3/6] Seleccionar disco de instalación..." -ForegroundColor Yellow
$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -ne "C" -and $_.Used -gt 0 }
if ($drives.Count -eq 0) {
    Write-Host "  No se encontraron discos externos. Usando directorio local." -ForegroundColor Orange
    $zoeHome = "$env:USERPROFILE\ZOE"
} else {
    Write-Host "  Discos disponibles:"
    $i = 1
    foreach ($drive in $drives) {
        $sizeGB = [math]::Round(($drive.Used + $drive.Free) / 1GB, 1)
        Write-Host "    [$i] $($drive.Name):\ ($sizeGB GB)"
        $i++
    }
    $choice = Read-Host "  Selecciona [1-$($drives.Count)] (o Enter para local)"
    if ($choice -and $choice -le $drives.Count) {
        $zoeHome = "$($drives[$choice - 1].Name):\ZOE"
    } else {
        $zoeHome = "$env:USERPROFILE\ZOE"
    }
}
Write-Host "  Instalando en: $zoeHome" -ForegroundColor Green

# --- 4. Crear directorio ---
Write-Host ""
Write-Host "[4/6] Creando directorio ZOE..." -ForegroundColor Yellow
if (Test-Path $zoeHome) {
    Write-Host "  ADVERTENCIA: $zoeHome ya existe." -ForegroundColor Orange
    $overwrite = Read-Host "  Sobrescribir? (s/N)"
    if ($overwrite -match "^[sS]$") {
        Remove-Item -Recurse -Force $zoeHome
    } else {
        Write-Host "  Cancelado." -ForegroundColor Red
        exit 0
    }
}
New-Item -ItemType Directory -Path $zoeHome -Force | Out-Null
Write-Host "  OK: $zoeHome creado" -ForegroundColor Green

# --- 5. Clonar repositorio ---
Write-Host ""
Write-Host "[5/6] Clonando repositorio ZOE..." -ForegroundColor Yellow
Push-Location $zoeHome
git clone https://github.com/fernandofondillo/ZOE-Organismo-Cognitivo-Sintetico-SCO.git zoe
Write-Host "  OK: Repositorio clonado" -ForegroundColor Green

# --- 6. Crear entorno virtual + instalar ---
Write-Host ""
Write-Host "[6/6] Creando entorno virtual e instalando dependencias (1-2 min)..." -ForegroundColor Yellow
python -m venv venv
& .\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .\zoe\
Write-Host "  OK: Dependencias instaladas" -ForegroundColor Green

# --- Crear directorio de datos ---
New-Item -ItemType Directory -Path "$zoeHome\data" -Force | Out-Null

# --- Crear scripts lanzadores .bat ---
Write-Host ""
Write-Host "Creando scripts lanzadores..." -ForegroundColor Yellow

# ZOE-Chat.bat (Mock)
@"
@echo off
cd /d "$zoeHome"
call venv\Scripts\activate.bat
python -m zoe.cli_chat --backend mock
pause
"@ | Set-Content "$zoeHome\ZOE-Chat.bat"

# ZOE-Chat-Ollama.bat
@"
@echo off
cd /d "$zoeHome"
call venv\Scripts\activate.bat
python -m zoe.cli_chat --backend ollama --model qwen2.5:3b
pause
"@ | Set-Content "$zoeHome\ZOE-Chat-Ollama.bat"

# ZOE-Dashboard.bat
@"
@echo off
cd /d "$zoeHome"
call venv\Scripts\activate.bat
python -m zoe.web_dashboard --backend mock
pause
"@ | Set-Content "$zoeHome\ZOE-Dashboard.bat"

# ZOE-Dashboard-Ollama.bat
@"
@echo off
cd /d "$zoeHome"
call venv\Scripts\activate.bat
python -m zoe.web_dashboard --backend ollama --model qwen2.5:3b
pause
"@ | Set-Content "$zoeHome\ZOE-Dashboard-Ollama.bat"

Write-Host "  OK: 4 scripts .bat creados" -ForegroundColor Green

# --- Configurar API key (opcional) ---
Write-Host ""
Write-Host "Configurar OpenAI API key (opcional)..." -ForegroundColor Yellow
$configOpenAI = Read-Host "  Configurar API key de OpenAI ahora? (s/N)"
if ($configOpenAI -match "^[sS]$") {
    $apiKey = Read-Host "  Pega tu API key (sk-...)" -AsSecureString
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
    )
    "OPENAI_API_KEY=$plainKey" | Set-Content "$zoeHome\data\.env"
    Write-Host "  OK: API key guardada en $zoeHome\data\.env" -ForegroundColor Green
}

# --- Verificación ---
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ZOE instalado correctamente!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para usar ZOE:" -ForegroundColor Cyan
Write-Host "  1. Doble clic en ZOE-Chat.bat (modo Mock)" -ForegroundColor White
Write-Host "  2. Doble clic en ZOE-Chat-Ollama.bat (con Ollama)" -ForegroundColor White
Write-Host "  3. Doble clic en ZOE-Dashboard.bat (Dashboard web)" -ForegroundColor White
Write-Host ""
Write-Host "Directorio: $zoeHome" -ForegroundColor Gray
Write-Host ""

Pop-Location
