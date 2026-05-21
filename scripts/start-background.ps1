$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OllamaScript = Join-Path $PSScriptRoot "start-ollama.ps1"
$AgentScript = Join-Path $PSScriptRoot "start-agent.ps1"

# Start Ollama at login so the report can begin quickly. The Python agent
# will stop Ollama after the report is sent to free RAM.
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$OllamaScript`"" -WindowStyle Hidden
Start-Sleep -Seconds 20
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$AgentScript`"" -WindowStyle Hidden
