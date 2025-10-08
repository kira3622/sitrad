@echo off
echo ============================================================
echo Configuration IP pour Test Android
echo ============================================================
echo.

echo 🌐 Adresses IP de cette machine:
ipconfig | findstr "IPv4"

echo.
echo 📱 Configuration pour l'application Android:
echo.
echo Pour EMULATEUR Android:
echo   URL API: http://10.0.2.2:8000/api/v1
echo.
echo Pour APPAREIL PHYSIQUE:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr /v "127.0.0.1"') do (
    set ip=%%a
    set ip=!ip: =!
    echo   URL API: http://!ip!:8000/api/v1
)

echo.
echo 🔧 Identifiants de test:
echo   Nom d'utilisateur: testuser
echo   Mot de passe: testpass123
echo.

echo 📋 Instructions:
echo 1. Installez l'APK: app\build\outputs\apk\debug\app-debug.apk
echo 2. Configurez l'URL API dans l'application
echo 3. Connectez-vous avec les identifiants de test
echo 4. Testez les notifications
echo.

echo ⚠️ Assurez-vous que:
echo - L'API locale fonctionne (python manage.py runserver)
echo - Le pare-feu Windows autorise le port 8000
echo - L'appareil Android est sur le même réseau WiFi
echo.

pause