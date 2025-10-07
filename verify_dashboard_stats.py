#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
import re

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def verify_dashboard_stats():
    print("🎯 Vérification finale des statistiques du tableau de bord")
    print("=" * 60)
    
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
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        print("✅ Accès à l'interface d'administration réussi")
        
        # Extraire les valeurs des statistiques
        stats_pattern = r'<div class="stat-value">(\d+)</div>\s*<div class="stat-label">([^<]+)</div>'
        matches = re.findall(stats_pattern, content)
        
        if matches:
            print("\n📊 Statistiques trouvées:")
            for value, label in matches:
                print(f"   • {label.strip()}: {value}")
        else:
            print("❌ Aucune statistique trouvée avec le pattern attendu")
        
        # Extraire les valeurs de debug
        debug_pattern = r'<li>([^:]+):\s*([^<]+)</li>'
        debug_matches = re.findall(debug_pattern, content)
        
        if debug_matches:
            print("\n🔍 Variables de debug:")
            for var_name, var_value in debug_matches:
                print(f"   • {var_name.strip()}: {var_value.strip()}")
        
        # Vérifier la présence du marqueur
        if "TEMPLATE PERSONNALISÉ ACTIF" in content:
            print("\n✅ Template personnalisé confirmé actif")
        
        print("\n🎉 Test terminé avec succès!")
        
    else:
        print(f"❌ Erreur d'accès: {response.status_code}")

if __name__ == "__main__":
    verify_dashboard_stats()