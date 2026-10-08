# Kibo - Windows installer
#
# Usage (PowerShell):
#   powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Dir

Write-Host ""
Write-Host "  KIBO - INSTALLER (Windows)" -ForegroundColor Cyan
Write-Host "  ----------------------------"
Write-Host ""


Write-Host "[1/4] Checking Python 3.9+..."
$py = $null
foreach ($cand in @("py -3", "python3", "python")) {
    try {
        $v = & $cand.Split(' ')[0] --version 2>$null
        if ($LASTEXITCODE -eq 0) { $py = $cand; break }
    } catch { }
}
if (-not $py) {
    Write-Host "  X Python not found. Install it from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "    (tick 'Add python.exe to PATH' during setup), then re-run this script."
    exit 1
}
Write-Host "  OK using: $py ($v)"


Write-Host "[2/4] Creating virtual environment..."
$VEnv = Join-Path $Dir ".venv"
$VEnvPy = Join-Path $VEnv "Scripts\python.exe"
if (-not (Test-Path $VEnvPy)) {
    & ($py.Split(' ')[0]) -m venv $VEnv
    Write-Host "  OK created $VEnv"
} else {
    Write-Host "  OK reusing existing venv"
}


Write-Host "[3/4] Installing dependencies..."
& $VEnvPy -m pip install --quiet --upgrade pip
& $VEnvPy -m pip install --quiet -e .
if ($LASTEXITCODE -ne 0) { Write-Host "  X pip install failed" -ForegroundColor Red; exit 1 }
Write-Host "  OK kibo package registered (editable)"


Write-Host "[3.5/4] Checking desktop widget support (tkinter)..."
& $VEnvPy -c "import tkinter" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK tkinter available"
} else {
    Write-Host "  ! tkinter missing - reinstall Python with 'tcl/tk' ticked for the widget" -ForegroundColor Yellow
}


Write-Host "[4/4] Verifying..."
$ToolCount = & $VEnvPy -c "from agent.tools import ALL_TOOLS; print(len(ALL_TOOLS))"
if ($LASTEXITCODE -ne 0) { Write-Host "  X agent import failed" -ForegroundColor Red; exit 1 }
Write-Host "  OK kibo importable - $ToolCount tools registered"

Write-Host ""
Write-Host "Done. Start it with:" -ForegroundColor Green
Write-Host "  $VEnvPy -m agent web      # chat UI in your browser"
Write-Host "  $VEnvPy -m agent          # interactive terminal chat"
Write-Host ""
