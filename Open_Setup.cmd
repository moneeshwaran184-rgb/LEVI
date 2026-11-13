@echo off
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Open-Setup.ps1"
if errorlevel 1 pause
