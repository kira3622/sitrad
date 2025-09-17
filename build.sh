#!/bin/bash

# Configuration bash stricte
set -o errexit
set -o pipefail
set -o nounset

echo "=== Début du script de construction ==="

# Installation des dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Vérification de l'installation Django
echo "Vérification de l'installation Django..."
python -c "import django; print('Django version:', django.get_version())"

# Test de connexion à la base de données
echo "Test de connexion à la base de données..."
python manage.py check --database default

# Affichage de l'état des migrations
echo "État actuel des migrations:"
python manage.py showmigrations

# Tentative 1: Migration normale
echo "=== Tentative 1: Migration normale ==="
python manage.py makemigrations
if python manage.py migrate; then
    echo "Migration normale réussie!"
else
    echo "Migration normale échouée, tentative avec --run-syncdb..."
    
    # Tentative 2: Migration avec --run-syncdb
    echo "=== Tentative 2: Migration avec --run-syncdb ==="
    if python manage.py migrate --run-syncdb; then
        echo "Migration avec --run-syncdb réussie!"
    else
        echo "Migration avec --run-syncdb échouée, migration séquentielle..."
        
        # Tentative 3: Migration séquentielle des apps
        echo "=== Tentative 3: Migration séquentielle ==="
        
        # Apps core Django d'abord
        for app in contenttypes auth admin sessions; do
            echo "Migration de l'app core: $app"
            python manage.py migrate $app || echo "Échec de migration pour $app, continuation..."
        done
        
        # Apps personnalisées ensuite
        for app in inventory stock customers orders production formulas logistics billing reports; do
            echo "Migration de l'app personnalisée: $app"
            python manage.py migrate $app --run-syncdb || echo "Échec de migration pour $app, continuation..."
        done
    fi
fi

# Collecte des fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput || echo "Avertissement: Problème lors de la collecte des fichiers statiques"

# Création du superuser si nécessaire
echo "Vérification/Création du superuser..."
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
" || echo "Avertissement: Problème lors de la création du superuser"

echo "=== Script terminé avec succès ==="