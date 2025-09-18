#!/usr/bin/env python
"""
Script pour vérifier le statut du déploiement sur Render
"""
import requests
import time
import sys

def check_deployment(url, max_attempts=10, delay=30):
    """
    Vérifie si le déploiement est accessible
    """
    print(f"🔍 Vérification du déploiement sur {url}")
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Tentative {attempt}/{max_attempts}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Déploiement réussi ! Status: {response.status_code}")
                print(f"📊 Taille du contenu: {len(response.content)} bytes")
                return True
            else:
                print(f"⚠️  Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur: {e}")
        
        if attempt < max_attempts:
            print(f"⏳ Attente de {delay} secondes avant la prochaine tentative...")
            time.sleep(delay)
    
    print("❌ Le déploiement n'est pas accessible après toutes les tentatives")
    return False

def test_admin_access(base_url):
    """
    Teste l'accès à l'interface d'administration
    """
    admin_url = f"{base_url}/admin/"
    try:
        response = requests.get(admin_url, timeout=30)
        if response.status_code == 200:
            print(f"✅ Interface d'administration accessible: {admin_url}")
            return True
        else:
            print(f"⚠️  Interface d'administration - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur d'accès à l'admin: {e}")
        return False

def test_production_endpoints(base_url):
    """
    Teste les endpoints de production
    """
    endpoints = [
        "/production/",
        "/production/preview-sorties/",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=30)
            print(f"📍 {endpoint} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur sur {endpoint}: {e}")

if __name__ == "__main__":
    # URL de déploiement Render
    DEPLOYMENT_URL = "https://beton-project.onrender.com"
    
    print("🚀 Vérification du déploiement Render...")
    print("=" * 50)
    
    # Vérification principale
    if check_deployment(DEPLOYMENT_URL):
        print("\n🔧 Test des fonctionnalités...")
        test_admin_access(DEPLOYMENT_URL)
        test_production_endpoints(DEPLOYMENT_URL)
        print("\n🎉 Vérification terminée !")
    else:
        print("\n❌ Le déploiement a échoué ou n'est pas encore prêt")
        print("💡 Vérifiez les logs sur Render Dashboard")
        sys.exit(1)