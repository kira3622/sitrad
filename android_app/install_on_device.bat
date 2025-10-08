@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo 📱 Installation BetonApp sur Appareil Android
echo ============================================================
echo.

echo 🔍 Vérification des appareils connectés...
adb devices
echo.

echo 📦 Vérification de l'APK...
if exist "app\build\outputs\apk\release\app-release.apk" (
    echo ✅ APK trouvé: app\build\outputs\apk\release\app-release.apk
    for %%A in ("app\build\outputs\apk\release\app-release.apk") do (
        echo    Taille: %%~zA bytes
        echo    Modifié: %%~tA
    )
) else (
    echo ❌ APK non trouvé! Construisez d'abord l'application avec:
    echo    gradlew.bat assembleRelease
    pause
    exit /b 1
)
echo.

echo 🚀 Installation de l'APK...
adb install -r "app\build\outputs\apk\release\app-release.apk"
if %ERRORLEVEL% EQU 0 (
    echo ✅ Installation réussie!
) else (
    echo ❌ Échec de l'installation
    echo.
    echo 💡 Solutions possibles:
    echo    1. Activez le débogage USB sur votre appareil
    echo    2. Autorisez les sources inconnues
    echo    3. Vérifiez que l'appareil est bien connecté
    pause
    exit /b 1
)
echo.

echo 📱 Lancement de l'application...
adb shell am start -n com.betonapp.android/.MainActivity
echo.

echo 🎯 Configuration requise dans l'application:
echo.
echo    URL API pour appareil physique:
echo    http://192.168.0.167:8000/api/v1
echo.
echo    Identifiants de test:
echo    Nom d'utilisateur: testuser
echo    Mot de passe: testpass123
echo.

echo 📋 Tests à effectuer:
echo    1. Configurer l'URL API
echo    2. Se connecter avec les identifiants
echo    3. Vérifier la liste des notifications (8 attendues)
echo    4. Tester les détails de notification
echo    5. Tester le marquage lue/non lue
echo.

echo 🔧 Débogage (optionnel):
echo    Pour voir les logs: adb logcat ^| findstr "BetonApp"
echo.

echo ✅ Installation terminée!
echo    L'application BetonApp devrait maintenant être visible sur votre appareil.
echo.
pause