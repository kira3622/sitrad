@echo off
echo ===================================
echo Nettoyage du cache Gradle
echo ===================================

echo 1. Arret du daemon Gradle...
call gradlew.bat --stop

echo 2. Suppression du cache de dependances...
rmdir /s /q %USERPROFILE%\.gradle\caches

echo 3. Nettoyage du projet...
call gradlew.bat clean

echo ===================================
echo Nettoyage termine!
echo Vous pouvez maintenant executer 'gradlew.bat build'
echo ===================================