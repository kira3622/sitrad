#!/usr/bin/env python
"""
Créer un utilisateur de démo pour les tests Android (login JWT)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from django.contrib.auth.models import User

USERNAME = os.environ.get('DEMO_USERNAME', 'demo')
EMAIL = os.environ.get('DEMO_EMAIL', 'demo@example.com')
PASSWORD = os.environ.get('DEMO_PASSWORD', 'demo1234')

def main():
    user, created = User.objects.get_or_create(username=USERNAME, defaults={
        'email': EMAIL,
        'is_active': True,
    })
    user.set_password(PASSWORD)
    user.save()
    if created:
        print(f"✓ Utilisateur créé: {USERNAME} / {PASSWORD}")
    else:
        print(f"✓ Utilisateur mis à jour: {USERNAME} (mot de passe réinitialisé)")

if __name__ == '__main__':
    main()