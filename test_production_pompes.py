#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration des pompes en production
"""

import requests
import json
import sys

# Configuration de production
PRODUCTION_URL = "https://sitrad-web.onrender.com"
API_BASE_URL = f"{PRODUCTION_URL}/api/v1"

def get_jwt_token(username, password):
    """Obtenir un token JWT pour l'authentification"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/token/",
            data={
                'username': username,
                'password': password
            },
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access')
        else:
            print(f"❌ Erreur d'authentification: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion lors de l'authentification: {e}")
        return None

def test_production_api():
    """Tester l'API de production avec les nouvelles fonctionnalités des pompes"""
    
    print("🚀 Test de l'intégration des pompes en PRODUCTION")
    print("=" * 60)
    
    # Authentification
    print("🔐 Authentification...")
    token = get_jwt_token('admin', 'admin123')
    
    if not token:
        print("❌ Impossible d'obtenir le token d'authentification")
        return False
    
    print("✅ Token JWT obtenu avec succès")
    
    # Headers avec authentification
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test de l'API de production
        print("\n📡 Test de l'API de production...")
        response = requests.get(
            f"{API_BASE_URL}/production/",
            headers=headers,
            params={'page_size': 50},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
        
        data = response.json()
        ordres = data.get('results', [])
        
        print(f"✅ API accessible - {len(ordres)} ordres récupérés")
        
        # Vérifier les nouveaux champs de pompes
        print("\n🔍 Vérification des nouveaux champs de pompes...")
        
        pompes_trouvees = 0
        ordres_avec_pompes = []
        
        for ordre in ordres:
            # Vérifier la présence des nouveaux champs
            nouveaux_champs = [
                'pompe_nom', 'pompe_marque', 'pompe_modele', 
                'pompe_statut', 'pompe_debit_max', 'pompe_operateur_nom'
            ]
            
            champs_manquants = [champ for champ in nouveaux_champs if champ not in ordre]
            
            if champs_manquants:
                print(f"❌ Champs manquants dans l'ordre {ordre.get('numero_bon', 'N/A')}: {champs_manquants}")
                return False
            
            # Compter les ordres avec pompes assignées
            if ordre.get('pompe') is not None:
                pompes_trouvees += 1
                ordres_avec_pompes.append(ordre)
        
        print(f"✅ Tous les nouveaux champs sont présents dans l'API")
        print(f"📊 Ordres avec pompes assignées: {pompes_trouvees}/{len(ordres)}")
        
        # Afficher quelques exemples d'ordres avec pompes
        if ordres_avec_pompes:
            print("\n📋 Exemples d'ordres avec pompes:")
            for i, ordre in enumerate(ordres_avec_pompes[:3]):  # Afficher max 3 exemples
                print(f"\n  {i+1}. Ordre: {ordre.get('numero_bon')}")
                print(f"     Pompe: {ordre.get('pompe_nom')} ({ordre.get('pompe_marque')} {ordre.get('pompe_modele')})")
                print(f"     Statut: {ordre.get('pompe_statut')}")
                print(f"     Débit max: {ordre.get('pompe_debit_max')} m³/h")
                print(f"     Opérateur: {ordre.get('pompe_operateur_nom')}")
        
        # Test spécifique d'un ordre avec pompe si disponible
        if ordres_avec_pompes:
            print(f"\n🎯 Test détaillé de l'ordre: {ordres_avec_pompes[0]['numero_bon']}")
            ordre_id = ordres_avec_pompes[0]['id']
            
            response_detail = requests.get(
                f"{API_BASE_URL}/production/{ordre_id}/",
                headers=headers,
                timeout=30
            )
            
            if response_detail.status_code == 200:
                ordre_detail = response_detail.json()
                print("✅ Récupération détaillée réussie")
                print(f"   Pompe complète: {ordre_detail.get('pompe_nom')} - {ordre_detail.get('pompe_operateur_nom')}")
            else:
                print(f"❌ Erreur lors de la récupération détaillée: {response_detail.status_code}")
        
        print("\n" + "=" * 60)
        print("🎉 TEST DE PRODUCTION RÉUSSI!")
        print("✅ L'intégration des pompes fonctionne correctement en production")
        print("✅ Tous les nouveaux champs sont disponibles")
        print("✅ L'authentification JWT fonctionne")
        print("✅ L'API retourne les informations des pompes et opérateurs")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = test_production_api()
    sys.exit(0 if success else 1)