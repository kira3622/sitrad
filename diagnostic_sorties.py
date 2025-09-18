#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from production.models import OrdreProduction
from formulas.models import FormuleBeton

def diagnostiquer_ordres():
    """Diagnostique tous les ordres de production pour identifier les problèmes"""
    
    print("🔍 DIAGNOSTIC DES ORDRES DE PRODUCTION")
    print("=" * 50)
    
    ordres_problematiques = []
    ordres_ok = []
    
    for ordre in OrdreProduction.objects.all():
        print(f"\n📋 Ordre #{ordre.id} - {ordre.formule.nom}")
        problemes = []
        
        # Vérifier la formule
        if not ordre.formule:
            problemes.append("❌ Aucune formule associée")
        else:
            # Vérifier quantité de référence
            if not ordre.formule.quantite_produite_reference or ordre.formule.quantite_produite_reference <= 0:
                problemes.append(f"❌ Quantité de référence invalide: {ordre.formule.quantite_produite_reference}")
            
            # Vérifier composition
            compositions = ordre.formule.composition.all()
            if not compositions.exists():
                problemes.append("❌ Formule sans composition (aucune matière première)")
            else:
                print(f"   ✅ {compositions.count()} matières premières dans la composition")
                
                # Vérifier chaque composition
                for comp in compositions:
                    if not comp.quantite or comp.quantite <= 0:
                        problemes.append(f"❌ Quantité invalide pour {comp.matiere_premiere.nom}: {comp.quantite}")
        
        # Vérifier quantité à produire
        if not ordre.quantite_produire or ordre.quantite_produire <= 0:
            problemes.append(f"❌ Quantité à produire invalide: {ordre.quantite_produire}")
        
        # Tester le calcul
        try:
            sorties = ordre.calculer_sorties_matieres()
            if sorties:
                print(f"   ✅ Calcul réussi: {len(sorties)} sorties calculées")
                ordres_ok.append(ordre)
            else:
                problemes.append("❌ Calcul retourne une liste vide")
        except Exception as e:
            problemes.append(f"❌ Erreur de calcul: {str(e)}")
        
        if problemes:
            ordres_problematiques.append((ordre, problemes))
            print("   🚨 PROBLÈMES DÉTECTÉS:")
            for probleme in problemes:
                print(f"      {probleme}")
        else:
            print("   ✅ Ordre OK")
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    print(f"✅ Ordres fonctionnels: {len(ordres_ok)}")
    print(f"🚨 Ordres problématiques: {len(ordres_problematiques)}")
    
    if ordres_problematiques:
        print("\n🔧 ACTIONS RECOMMANDÉES:")
        for ordre, problemes in ordres_problematiques:
            print(f"\n📋 Ordre #{ordre.id}:")
            for probleme in problemes:
                print(f"   {probleme}")

def diagnostiquer_formules():
    """Diagnostique toutes les formules"""
    
    print("\n🧪 DIAGNOSTIC DES FORMULES")
    print("=" * 50)
    
    for formule in FormuleBeton.objects.all():
        print(f"\n📋 Formule: {formule.nom}")
        
        if not formule.quantite_produite_reference or formule.quantite_produite_reference <= 0:
            print(f"   ❌ Quantité de référence invalide: {formule.quantite_produite_reference}")
        else:
            print(f"   ✅ Quantité de référence: {formule.quantite_produite_reference}")
        
        compositions = formule.composition.all()
        if not compositions.exists():
            print("   ❌ Aucune composition définie")
        else:
            print(f"   ✅ {compositions.count()} matières premières")
            for comp in compositions:
                if comp.quantite <= 0:
                    print(f"      ❌ {comp.matiere_premiere.nom}: quantité invalide ({comp.quantite})")
                else:
                    print(f"      ✅ {comp.matiere_premiere.nom}: {comp.quantite}")

if __name__ == "__main__":
    diagnostiquer_formules()
    diagnostiquer_ordres()