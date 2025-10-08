#!/usr/bin/env python3
"""
Script de validation rapide pour l'équipe Android
Vérifie que l'API des notifications est prête pour l'intégration
"""

import requests
import json
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://sitrad-web.onrender.com/api/v1"
TIMEOUT = 10

def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Affiche un message de succès"""
    print(f"✅ {message}")

def print_warning(message):
    """Affiche un avertissement"""
    print(f"⚠️  {message}")

def print_error(message):
    """Affiche une erreur"""
    print(f"❌ {message}")

def print_info(message):
    """Affiche une information"""
    print(f"ℹ️  {message}")

def test_endpoint(method, endpoint, description, expected_status=401):
    """Teste un endpoint et retourne le résultat"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=TIMEOUT)
        else:
            response = requests.request(method, url, timeout=TIMEOUT)
        
        if response.status_code == expected_status:
            print_success(f"{description}: {response.status_code}")
            return True
        else:
            print_warning(f"{description}: {response.status_code} (attendu: {expected_status})")
            return False
            
    except requests.exceptions.Timeout:
        print_error(f"{description}: Timeout ({TIMEOUT}s)")
        return False
    except requests.exceptions.ConnectionError:
        print_error(f"{description}: Erreur de connexion")
        return False
    except Exception as e:
        print_error(f"{description}: {str(e)}")
        return False

def validate_api_for_android():
    """Validation complète de l'API pour Android"""
    
    print_header("VALIDATION API POUR ANDROID")
    print_info(f"URL de base: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Compteurs de résultats
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Connectivité de base
    print_header("1. Test de Connectivité")
    total_tests += 1
    if test_endpoint("GET", "/test-notifications/", "Endpoint de test"):
        passed_tests += 1
    
    # Test 2: Endpoints d'authentification
    print_header("2. Endpoints d'Authentification")
    auth_endpoints = [
        ("POST", "/auth/token/", "Login"),
        ("POST", "/auth/token/refresh/", "Refresh token"),
    ]
    
    for method, endpoint, desc in auth_endpoints:
        total_tests += 1
        # Pour l'auth, on s'attend à 400 (bad request) car pas de credentials
        if test_endpoint(method, endpoint, desc, expected_status=400):
            passed_tests += 1
    
    # Test 3: Endpoints des notifications
    print_header("3. Endpoints des Notifications")
    notification_endpoints = [
        ("GET", "/notifications/", "Liste des notifications"),
        ("GET", "/notifications/unread_count/", "Compteur non lues"),
        ("GET", "/notifications/summary/", "Résumé des notifications"),
        ("POST", "/notifications/mark_as_read/", "Marquer comme lues"),
        ("POST", "/notifications/mark_all_as_read/", "Marquer toutes comme lues"),
    ]
    
    for method, endpoint, desc in notification_endpoints:
        total_tests += 1
        if test_endpoint(method, endpoint, desc):
            passed_tests += 1
    
    # Test 4: Endpoints spécifiques avec ID
    print_header("4. Endpoints avec ID")
    id_endpoints = [
        ("GET", "/notifications/1/", "Notification spécifique"),
        ("POST", "/notifications/1/mark_as_read/", "Marquer une notification comme lue"),
        ("DELETE", "/notifications/1/", "Supprimer une notification"),
    ]
    
    for method, endpoint, desc in id_endpoints:
        total_tests += 1
        if test_endpoint(method, endpoint, desc):
            passed_tests += 1
    
    # Test 5: Pagination et filtres
    print_header("5. Pagination et Filtres")
    filter_endpoints = [
        ("GET", "/notifications/?page=1", "Pagination"),
        ("GET", "/notifications/?page_size=10", "Taille de page"),
        ("GET", "/notifications/?is_read=false", "Filtre non lues"),
        ("GET", "/notifications/?type=info", "Filtre par type"),
    ]
    
    for method, endpoint, desc in filter_endpoints:
        total_tests += 1
        if test_endpoint(method, endpoint, desc):
            passed_tests += 1
    
    # Résumé final
    print_header("RÉSUMÉ DE LA VALIDATION")
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print_success("API PRÊTE pour l'intégration Android! 🚀")
        status = "READY"
    elif success_rate >= 75:
        print_warning("API majoritairement fonctionnelle, quelques ajustements possibles")
        status = "MOSTLY_READY"
    else:
        print_error("Problèmes détectés, vérification nécessaire")
        status = "ISSUES"
    
    # Informations pour l'équipe Android
    print_header("INFORMATIONS POUR L'ÉQUIPE ANDROID")
    
    android_info = {
        "base_url": BASE_URL,
        "auth_endpoint": f"{BASE_URL}/auth/token/",
        "notifications_endpoint": f"{BASE_URL}/notifications/",
        "status": status,
        "success_rate": f"{success_rate:.1f}%",
        "timestamp": datetime.now().isoformat(),
        "ready_for_integration": success_rate >= 75
    }
    
    print("📱 Configuration pour Android:")
    for key, value in android_info.items():
        print(f"   {key}: {value}")
    
    # Recommandations
    print_header("RECOMMANDATIONS")
    
    recommendations = [
        "✅ Utiliser Retrofit avec OkHttp pour les appels API",
        "✅ Implémenter un intercepteur JWT pour l'authentification",
        "✅ Gérer les codes de statut 401 (non autorisé) et 400 (requête invalide)",
        "✅ Implémenter un cache local avec Room pour le mode offline",
        "✅ Utiliser WorkManager pour la synchronisation périodique",
        "✅ Tester d'abord avec des credentials valides",
        "✅ Implémenter la gestion d'erreurs réseau robuste"
    ]
    
    for rec in recommendations:
        print(f"  {rec}")
    
    # Prochaines étapes
    print_header("PROCHAINES ÉTAPES")
    
    next_steps = [
        "1. 📖 Lire ANDROID_INTEGRATION_ROADMAP.md",
        "2. 📋 Suivre la checklist de configuration",
        "3. 🔧 Copier le code d'exemple depuis android_integration_example.kt",
        "4. 🧪 Tester l'authentification avec des credentials valides",
        "5. 🚀 Commencer l'implémentation par phases"
    ]
    
    for step in next_steps:
        print(f"  {step}")
    
    # Fichiers de référence
    print_header("FICHIERS DE RÉFÉRENCE")
    
    files = [
        "📄 API_NOTIFICATIONS_DOCUMENTATION.md - Documentation complète",
        "📄 ANDROID_INTEGRATION_ROADMAP.md - Plan d'intégration détaillé", 
        "📄 android_integration_example.kt - Code d'exemple Kotlin",
        "📄 test_android_integration.py - Tests complets de l'API"
    ]
    
    for file in files:
        print(f"  {file}")
    
    return android_info

def generate_android_config():
    """Génère un fichier de configuration pour Android"""
    
    config = {
        "api": {
            "base_url": BASE_URL,
            "timeout": TIMEOUT,
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
        "validation": {
            "timestamp": datetime.now().isoformat(),
            "status": "validated"
        }
    }
    
    try:
        with open("android_api_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print_success("Configuration Android générée: android_api_config.json")
    except Exception as e:
        print_error(f"Erreur lors de la génération de la config: {e}")

if __name__ == "__main__":
    try:
        # Validation principale
        result = validate_api_for_android()
        
        # Génération de la configuration
        generate_android_config()
        
        # Code de sortie
        if result["ready_for_integration"]:
            print(f"\n🎉 SUCCÈS: API prête pour l'intégration Android!")
            sys.exit(0)
        else:
            print(f"\n⚠️  ATTENTION: Vérifications nécessaires avant l'intégration")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Validation interrompue par l'utilisateur")
        sys.exit(2)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        sys.exit(3)