#!/usr/bin/env python3
"""
Script pour forcer l'application des migrations en production
"""

import requests
import json
import sys
import time

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

def check_migration_status():
    """Vérifier le statut des migrations"""
    print("🔍 Vérification du statut des migrations...")
    
    # Essayer d'accéder à l'interface d'administration
    try:
        response = requests.get(f"{PRODUCTION_URL}/admin/", timeout=30)
        if response.status_code == 200:
            print("✅ Interface d'administration accessible")
        else:
            print(f"⚠️ Interface d'administration: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur d'accès à l'admin: {e}")

def trigger_migration():
    """Déclencher une migration en créant un commit vide"""
    print("🚀 Tentative de déclenchement des migrations...")
    
    # Créer un commit vide pour forcer un redéploiement
    import subprocess
    
    try:
        # Commit vide avec message spécifique pour les migrations
        result = subprocess.run([
            "git", "commit", "--allow-empty", 
            "-m", "deploy: Force migration application for pompes integration"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Commit vide créé")
            
            # Push vers le dépôt
            push_result = subprocess.run([
                "git", "push", "origin", "main"
            ], capture_output=True, text=True, cwd=".")
            
            if push_result.returncode == 0:
                print("✅ Push réussi - déploiement en cours...")
                return True
            else:
                print(f"❌ Erreur de push: {push_result.stderr}")
                return False
        else:
            print(f"❌ Erreur de commit: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du déclenchement: {e}")
        return False

def wait_for_deployment(wait_time=180):
    """Attendre que le déploiement se termine"""
    print(f"⏳ Attente du déploiement ({wait_time} secondes)...")
    
    for i in range(wait_time // 10):
        time.sleep(10)
        print(f"⏳ {(i+1)*10}/{wait_time} secondes écoulées...")
    
    print("✅ Attente terminée")

def verify_migration():
    """Vérifier que les migrations ont été appliquées"""
    print("🔍 Vérification des migrations appliquées...")
    
    token = get_jwt_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/production/",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            orders = data['results']
        elif isinstance(data, list):
            orders = data
        else:
            orders = []
        
        if orders and len(orders) > 0:
            first_order = orders[0]
            
            # Vérifier les nouveaux champs
            new_fields = ['pompe_nom', 'pompe_marque', 'pompe_modele', 'pompe_statut', 'pompe_debit_max', 'pompe_operateur_nom']
            missing_fields = [field for field in new_fields if field not in first_order]
            
            if not missing_fields:
                print("✅ Tous les nouveaux champs de pompes sont présents!")
                return True
            else:
                print(f"❌ Champs manquants: {missing_fields}")
                return False
        else:
            print("❌ Aucun ordre trouvé pour vérification")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de vérification: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Force Application des Migrations en PRODUCTION")
    print("=" * 60)
    
    # Étape 1: Vérifier le statut actuel
    check_migration_status()
    
    # Étape 2: Déclencher un redéploiement
    if trigger_migration():
        # Étape 3: Attendre le déploiement
        wait_for_deployment(120)  # 2 minutes
        
        # Étape 4: Vérifier les résultats
        if verify_migration():
            print("\n🎉 SUCCESS: Migrations appliquées avec succès!")
            sys.exit(0)
        else:
            print("\n❌ ÉCHEC: Les migrations n'ont pas été appliquées")
            sys.exit(1)
    else:
        print("\n❌ ÉCHEC: Impossible de déclencher le redéploiement")
        sys.exit(1)