#!/usr/bin/env python3
"""
Script pour déboguer les modèles en production et comprendre pourquoi les migrations ne s'appliquent pas
"""

import requests
import json
import sys

# Configuration de production
PRODUCTION_URL = "https://sitrad-web.onrender.com"
API_BASE_URL = f"{PRODUCTION_URL}/api/v1"

def get_jwt_token():
    """Obtenir un token JWT pour l'authentification"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/token/",
            json=login_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["access"]
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")
        return None

def check_api_endpoints():
    """Vérifier tous les endpoints API disponibles"""
    print("🔍 Vérification des endpoints API...")
    
    token = get_jwt_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Endpoints à tester
    endpoints = [
        "/production/",
        "/pompes/",
        "/users/",
        "/auth/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers=headers,
                timeout=30
            )
            print(f"📍 {endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'results' in data:
                            print(f"   📊 {len(data['results'])} éléments trouvés")
                            if data['results']:
                                print(f"   🔑 Clés du premier élément: {list(data['results'][0].keys())}")
                        else:
                            print(f"   🔑 Clés de la réponse: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   📊 {len(data)} éléments trouvés")
                        if data:
                            print(f"   🔑 Clés du premier élément: {list(data[0].keys())}")
                except:
                    print(f"   ⚠️ Réponse non-JSON")
            
        except Exception as e:
            print(f"❌ Erreur pour {endpoint}: {e}")

def check_admin_models():
    """Vérifier les modèles disponibles via l'interface admin"""
    print("\n🔍 Vérification de l'interface d'administration...")
    
    try:
        # Accéder à la page d'administration
        response = requests.get(f"{PRODUCTION_URL}/admin/", timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            # Chercher des indices sur les modèles disponibles
            if "production" in content.lower():
                print("✅ Modèle 'production' détecté dans l'admin")
            if "pompe" in content.lower():
                print("✅ Modèle 'pompe' détecté dans l'admin")
            else:
                print("❌ Modèle 'pompe' non détecté dans l'admin")
                
            # Chercher des liens vers les modèles
            import re
            model_links = re.findall(r'/admin/(\w+)/(\w+)/', content)
            if model_links:
                print("📋 Modèles détectés:")
                for app, model in set(model_links):
                    print(f"   - {app}.{model}")
        else:
            print(f"❌ Erreur d'accès à l'admin: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification admin: {e}")

def check_database_schema():
    """Vérifier le schéma de la base de données via une requête spéciale"""
    print("\n🔍 Vérification du schéma de base de données...")
    
    token = get_jwt_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Essayer d'obtenir un ordre avec tous les champs possibles
        response = requests.get(
            f"{API_BASE_URL}/production/?limit=1",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data and data['results']:
            order = data['results'][0]
            
            print("📋 Champs disponibles dans le modèle Production:")
            for key, value in order.items():
                print(f"   - {key}: {type(value).__name__} = {value}")
                
            # Vérifier spécifiquement les champs de pompe
            pompe_fields = [k for k in order.keys() if 'pompe' in k.lower()]
            print(f"\n🔧 Champs liés aux pompes: {pompe_fields}")
            
            # Champs attendus
            expected_fields = ['pompe_nom', 'pompe_marque', 'pompe_modele', 'pompe_statut', 'pompe_debit_max', 'pompe_operateur_nom']
            missing_fields = [f for f in expected_fields if f not in order]
            
            if missing_fields:
                print(f"❌ Champs manquants: {missing_fields}")
            else:
                print("✅ Tous les champs de pompe sont présents!")
                
        else:
            print("❌ Aucun ordre trouvé pour analyser le schéma")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du schéma: {e}")

if __name__ == "__main__":
    print("🔍 DEBUG: Analyse des Modèles en PRODUCTION")
    print("=" * 60)
    
    # Vérifier les endpoints API
    check_api_endpoints()
    
    # Vérifier l'interface d'administration
    check_admin_models()
    
    # Vérifier le schéma de la base de données
    check_database_schema()
    
    print("\n" + "=" * 60)
    print("🏁 Analyse terminée")