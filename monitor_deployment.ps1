param (
    [string]$subdomain
)

# Script de surveillance du déploiement Render
$baseUrl = "https://$subdomain.onrender.com"
$maxAttempts = 10
$waitTime = 30  # secondes entre chaque tentative

Write-Host "=== SURVEILLANCE DU DÉPLOIEMENT RENDER ===" -ForegroundColor Green
Write-Host "Vérification de l'endpoint chantiers toutes les $waitTime secondes..." -ForegroundColor Yellow

for ($i = 1; $i -le $maxAttempts; $i++) {
    Write-Host "`nTentative $i/$maxAttempts..." -ForegroundColor Cyan
    
    try {
        # Test d'authentification
        $loginData = @{
            username = "admin"
            password = "admin123"
        } | ConvertTo-Json
        
        $authResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/token/" -Method POST -Body $loginData -ContentType "application/json" -ErrorAction Stop
        $token = $authResponse.access
        Write-Host "✅ Authentification réussie" -ForegroundColor Green
        
        # Vérification de l'index API
        $indexResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/" -Headers @{Authorization="Bearer $token"} -ErrorAction Stop
        $endpoints = $indexResponse.PSObject.Properties.Name | Sort-Object
        
        Write-Host "Endpoints disponibles: $($endpoints -join ', ')" -ForegroundColor Yellow
        
        # Vérification spécifique de l'endpoint chantiers
        if ($endpoints -contains "chantiers") {
            Write-Host "🎉 SUCCÈS! L'endpoint chantiers est maintenant disponible!" -ForegroundColor Green
            
            # Test de l'endpoint chantiers
            try {
                $chantiersResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chantiers/" -Headers @{Authorization="Bearer $token"} -ErrorAction Stop
                $count = $chantiersResponse.Count
                Write-Host "✅ Endpoint chantiers fonctionnel - $count chantiers trouvés" -ForegroundColor Green
                
                # Test du filtrage
                $filteredResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chantiers/?client=1" -Headers @{Authorization="Bearer $token"} -ErrorAction Stop
                $filteredCount = $filteredResponse.Count
                Write-Host "✅ Filtrage par client fonctionnel - $filteredCount chantiers pour le client 1" -ForegroundColor Green
                
                Write-Host "`n🚀 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!" -ForegroundColor Green
                exit 0
            }
            catch {
                Write-Host "⚠️ Endpoint chantiers trouvé mais non fonctionnel: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "❌ Endpoint chantiers non trouvé. Déploiement en cours..." -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Erreur de connexion: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    if ($i -lt $maxAttempts) {
        Write-Host "Attente de $waitTime secondes avant la prochaine tentative..." -ForegroundColor Gray
        Start-Sleep -Seconds $waitTime
    }
}

Write-Host "`n⏰ Temps d'attente dépassé. Le déploiement peut prendre plus de temps." -ForegroundColor Yellow
Write-Host "Vous pouvez relancer ce script ou vérifier manuellement." -ForegroundColor Yellow