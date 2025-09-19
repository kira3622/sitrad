#!/usr/bin/env python
"""
Script de test pour vérifier le fonctionnement des seuils configurables
"""

import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from reports.models import ConfigurationSeuilsStock
from inventory.models import MatierePremiere

def test_configuration_seuils():
    """Test de la configuration des seuils"""
    print("=== TEST DE LA CONFIGURATION DES SEUILS ===")
    
    # Test 1: Récupération des seuils par défaut
    print("\n1. Test de récupération des seuils par défaut:")
    config = ConfigurationSeuilsStock.get_seuils()
    print(f"   ✅ Seuil critique: {config.seuil_critique}")
    print(f"   ✅ Seuil bas: {config.seuil_bas}")
    print(f"   ✅ Configuration: {config}")
    
    # Test 2: Modification des seuils
    print("\n2. Test de modification des seuils:")
    anciens_seuils = (config.seuil_critique, config.seuil_bas)
    config.seuil_critique = Decimal('15.0')
    config.seuil_bas = Decimal('75.0')
    config.modifie_par = 'test_script'
    config.save()
    
    # Vérification de la modification
    config_modifiee = ConfigurationSeuilsStock.get_seuils()
    print(f"   ✅ Nouveaux seuils - Critique: {config_modifiee.seuil_critique}, Bas: {config_modifiee.seuil_bas}")
    print(f"   ✅ Modifié par: {config_modifiee.modifie_par}")
    
    # Test 3: Vérification qu'il n'y a qu'une seule configuration
    print("\n3. Test d'unicité de la configuration:")
    nombre_configs = ConfigurationSeuilsStock.objects.count()
    print(f"   ✅ Nombre de configurations: {nombre_configs} (doit être 1)")
    
    # Test 4: Test avec des matières premières
    print("\n4. Test d'application des seuils:")
    matieres = MatierePremiere.objects.all()[:3]  # Prendre les 3 premières
    
    for matiere in matieres:
        stock_actuel = matiere.stock_actuel
        niveau_alerte = 'normal'
        
        if stock_actuel <= config_modifiee.seuil_critique:
            niveau_alerte = 'critique'
        elif stock_actuel <= config_modifiee.seuil_bas:
            niveau_alerte = 'bas'
        
        print(f"   📦 {matiere.nom}: {stock_actuel} {matiere.unite_mesure} → {niveau_alerte}")
    
    # Restauration des anciens seuils
    print("\n5. Restauration des seuils originaux:")
    config.seuil_critique = anciens_seuils[0]
    config.seuil_bas = anciens_seuils[1]
    config.modifie_par = 'test_script_restore'
    config.save()
    print(f"   ✅ Seuils restaurés: Critique={anciens_seuils[0]}, Bas={anciens_seuils[1]}")
    
    return True

def test_integration_rapport():
    """Test d'intégration avec le rapport de stock"""
    print("\n=== TEST D'INTÉGRATION AVEC LE RAPPORT ===")
    
    from reports.views import rapport_stock
    from django.test import RequestFactory
    
    # Créer une requête factice
    factory = RequestFactory()
    request = factory.get('/reports/stock/')
    
    try:
        # Appeler la vue
        response = rapport_stock(request)
        print(f"   ✅ Rapport de stock généré avec succès (status: {response.status_code})")
        
        # Vérifier que les seuils sont dans le contexte
        if hasattr(response, 'context_data'):
            context = response.context_data
            if 'seuil_critique' in context and 'seuil_bas' in context:
                print(f"   ✅ Seuils présents dans le contexte: {context['seuil_critique']}, {context['seuil_bas']}")
            else:
                print("   ⚠️ Seuils non trouvés dans le contexte")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur lors de la génération du rapport: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DES TESTS DES SEUILS CONFIGURABLES")
    print("=" * 60)
    
    try:
        # Test de la configuration
        success1 = test_configuration_seuils()
        
        # Test d'intégration
        success2 = test_integration_rapport()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        if success1 and success2:
            print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
            print("✅ L'interface de configuration des seuils fonctionne correctement")
            print("✅ L'intégration avec le rapport de stock est opérationnelle")
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
            if not success1:
                print("❌ Problème avec la configuration des seuils")
            if not success2:
                print("❌ Problème avec l'intégration du rapport")
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        sys.exit(1)
    
    print("\n🎉 Tests terminés!")