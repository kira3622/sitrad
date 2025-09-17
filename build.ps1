# Script PowerShell pour Windows - Équivalent de build.sh
Write-Host "=== Début du script de construction ===" -ForegroundColor Green

# Installation des dépendances
Write-Host "Installation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de l'installation des dépendances" -ForegroundColor Red
    exit 1
}

# Vérification de l'installation Django
Write-Host "Vérification de l'installation Django..." -ForegroundColor Yellow
python -c "import django; print('Django version:', django.get_version())"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Django n'est pas installé correctement" -ForegroundColor Red
    exit 1
}

# Test de connexion à la base de données
Write-Host "Test de connexion à la base de données..." -ForegroundColor Yellow
python manage.py check --database default
if ($LASTEXITCODE -ne 0) {
    Write-Host "Problème de connexion à la base de données" -ForegroundColor Red
    exit 1
}

# Affichage de l'état des migrations
Write-Host "État actuel des migrations:" -ForegroundColor Yellow
python manage.py showmigrations

# Tentative 1: Migration normale
Write-Host "=== Tentative 1: Migration normale ===" -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration normale réussie!" -ForegroundColor Green
} else {
    Write-Host "Migration normale échouée, tentative avec --run-syncdb..." -ForegroundColor Yellow
    
    # Tentative 2: Migration avec --run-syncdb
    Write-Host "=== Tentative 2: Migration avec --run-syncdb ===" -ForegroundColor Cyan
    python manage.py migrate --run-syncdb
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Migration avec --run-syncdb réussie!" -ForegroundColor Green
    } else {
        Write-Host "Migration avec --run-syncdb échouée, migration séquentielle..." -ForegroundColor Yellow
        
        # Tentative 3: Migration séquentielle des apps
        Write-Host "=== Tentative 3: Migration séquentielle ===" -ForegroundColor Cyan
        
        # Apps core Django d'abord
        $coreApps = @("contenttypes", "auth", "admin", "sessions")
        foreach ($app in $coreApps) {
            Write-Host "Migration de l'app core: $app" -ForegroundColor Magenta
            python manage.py migrate $app
        }
        
        # Apps personnalisées ensuite
        $customApps = @("inventory", "stock", "customers", "orders", "production", "formulas", "logistics", "billing", "reports")
        foreach ($app in $customApps) {
            Write-Host "Migration de l'app personnalisée: $app" -ForegroundColor Magenta
            python manage.py migrate $app --run-syncdb
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Échec de migration pour $app, continuation..." -ForegroundColor Yellow
            }
        }
    }
}

# Collecte des fichiers statiques
Write-Host "Collecte des fichiers statiques..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "Avertissement: Problème lors de la collecte des fichiers statiques" -ForegroundColor Yellow
}

# Création du superuser si nécessaire
Write-Host "Vérification/Création du superuser..." -ForegroundColor Yellow
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser créé: admin/admin123')
else:
    print('Superuser existe déjà')
"

Write-Host "=== Script terminé avec succès ===" -ForegroundColor Green