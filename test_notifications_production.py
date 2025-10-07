#!/usr/bin/env python3
"""
Script de diagnostic pour tester l'API des notifications en production
"""

import requests
import json
from datetime import datetime

def test_notifications_api():
    """Test de l'API des notifications sur le serveur de production"""
    
    base_url = "https://sitrad-web.onrender.com"
    
    print(f"=== Test de l'API des Notifications - {datetime.now()} ===\n")
    
    # Test 1: Vérifier que le serveur principal fonctionne
    print("1. Test du serveur principal...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   ✓ Serveur principal: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Erreur serveur principal: {e}")
        return
    
    # Test 2: Tester l'API de base
    print("\n2. Test de l'API de base...")
    try:
        response = requests.get(f"{base_url}/api/v1/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ API de base fonctionne (401 = authentification requise)")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Erreur API de base: {e}")
    
    # Test 3: Tester l'endpoint des notifications
    print("\n3. Test de l'endpoint des notifications...")
    try:
        response = requests.get(f"{base_url}/api/v1/notifications/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✓ Endpoint notifications fonctionne (401 = authentification requise)")
        elif response.status_code == 404:
            print("   ✗ Endpoint notifications non trouvé (404)")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Erreur endpoint notifications: {e}")
    
    # Test 4: Tester d'autres endpoints pour comparaison
    print("\n4. Test d'autres endpoints pour comparaison...")
    endpoints = [
        "chantiers/",
        "clients/", 
        "commandes/",
        "dashboard/stats/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}/api/v1/{endpoint}", timeout=10)
            status_text = "✓" if response.status_code in [200, 401] else "✗"
            print(f"   {status_text} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ✗ {endpoint}: Erreur - {e}")
    
    print(f"\n=== Fin du diagnostic - {datetime.now()} ===")

if __name__ == "__main__":
    test_notifications_api()