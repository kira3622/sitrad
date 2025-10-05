# Script pour tester l'API locale avec authentification
Write-Host "Test de l'authentification locale..."

# Etape 1: Authentification
$authBody = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    $authResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/auth/token/" -Method POST -Body $authBody -ContentType "application/json"
    $authData = $authResponse.Content | ConvertFrom-Json
    $token = $authData.access
    Write-Host "Authentification reussie!"
    
    # Etape 2: Test de l'index API avec token
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    Write-Host "Test de l'index API local..."
    $indexResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/" -Method GET -Headers $headers
    Write-Host "Index API local accessible!"
    Write-Host "Contenu de l'index local:"
    Write-Host $indexResponse.Content
    
    # Etape 3: Test de l'endpoint formules
    Write-Host "Test de l'endpoint /formules/ local..."
    try {
        $formulesResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/formules/" -Method GET -Headers $headers
        Write-Host "Endpoint /formules/ accessible en local!"
        Write-Host "Statut: $($formulesResponse.StatusCode)"
        Write-Host "Contenu: $($formulesResponse.Content)"
    } catch {
        Write-Host "Erreur sur l'endpoint /formules/ local:"
        Write-Host "Statut: $($_.Exception.Response.StatusCode)"
        Write-Host "Message: $($_.Exception.Message)"
    }
    
} catch {
    Write-Host "Erreur d'authentification locale:"
    Write-Host $_.Exception.Message
}