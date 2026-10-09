# Kibo - Windows installer
#
# Usage (PowerShell):
#   powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Dir

function Say-Ok   { param([string]$m) Write-Host "  OK $m" -ForegroundColor Green }
function Say-Warn { param([string]$m) Write-Host "  ! $m" -ForegroundColor Yellow }
function Say-Err  { param([string]$m) Write-Host "  X $m" -ForegroundColor Red; exit 1 }
function Say-Info { param([string]$m) Write-Host "  - $m" -ForegroundColor DarkGray }
function Step     { param([string]$n, [string]$m) Write-Host ""; Write-Host "[$n] $m" -ForegroundColor Cyan; Write-Host "  ------------" -ForegroundColor DarkGray }


Write-Host ""
Write-Host "  KIBO - INSTALLER (Windows)" -ForegroundColor Cyan
Write-Host "  ----------------------------"
Write-Host ""


Step "1/5" "Checking Python 3.9+"
$Py = $null
$PyVer = ""
foreach ($cand in @("py -3", "python3", "python")) {
    $exe = $cand.Split(' ')[0]
    try {
        $v = & $exe --version 2>$null
        if ($LASTEXITCODE -eq 0) { $Py = $exe; $PyVer = ($v -join " "); break }
    } catch { }
}
if (-not $Py) { Say-Err "Python not found. Install it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH')" }
Say-Ok "using $Py ($PyVer)"


Step "2/5" "Creating virtual environment"
$VEnv = Join-Path $Dir ".venv"
$VEnvPy = Join-Path $VEnv "Scripts\python.exe"
if (-not (Test-Path $VEnvPy)) {
    & $Py -m venv $VEnv
    if ($LASTEXITCODE -ne 0) { Say-Err "Could not create the virtual environment" }
    Say-Ok "created $VEnv"
} else {
    Say-Ok "reusing existing venv"
}


Step "3/5" "Installing dependencies"
& $VEnvPy -m pip install --quiet --upgrade pip
& $VEnvPy -m pip install --quiet -e .
if ($LASTEXITCODE -ne 0) { Say-Err "pip install failed" }
Say-Ok "kibo package registered (editable)"

& $VEnvPy -c "import tkinter" 2>$null
if ($LASTEXITCODE -eq 0) { Say-Ok "tkinter available (widget supported)" }
else { Say-Warn "tkinter missing - widget unavailable, reinstall Python with 'tcl/tk' ticked" }


Step "4/5" "Telegram Chats"
Write-Host ""
Write-Host "  Which chats may drive this PC?" -ForegroundColor DarkGray
Write-Host "  Group ids look like -1001234567890. Your own id comes from /chatid in the bot." -ForegroundColor DarkGray
Write-Host ""

$AllowFile = Join-Path $HOME ".config\kibo\telegram_allowed.json"
$AllowDir = Split-Path -Parent $AllowFile
if (-not (Test-Path $AllowDir)) { New-Item -ItemType Directory -Force -Path $AllowDir | Out-Null }

function Add-ChatId {
    param([long]$Id)
    $ids = @()
    if (Test-Path $AllowFile) {
        try {
            $raw = Get-Content $AllowFile -Raw | ConvertFrom-Json
            if ($raw.chats) { $ids = @($raw.chats) }
        } catch { }
    }
    $ids = @($ids + $Id) | Select-Object -Unique
    @{ chats = $ids } | ConvertTo-Json -Depth 3 | Set-Content $AllowFile -Encoding UTF8
}

$AnyId = $false

$GroupId = Read-Host "  Group chat id (press Enter to skip)"
if ($GroupId -match '^-?\d+$') {
    Add-ChatId -Id ([long]$GroupId)
    Say-Ok "group $GroupId allowed"
    $AnyId = $true
} else {
    Say-Info "no group id - add one later with /allow <chat_id>"
}

$UserId = Read-Host "  Your user id for DM (press Enter to skip)"
if ($UserId -match '^-?\d+$') {
    Add-ChatId -Id ([long]$UserId)
    Say-Ok "user $UserId allowed"
    $AnyId = $true
} else {
    Say-Info "no user id - the first chat to message the bot becomes the owner"
}

Write-Host ""
if ($AnyId) { Say-Ok "allowed chats stored in $AllowFile" }
else { Say-Warn "no chats set - message the bot once, it locks you in as owner" }


Step "5/5" "Verifying"
$ToolCount = & $VEnvPy -c "from agent.tools import ALL_TOOLS; print(len(ALL_TOOLS))"
if ($LASTEXITCODE -ne 0) { Say-Err "agent import failed" }
Say-Ok "kibo importable - $ToolCount tools registered"


$KiboBinDir = Join-Path $HOME ".local\bin"
if (-not (Test-Path $KiboBinDir)) { New-Item -ItemType Directory -Force -Path $KiboBinDir | Out-Null }
$KiboExe = Join-Path $KiboBinDir "kibo.cmd"

$KiboCmd = @"
@echo off
setlocal
set "KIBO_HOME=%~dp0..\.."
if "%KIBO_PY%"=="" set "KIBO_PY=$VEnvPy"
if "%KIBO_HOME:~-1%"=="\\" set "KIBO_HOME=%KIBO_HOME:~0,-1%"
"%KIBO_PY%" "%~dp0..\..\agent\kibo_cli.py" %*
"@
Set-Content -Path $KiboExe -Value $KiboCmd -Encoding ASCII
Say-Ok "global command installed: kibo"

$ProfileDir = Split-Path -Parent $PROFILE
if (-not (Test-Path $ProfileDir)) { New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null }
$ProfileBody = if (Test-Path $PROFILE) { Get-Content $PROFILE -Raw } else { "" }
if ($ProfileBody -notmatch [regex]::Escape($KiboBinDir)) {
    Add-Content -Path $PROFILE -Value "`n`$env:PATH = `"$KiboBinDir;`$env:PATH`"" -Encoding UTF8
    Say-Ok "added $KiboBinDir to PATH in your PowerShell profile"
} else {
    Say-Ok "$KiboBinDir already on PATH"
}


Write-Host ""
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  Quick Start:" -ForegroundColor Green
Write-Host ""
Write-Host "    kibo help               show every command"
Write-Host "    kibo chat               interactive terminal chat"
Write-Host "    kibo web                browser UI on 127.0.0.1:5000"
Write-Host "    kibo telegram           telegram bot + widget"
Write-Host "    kibo status             what is running"
Write-Host ""
Write-Host "  Open a new PowerShell window first so kibo is on your PATH." -ForegroundColor DarkGray
Write-Host ""
