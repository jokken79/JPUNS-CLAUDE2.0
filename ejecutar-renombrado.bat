@echo off
REM Script para renombrar archivos de fábricas - UNS-ClaudeJP 2.0
cd /d %~dp0
python scripts\renombrar_fabricas.py
pause