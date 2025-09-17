#!/usr/bin/env python
"""
Script pour créer un superutilisateur Django automatiquement
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Crée un superutilisateur si il n'existe pas déjà"""
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'✅ Superutilisateur {username} créé avec succès')
    else:
        print(f'✅ Superutilisateur {username} existe déjà')

if __name__ == '__main__':
    create_superuser()