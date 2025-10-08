#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration des notifications
avec l'application Android installée sur l'émulateur.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://sitrad-web.onrender.com/api/v1"
EMULATOR_PACKAGE = "com.betonapp.debug"

def test_api_connectivity():
    """Test de connectivité avec l'API"""
    print("🔗 Test de connectivité avec l'API...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API non accessible (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Erreur de connectivité: {e}")
        return False

def test_notifications_endpoint():
    """Test de l'endpoint des notifications"""
    print("\n📱 Test de l'endpoint des notifications...")
    try:
        response = requests.get(f"{API_BASE_URL}/notifications/", timeout=10)
        if response.status_code == 401:
            print("✅ Endpoint des notifications accessible (authentification requise)")
            return True
        elif response.status_code == 200:
            print("✅ Endpoint des notifications accessible")
            return True
        else:
            print(f"❌ Endpoint non accessible (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_app_installation():
    """Vérifier que l'application est installée"""
    print("\n📲 Vérification de l'installation de l'application...")
    import subprocess
    try:
        result = subprocess.run(
            ["adb", "shell", "pm", "list", "packages", EMULATOR_PACKAGE],
            capture_output=True,
            text=True,
            timeout=10
        )
        if EMULATOR_PACKAGE in result.stdout:
            print("✅ Application BetonApp installée sur l'émulateur")
            return True
        else:
            print("❌ Application non trouvée sur l'émulateur")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def test_app_running():
    """Vérifier que l'application est en cours d'exécution"""
    print("\n🏃 Vérification de l'exécution de l'application...")
    import subprocess
    try:
        result = subprocess.run(
            ["adb", "shell", "pidof", EMULATOR_PACKAGE],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout.strip():
            pid = result.stdout.strip()
            print(f"✅ Application en cours d'exécution (PID: {pid})")
            return True
        else:
            print("❌ Application non en cours d'exécution")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def test_network_connectivity_from_emulator():
    """Test de connectivité réseau depuis l'émulateur"""
    print("\n🌐 Test de connectivité réseau depuis l'émulateur...")
    import subprocess
    try:
        result = subprocess.run(
            ["adb", "shell", "ping", "-c", "1", "sitrad-web.onrender.com"],
            capture_output=True,
            text=True,
            timeout=15
        )
        if "1 packets transmitted, 1 received" in result.stdout:
            print("✅ Connectivité réseau OK depuis l'émulateur")
            return True
        else:
            print("❌ Problème de connectivité réseau depuis l'émulateur")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test de connectivité: {e}")
        return False

def generate_test_report():
    """Générer un rapport de test"""
    print("\n" + "="*60)
    print("📊 RAPPORT DE TEST - INTÉGRATION NOTIFICATIONS")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_BASE_URL}")
    print(f"Application: {EMULATOR_PACKAGE}")
    
    tests = [
        ("Connectivité API", test_api_connectivity),
        ("Endpoint Notifications", test_notifications_endpoint),
        ("Installation App", test_app_installation),
        ("Exécution App", test_app_running),
        ("Connectivité Émulateur", test_network_connectivity_from_emulator)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    print(f"\nTaux de réussite: {success_rate:.1f}% ({passed}/{len(results)})")
    
    if success_rate >= 80:
        print("\n🎉 INTÉGRATION PRÊTE POUR LES TESTS UTILISATEUR!")
        print("L'application peut maintenant être testée avec l'API des notifications.")
    else:
        print("\n⚠️ PROBLÈMES DÉTECTÉS")
        print("Certains tests ont échoué. Vérifiez la configuration.")
    
    return success_rate

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE DES TESTS D'INTÉGRATION NOTIFICATIONS")
    print("="*60)
    
    success_rate = generate_test_report()
    
    print("\n📝 PROCHAINES ÉTAPES:")
    if success_rate >= 80:
        print("1. Tester la connexion utilisateur dans l'app")
        print("2. Vérifier l'affichage des notifications")
        print("3. Tester les actions (marquer comme lu, etc.)")
        print("4. Valider la synchronisation en temps réel")
    else:
        print("1. Résoudre les problèmes identifiés")
        print("2. Relancer les tests")
        print("3. Vérifier la configuration réseau")
    
    return success_rate

if __name__ == "__main__":
    main()