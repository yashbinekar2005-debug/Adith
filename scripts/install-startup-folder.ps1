$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LauncherScript = Join-Path $PSScriptRoot "start-background.ps1"
$StartupFolder = [Environment]::GetFolderPath("Startup")
$StartupFile = Join-Path $StartupFolder "AI News Agent.cmd"

$Command = "@echo off`r`n"
$Command += "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$LauncherScript`"`r`n"

Set-Content -LiteralPath $StartupFile -Value $Command -Encoding ASCII

Write-Host "Installed startup launcher:"
Write-Host $StartupFile
Write-Host "It will start Ollama and the AI News Agent after Windows login."
