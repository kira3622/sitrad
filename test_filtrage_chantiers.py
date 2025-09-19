#!/usr/bin/env python
"""
Script de test pour vérifier le filtrage des chantiers par client
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from customers.models import Client, Chantier
from django.test import Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse

def test_filtrage_chantiers():
    """Test du filtrage des chantiers par client"""
    print("=== Test du filtrage des chantiers par client ===\n")
    
    # Créer un client de test Django
    client = TestClient()
    
    # Créer un superuser pour les tests
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    # Se connecter en tant qu'admin
    client.login(username='admin', password='admin123')
    
    # Récupérer les clients existants
    clients = Client.objects.all()
    print(f"Clients disponibles : {clients.count()}")
    
    for client_obj in clients[:3]:  # Tester les 3 premiers clients
        print(f"\n--- Test pour le client : {client_obj.nom} (ID: {client_obj.id}) ---")
        
        # Récupérer les chantiers de ce client
        chantiers_attendus = Chantier.objects.filter(client=client_obj)
        print(f"Chantiers attendus : {chantiers_attendus.count()}")
        for chantier in chantiers_attendus:
            print(f"  - {chantier.nom}")
        
        # Tester l'endpoint AJAX
        response = client.get(f'/admin/orders/commande/ajax/filter-chantiers/?client_id={client_obj.id}')
        
        if response.status_code == 200:
            data = response.json()
            chantiers_retournes = data.get('chantiers', [])
            print(f"Chantiers retournés par l'API : {len(chantiers_retournes)}")
            
            for chantier in chantiers_retournes:
                print(f"  - {chantier['nom']} (ID: {chantier['id']})")
            
            # Vérifier que les IDs correspondent
            ids_attendus = set(chantiers_attendus.values_list('id', flat=True))
            ids_retournes = set(chantier['id'] for chantier in chantiers_retournes)
            
            if ids_attendus == ids_retournes:
                print("✅ SUCCÈS : Les chantiers retournés correspondent exactement")
            else:
                print("❌ ERREUR : Les chantiers ne correspondent pas")
                print(f"   Attendus : {ids_attendus}")
                print(f"   Retournés : {ids_retournes}")
        else:
            print(f"❌ ERREUR : Code de réponse {response.status_code}")
    
    # Test avec un client inexistant
    print(f"\n--- Test avec un client inexistant (ID: 99999) ---")
    response = client.get('/admin/orders/commande/ajax/filter-chantiers/?client_id=99999')
    if response.status_code == 200:
        data = response.json()
        if data.get('chantiers') == []:
            print("✅ SUCCÈS : Aucun chantier retourné pour un client inexistant")
        else:
            print("❌ ERREUR : Des chantiers ont été retournés pour un client inexistant")
    
    # Test sans client_id
    print(f"\n--- Test sans client_id ---")
    response = client.get('/admin/orders/commande/ajax/filter-chantiers/')
    if response.status_code == 200:
        data = response.json()
        if data.get('chantiers') == []:
            print("✅ SUCCÈS : Aucun chantier retourné sans client_id")
        else:
            print("❌ ERREUR : Des chantiers ont été retournés sans client_id")
    
    print(f"\n=== Fin des tests ===")

if __name__ == '__main__':
    test_filtrage_chantiers()