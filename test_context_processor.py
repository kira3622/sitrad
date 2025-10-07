#!/usr/bin/env python
"""
Script pour tester le context processor directement
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from core.context_processors import admin_dashboard_stats

def test_context_processor():
    """Test direct du context processor"""
    print("🔍 Test du context processor admin_dashboard_stats")
    print("=" * 50)
    
    # Créer une requête factice
    factory = RequestFactory()
    request = factory.get('/admin/')
    
    # Créer un utilisateur staff
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    request.user = user
    
    # Tester le context processor
    context = admin_dashboard_stats(request)
    
    print("📊 Résultats du context processor:")
    for key, value in context.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Test terminé")

if __name__ == "__main__":
    test_context_processor()