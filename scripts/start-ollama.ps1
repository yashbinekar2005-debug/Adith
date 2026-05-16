$ErrorActionPreference = "Stop"

Write-Host "Starting Ollama..."
$Existing = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($Existing) {
    Write-Host "Ollama is already running."
    exit 0
}

Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
