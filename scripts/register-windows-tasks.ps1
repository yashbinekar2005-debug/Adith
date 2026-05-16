$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OllamaScript = Join-Path $PSScriptRoot "start-ollama.ps1"
$AgentScript = Join-Path $PSScriptRoot "start-agent.ps1"

$PowerShell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"

$OllamaAction = New-ScheduledTaskAction -Execute $PowerShell -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$OllamaScript`""
$AgentAction = New-ScheduledTaskAction -Execute $PowerShell -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$AgentScript`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "AI News Agent - Ollama" -Action $OllamaAction -Trigger $Trigger -Settings $Settings -Description "Start Ollama for local AI news agent." -Force
Register-ScheduledTask -TaskName "AI News Agent - Reporter" -Action $AgentAction -Trigger $Trigger -Settings $Settings -Description "Start local AI news reporter agent." -Force

Write-Host "Registered startup tasks for Ollama and AI News Agent."
Write-Host "Project root: $ProjectRoot"
