@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0docker-dev.ps1" %*
