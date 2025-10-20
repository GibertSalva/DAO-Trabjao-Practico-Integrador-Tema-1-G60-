@echo off
echo ========================================
echo ACTUALIZANDO MODELO TORNEO
echo ========================================
echo.

echo Paso 1: Creando migraciones...
python manage.py makemigrations
echo.

echo Paso 2: Aplicando migraciones...
python manage.py migrate
echo.

echo ========================================
echo ACTUALIZACION COMPLETADA
echo ========================================
echo.
echo Ahora puedes iniciar el servidor con:
echo python manage.py runserver
echo.
pause
