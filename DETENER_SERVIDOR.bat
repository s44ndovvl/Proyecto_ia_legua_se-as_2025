@echo off
echo Deteniendo servidor Django...

REM Buscar y terminar procesos de Python relacionados con Django
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo table /nh ^| findstr manage.py') do (
    echo Terminando proceso %%i...
    taskkill /pid %%i /f
)

echo.
echo Servidor detenido.
echo Presiona cualquier tecla para cerrar...
pause >nul
