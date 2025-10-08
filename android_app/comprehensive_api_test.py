#!/usr/bin/env python3
"""
Test complet de l'API pour simuler l'application Android BetonApp
Ce script teste toutes les fonctionnalités de notification et d'authentification
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuration de l'API
API_BASE_URL = "http://localhost:8000/api/v1"
CONFIG_FILE = "local_test_config.json"

class BetonAppAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.config = self.load_config()
        self.access_token = None
        self.refresh_token = None
        
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Fichier de configuration {CONFIG_FILE} non trouvé")
            return None
    
    def print_header(self, title):
        """Affiche un en-tête formaté"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step, description):
        """Affiche une étape de test"""
        print(f"\n📋 Étape {step}: {description}")
        print("-" * 50)
    
    def test_health_endpoint(self):
        """Test de l'endpoint de santé"""
        self.print_step(1, "Test de l'endpoint de santé")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/health/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Endpoint de santé OK")
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                return True
            else:
                print(f"❌ Endpoint de santé échoué: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def test_authentication(self):
        """Test de l'authentification"""
        self.print_step(2, "Test de l'authentification")
        
        if not self.config:
            print("❌ Configuration manquante")
            return False
        
        auth_data = {
            "username": self.config["test_user"]["username"],
            "password": self.config["test_user"]["password"]
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/auth/token/",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                self.refresh_token = data.get("refresh")
                
                print(f"✅ Authentification réussie")
                print(f"   Utilisateur: {auth_data['username']}")
                print(f"   Token reçu: {self.access_token[:50]}...")
                
                # Mise à jour des headers pour les requêtes suivantes
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                return True
            else:
                print(f"❌ Authentification échouée: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de l'authentification: {e}")
            return False
    
    def test_token_refresh(self):
        """Test du rafraîchissement de token"""
        self.print_step(3, "Test du rafraîchissement de token")
        
        if not self.refresh_token:
            print("❌ Pas de refresh token disponible")
            return False
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/auth/token/refresh/",
                json={"refresh": self.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get("access")
                
                print(f"✅ Rafraîchissement de token réussi")
                print(f"   Nouveau token: {new_access_token[:50]}...")
                
                # Mise à jour du token
                self.access_token = new_access_token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                return True
            else:
                print(f"❌ Rafraîchissement échoué: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors du rafraîchissement: {e}")
            return False
    
    def test_notifications_endpoint(self):
        """Test de l'endpoint des notifications"""
        self.print_step(4, "Test de l'endpoint des notifications")
        
        if not self.access_token:
            print("❌ Pas de token d'accès disponible")
            return False
        
        try:
            response = self.session.get(
                f"{API_BASE_URL}/notifications/",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('results', [])
                
                print(f"✅ Récupération des notifications réussie")
                print(f"   Nombre total: {data.get('count', 0)}")
                print(f"   Notifications récupérées: {len(notifications)}")
                
                # Affichage des premières notifications
                if notifications:
                    print(f"\n📱 Aperçu des notifications:")
                    for i, notif in enumerate(notifications[:3]):
                        print(f"   {i+1}. {notif.get('title', 'Sans titre')}")
                        print(f"      Message: {notif.get('message', 'Sans message')[:50]}...")
                        print(f"      Type: {notif.get('notification_type', 'N/A')}")
                        print(f"      Lue: {'Oui' if notif.get('is_read') else 'Non'}")
                        print()
                
                return True
            else:
                print(f"❌ Récupération des notifications échouée: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la récupération: {e}")
            return False
    
    def test_notification_details(self):
        """Test de récupération des détails d'une notification"""
        self.print_step(5, "Test des détails de notification")
        
        # D'abord, récupérer une notification
        try:
            response = self.session.get(f"{API_BASE_URL}/notifications/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('results', [])
                
                if notifications:
                    first_notif = notifications[0]
                    notif_id = first_notif.get('id')
                    
                    # Récupérer les détails
                    detail_response = self.session.get(
                        f"{API_BASE_URL}/notifications/{notif_id}/",
                        timeout=10
                    )
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        print(f"✅ Détails de notification récupérés")
                        print(f"   ID: {detail_data.get('id')}")
                        print(f"   Titre: {detail_data.get('title')}")
                        print(f"   Message: {detail_data.get('message')}")
                        print(f"   Date: {detail_data.get('created_at')}")
                        return True
                    else:
                        print(f"❌ Récupération des détails échouée: {detail_response.status_code}")
                        return False
                else:
                    print("⚠️ Aucune notification disponible pour tester les détails")
                    return True
            else:
                print(f"❌ Impossible de récupérer les notifications: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors du test des détails: {e}")
            return False
    
    def test_mark_notification_read(self):
        """Test de marquage d'une notification comme lue"""
        self.print_step(6, "Test de marquage comme lue")
        
        try:
            # Récupérer une notification non lue
            response = self.session.get(f"{API_BASE_URL}/notifications/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('results', [])
                
                unread_notif = None
                for notif in notifications:
                    if not notif.get('is_read', True):
                        unread_notif = notif
                        break
                
                if unread_notif:
                    notif_id = unread_notif.get('id')
                    
                    # Marquer comme lue
                    mark_response = self.session.patch(
                        f"{API_BASE_URL}/notifications/{notif_id}/",
                        json={"is_read": True},
                        timeout=10
                    )
                    
                    if mark_response.status_code == 200:
                        print(f"✅ Notification marquée comme lue")
                        print(f"   ID: {notif_id}")
                        print(f"   Titre: {unread_notif.get('title')}")
                        return True
                    else:
                        print(f"❌ Marquage échoué: {mark_response.status_code}")
                        return False
                else:
                    print("⚠️ Aucune notification non lue trouvée")
                    return True
            else:
                print(f"❌ Impossible de récupérer les notifications: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors du marquage: {e}")
            return False
    
    def test_performance(self):
        """Test de performance de l'API"""
        self.print_step(7, "Test de performance")
        
        print("🚀 Test de performance en cours...")
        
        # Test de 10 requêtes consécutives
        times = []
        success_count = 0
        
        for i in range(10):
            start_time = time.time()
            try:
                response = self.session.get(f"{API_BASE_URL}/notifications/", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    success_count += 1
                    times.append(end_time - start_time)
                    
            except requests.exceptions.RequestException:
                pass
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"✅ Test de performance terminé")
            print(f"   Requêtes réussies: {success_count}/10")
            print(f"   Temps moyen: {avg_time:.3f}s")
            print(f"   Temps minimum: {min_time:.3f}s")
            print(f"   Temps maximum: {max_time:.3f}s")
            
            return success_count >= 8  # Au moins 80% de réussite
        else:
            print("❌ Aucune requête réussie")
            return False
    
    def run_comprehensive_test(self):
        """Lance tous les tests"""
        self.print_header("TEST COMPLET DE L'API BETONAPP")
        
        print(f"🕐 Début des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL de l'API: {API_BASE_URL}")
        
        tests = [
            ("Santé de l'API", self.test_health_endpoint),
            ("Authentification", self.test_authentication),
            ("Rafraîchissement de token", self.test_token_refresh),
            ("Récupération des notifications", self.test_notifications_endpoint),
            ("Détails de notification", self.test_notification_details),
            ("Marquage comme lue", self.test_mark_notification_read),
            ("Performance", self.test_performance)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: RÉUSSI")
                else:
                    print(f"❌ {test_name}: ÉCHOUÉ")
                    
                time.sleep(1)  # Pause entre les tests
                
            except Exception as e:
                print(f"❌ {test_name}: ERREUR - {e}")
                results.append((test_name, False))
        
        # Résumé final
        self.print_header("RÉSUMÉ DES TESTS")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"📊 Résultats: {passed}/{total} tests réussis")
        print(f"📈 Taux de réussite: {(passed/total)*100:.1f}%")
        
        print(f"\n📋 Détail des résultats:")
        for test_name, result in results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
            print(f"   {test_name}: {status}")
        
        if passed == total:
            print(f"\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
            print(f"   L'application Android devrait fonctionner parfaitement avec cette API.")
        elif passed >= total * 0.8:
            print(f"\n⚠️ LA PLUPART DES TESTS SONT RÉUSSIS")
            print(f"   L'application Android devrait fonctionner correctement.")
        else:
            print(f"\n❌ PLUSIEURS TESTS ONT ÉCHOUÉ")
            print(f"   Des problèmes peuvent survenir avec l'application Android.")
        
        print(f"\n🕐 Fin des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed == total

def main():
    """Fonction principale"""
    print("🤖 BetonApp API Tester - Simulation complète de l'application Android")
    print("=" * 80)
    
    tester = BetonAppAPITester()
    success = tester.run_comprehensive_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()