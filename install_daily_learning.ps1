$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonw = Join-Path $projectRoot ".venv\Scripts\pythonw.exe"
if (-not (Test-Path $pythonw)) {
    $pythonw = (Get-Command pythonw.exe -ErrorAction Stop).Source
}

$scriptPath = Join-Path $projectRoot "daily_learning.py"
$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$scriptPath`"" -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
Register-ScheduledTask -TaskName "PythonDailyLearning" -Action $action -Trigger $trigger -Description "Shows the daily Python learning step" -Force

Write-Host "Done. The notification will appear when you sign in to Windows."
Write-Host "Test it with: python daily_learning.py"
