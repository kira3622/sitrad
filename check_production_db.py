#!/usr/bin/env python3
"""
Script pour vérifier l'état de la base de données en production
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

def check_database_schema():
    """Vérifier le schéma de la base de données"""
    token = get_jwt_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Vérification du schéma de la base de données...")
    
    try:
        # Récupérer un ordre de production pour examiner sa structure
        response = requests.get(
            f"{API_BASE_URL}/production/",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"📊 Réponse API: {type(data)}")
        
        # Gérer différents formats de réponse
        if isinstance(data, dict):
            if 'results' in data:
                orders = data['results']
            else:
                orders = [data] if data else []
        elif isinstance(data, list):
            orders = data
        else:
            orders = []
            
        print(f"📋 Nombre d'ordres trouvés: {len(orders)}")
        
        if orders and len(orders) > 0:
            first_order = orders[0]
            print(f"📋 Structure de l'ordre {first_order.get('id', 'N/A')}:")
            
            # Afficher tous les champs disponibles
            for key, value in first_order.items():
                print(f"  - {key}: {type(value).__name__}")
            
            # Vérifier spécifiquement les champs de pompes
            pompe_fields = [
                'pompe', 'pompe_nom', 'pompe_marque', 'pompe_modele', 
                'pompe_statut', 'pompe_debit_max', 'pompe_operateur_nom'
            ]
            
            print("\n🔧 Champs de pompes:")
            for field in pompe_fields:
                if field in first_order:
                    print(f"  ✅ {field}: {first_order[field]}")
                else:
                    print(f"  ❌ {field}: MANQUANT")
            
            return True
        else:
            print("❌ Aucun ordre trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def check_admin_interface():
    """Vérifier l'interface d'administration"""
    print("\n🔗 URLs importantes:")
    print(f"  - Interface admin: {PRODUCTION_URL}/admin/")
    print(f"  - Ordres de production: {PRODUCTION_URL}/admin/production/ordreproduction/")
    print(f"  - API production: {API_BASE_URL}/production/")

if __name__ == "__main__":
    print("🚀 Vérification de la base de données en PRODUCTION")
    print("=" * 60)
    
    success = check_database_schema()
    check_admin_interface()
    
    if success:
        print("\n✅ Vérification terminée")
    else:
        print("\n❌ Vérification échouée")
        sys.exit(1)