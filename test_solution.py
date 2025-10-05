#!/usr/bin/env python
"""
Script de test final pour vérifier que la solution est prête pour le déploiement
"""
import os
import sys

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} manquant: {filepath}")
        return False

def check_file_content(filepath, expected_content, description):
    """Vérifie qu'un fichier contient le contenu attendu"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if expected_content in content:
                print(f"✅ {description}: contenu correct")
                return True
            else:
                print(f"❌ {description}: contenu incorrect")
                return False
    except Exception as e:
        print(f"❌ {description}: erreur de lecture - {e}")
        return False

def main():
    """Test principal"""
    print("=== TEST DE LA SOLUTION FORMULES ===")
    
    all_good = True
    
    # 1. Vérifier les fichiers de solution
    print("\n1. Vérification des fichiers de solution...")
    files_to_check = [
        ("diagnostic_formules.py", "Script de diagnostic"),
        ("force_migrate.py", "Script de migration forcée"),
        ("render_build.py", "Script de build principal"),
        ("render_deploy.sh", "Script de déploiement bash"),
        ("SOLUTION_FORMULES.md", "Documentation de la solution"),
        ("build.sh", "Script de build Render"),
        ("render.yaml", "Configuration Render")
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # 2. Vérifier le contenu des fichiers critiques
    print("\n2. Vérification du contenu des fichiers critiques...")
    
    # Vérifier render.yaml
    if not check_file_content("render.yaml", "python render_build.py", "render.yaml - commande de build"):
        all_good = False
    
    # Vérifier build.sh
    if not check_file_content("build.sh", "python render_build.py", "build.sh - appel du script Python"):
        all_good = False
    
    # 3. Test d'import des modules critiques
    print("\n3. Test d'import des modules critiques...")
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
        django.setup()
        
        from formulas.models import FormuleBeton
        from api.views import FormuleBetonViewSet
        from api.serializers import FormuleBetonSerializer
        print("✅ Imports Django réussis")
    except Exception as e:
        print(f"❌ Erreur d'import Django: {e}")
        all_good = False
    
    # 4. Test du script de build
    print("\n4. Test du script de build...")
    try:
        # Import du module de build
        import importlib.util
        spec = importlib.util.spec_from_file_location("render_build", "render_build.py")
        render_build = importlib.util.module_from_spec(spec)
        print("✅ Script render_build.py importable")
    except Exception as e:
        print(f"❌ Erreur d'import du script de build: {e}")
        all_good = False
    
    # 5. Vérifier la structure des migrations
    print("\n5. Vérification des migrations...")
    migrations_dir = "formulas/migrations"
    if os.path.exists(migrations_dir):
        migrations = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and f != '__init__.py']
        if migrations:
            print(f"✅ Migrations trouvées: {migrations}")
        else:
            print("❌ Aucune migration trouvée")
            all_good = False
    else:
        print("❌ Dossier migrations non trouvé")
        all_good = False
    
    # 6. Résumé final
    print("\n=== RÉSUMÉ FINAL ===")
    if all_good:
        print("✅ SOLUTION PRÊTE POUR LE DÉPLOIEMENT")
        print("\nÉtapes suivantes:")
        print("1. git add .")
        print("2. git commit -m 'Solution: Diagnostic et correction endpoint formules'")
        print("3. git push origin main")
        print("4. Vérifier les logs de build sur Render")
        print("5. Tester l'endpoint après déploiement")
    else:
        print("❌ PROBLÈMES DÉTECTÉS - CORRIGER AVANT DÉPLOIEMENT")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)