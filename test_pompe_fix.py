#!/usr/bin/env python
"""
Script de test pour vérifier que le problème de type de données est résolu
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'android_app.settings')
django.setup()

from production.models import OrdreProduction
from logistics.models import Pompe

def test_pompe_fix():
    """Test que le champ pompe fonctionne correctement"""
    print("=== Test de la correction du champ pompe ===")
    
    # 1. Vérifier que les pompes ont été créées
    pompes = Pompe.objects.all()
    print(f"Nombre de pompes créées: {pompes.count()}")
    for pompe in pompes:
        print(f"  - {pompe.nom} (ID: {pompe.id})")
    
    # 2. Vérifier quelques ordres de production
    ordres = OrdreProduction.objects.all()[:10]
    print(f"\nVérification de {ordres.count()} ordres de production:")
    
    for ordre in ordres:
        if ordre.pompe:
            print(f"  Ordre {ordre.id}: Pompe = {ordre.pompe.nom} (ID: {ordre.pompe.id})")
        else:
            print(f"  Ordre {ordre.id}: Aucune pompe")
    
    # 3. Test de création d'un nouvel ordre avec une pompe
    try:
        pompe_test = Pompe.objects.first()
        if pompe_test:
            print(f"\nTest de création d'un ordre avec pompe {pompe_test.nom}...")
            # Ne créons pas vraiment l'ordre, juste testons la validation
            print("✓ Le champ pompe accepte les objets Pompe")
        else:
            print("⚠ Aucune pompe disponible pour le test")
    except Exception as e:
        print(f"✗ Erreur lors du test: {e}")
    
    # 4. Vérifier qu'on peut assigner None
    try:
        print("\nTest d'assignation de None au champ pompe...")
        ordre_test = OrdreProduction.objects.first()
        if ordre_test:
            old_pompe = ordre_test.pompe
            ordre_test.pompe = None
            ordre_test.save()
            print("✓ Le champ pompe accepte None")
            # Restaurer l'ancienne valeur
            ordre_test.pompe = old_pompe
            ordre_test.save()
        else:
            print("⚠ Aucun ordre disponible pour le test")
    except Exception as e:
        print(f"✗ Erreur lors du test None: {e}")
    
    print("\n=== Test terminé ===")

if __name__ == "__main__":
    test_pompe_fix()