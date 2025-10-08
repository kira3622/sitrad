@echo off
echo ============================================================
echo BetonApp - Installation et Test Android
echo ============================================================
echo.

echo 📱 Verification des appareils Android connectes...
adb devices

echo.
echo 🔧 Construction de l'application...
call gradlew.bat assembleDebug

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de la construction
    pause
    exit /b 1
)

echo.
echo ✅ Construction reussie!
echo 📦 APK genere: app\build\outputs\apk\debug\app-debug.apk

echo.
echo 📱 Tentative d'installation sur l'appareil...
adb install -r app\build\outputs\apk\debug\app-debug.apk

if %ERRORLEVEL% EQU 0 (
    echo ✅ Installation reussie!
    echo.
    echo 🚀 Lancement de l'application...
    adb shell am start -n com.betonapp.notifications/.MainActivity
    
    echo.
    echo 📋 Capture des logs de l'application...
    echo Appuyez sur Ctrl+C pour arreter la capture des logs
    adb logcat | findstr "BetonApp\|com.betonapp"
) else (
    echo ⚠️ Aucun appareil connecte ou erreur d'installation
    echo.
    echo 📁 L'APK est disponible ici:
    echo    %CD%\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo 📋 Instructions d'installation manuelle:
    echo 1. Copiez l'APK sur votre appareil Android
    echo 2. Activez "Sources inconnues" dans les parametres
    echo 3. Installez l'APK
    echo 4. Configurez l'URL de l'API: http://[VOTRE_IP]:8000/api/v1
)

echo.
echo 🔧 Test de l'API locale...
python comprehensive_api_test.py

echo.
echo ============================================================
echo Installation et test termines
echo ============================================================
pause