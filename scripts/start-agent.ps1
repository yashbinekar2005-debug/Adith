$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Start-Sleep -Seconds 15

if (Test-Path ".venv\Scripts\python.exe") {
    $Python = ".venv\Scripts\python.exe"
} elseif (Test-Path "venv\Scripts\python.exe") {
    $Python = "venv\Scripts\python.exe"
} else {
    $Python = "python"
}

Start-Process -FilePath $Python -ArgumentList "main.py" -WorkingDirectory $ProjectRoot -WindowStyle Hidden
