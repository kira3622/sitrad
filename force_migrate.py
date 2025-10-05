#!/usr/bin/env python
"""
Script pour forcer les migrations et vérifier l'état de la base de données
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

def force_migrate():
    print("=== FORCE MIGRATION ===")
    
    # 1. Afficher l'état des migrations
    print("\n1. État actuel des migrations...")
    try:
        execute_from_command_line(['manage.py', 'showmigrations'])
    except Exception as e:
        print(f"Erreur showmigrations: {e}")
    
    # 2. Créer les migrations si nécessaire
    print("\n2. Création des migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
    except Exception as e:
        print(f"Erreur makemigrations: {e}")
    
    # 3. Appliquer toutes les migrations
    print("\n3. Application des migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
    except Exception as e:
        print(f"Erreur migrate: {e}")
    
    # 4. Vérifier que les tables existent
    print("\n4. Vérification des tables...")
    try:
        from formulas.models import FormuleBeton
        count = FormuleBeton.objects.count()
        print(f"✅ Table FormuleBeton accessible, {count} objets")
    except Exception as e:
        print(f"❌ Erreur d'accès à FormuleBeton: {e}")
    
    print("\n=== FIN FORCE MIGRATION ===")

if __name__ == "__main__":
    force_migrate()