#!/usr/bin/env bash
# Script de build pour Render - Version simplifiée
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
python -c "import django; print('Django version:', django.get_version())"


# Collecte des fichiers statiques
echo "🔄 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "🎉 Build Render terminé avec succès!"