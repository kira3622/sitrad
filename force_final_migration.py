#!/usr/bin/env python3
"""
Script pour forcer une migration finale en créant un commit spécial
"""

import subprocess
import time
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "https://sitrad-web.onrender.com"
USERNAME = "admin"
PASSWORD = "admin123"

def run_command(command, cwd=None):
    """Exécuter une commande shell"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def get_auth_token():
    """Obtenir le token d'authentification"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("access")
        return None
    except:
        return None

def check_migrations_applied():
    """Vérifier si les migrations sont appliquées"""
    token = get_auth_token()
    if not token:
        return False, "Impossible d'obtenir le token"
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test endpoint /pompes/
        pompes_response = requests.get(f"{API_BASE_URL}/pompes/", headers=headers, timeout=30)
        pompes_ok = pompes_response.status_code == 200
        
        # Test champs Production
        prod_response = requests.get(f"{API_BASE_URL}/production/", headers=headers, timeout=30)
        if prod_response.status_code == 200:
            data = prod_response.json()
            if data.get("results") and len(data["results"]) > 0:
                first_order = data["results"][0]
                pompe_fields = [
                    "pompe_nom", "pompe_marque", "pompe_modele", 
                    "pompe_statut", "pompe_debit_max", "pompe_operateur_nom"
                ]
                fields_present = all(field in first_order for field in pompe_fields)
                
                return pompes_ok and fields_present, {
                    "pompes_endpoint": pompes_ok,
                    "production_fields": fields_present,
                    "missing_fields": [f for f in pompe_fields if f not in first_order]
                }
        
        return False, "Erreur lors de la vérification"
    except Exception as e:
        return False, str(e)

def create_migration_trigger():
    """Créer un fichier trigger pour forcer les migrations"""
    trigger_content = f"""# Migration Trigger - {datetime.now().isoformat()}
# Ce fichier force l'exécution des migrations lors du déploiement

FORCE_MIGRATION = True
MIGRATION_TIMESTAMP = "{datetime.now().isoformat()}"

# Commandes à exécuter:
# 1. python manage.py makemigrations production --name add_pompes_fields
# 2. python manage.py migrate --noinput
# 3. python manage.py collectstatic --noinput
"""
    
    with open("migration_trigger.py", "w", encoding="utf-8") as f:
        f.write(trigger_content)
    
    return True

def force_deployment():
    """Forcer un nouveau déploiement avec trigger de migration"""
    print("🚀 Forçage d'un nouveau déploiement avec migration...")
    
    # 1. Créer le fichier trigger
    print("📝 Création du fichier trigger...")
    create_migration_trigger()
    
    # 2. Modifier render_build.py pour être plus agressif
    print("🔧 Modification du script de build...")
    
    # Lire le contenu actuel
    with open("render_build.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Ajouter une section de debug plus agressive
    debug_section = '''
    
    # === SECTION DE DEBUG AGRESSIVE ===
    print("🔥 FORÇAGE DES MIGRATIONS - DEBUG AGRESSIF")
    print(f"📅 Timestamp: {datetime.now()}")
    
    # Vérifier les migrations en attente
    print("🔍 Vérification des migrations en attente...")
    result = subprocess.run([
        sys.executable, "manage.py", "showmigrations", "--plan"
    ], capture_output=True, text=True)
    print(f"📋 Migrations plan:\\n{result.stdout}")
    
    # Forcer la création de migrations pour production
    print("🏗️  Création forcée des migrations production...")
    result = subprocess.run([
        sys.executable, "manage.py", "makemigrations", "production", 
        "--name", "force_add_pompes_fields", "--verbosity", "2"
    ], capture_output=True, text=True)
    print(f"📝 Makemigrations output:\\n{result.stdout}")
    if result.stderr:
        print(f"⚠️  Makemigrations errors:\\n{result.stderr}")
    
    # Appliquer toutes les migrations avec verbosité maximale
    print("🚀 Application forcée de toutes les migrations...")
    result = subprocess.run([
        sys.executable, "manage.py", "migrate", "--verbosity", "2", "--noinput"
    ], capture_output=True, text=True)
    print(f"✅ Migration output:\\n{result.stdout}")
    if result.stderr:
        print(f"⚠️  Migration errors:\\n{result.stderr}")
    
    # Vérifier l'état final
    print("🔍 Vérification finale des migrations...")
    result = subprocess.run([
        sys.executable, "manage.py", "showmigrations"
    ], capture_output=True, text=True)
    print(f"📊 État final des migrations:\\n{result.stdout}")
    
    print("🏁 SECTION DE DEBUG AGRESSIVE TERMINÉE")
    # === FIN SECTION DE DEBUG AGRESSIVE ===
'''
    
    # Insérer avant la ligne "if __name__ == '__main__':"
    if 'if __name__ == "__main__":' in content:
        content = content.replace(
            'if __name__ == "__main__":',
            debug_section + '\nif __name__ == "__main__":'
        )
    
    # Écrire le contenu modifié
    with open("render_build.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    # 3. Commit et push
    print("📦 Création du commit de migration forcée...")
    
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ Erreur git add: {stderr}")
        return False
    
    commit_msg = f"FORCE MIGRATION: Déploiement avec debug agressif - {datetime.now().strftime('%H:%M:%S')}"
    success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    if not success:
        print(f"❌ Erreur git commit: {stderr}")
        return False
    
    print("🚀 Push vers le dépôt...")
    success, stdout, stderr = run_command("git push origin main")
    if not success:
        print(f"❌ Erreur git push: {stderr}")
        return False
    
    print("✅ Déploiement déclenché avec succès!")
    return True

def monitor_final_deployment():
    """Surveiller le déploiement final"""
    print("\n🔍 Surveillance du déploiement final...")
    
    max_attempts = 15  # 7.5 minutes
    for attempt in range(1, max_attempts + 1):
        print(f"\n📊 Tentative {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        # Vérifier l'API
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=10)
            api_ok = response.status_code == 200
            print(f"   API Status: {'✅ OK' if api_ok else '❌ DOWN'}")
            
            if api_ok:
                # Vérifier les migrations
                migrations_ok, details = check_migrations_applied()
                print(f"   Migrations: {'✅ APPLIQUÉES' if migrations_ok else '❌ EN ATTENTE'}")
                
                if not migrations_ok and isinstance(details, dict):
                    print(f"   - Endpoint /pompes/: {'✅' if details.get('pompes_endpoint') else '❌'}")
                    print(f"   - Champs Production: {'✅' if details.get('production_fields') else '❌'}")
                    if details.get('missing_fields'):
                        print(f"   - Champs manquants: {details['missing_fields']}")
                
                if migrations_ok:
                    print("\n🎉 SUCCÈS! Toutes les migrations sont appliquées!")
                    return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        if attempt < max_attempts:
            print("   ⏳ Attente de 30 secondes...")
            time.sleep(30)
    
    print(f"\n⏰ Timeout atteint après {max_attempts} tentatives")
    return False

if __name__ == "__main__":
    print("🔥 FORÇAGE FINAL DES MIGRATIONS")
    print("=" * 50)
    
    # Vérifier l'état actuel
    print("🔍 Vérification de l'état actuel...")
    migrations_ok, details = check_migrations_applied()
    
    if migrations_ok:
        print("✅ Les migrations sont déjà appliquées!")
    else:
        print("❌ Les migrations ne sont pas appliquées")
        print(f"📋 Détails: {details}")
        
        # Forcer le déploiement
        if force_deployment():
            print("\n🚀 Déploiement forcé lancé!")
            
            # Surveiller
            success = monitor_final_deployment()
            
            if success:
                print("\n🎉 DÉPLOIEMENT RÉUSSI!")
                print("✅ Toutes les migrations ont été appliquées")
                print("✅ L'intégration des pompes est complète")
            else:
                print("\n⚠️  DÉPLOIEMENT INCOMPLET")
                print("❌ Intervention manuelle requise sur Render.com")
        else:
            print("❌ Échec du forçage du déploiement")