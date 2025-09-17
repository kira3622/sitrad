#!/usr/bin/env bash
# Script de build pour Render - Version améliorée
set -o errexit

echo "🔄 Installation des dépendances..."
pip install -r requirements.txt

echo "🔄 Vérification de la base de données..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Connexion DB OK')
except Exception as e:
    print(f'❌ Erreur DB: {e}')
    exit(1)
"

echo "🔄 Exécution des migrations..."
python manage.py migrate --noinput

echo "🔄 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🔄 Création du superutilisateur si nécessaire..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()
from django.contrib.auth.models import User
try:
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
            email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
            password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        )
        print('✅ Superutilisateur créé')
    else:
        print('✅ Superutilisateur existe')
except Exception as e:
    print(f'⚠️ Superutilisateur: {e}')
"

echo "🎉 Build terminé avec succès!"