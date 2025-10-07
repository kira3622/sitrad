#!/usr/bin/env python3
"""
Script de test robuste pour l'API des notifications avec retry
"""

import requests
import time
from datetime import datetime

def test_notifications_with_retry():
    """Test de l'API des notifications avec plusieurs tentatives"""
    
    base_url = "https://sitrad-web.onrender.com"
    max_attempts = 10
    delay_between_attempts = 30  # 30 secondes
    
    print(f"=== Test Robuste de l'API des Notifications - {datetime.now()} ===\n")
    
    for attempt in range(1, max_attempts + 1):
        print(f"Tentative {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Test de l'endpoint des notifications
            response = requests.get(f"{base_url}/api/v1/notifications/", timeout=15)
            status_code = response.status_code
            
            print(f"   Status: {status_code}")
            
            if status_code == 401:
                print("   ✅ SUCCÈS! Endpoint notifications fonctionne (401 = authentification requise)")
                
                # Test de comparaison avec d'autres endpoints
                print("\n   Vérification des autres endpoints:")
                test_endpoints = ["chantiers/", "clients/", "commandes/"]
                for endpoint in test_endpoints:
                    try:
                        resp = requests.get(f"{base_url}/api/v1/{endpoint}", timeout=10)
                        print(f"   - {endpoint}: {resp.status_code}")
                    except Exception as e:
                        print(f"   - {endpoint}: Erreur - {e}")
                
                print(f"\n✅ API des notifications déployée avec succès!")
                return True
                
            elif status_code == 404:
                print("   ❌ Endpoint toujours non trouvé (404)")
                if attempt < max_attempts:
                    print(f"   ⏳ Attente de {delay_between_attempts} secondes avant la prochaine tentative...")
                    time.sleep(delay_between_attempts)
                else:
                    print("   ❌ Échec après toutes les tentatives")
                    
            else:
                print(f"   ⚠️ Status inattendu: {status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erreur de connexion: {e}")
            if attempt < max_attempts:
                print(f"   ⏳ Attente de {delay_between_attempts} secondes avant la prochaine tentative...")
                time.sleep(delay_between_attempts)
    
    print(f"\n❌ Échec du déploiement après {max_attempts} tentatives")
    return False

if __name__ == "__main__":
    success = test_notifications_with_retry()
    exit(0 if success else 1)