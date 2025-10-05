# Script PowerShell pour tester l'API des formules
Write-Host "=== Test de l'API Sitrad ===" -ForegroundColor Green

# Configuration
$baseUrl = "https://sitrad-web.onrender.com/api/v1"
$username = Read-Host "Entrez votre nom d'utilisateur"
$password = Read-Host "Entrez votre mot de passe" -AsSecureString
$passwordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

Write-Host "`n1. Test de l'endpoint d'authentification..." -ForegroundColor Yellow

# Préparer les données d'authentification
$authData = @{
    username = $username
    password = $passwordText
} | ConvertTo-Json

try {
    # Obtenir le token JWT
    $authResponse = Invoke-WebRequest -Uri "$baseUrl/auth/token/" -Method POST -Body $authData -ContentType "application/json" -UseBasicParsing
    $authResult = $authResponse.Content | ConvertFrom-Json
    $token = $authResult.access
    
    Write-Host "✅ Authentification réussie!" -ForegroundColor Green
    Write-Host "Token obtenu: $($token.Substring(0,20))..." -ForegroundColor Gray
    
    Write-Host "`n2. Test de l'index API..." -ForegroundColor Yellow
    
    # Tester l'index de l'API avec le token
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $indexResponse = Invoke-WebRequest -Uri "$baseUrl/" -Headers $headers -UseBasicParsing
    Write-Host "✅ Index API accessible!" -ForegroundColor Green
    Write-Host "Contenu de l'index:" -ForegroundColor Gray
    Write-Host $indexResponse.Content
    
    Write-Host "`n3. Test de l'endpoint formules..." -ForegroundColor Yellow
    
    # Tester l'endpoint formules
    $formulesResponse = Invoke-WebRequest -Uri "$baseUrl/formules/" -Headers $headers -UseBasicParsing
    Write-Host "✅ Endpoint formules accessible!" -ForegroundColor Green
    Write-Host "Réponse formules:" -ForegroundColor Gray
    $formulesData = $formulesResponse.Content | ConvertFrom-Json
    Write-Host "Nombre de formules trouvées: $($formulesData.count)" -ForegroundColor Cyan
    
    if ($formulesData.results.Count -gt 0) {
        Write-Host "Formules disponibles:" -ForegroundColor Cyan
        foreach ($formule in $formulesData.results) {
            Write-Host "  - $($formule.nom): $($formule.description)" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️  Aucune formule trouvée dans la base de données" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Code de statut: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "`n=== Test terminé ===" -ForegroundColor Green