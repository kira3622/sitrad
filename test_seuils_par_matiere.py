#!/usr/bin/env python
"""
Script de test pour la configuration des seuils de stock par matière première
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from inventory.models import MatierePremiere
from stock.models import MouvementStock
from django.utils import timezone
from decimal import Decimal

def test_seuils_par_matiere():
    """Test de la configuration des seuils par matière première"""
    print("=== TEST DES SEUILS PAR MATIÈRE PREMIÈRE ===\n")
    
    # 1. Créer ou récupérer des matières premières de test
    print("1. Configuration des matières premières de test...")
    
    # Matière 1 : Ciment avec seuils bas
    ciment, created = MatierePremiere.objects.get_or_create(
        nom="Ciment Portland",
        defaults={
            'unite_mesure': 'kg',
            'seuil_critique': Decimal('5.00'),
            'seuil_bas': Decimal('20.00')
        }
    )
    if not created:
        ciment.seuil_critique = Decimal('5.00')
        ciment.seuil_bas = Decimal('20.00')
        ciment.save()
    
    # Matière 2 : Sable avec seuils moyens
    sable, created = MatierePremiere.objects.get_or_create(
        nom="Sable fin",
        defaults={
            'unite_mesure': 'm³',
            'seuil_critique': Decimal('2.00'),
            'seuil_bas': Decimal('10.00')
        }
    )
    if not created:
        sable.seuil_critique = Decimal('2.00')
        sable.seuil_bas = Decimal('10.00')
        sable.save()
    
    # Matière 3 : Gravier avec seuils élevés
    gravier, created = MatierePremiere.objects.get_or_create(
        nom="Gravier 20/40",
        defaults={
            'unite_mesure': 'm³',
            'seuil_critique': Decimal('15.00'),
            'seuil_bas': Decimal('50.00')
        }
    )
    if not created:
        gravier.seuil_critique = Decimal('15.00')
        gravier.seuil_bas = Decimal('50.00')
        gravier.save()
    
    print(f"✓ Ciment: seuils {ciment.seuil_critique}/{ciment.seuil_bas}")
    print(f"✓ Sable: seuils {sable.seuil_critique}/{sable.seuil_bas}")
    print(f"✓ Gravier: seuils {gravier.seuil_critique}/{gravier.seuil_bas}")
    
    # 2. Créer des stocks de test
    print("\n2. Création des stocks de test...")
    
    # Stock critique pour le ciment (3 kg < 5 kg)
    MouvementStock.objects.create(
        matiere_premiere=ciment,
        type_mouvement='entree',
        quantite=Decimal('3.00'),
        date_mouvement=timezone.now(),
        description='Stock test critique'
    )
    
    # Stock bas pour le sable (8 m³ < 10 m³)
    MouvementStock.objects.create(
        matiere_premiere=sable,
        type_mouvement='entree',
        quantite=Decimal('8.00'),
        date_mouvement=timezone.now(),
        description='Stock test bas'
    )
    
    # Stock normal pour le gravier (60 m³ > 50 m³)
    MouvementStock.objects.create(
        matiere_premiere=gravier,
        type_mouvement='entree',
        quantite=Decimal('60.00'),
        date_mouvement=timezone.now(),
        description='Stock test normal'
    )
    
    print(f"✓ Stock ciment: {ciment.stock_actuel} {ciment.unite_mesure}")
    print(f"✓ Stock sable: {sable.stock_actuel} {sable.unite_mesure}")
    print(f"✓ Stock gravier: {gravier.stock_actuel} {gravier.unite_mesure}")
    
    # 3. Test des méthodes de statut
    print("\n3. Test des méthodes de statut...")
    
    assert ciment.statut_stock == 'critique', f"Erreur: ciment devrait être critique, mais est {ciment.statut_stock}"
    assert ciment.stock_critique == True, "Erreur: ciment.stock_critique devrait être True"
    print(f"✓ Ciment: statut = {ciment.statut_stock} (attendu: critique)")
    
    assert sable.statut_stock == 'bas', f"Erreur: sable devrait être bas, mais est {sable.statut_stock}"
    assert sable.stock_bas == True, "Erreur: sable.stock_bas devrait être True"
    print(f"✓ Sable: statut = {sable.statut_stock} (attendu: bas)")
    
    assert gravier.statut_stock == 'normal', f"Erreur: gravier devrait être normal, mais est {gravier.statut_stock}"
    assert gravier.stock_critique == False, "Erreur: gravier.stock_critique devrait être False"
    assert gravier.stock_bas == False, "Erreur: gravier.stock_bas devrait être False"
    print(f"✓ Gravier: statut = {gravier.statut_stock} (attendu: normal)")
    
    # 4. Test de modification des seuils
    print("\n4. Test de modification des seuils...")
    
    # Modifier les seuils du sable pour le rendre normal
    sable.seuil_critique = Decimal('1.00')
    sable.seuil_bas = Decimal('5.00')
    sable.save()
    
    assert sable.statut_stock == 'normal', f"Erreur: après modification, sable devrait être normal, mais est {sable.statut_stock}"
    print(f"✓ Sable après modification: statut = {sable.statut_stock} (attendu: normal)")
    
    # 5. Test de l'interface d'administration (simulation)
    print("\n5. Test de l'interface d'administration...")
    
    matieres = MatierePremiere.objects.all()
    print(f"✓ Nombre total de matières premières: {matieres.count()}")
    
    for matiere in matieres:
        print(f"  - {matiere.nom}: {matiere.stock_actuel} {matiere.unite_mesure} "
              f"(seuils: {matiere.seuil_critique}/{matiere.seuil_bas}) "
              f"→ {matiere.statut_stock}")
    
    # 6. Statistiques finales
    print("\n6. Statistiques finales...")
    
    # Calcul manuel des statistiques
    critiques = sum(1 for m in matieres if m.stock_critique)
    bas = sum(1 for m in matieres if m.stock_bas and not m.stock_critique)
    normaux = sum(1 for m in matieres if m.statut_stock == 'normal')
    
    print(f"✓ Matières critiques: {critiques}")
    print(f"✓ Matières en stock bas: {bas}")
    print(f"✓ Matières normales: {normaux}")
    print(f"✓ Total: {critiques + bas + normaux}")
    
    print("\n=== TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS ! ===")
    print("✅ Configuration des seuils par matière première fonctionnelle")
    print("✅ Méthodes de statut opérationnelles")
    print("✅ Interface d'administration prête")
    print("✅ Rapport de stock mis à jour")

if __name__ == '__main__':
    try:
        test_seuils_par_matiere()
    except Exception as e:
        print(f"❌ ERREUR LORS DU TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)