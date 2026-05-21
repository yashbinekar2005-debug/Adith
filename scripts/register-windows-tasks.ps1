$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LauncherScript = Join-Path $PSScriptRoot "start-background.ps1"

$PowerShell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"

$Action = New-ScheduledTaskAction -Execute $PowerShell -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$LauncherScript`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

$OldTasks = @("AI News Agent - Ollama", "AI News Agent - Reporter")
foreach ($TaskName in $OldTasks) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
}

Register-ScheduledTask -TaskName "AI News Agent" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Start Ollama and the local AI news reporter at Windows login." -Force

Write-Host "Registered startup task: AI News Agent"
Write-Host "Project root: $ProjectRoot"
