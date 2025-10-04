@echo off
echo Testing Android project dependencies...
echo.

echo Checking if gradlew exists...
if exist gradlew.bat (
    echo ✓ gradlew.bat found
) else (
    echo ✗ gradlew.bat not found
    exit /b 1
)

echo.
echo Attempting to resolve dependencies...
echo This will download dependencies and check for conflicts...
echo.

REM Try to run dependency resolution
gradlew.bat app:dependencies --configuration debugCompileClasspath

echo.
echo Dependency test completed.
echo If you see MPAndroidChart in the dependency tree above, the fix worked!
echo.
pause