#!/usr/bin/env python3
"""
Script pour surveiller le déploiement et vérifier l'application des migrations
"""

import requests
import time
import json
from datetime import datetime

print("Executing monitor_deployment.py...")

# Configuration
API_BASE_URL = "https://sitrad-web.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

def get_auth_token():
    """Obtenir le token d'authentification"""
    print("Attempting to get auth token...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/token/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("access")
        else:
            print(f"❌ Échec de l'authentification: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de l'authentification: {e}")
        return None

def check_api_status():
    """Vérifier le statut général de l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        return response.status_code == 200
    except:
        return False

def check_pompes_endpoint(token):
    """Vérifier si l'endpoint /pompes/ fonctionne"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/pompes/", headers=headers, timeout=30)
        return response.status_code, response.text[:200] if response.text else ""
    except Exception as e:
        return None, str(e)

def check_production_fields(token):
    """Vérifier si les nouveaux champs pompe sont présents dans Production"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE_URL}/production/", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                first_order = data["results"][0]
                
                # Vérifier la présence des nouveaux champs
                pompe_fields = [
                    "pompe_nom", "pompe_marque", "pompe_modele", 
                    "pompe_statut", "pompe_debit_max", "pompe_operateur_nom"
                ]
                
                missing_fields = [field for field in pompe_fields if field not in first_order]
                present_fields = [field for field in pompe_fields if field in first_order]
                
                return {
                    "status": "success",
                    "total_orders": len(data["results"]),
                    "present_fields": present_fields,
                    "missing_fields": missing_fields,
                    "migration_complete": len(missing_fields) == 0
                }
            else:
                return {"status": "no_data", "message": "Aucun ordre trouvé"}
        else:
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "exception", "error": str(e)}

def monitor_deployment():
    """Surveiller le déploiement"""
    print("🚀 Surveillance du déploiement en cours...")
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 60)
    
    max_attempts = 20  # 10 minutes maximum
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n📊 Tentative {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        # 1. Vérifier si l'API répond
        api_status = check_api_status()
        print(f"   API Status: {'✅ OK' if api_status else '❌ DOWN'}")
        
        if not api_status:
            print("   ⏳ API non disponible, attente...")
            time.sleep(30)
            continue
        
        # 2. Obtenir le token
        token = get_auth_token()
        if not token:
            print("   ❌ Impossible d'obtenir le token")
            time.sleep(30)
            continue
        
        print("   ✅ Token obtenu")
        
        # 3. Vérifier l'endpoint /pompes/
        pompes_status, pompes_response = check_pompes_endpoint(token)
        print(f"   Endpoint /pompes/: {pompes_status}")
        
        # 4. Vérifier les champs Production
        production_check = check_production_fields(token)
        print(f"   Production check: {production_check.get('status')}")
        
        if production_check.get("status") == "success":
            print(f"   📦 Total ordres: {production_check.get('total_orders')}")
            print(f"   ✅ Champs présents: {len(production_check.get('present_fields', []))}")
            print(f"   ❌ Champs manquants: {len(production_check.get('missing_fields', []))}")
            
            if production_check.get("migration_complete"):
                print("\n🎉 SUCCÈS! Les migrations ont été appliquées!")
                print("✅ Tous les champs pompe sont présents dans le modèle Production")
                
                # Test final de l'endpoint /pompes/
                if pompes_status == 200:
                    print("✅ L'endpoint /pompes/ fonctionne correctement")
                else:
                    print(f"⚠️  L'endpoint /pompes/ retourne: {pompes_status}")
                
                return True
            else:
                missing = production_check.get('missing_fields', [])
                print(f"   ⏳ Champs encore manquants: {missing}")
        
        print("   ⏳ Attente de 30 secondes...")
        time.sleep(30)
    
    print(f"\n⏰ Timeout atteint après {max_attempts} tentatives")
    print("❌ Les migrations ne semblent pas s'être appliquées automatiquement")
    return False

def final_verification():
    """Vérification finale complète"""
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION FINALE")
    print("="*60)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir le token pour la vérification finale")
        return
    
    # Vérifier les endpoints
    endpoints_to_check = [
        ("/production/", "Production"),
        ("/pompes/", "Pompes"),
        ("/users/", "Users")
    ]
    
    for endpoint, name in endpoints_to_check:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=30)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   {name}: {status}")
        except Exception as e:
            print(f"   {name}: ❌ Erreur - {e}")
    
    # Vérification détaillée des champs Production
    production_check = check_production_fields(token)
    if production_check.get("status") == "success":
        print(f"\n📊 Analyse du modèle Production:")
        print(f"   Total ordres: {production_check.get('total_orders')}")
        print(f"   Champs pompe présents: {production_check.get('present_fields', [])}")
        print(f"   Champs pompe manquants: {production_check.get('missing_fields', [])}")
        
        if production_check.get("migration_complete"):
            print("\n🎉 INTÉGRATION RÉUSSIE!")
            print("✅ Toutes les migrations ont été appliquées")
            print("✅ L'API est entièrement fonctionnelle")
        else:
            print("\n⚠️  INTÉGRATION PARTIELLE")
            print("❌ Certaines migrations ne sont pas appliquées")

if __name__ == "__main__":
    try:
        success = monitor_deployment()
        final_verification()
        
        if success:
            print("\n🎉 DÉPLOIEMENT RÉUSSI!")
        else:
            print("\n⚠️  DÉPLOIEMENT INCOMPLET - Intervention manuelle requise")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Surveillance interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de la surveillance: {e}")