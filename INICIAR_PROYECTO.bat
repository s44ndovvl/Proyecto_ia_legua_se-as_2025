@echo off
echo ========================================
echo   DETECTOR DE LENGUAJE DE SEÑAS
echo   Iniciando proyecto automaticamente...
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Verificar si existe el entorno virtual
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    echo.
)

REM Activar entorno virtual
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Cambiar al directorio de Django
cd django_app

REM Instalar dependencias si es necesario
echo Verificando dependencias...
pip install -r requirements.txt --quiet

REM Hacer migraciones si es necesario
echo Preparando base de datos...
python manage.py makemigrations --verbosity=0
python manage.py migrate --verbosity=0

echo.
echo ========================================
echo   SERVIDOR INICIADO CORRECTAMENTE
echo   Abriendo navegador en 3 segundos...
echo   Presiona Ctrl+C para detener
echo ========================================
echo.

REM Abrir navegador después de 3 segundos
timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000

REM Iniciar servidor Django
python manage.py runserver
