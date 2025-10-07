#!/usr/bin/env python3
"""
Script pour créer un endpoint de test simple
"""

import os
import sys

# Ajouter le contenu à api/views.py
views_content = '''
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_notifications_endpoint(request):
    """Endpoint de test pour vérifier le déploiement des notifications"""
    return Response({
        'status': 'success',
        'message': 'Endpoint de test des notifications fonctionne',
        'notifications_app_loaded': 'notifications' in settings.INSTALLED_APPS
    })
'''

# Ajouter l'URL à api/urls.py
url_line = "    path('test-notifications/', views.test_notifications_endpoint, name='test_notifications'),"

print("Ajout d'un endpoint de test pour diagnostiquer le problème de déploiement...")
print("Cet endpoint permettra de vérifier si le problème vient spécifiquement des notifications.")
print("\nPour ajouter manuellement :")
print("1. Dans api/views.py, ajouter :")
print(views_content)
print("\n2. Dans api/urls.py, ajouter dans urlpatterns :")
print(url_line)