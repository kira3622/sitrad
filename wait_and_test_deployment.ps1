# Script de surveillance du deploiement Render - API Chantiers
# Attend que le deploiement soit termine et teste l'endpoint

$maxAttempts = 15
$waitTime = 30
$attempt = 1

$headers = @{
    'Content-Type' = 'application/json'
}

$loginData = @{
    username = 'admin'
    password = 'admin123'
} | ConvertTo-Json

Write-Host "=== SURVEILLANCE DU DEPLOIEMENT RENDER ===" -ForegroundColor Cyan
Write-Host "Attente du deploiement de la correction ChantierViewSet..." -ForegroundColor Yellow
Write-Host "Tentatives max: $maxAttempts | Intervalle: $waitTime secondes" -ForegroundColor Gray

while ($attempt -le $maxAttempts) {
    Write-Host ""
    Write-Host "--- Tentative $attempt/$maxAttempts ---" -ForegroundColor White
    
    try {
        # Test d'authentification
        Write-Host "Authentification..." -NoNewline
        $authResponse = Invoke-RestMethod -Uri "https://sitrad-web.onrender.com/api/v1/auth/token/" -Method POST -Body $loginData -Headers $headers -TimeoutSec 30
        $token = $authResponse.access
        Write-Host " OK" -ForegroundColor Green
        
        # Headers avec token
        $authHeaders = @{
            'Content-Type' = 'application/json'
            'Authorization' = "Bearer $token"
        }
        
        # Test de l'index API
        Write-Host "Verification index API..." -NoNewline
        $indexResponse = Invoke-RestMethod -Uri "https://sitrad-web.onrender.com/api/v1/" -Method GET -Headers $authHeaders -TimeoutSec 30
        Write-Host " OK" -ForegroundColor Green
        
        # Verification de la presence de l'endpoint chantiers
        if ($indexResponse -match "chantiers") {
            Write-Host "Endpoint 'chantiers' trouve!" -ForegroundColor Green
            
            # Test de l'endpoint chantiers
            Write-Host "Test endpoint chantiers..." -NoNewline
            $chantiersResponse = Invoke-RestMethod -Uri "https://sitrad-web.onrender.com/api/v1/chantiers/" -Method GET -Headers $authHeaders -TimeoutSec 30
            $count = $chantiersResponse.count
            Write-Host " OK" -ForegroundColor Green
            
            Write-Host ""
            Write-Host "DEPLOIEMENT REUSSI!" -ForegroundColor Green -BackgroundColor Black
            Write-Host "API Chantiers accessible" -ForegroundColor Green
            Write-Host "Nombre de chantiers: $count" -ForegroundColor Green
            Write-Host "URL: https://sitrad-web.onrender.com/api/v1/chantiers/" -ForegroundColor Green
            
            # Test de filtrage
            Write-Host ""
            Write-Host "Test de filtrage par client..." -ForegroundColor Yellow
            try {
                $filteredResponse = Invoke-RestMethod -Uri "https://sitrad-web.onrender.com/api/v1/chantiers/?client=1" -Method GET -Headers $authHeaders -TimeoutSec 30
                $filteredCount = $filteredResponse.count
                Write-Host "Filtrage fonctionnel - Chantiers pour client 1: $filteredCount" -ForegroundColor Green
            } catch {
                Write-Host "Filtrage non teste: $($_.Exception.Message)" -ForegroundColor Yellow
            }
            
            exit 0
        } else {
            Write-Host "Endpoint 'chantiers' non trouve dans l'index" -ForegroundColor Red
        }
        
    } catch {
        Write-Host " Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    if ($attempt -lt $maxAttempts) {
        Write-Host "Attente de $waitTime secondes avant la prochaine tentative..." -ForegroundColor Gray
        Start-Sleep -Seconds $waitTime
    }
    
    $attempt++
}

Write-Host ""
Write-Host "ECHEC DU DEPLOIEMENT" -ForegroundColor Red -BackgroundColor Black
Write-Host "L'endpoint chantiers n'est toujours pas accessible apres $maxAttempts tentatives." -ForegroundColor Red
Write-Host "Verifiez les logs de deploiement sur Render." -ForegroundColor Yellow
exit 1