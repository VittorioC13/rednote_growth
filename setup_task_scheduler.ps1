# PowerShell script to setup Windows Task Scheduler
# Run this with administrator privileges

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptPath "run_daily_generation.py"

$action = New-ScheduledTaskAction -Execute "python" -Argument "`"$pythonScript`"" -WorkingDirectory $scriptPath
$trigger = New-ScheduledTaskTrigger -Daily -At "17:00"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Write-Host "Creating scheduled task: RedNoteContentGenerator" -ForegroundColor Green
Write-Host "Script path: $pythonScript" -ForegroundColor Yellow
Write-Host "Run time: Daily at 17:00" -ForegroundColor Yellow

try {
    Register-ScheduledTask -TaskName "RedNoteContentGenerator" -Action $action -Trigger $trigger -Settings $settings -Force
    Write-Host "`nTask created successfully!" -ForegroundColor Green
    Write-Host "You can view it in Task Scheduler (taskschd.msc)" -ForegroundColor Cyan
} catch {
    Write-Host "`nError creating task: $_" -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
