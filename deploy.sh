#!/bin/bash

# Script de déploiement pour Django

# Activer l'environnement virtuel
source .venv/bin/activate

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collection des fichiers statiques..."
python manage.py collectstatic --noinput

# Créer le superutilisateur s'il n'existe pas
echo "Création du superutilisateur..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superutilisateur créé avec succès')
else:
    print('Le superutilisateur existe déjà')
"

# Démarrer Gunicorn
echo "Démarrage de Gunicorn..."
gunicorn beton_project.wsgi:application --config gunicorn.conf.py