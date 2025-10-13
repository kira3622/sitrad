#!/usr/bin/env python3
"""
Script de déploiement automatisé pour l'API Béton sur Render
"""
import os
import subprocess
import sys
import json
import time

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            if result.stdout:
                print(f"📝 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Erreur")
            print(f"📝 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def check_git_status():
    """Vérifie le statut Git"""
    print("\n📋 Vérification du statut Git...")
    run_command("git status", "Statut Git")
    
def commit_and_push():
    """Commit et push les changements"""
    print("\n📤 Préparation du déploiement...")
    
    # Ajouter tous les fichiers
    if run_command("git add .", "Ajout des fichiers"):
        # Commit avec message automatique
        commit_msg = f"Deploy API with full features - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        if run_command(f'git commit -m "{commit_msg}"', "Commit des changements"):
            # Push vers le repository
            if run_command("git push origin main", "Push vers GitHub"):
                print("✅ Code déployé avec succès sur GitHub!")
                return True
    return False

def display_deployment_info():
    """Affiche les informations de déploiement"""
    print("\n" + "="*60)
    print("🚀 DÉPLOIEMENT DE L'API BÉTON")
    print("="*60)
    print("\n📋 Informations de déploiement:")
    print("• Service: Render.com")
    print("• Type: Web Service (Free Plan)")
    print("• Base de données: PostgreSQL (Free Plan)")
    print("• URL de production: https://sitrad-web.onrender.com")
    print("• API Endpoint: https://sitrad-web.onrender.com/api/v1/")
    print("\n🔧 Configuration:")
    print("• Python 3.11")
    print("• Django + Django REST Framework")
    print("• Authentification JWT")
    print("• Base de données PostgreSQL")
    print("• Fichiers statiques avec WhiteNoise")

def main():
    """Fonction principale"""
    display_deployment_info()
    
    print("\n🔍 Vérifications pré-déploiement...")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("manage.py"):
        print("❌ Erreur: manage.py non trouvé. Assurez-vous d'être dans le répertoire du projet.")
        sys.exit(1)
    
    # Vérifier la configuration
    if not os.path.exists("render.yaml"):
        print("❌ Erreur: render.yaml non trouvé.")
        sys.exit(1)
    
    if not os.path.exists("requirements.txt"):
        print("❌ Erreur: requirements.txt non trouvé.")
        sys.exit(1)
    
    print("✅ Tous les fichiers de configuration sont présents")
    
    # Vérifier le statut Git
    check_git_status()
    
    # Demander confirmation
    response = input("\n❓ Voulez-vous procéder au déploiement? (y/N): ")
    if response.lower() not in ['y', 'yes', 'oui']:
        print("🚫 Déploiement annulé.")
        sys.exit(0)
    
    # Effectuer le déploiement
    if commit_and_push():
        print("\n" + "="*60)
        print("🎉 DÉPLOIEMENT INITIÉ AVEC SUCCÈS!")
        print("="*60)
        print("\n📋 Prochaines étapes:")
        print("1. Connectez-vous à https://render.com")
        print("2. Créez un nouveau Web Service")
        print("3. Connectez votre repository GitHub")
        print("4. Render détectera automatiquement render.yaml")
        print("5. Le déploiement commencera automatiquement")
        print("\n⏱️  Temps de déploiement estimé: 5-10 minutes")
        print("\n🔗 Une fois déployé, votre API sera accessible à:")
        print("   https://sitrad-web.onrender.com/api/v1/")
        print("\n📚 Documentation de l'API:")
        print("   https://sitrad-web.onrender.com/api/v1/")
        print("   (Interface de navigation Django REST Framework)")
    else:
        print("\n❌ Échec du déploiement. Vérifiez les erreurs ci-dessus.")
        sys.exit(1)

if __name__ == "__main__":
    main()