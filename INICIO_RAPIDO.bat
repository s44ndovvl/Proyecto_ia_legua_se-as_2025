@echo off
echo Iniciando Detector de Lenguaje de Señas...

REM Ir al directorio del proyecto
cd /d "%~dp0"

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Ir a Django
cd django_app

REM Abrir navegador
start http://127.0.0.1:8000

REM Iniciar servidor
python manage.py runserver
