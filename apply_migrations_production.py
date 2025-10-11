#!/usr/bin/env python3
"""
Script pour forcer l'application des migrations en production
en créant les champs manquants via l'API Django
"""

import requests
import json
import sys
import time
import subprocess

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

def create_migration_commit():
    """Créer un commit spécial pour forcer les migrations"""
    print("🚀 Création d'un commit de migration forcée...")
    
    try:
        # Créer un fichier temporaire pour forcer le redéploiement
        with open("FORCE_MIGRATION.txt", "w") as f:
            f.write(f"Force migration at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("This file forces the application of pending migrations.\n")
        
        # Ajouter le fichier
        result = subprocess.run([
            "git", "add", "FORCE_MIGRATION.txt"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode != 0:
            print(f"❌ Erreur git add: {result.stderr}")
            return False
        
        # Commit avec message spécial
        result = subprocess.run([
            "git", "commit", 
            "-m", "migrate: Force application of pompes migrations in production"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Commit de migration créé")
            
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
        print(f"❌ Erreur lors de la création du commit: {e}")
        return False

def wait_for_deployment_with_checks(max_wait=300):
    """Attendre le déploiement en vérifiant périodiquement"""
    print(f"⏳ Attente du déploiement avec vérifications (max {max_wait} secondes)...")
    
    start_time = time.time()
    check_interval = 30  # Vérifier toutes les 30 secondes
    
    while time.time() - start_time < max_wait:
        elapsed = int(time.time() - start_time)
        print(f"⏳ {elapsed}/{max_wait} secondes écoulées...")
        
        # Vérifier si les migrations sont appliquées
        if elapsed > 60 and elapsed % check_interval == 0:  # Commencer à vérifier après 1 minute
            print("🔍 Vérification intermédiaire...")
            if check_migrations_applied():
                print("✅ Migrations détectées! Déploiement réussi.")
                return True
        
        time.sleep(10)
    
    print("⚠️ Temps d'attente maximum atteint")
    return False

def check_migrations_applied():
    """Vérifier si les migrations ont été appliquées"""
    token = get_jwt_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Vérifier l'endpoint pompes
        pompes_response = requests.get(
            f"{API_BASE_URL}/pompes/",
            headers=headers,
            timeout=30
        )
        
        if pompes_response.status_code == 200:
            print("✅ Endpoint /pompes/ accessible!")
            return True
        
        # Vérifier les champs dans production
        response = requests.get(
            f"{API_BASE_URL}/production/?limit=1",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data and data['results']:
            order = data['results'][0]
            
            # Vérifier les nouveaux champs
            new_fields = ['pompe_nom', 'pompe_marque', 'pompe_modele', 'pompe_statut', 'pompe_debit_max', 'pompe_operateur_nom']
            missing_fields = [field for field in new_fields if field not in order]
            
            if not missing_fields:
                print("✅ Tous les nouveaux champs de pompes sont présents!")
                return True
            else:
                print(f"⏳ Champs encore manquants: {missing_fields}")
                return False
        
        return False
        
    except Exception as e:
        print(f"⏳ Vérification en cours... ({e})")
        return False

def final_verification():
    """Vérification finale complète"""
    print("\n🔍 Vérification finale des migrations...")
    
    token = get_jwt_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test 1: Vérifier l'endpoint pompes
        print("📍 Test 1: Endpoint /pompes/")
        pompes_response = requests.get(
            f"{API_BASE_URL}/pompes/",
            headers=headers,
            timeout=30
        )
        
        if pompes_response.status_code == 200:
            pompes_data = pompes_response.json()
            pompes_count = len(pompes_data) if isinstance(pompes_data, list) else len(pompes_data.get('results', []))
            print(f"✅ Endpoint /pompes/ accessible - {pompes_count} pompes trouvées")
        else:
            print(f"❌ Endpoint /pompes/ inaccessible (Status: {pompes_response.status_code})")
        
        # Test 2: Vérifier les champs dans production
        print("📍 Test 2: Nouveaux champs dans Production")
        response = requests.get(
            f"{API_BASE_URL}/production/?limit=1",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, dict) and 'results' in data and data['results']:
            order = data['results'][0]
            
            # Vérifier les nouveaux champs
            new_fields = ['pompe_nom', 'pompe_marque', 'pompe_modele', 'pompe_statut', 'pompe_debit_max', 'pompe_operateur_nom']
            present_fields = [field for field in new_fields if field in order]
            missing_fields = [field for field in new_fields if field not in order]
            
            print(f"✅ Champs présents: {present_fields}")
            if missing_fields:
                print(f"❌ Champs manquants: {missing_fields}")
                return False
            else:
                print("✅ Tous les nouveaux champs de pompes sont présents!")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification finale: {e}")
        return False

def cleanup():
    """Nettoyer le fichier temporaire"""
    try:
        import os
        if os.path.exists("FORCE_MIGRATION.txt"):
            os.remove("FORCE_MIGRATION.txt")
            print("🧹 Fichier temporaire supprimé")
    except:
        pass

if __name__ == "__main__":
    print("🚀 Application Forcée des Migrations en PRODUCTION")
    print("=" * 60)
    
    try:
        # Étape 1: Créer un commit de migration
        if create_migration_commit():
            # Étape 2: Attendre le déploiement avec vérifications
            if wait_for_deployment_with_checks(300):  # 5 minutes max
                # Étape 3: Vérification finale
                if final_verification():
                    print("\n🎉 SUCCESS: Migrations appliquées avec succès!")
                    cleanup()
                    sys.exit(0)
                else:
                    print("\n❌ ÉCHEC: Vérification finale échouée")
                    cleanup()
                    sys.exit(1)
            else:
                print("\n⚠️ TIMEOUT: Déploiement trop long")
                cleanup()
                sys.exit(1)
        else:
            print("\n❌ ÉCHEC: Impossible de créer le commit de migration")
            cleanup()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Interruption par l'utilisateur")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        cleanup()
        sys.exit(1)