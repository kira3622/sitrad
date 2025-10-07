# Script de test pour vérifier la communication Android -> Backend
param(
    [string]$baseUrl = "https://sitrad-web.onrender.com"
)

Write-Host "=== Test de communication Android -> Backend ===" -ForegroundColor Green
Write-Host "URL du backend: $baseUrl" -ForegroundColor Cyan

# Test 1: Vérifier que le backend est accessible
Write-Host "`n1. Test de connectivité au backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -UseBasicParsing
    Write-Host "Backend accessible (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Erreur de connectivité: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Test d'authentification
Write-Host "`n2. Test d'authentification..." -ForegroundColor Yellow
$authBody = '{"username": "admin", "password": "admin123"}'

try {
    $authResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/token/" -Method POST -Body $authBody -ContentType "application/json"
    $token = $authResponse.access
    Write-Host "Authentification réussie" -ForegroundColor Green
    Write-Host "Token obtenu: $($token.Substring(0, 20))..." -ForegroundColor Cyan
    
    # Test 3: Test de l'endpoint chantiers
    Write-Host "`n3. Test de l'endpoint chantiers..." -ForegroundColor Yellow
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    $chantiersResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chantiers/" -Method GET -Headers $headers
    Write-Host "Endpoint chantiers accessible" -ForegroundColor Green
    Write-Host "Nombre de chantiers: $($chantiersResponse.Count)" -ForegroundColor Cyan
    
} catch {
    Write-Host "Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Lancer l'application Android
Write-Host "`n4. Test de l'application Android..." -ForegroundColor Yellow
try {
    adb shell am start -n com.sitrad.app/.MainActivity
    Write-Host "Application lancée sur l'émulateur" -ForegroundColor Green
    
    Start-Sleep -Seconds 3
    
    # Capturer les logs récents
    adb logcat -d | Out-File -FilePath "logcat_backend_test.txt" -Encoding UTF8
    Write-Host "Logs capturés dans logcat_backend_test.txt" -ForegroundColor Green
    
} catch {
    Write-Host "Erreur lors du lancement: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test terminé ===" -ForegroundColor Green