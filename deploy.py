#!/usr/bin/env python
"""
Script de déploiement pour Render
Résout les problèmes courants de base de données et de migrations
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Configure Django pour le script"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
    django.setup()

def run_migrations():
    """Exécute les migrations de base de données"""
    print("🔄 Exécution des migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations terminées avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors des migrations: {e}")
        return False

def collect_static():
    """Collecte les fichiers statiques"""
    print("🔄 Collecte des fichiers statiques...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Fichiers statiques collectés")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la collecte: {e}")
        return False

def create_superuser():
    """Crée un superutilisateur si nécessaire"""
    print("🔄 Vérification du superutilisateur...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
                email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
                password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
            )
            print("✅ Superutilisateur créé")
        else:
            print("✅ Superutilisateur existe déjà")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du superutilisateur: {e}")
        return False

def check_database():
    """Vérifie la connexion à la base de données"""
    print("🔄 Vérification de la base de données...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Connexion à la base de données OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def main():
    """Fonction principale de déploiement"""
    print("🚀 Début du déploiement...")
    
    setup_django()
    
    success = True
    
    # Vérification de la base de données
    if not check_database():
        success = False
    
    # Exécution des migrations
    if success and not run_migrations():
        success = False
    
    # Collecte des fichiers statiques
    if success and not collect_static():
        success = False
    
    # Création du superutilisateur
    if success and not create_superuser():
        success = False
    
    if success:
        print("🎉 Déploiement terminé avec succès!")
        return 0
    else:
        print("💥 Échec du déploiement")
        return 1

if __name__ == '__main__':
    sys.exit(main())