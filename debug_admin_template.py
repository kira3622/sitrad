#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_admin_template():
    print("🔍 Test de l'interface d'administration...")
    
    # Créer un client de test
    client = Client()
    
    # Créer un superutilisateur temporaire
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
    
    # Se connecter
    client.force_login(admin_user)
    
    # Accéder à la page d'administration
    response = client.get('/admin/')
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Content-Type: {response.get('Content-Type', 'Non défini')}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Rechercher le marqueur de template personnalisé
        if "TEMPLATE PERSONNALISÉ ACTIF" in content:
            print("✅ Template personnalisé détecté!")
        else:
            print("❌ Template personnalisé non détecté")
        
        # Rechercher les statistiques
        if "stat-value" in content:
            print("✅ Classes stat-value trouvées")
        else:
            print("❌ Classes stat-value non trouvées")
        
        # Rechercher les valeurs de debug
        if "total_clients:" in content:
            print("✅ Variables de debug trouvées")
        else:
            print("❌ Variables de debug non trouvées")
        
        # Afficher un extrait du contenu
        print("\n📝 Extrait du contenu HTML (premiers 1000 caractères):")
        print("-" * 50)
        print(content[:1000])
        print("-" * 50)
        
        # Rechercher les templates utilisés
        if hasattr(response, 'templates'):
            print(f"\n📋 Templates utilisés: {[t.name for t in response.templates]}")
        
    else:
        print(f"❌ Erreur d'accès: {response.status_code}")
        print(f"Contenu: {response.content.decode('utf-8')[:500]}")

if __name__ == "__main__":
    test_admin_template()