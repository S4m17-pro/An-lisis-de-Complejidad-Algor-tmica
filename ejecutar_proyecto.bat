@echo off
TITLE Analizador de Complejidad Algoritmica
echo ==========================================
echo   Iniciando Proyecto con Entorno Virtual
echo ==========================================
echo.
if exist .venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe main.py
) else (
    echo [ERROR] No se encontro el entorno virtual en la carpeta .venv
    echo Por favor, asegurese de estar en la carpeta correcta.
    pause
)
