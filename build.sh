#!/usr/bin/env bash
# Script de build pour Render - Diagnostic et correction formules
set -o errexit  # Exit on any error

echo "🚀 Début du build Render avec diagnostic formules..."

# Mise à jour de pip
echo "🔄 Mise à jour de pip..."
python -m pip install --upgrade pip

# Exécution du script de build Python avec diagnostic complet
echo "🔄 Exécution du diagnostic et build Python..."
python render_build.py

echo "🎉 Build Render terminé avec succès!"