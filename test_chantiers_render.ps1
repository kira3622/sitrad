# Test final de l'API des chantiers sur Render après correction
$baseUrl = "https://sitrad-web.onrender.com"

Write-Host "=== TEST FINAL API CHANTIERS SUR RENDER ===" -ForegroundColor Green
Write-Host "URL de base: $baseUrl" -ForegroundColor Yellow

try {
    # 1. Authentification
    Write-Host "`n1. Test d'authentification..." -ForegroundColor Cyan
    $loginData = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json
    
    $authResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/token/" -Method POST -Body $loginData -ContentType "application/json"
    $token = $authResponse.access
    Write-Host "✅ Authentification réussie" -ForegroundColor Green
    
    # 2. Test de l'index API
    Write-Host "`n2. Test de l'index API..." -ForegroundColor Cyan
    $indexResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/" -Headers @{Authorization="Bearer $token"}
    Write-Host "✅ Index API accessible" -ForegroundColor Green
    
    # 3. Vérification de la présence de l'endpoint chantiers
    Write-Host "`n3. Vérification de l'endpoint chantiers dans l'index..." -ForegroundColor Cyan
    if ($indexResponse.chantiers) {
        Write-Host "✅ Endpoint chantiers trouvé dans l'index: $($indexResponse.chantiers)" -ForegroundColor Green
    } else {
        Write-Host "❌ Endpoint chantiers non trouvé dans l'index" -ForegroundColor Red
        Write-Host "Endpoints disponibles:" -ForegroundColor Yellow
        $indexResponse | ConvertTo-Json -Depth 2
    }
    
    # 4. Test direct de l'endpoint chantiers
    Write-Host "`n4. Test direct de l'endpoint chantiers..." -ForegroundColor Cyan
    try {
        $chantiersResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chantiers/" -Headers @{Authorization="Bearer $token"}
        $count = $chantiersResponse.Count
        Write-Host "✅ Endpoint chantiers accessible - $count chantiers trouvés" -ForegroundColor Green
        
        if ($count -gt 0) {
            Write-Host "`nPremier chantier:" -ForegroundColor Yellow
            $chantiersResponse[0] | ConvertTo-Json -Depth 2
        }
    }
    catch {
        Write-Host "❌ Erreur lors de l'accès à l'endpoint chantiers: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "Code de statut: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
    }
    
    # 5. Test avec filtrage par client
    Write-Host "`n5. Test de filtrage par client..." -ForegroundColor Cyan
    try {
        $filteredResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chantiers/?client=1" -Headers @{Authorization="Bearer $token"}
        $filteredCount = $filteredResponse.Count
        Write-Host "✅ Filtrage par client fonctionnel - $filteredCount chantiers pour le client 1" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Erreur lors du filtrage: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`n🎉 TEST TERMINÉ" -ForegroundColor Green
}
catch {
    Write-Host "❌ Erreur générale: $($_.Exception.Message)" -ForegroundColor Red
}