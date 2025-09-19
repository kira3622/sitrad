#!/usr/bin/env python
import os
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from orders.models import Client, Chantier

def test_endpoint():
    print("=== Test de l'endpoint AJAX de filtrage des chantiers ===\n")
    
    # URL de base
    base_url = "http://127.0.0.1:8000/admin/orders/commande/ajax/filter-chantiers/"
    
    # Récupérer les premiers clients
    clients = Client.objects.all()[:3]
    
    for client in clients:
        print(f"Client: {client.nom} (ID: {client.id})")
        
        # Chantiers dans la base de données
        chantiers_db = list(Chantier.objects.filter(client=client).values('id', 'nom'))
        print(f"  Chantiers en base: {len(chantiers_db)}")
        for chantier in chantiers_db:
            print(f"    - {chantier['nom']} (ID: {chantier['id']})")
        
        # Test de l'endpoint
        try:
            response = requests.get(base_url, params={'client_id': client.id})
            print(f"  Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    chantiers_api = data.get('chantiers', [])
                    print(f"  Chantiers retournés par l'API: {len(chantiers_api)}")
                    
                    # Vérification des correspondances
                    ids_db = set(c['id'] for c in chantiers_db)
                    ids_api = set(c['id'] for c in chantiers_api)
                    
                    if ids_db == ids_api:
                        print("  ✅ SUCCÈS: Les IDs correspondent parfaitement")
                    else:
                        print("  ❌ ERREUR: Les IDs ne correspondent pas")
                        print(f"    En base: {ids_db}")
                        print(f"    API: {ids_api}")
                        
                except json.JSONDecodeError as e:
                    print(f"  ❌ ERREUR JSON: {e}")
                    print(f"  Réponse brute: {response.text[:200]}...")
            else:
                print(f"  ❌ ERREUR HTTP: {response.status_code}")
                print(f"  Réponse: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ ERREUR de connexion: {e}")
        
        print()
    
    print("=== Test terminé ===")

if __name__ == "__main__":
    test_endpoint()