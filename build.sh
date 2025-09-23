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
echo "📁 Contenu du dossier static avant collectstatic:"
ls -la static/ || echo "Dossier static non trouvé"

python manage.py collectstatic --noinput --clear --verbosity=2

echo "📁 Contenu du dossier staticfiles après collectstatic:"
ls -la staticfiles/ || echo "Dossier staticfiles non trouvé"
echo "📁 Contenu de staticfiles/css:"
ls -la staticfiles/css/ || echo "Dossier staticfiles/css non trouvé"
echo "📁 Contenu de staticfiles/js:"
ls -la staticfiles/js/ || echo "Dossier staticfiles/js non trouvé"

echo "🎉 Build Render terminé avec succès!"