@echo off
echo ====================================================
echo RedNote Content Generator - Task Scheduler Setup
echo ====================================================
echo.
echo This will create a Windows Task to run daily at 17:00
echo.
pause

REM Get the current directory
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Create the scheduled task
schtasks /create /tn "RedNoteContentGenerator" /tr "python \"%SCRIPT_DIR%\run_daily_generation.py\"" /sc daily /st 17:00 /f

echo.
echo ====================================================
echo Task created successfully!
echo ====================================================
echo.
echo Task Name: RedNoteContentGenerator
echo Run Time: Daily at 17:00
echo Script Location: %SCRIPT_DIR%
echo.
echo You can manage this task in Task Scheduler (taskschd.msc)
echo.
pause
