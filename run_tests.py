#!/usr/bin/env python
"""
Script pour exécuter tous les tests automatisés de l'application Béton App
"""
import os
import sys
import subprocess
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

def run_command(command, description):
    """Exécuter une commande et afficher le résultat"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.stdout:
            print("📋 SORTIE:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ ERREURS:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCÈS")
        else:
            print(f"❌ {description} - ÉCHEC (code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False

def check_dependencies():
    """Vérifier que les dépendances nécessaires sont installées"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = ['pytest', 'pytest-django', 'pytest-cov']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Packages manquants: {', '.join(missing_packages)}")
        print("📦 Installation des packages manquants...")
        
        install_cmd = f"pip install {' '.join(missing_packages)}"
        if not run_command(install_cmd, "Installation des dépendances"):
            return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def run_django_tests():
    """Exécuter les tests Django natifs"""
    return run_command(
        "python manage.py test --verbosity=2",
        "Tests Django natifs"
    )

def run_pytest_tests():
    """Exécuter les tests pytest"""
    return run_command(
        "pytest tests/ -v --tb=short",
        "Tests pytest"
    )

def run_pytest_with_coverage():
    """Exécuter les tests avec coverage"""
    return run_command(
        "pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-exclude=*/migrations/* --cov-exclude=*/venv/* --cov-exclude=*/env/* --cov-exclude=manage.py",
        "Tests avec couverture de code"
    )

def run_api_integration_tests():
    """Exécuter les tests d'intégration de l'API"""
    return run_command(
        "python test_endpoint_simple.py",
        "Tests d'intégration API existants"
    )

def run_specific_tests():
    """Exécuter des tests spécifiques existants"""
    test_files = [
        "test_clients_chantiers.py",
        "test_filtrage_chantiers.py",
        "test_fuel_system.py",
        "test_material_calculation.py",
        "test_seuils_configurables.py",
        "test_seuils_par_matiere.py"
    ]
    
    success_count = 0
    for test_file in test_files:
        if Path(test_file).exists():
            if run_command(f"python {test_file}", f"Test spécifique: {test_file}"):
                success_count += 1
    
    print(f"\n📊 Tests spécifiques: {success_count}/{len(test_files)} réussis")
    return success_count == len(test_files)

def generate_test_report():
    """Générer un rapport de test"""
    print(f"\n{'='*60}")
    print("📊 RAPPORT DE TESTS")
    print(f"{'='*60}")
    
    # Vérifier si le rapport de couverture existe
    coverage_html = Path("htmlcov/index.html")
    if coverage_html.exists():
        print(f"📈 Rapport de couverture généré: {coverage_html.absolute()}")
    
    # Statistiques des fichiers de test
    test_files = list(Path("tests").glob("*.py")) if Path("tests").exists() else []
    print(f"📁 Fichiers de test pytest: {len(test_files)}")
    
    existing_tests = [f for f in Path(".").glob("test_*.py")]
    print(f"📁 Tests spécifiques existants: {len(existing_tests)}")
    
    print("\n🎯 RECOMMANDATIONS:")
    print("1. Consultez le rapport de couverture HTML pour identifier les zones non testées")
    print("2. Ajoutez des tests pour les nouvelles fonctionnalités")
    print("3. Exécutez les tests régulièrement pendant le développement")
    print("4. Configurez l'intégration continue pour automatiser les tests")

def main():
    """Fonction principale"""
    print("🚀 LANCEMENT DES TESTS AUTOMATISÉS - BÉTON APP")
    print(f"📍 Répertoire: {Path.cwd()}")
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("❌ Impossible de continuer sans les dépendances requises")
        sys.exit(1)
    
    # Compteur de succès
    tests_passed = 0
    total_tests = 0
    
    # Tests Django natifs
    total_tests += 1
    if run_django_tests():
        tests_passed += 1
    
    # Tests pytest
    if Path("tests").exists():
        total_tests += 1
        if run_pytest_tests():
            tests_passed += 1
        
        # Tests avec couverture
        total_tests += 1
        if run_pytest_with_coverage():
            tests_passed += 1
    
    # Tests d'intégration API
    total_tests += 1
    if run_api_integration_tests():
        tests_passed += 1
    
    # Tests spécifiques
    total_tests += 1
    if run_specific_tests():
        tests_passed += 1
    
    # Rapport final
    generate_test_report()
    
    print(f"\n{'='*60}")
    print(f"🏁 RÉSULTAT FINAL: {tests_passed}/{total_tests} suites de tests réussies")
    print(f"{'='*60}")
    
    if tests_passed == total_tests:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        sys.exit(0)
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)

if __name__ == "__main__":
    main()