# Kibo - Windows installer
#
# Usage (PowerShell):
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Model qwen2.5-3b
param(
    [string]$Model = ""
)
$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Dir

function Say-Ok   { param([string]$m) Write-Host "  OK $m" -ForegroundColor Green }
function Say-Warn { param([string]$m) Write-Host "  ! $m" -ForegroundColor Yellow }
function Say-Err  { param([string]$m) Write-Host "  X $m" -ForegroundColor Red; exit 1 }
function Say-Info { param([string]$m) Write-Host "  - $m" -ForegroundColor DarkGray }
function Step     { param([string]$n, [string]$m) Write-Host ""; Write-Host "[$n] $m" -ForegroundColor Cyan; Write-Host "  ------------" -ForegroundColor DarkGray }

function Set-ActiveModel {
    param([string]$Key)
    @{ active_model = $Key } | ConvertTo-Json |
        Set-Content (Join-Path $HOME ".agent_model_config.json") -Encoding UTF8
}

function Download-Gguf {
    param([string]$Key, [string]$Repo, [string]$File, [string]$Label, [string]$Size)
    $dir = Join-Path $HOME ".agent_models\$Key"
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $path = Join-Path $dir $File
    if (Test-Path $path) { Say-Ok "$Label already downloaded"; return }
    $url = "https://huggingface.co/$Repo/resolve/main/$File"
    $tmp = "$path.part"
    Say-Info "Downloading $Label ($Size) - this may take a few minutes..."
    try {
        if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
            & curl.exe -L --fail -o $tmp $url
            if ($LASTEXITCODE -ne 0) { throw "curl exited $LASTEXITCODE" }
        } else {
            Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
        }
        Move-Item -Force $tmp $path
        Say-Ok "$Label downloaded"
    } catch {
        if (Test-Path $tmp) { Remove-Item -Force $tmp }
        Say-Warn "$Label download failed: $_"
    }
}




function Select-KiboModel {
    if ($Model) {
        $key = $Model.ToLower()
        switch -Regex ($key) {
            '^(needle|needle2|n)$'                         { return 1 }
            '^(gemma|functiongemma|fg|google|func)$'       { return 2 }
            '^both$'                                       { return 3 }
            '^(qwen|qwen3|qwen3-0\.6b|qwen-0\.6b|qwen0\.6b)$' { return 4 }
            '^(qwen2\.5-1\.5b|qwen1\.5b|qwen-1\.5b)$'      { return 5 }
            '^(qwen2\.5-3b|qwen3b|qwen-3b)$'               { return 6 }
            '^(gemma3|gemma3-1b|gemma-3-1b|gemma-1b|g3-1b)$' { return 7 }
            '^(gemma3-4b|gemma-3-4b|gemma-4b|g3-4b)$'      { return 8 }
            '^all$'                                        { return 9 }
            default { Say-Warn "Unknown -Model '$Model', using default Needle"; return 1 }
        }
    }



    Write-Host ""
    Write-Host "  Choose your AI model:" -ForegroundColor White
    Write-Host "  ---------------------" -ForegroundColor DarkGray
    Write-Host "    [1] Needle 2        14 MB    Fast, lightweight"
    Write-Host "    [2] FunctionGemma   253 MB   Smarter reasoning" -ForegroundColor DarkGray
    Write-Host "    [3] Needle + Gemma  267 MB   Switch anytime"
    Write-Host "    [4] Qwen3 0.6B      397 MB   32k context"
    Write-Host "    [5] Qwen2.5 1.5B    1.1 GB   Balanced"
    Write-Host "    [6] Qwen2.5 3B      2.1 GB   Most capable Qwen"
    Write-Host "    [7] Gemma 3 1B      806 MB   128k context"
    Write-Host "    [8] Gemma 3 4B      2.5 GB   Most capable"
    Write-Host "    [9] Download all    ~9 GB    Everything"
    Write-Host ""
    $choice = Read-Host "  Enter 1-9 [default: 1]"
    if ([string]::IsNullOrWhiteSpace($choice)) { return 1 }
    if ($choice -notmatch '^\d+$') { Say-Warn "Invalid choice, using default Needle"; return 1 }
    return [int]$choice
}

function Install-KiboModels {
    param([int]$Choice)
    $env:PYTHONWARNINGS = "ignore"
    $downloads = @{
        4  = @{ Key="qwen3-0.6b";  Repo="unsloth/Qwen3-0.6B-GGUF";               File="Qwen3-0.6B-Q4_K_M.gguf";          Label="Qwen3 0.6B";   Size="397 MB" }
        5  = @{ Key="qwen2.5-1.5b"; Repo="Qwen/Qwen2.5-1.5B-Instruct-GGUF";      File="qwen2.5-1.5b-instruct-q4_k_m.gguf"; Label="Qwen2.5 1.5B"; Size="1.1 GB" }
        6  = @{ Key="qwen2.5-3b";  Repo="Qwen/Qwen2.5-3B-Instruct-GGUF";         File="qwen2.5-3b-instruct-q4_k_m.gguf"; Label="Qwen2.5 3B";   Size="2.1 GB" }
        7  = @{ Key="gemma3-1b";   Repo="unsloth/gemma-3-1b-it-GGUF";            File="gemma-3-1b-it-Q4_K_M.gguf";       Label="Gemma 3 1B";   Size="806 MB" }
        8  = @{ Key="gemma3-4b";   Repo="unsloth/gemma-3-4b-it-GGUF";            File="gemma-3-4b-it-Q4_K_M.gguf";       Label="Gemma 3 4B";   Size="2.5 GB" }
    }
    $funcGemma = @{ Key="functiongemma"; Repo="unsloth/functiongemma-270m-it-GGUF"; File="functiongemma-270m-it-Q4_K_M.gguf"; Label="FunctionGemma 270M"; Size="253 MB" }

    $needle = {
        & $VEnvPy -c "import needle" 2>$null
        if ($LASTEXITCODE -eq 0) { Say-Ok "Needle engine ready" } else { Say-Warn "Needle not found" }
    }
    $llamaCpp = {
        & $VEnvPy -m pip install --quiet llama-cpp-python 2>$null
        if ($LASTEXITCODE -eq 0) { Say-Ok "llama-cpp-python installed" } else { Say-Warn "llama-cpp-python install failed" }
    }
    $download = { param($spec) Download-Gguf $spec.Key $spec.Repo $spec.File $spec.Label $spec.Size }

    switch ($Choice) {
        1 { & $needle; Set-ActiveModel "needle"; Say-Ok "Default model: Needle 2" }
        2 { & $download $funcGemma; & $llamaCpp; Set-ActiveModel "functiongemma"; Say-Ok "Default model: FunctionGemma" }
        3 { & $needle; & $download $funcGemma; & $llamaCpp; Set-ActiveModel "needle"; Say-Ok "Default model: Needle 2"; Say-Info "Type 'gemma' to switch to FunctionGemma" }
        4 { & $llamaCpp; & $download $downloads[4]; Set-ActiveModel "qwen3-0.6b"; Say-Ok "Default model: Qwen3 0.6B" }
        5 { & $llamaCpp; & $download $downloads[5]; Set-ActiveModel "qwen2.5-1.5b"; Say-Ok "Default model: Qwen2.5 1.5B" }
        6 { & $llamaCpp; & $download $downloads[6]; Set-ActiveModel "qwen2.5-3b"; Say-Ok "Default model: Qwen2.5 3B" }
        7 { & $llamaCpp; & $download $downloads[7]; Set-ActiveModel "gemma3-1b"; Say-Ok "Default model: Gemma 3 1B" }
        8 { & $llamaCpp; & $download $downloads[8]; Set-ActiveModel "gemma3-4b"; Say-Ok "Default model: Gemma 3 4B" }
        9 {
            & $needle; & $llamaCpp
            & $download $funcGemma
            4,5,6,7,8 | ForEach-Object { & $download $downloads[$_] }
            Set-ActiveModel "needle"; Say-Ok "Default model: Needle 2"
            Say-Info "Type 'models' to see and switch between all downloaded models"
        }
        default { & $needle; & $download $funcGemma; & $llamaCpp; Set-ActiveModel "needle" }
    }
}


Write-Host ""
Write-Host "  KIBO - INSTALLER (Windows)" -ForegroundColor Cyan
Write-Host "  ----------------------------"
Write-Host ""


Step "1/6" "Checking Python 3.9+"
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


Step "2/6" "Creating virtual environment"
$VEnv = Join-Path $Dir ".venv"
$VEnvPy = Join-Path $VEnv "Scripts\python.exe"
if (-not (Test-Path $VEnvPy)) {
    & $Py -m venv $VEnv
    if ($LASTEXITCODE -ne 0) { Say-Err "Could not create the virtual environment" }
    Say-Ok "created $VEnv"
} else {
    Say-Ok "reusing existing venv"
}


Step "3/6" "Installing dependencies"
& $VEnvPy -m pip install --quiet --upgrade pip
& $VEnvPy -m pip install --quiet -e .
if ($LASTEXITCODE -ne 0) { Say-Err "pip install failed" }
Say-Ok "kibo package registered (editable)"

& $VEnvPy -c "import tkinter" 2>$null
if ($LASTEXITCODE -eq 0) { Say-Ok "tkinter available (widget supported)" }
else { Say-Warn "tkinter missing - widget unavailable, reinstall Python with 'tcl/tk' ticked" }


Step "4/6" "AI Model Selection"
$ModelChoice = Select-KiboModel
Install-KiboModels -Choice $ModelChoice


Step "5/6" "Telegram Chats"
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


Step "6/6" "Verifying"
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
