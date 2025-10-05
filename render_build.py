#!/usr/bin/env python
"""
Script de build pour Render avec diagnostic complet
"""
import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} réussi")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} échoué")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors de {description}: {e}")
        return False

def diagnostic_formules():
    """Diagnostic complet des formules"""
    print("\n=== DIAGNOSTIC FORMULES ===")
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
    django.setup()
    
    try:
        # Test des imports
        from formulas.models import FormuleBeton, CompositionFormule
        from api.views import FormuleBetonViewSet
        from api.serializers import FormuleBetonSerializer
        print("✅ Tous les imports réussis")
        
        # Test de la base de données
        count = FormuleBeton.objects.count()
        print(f"✅ Base de données accessible: {count} formules")
        
        # Test du ViewSet
        viewset = FormuleBetonViewSet()
        queryset = viewset.get_queryset()
        print(f"✅ ViewSet fonctionnel: {queryset.count()} objets")
        
        # Test du routeur
        from api.urls import router
        registry_names = [item[0] for item in router.registry]
        if 'formules' in registry_names:
            print("✅ Formules enregistrées dans le routeur")
        else:
            print("❌ Formules absentes du routeur")
        
        print(f"Routes enregistrées: {registry_names}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")
        return False

def test_api_endpoints():
    """Test des endpoints API"""
    print("\n=== TEST API ENDPOINTS ===")
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_render',
            defaults={'email': 'test@render.com'}
        )
        if created:
            user.set_password('render123')
            user.save()
        
        # Générer un token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Tester l'API
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Test de l'index
        response = client.get('/api/v1/')
        print(f"Index API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'formules' in str(data):
                print("✅ Endpoint formules trouvé dans l'index")
            else:
                print("❌ Endpoint formules absent de l'index")
                print(f"Endpoints disponibles: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        
        # Test direct de l'endpoint formules
        response = client.get('/api/v1/formules/')
        print(f"Endpoint formules direct: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', data))
            print(f"✅ Endpoint formules accessible: {count} éléments")
            return True
        else:
            print(f"❌ Endpoint formules inaccessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return False

def main():
    """Fonction principale de build"""
    print("=== BUILD RENDER - DIAGNOSTIC FORMULES ===")
    
    # 1. Variables d'environnement
    print(f"\n1. DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Non défini')}")
    
    # 2. Installation des dépendances
    if not run_command("pip install -r requirements.txt", "Installation des dépendances"):
        sys.exit(1)
    
    # 3. Collecte des fichiers statiques
    if not run_command("python manage.py collectstatic --noinput", "Collecte des fichiers statiques"):
        print("⚠️ Collecte des fichiers statiques échouée, mais on continue...")
    
    # 4. Diagnostic pré-migration
    print("\n4. Diagnostic pré-migration...")
    diagnostic_formules()
    
    # 5. Migrations
    print("\n5. Gestion des migrations...")
    run_command("python manage.py showmigrations", "Affichage des migrations")
    run_command("python manage.py makemigrations", "Création des migrations")
    
    if not run_command("python manage.py migrate", "Application des migrations"):
        print("❌ Échec des migrations")
        sys.exit(1)
    
    # 6. Diagnostic post-migration
    print("\n6. Diagnostic post-migration...")
    if not diagnostic_formules():
        print("❌ Diagnostic post-migration échoué")
        sys.exit(1)
    
    # 7. Test des endpoints
    print("\n7. Test des endpoints...")
    if not test_api_endpoints():
        print("❌ Test des endpoints échoué")
        sys.exit(1)
    
    print("\n✅ BUILD RENDER TERMINÉ AVEC SUCCÈS")

if __name__ == "__main__":
    main()