#!/usr/bin/env bash
# Script de build pour Render - Version robuste
set -o errexit  # Exit on any error

echo "🚀 Début du build Render..."

# Mise à jour de pip
echo "🔄 Mise à jour de pip..."
python -m pip install --upgrade pip

# Installation des dépendances
echo "🔄 Installation des dépendances..."
pip install -r requirements.txt

# Vérification de Django
echo "🔄 Vérification de Django..."
python -c "import django; print(f'Django version: {django.get_version()}')"

# Test de la configuration Django
echo "🔄 Test de la configuration Django..."
python manage.py check --deploy

# Attendre que la DB soit prête (pour PostgreSQL sur Render)
echo "🔄 Attente de la base de données..."
python -c "
import os
import time
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()
from django.db import connection
from django.core.management.color import no_style
style = no_style()

max_attempts = 30
for attempt in range(max_attempts):
    try:
        connection.ensure_connection()
        print('✅ Base de données prête')
        break
    except Exception as e:
        if attempt < max_attempts - 1:
            print(f'⏳ Tentative {attempt + 1}/{max_attempts} - Attente DB...')
            time.sleep(2)
        else:
            print(f'❌ Impossible de se connecter à la DB: {e}')
            raise
"

# Exécution des migrations
echo "🔄 Exécution des migrations..."
python manage.py migrate --noinput

# Collecte des fichiers statiques
echo "🔄 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# Création du superutilisateur
echo "🔄 Configuration du superutilisateur..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'✅ Superutilisateur {username} créé')
else:
    print(f'✅ Superutilisateur {username} existe déjà')
"

echo "🎉 Build Render terminé avec succès!"