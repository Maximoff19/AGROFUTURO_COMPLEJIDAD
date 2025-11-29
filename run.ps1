# Bootstraps and runs AgroFuturo on PowerShell (Windows/macOS/Linux).
# Uso:
#   .\run.ps1           # levanta backend en http://localhost:8000
#   .\run.ps1 frontend  # sirve frontend estático en http://localhost:8080

param(
  [ValidateSet("backend", "frontend")]
  [string]$mode = "backend"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root

$venvPath = Join-Path $root ".venv"
$reqFile = Join-Path $root "backend/requirements.txt"
$backendPort = if ($env:PORT) { $env:PORT } else { 8000 }
$frontendPort = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { 8080 }

function Find-Python {
  foreach ($name in @("python3", "python", "py")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Path }
  }
  return $null
}

$python = Find-Python
if (-not $python) {
  Write-Error "No se encontró python3/python/py en PATH."
  exit 1
}

if (-not (Test-Path $venvPath)) {
  & $python -m venv $venvPath
}

$venvPython = Join-Path $venvPath "Scripts/python.exe"
if (-not (Test-Path $venvPython)) {
  $venvPython = Join-Path $venvPath "bin/python"
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $reqFile

switch ($mode) {
  "frontend" {
    Set-Location (Join-Path $root "FRONTEND")
    Write-Host "Frontend en http://localhost:$frontendPort"
    & $venvPython -m http.server $frontendPort
  }
  default {
    Set-Location $root
    Write-Host "Backend en http://localhost:$backendPort (docs en /docs)"
    & $venvPython -m uvicorn backend.main:app --reload --port $backendPort
  }
}
