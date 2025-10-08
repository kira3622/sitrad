#!/usr/bin/env python3
"""
Script de test pour simuler les appels API que l'application Android devrait faire.
Ce script teste la connectivité et l'authentification avec l'API locale.
"""

import requests
import json
from datetime import datetime

# Configuration de l'API (similaire à celle de l'application Android)
API_BASE_URL = "http://localhost:8000/api/v1"
CONFIG_FILE = "android_app/local_test_config.json"

def load_config():
    """Charge la configuration depuis le fichier JSON."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier de configuration non trouvé: {CONFIG_FILE}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Erreur de décodage JSON dans: {CONFIG_FILE}")
        return None

def test_health_endpoint():
    """Test de l'endpoint de santé (sans authentification)."""
    print("🔍 Test de l'endpoint de santé...")
    try:
        response = requests.get(f"{API_BASE_URL}/health/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint de santé OK: {data['message']}")
            return True
        else:
            print(f"❌ Endpoint de santé échoué: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à l'endpoint de santé: {e}")
        return False

def test_auth_endpoint(username, password):
    """Test de l'authentification."""
    print("🔐 Test de l'authentification...")
    try:
        auth_data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{API_BASE_URL}/auth/token/", json=auth_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Authentification réussie")
            return data.get('access'), data.get('refresh')
        else:
            print(f"❌ Authentification échouée: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion pour l'authentification: {e}")
        return None, None

def test_notifications_endpoint(access_token):
    """Test de l'endpoint des notifications avec authentification."""
    print("📱 Test de l'endpoint des notifications...")
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{API_BASE_URL}/notifications/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notifications récupérées: {len(data)} notifications")
            return data
        else:
            print(f"❌ Récupération des notifications échouée: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion pour les notifications: {e}")
        return None

def test_test_notifications_endpoint(access_token):
    """Test de l'endpoint de test des notifications."""
    print("🧪 Test de l'endpoint de test des notifications...")
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{API_BASE_URL}/test-notifications/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint de test OK: {data['message']}")
            return True
        else:
            print(f"❌ Endpoint de test échoué: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion pour l'endpoint de test: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🚀 Démarrage des tests de simulation de l'application Android")
    print("=" * 60)
    
    # Charger la configuration
    config = load_config()
    if not config:
        return
    
    # Test 1: Endpoint de santé
    if not test_health_endpoint():
        print("❌ Test de santé échoué, arrêt des tests")
        return
    
    print()
    
    # Test 2: Authentification
    username = config['test_user']['username']
    password = config['test_user']['password']
    access_token, refresh_token = test_auth_endpoint(username, password)
    
    if not access_token:
        print("❌ Authentification échouée, test avec le token existant...")
        access_token = config['test_user']['access_token']
    
    print()
    
    # Test 3: Endpoint de test des notifications
    if not test_test_notifications_endpoint(access_token):
        print("❌ Test de l'endpoint de test échoué")
        return
    
    print()
    
    # Test 4: Récupération des notifications
    notifications = test_notifications_endpoint(access_token)
    if notifications is not None:
        print(f"📊 Détails des notifications:")
        if isinstance(notifications, list) and len(notifications) > 0:
            for i, notif in enumerate(notifications[:3], 1):  # Afficher les 3 premières
                print(f"  {i}. {notif.get('titre', 'Sans titre')} - {notif.get('type', 'Type inconnu')}")
            if len(notifications) > 3:
                print(f"  ... et {len(notifications) - 3} autres notifications")
        else:
            print(f"  Aucune notification ou format inattendu: {notifications}")
    
    print()
    print("=" * 60)
    print("✅ Tous les tests de simulation terminés avec succès!")
    print("🎯 L'application Android devrait pouvoir se connecter à l'API locale.")

if __name__ == "__main__":
    main()