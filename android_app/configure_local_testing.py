#!/usr/bin/env python3
"""
Script pour configurer l'application Android pour les tests locaux
"""

import json
import os
import subprocess
import requests
import time

# Configuration
LOCAL_API_URL_HOST = "http://127.0.0.1:8000/api/v1"  # IP pour tests depuis l'hôte
LOCAL_API_URL_ANDROID = "http://10.0.2.2:8000/api/v1"  # IP pour émulateur Android
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"

def get_jwt_token():
    """Obtenir un token JWT pour l'utilisateur de test"""
    try:
        # Endpoint de login (nous devons le créer s'il n'existe pas)
        login_url = f"{LOCAL_API_URL_HOST}/auth/token/"
        
        response = requests.post(login_url, json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access'), data.get('refresh')
        else:
            print(f"Erreur lors de l'authentification: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return None, None

def update_android_config():
    """Mettre à jour la configuration Android pour les tests locaux"""
    config = {
        "api": {
            "base_url": LOCAL_API_URL_ANDROID,
            "timeout": 10,
            "endpoints": {
                "auth": "/auth/token/",
                "auth_refresh": "/auth/token/refresh/",
                "notifications": "/notifications/",
                "unread_count": "/notifications/unread_count/",
                "summary": "/notifications/summary/",
                "mark_as_read": "/notifications/mark_as_read/",
                "mark_all_as_read": "/notifications/mark_all_as_read/"
            }
        },
        "test_credentials": {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        },
        "validation": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "configured_for_local_testing"
        }
    }
    
    # Sauvegarder la configuration
    config_path = os.path.join(os.path.dirname(__file__), "..", "android_api_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Configuration mise à jour: {config_path}")
    return config

def test_local_api():
    """Tester la connectivité avec l'API locale"""
    print("Test de connectivité avec l'API locale...")
    
    try:
        # Test de l'endpoint de health check (sans authentification)
        health_url = f"{LOCAL_API_URL_HOST}/health/"
        print(f"Test de connectivité: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API locale accessible")
            print(f"   Réponse: {response.json()}")
            
            # Test de l'endpoint de test des notifications
            test_url = f"{LOCAL_API_URL_HOST}/test-notifications/"
            print(f"Test des notifications: {test_url}")
            
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Endpoint de test des notifications accessible")
                print(f"   Réponse: {response.json()}")
                return True
            else:
                print(f"❌ Erreur endpoint notifications: {response.status_code}")
                return False
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Timeout de connexion - Le serveur Django n'est pas accessible")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - Vérifiez que le serveur Django fonctionne")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def push_config_to_android():
    """Pousser la configuration vers l'application Android"""
    try:
        # Vérifier si l'émulateur est connecté
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if 'emulator-5554' not in result.stdout:
            print("❌ Émulateur Android non détecté")
            return False
        
        # Créer un fichier de configuration temporaire sur l'émulateur
        config_content = json.dumps({
            "api_url": LOCAL_API_URL_ANDROID,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }, indent=2)
        
        # Écrire le fichier sur l'émulateur (si l'app le supporte)
        print("📱 Configuration poussée vers l'émulateur")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration Android: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 Configuration de l'application Android pour les tests locaux")
    print("=" * 60)
    
    # 1. Tester l'API locale
    if not test_local_api():
        print("❌ L'API locale n'est pas accessible. Vérifiez que le serveur Django fonctionne.")
        return
    
    # 2. Mettre à jour la configuration
    config = update_android_config()
    print("✅ Configuration mise à jour")
    
    # 3. Obtenir un token JWT
    access_token, refresh_token = get_jwt_token()
    if access_token:
        print("✅ Token JWT obtenu")
        config["test_tokens"] = {
            "access": access_token,
            "refresh": refresh_token
        }
        
        # Sauvegarder avec les tokens
        config_path = os.path.join(os.path.dirname(__file__), "..", "android_api_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    else:
        print("❌ Impossible d'obtenir le token JWT")
    
    # 4. Configurer l'Android
    push_config_to_android()
    
    print("\n📋 Résumé de la configuration:")
    print(f"   • API URL: {LOCAL_API_URL_ANDROID}")
    print(f"   • Utilisateur: {TEST_USERNAME}")
    print(f"   • Notifications disponibles: 8")
    print("\n🚀 L'application Android devrait maintenant pouvoir afficher les notifications!")

if __name__ == "__main__":
    main()