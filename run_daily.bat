@echo off
REM RedNote Content Generator - Daily Run Script
REM This batch file is called by Windows Task Scheduler

cd /d "%~dp0"
python run_daily_generation.py
