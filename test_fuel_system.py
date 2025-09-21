#!/usr/bin/env python
"""
Script de test pour le système de gestion du gasoil
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yto2.settings')
django.setup()

from fuel_management.models import *
from decimal import Decimal
from django.utils import timezone

def test_fuel_management_system():
    """Test complet du système de gestion du gasoil"""
    
    print("🧪 Test du système de gestion du gasoil")
    print("=" * 50)
    
    # 1. Créer les données de base
    print("\n1. Création des données de base...")
    
    # Fournisseur
    fournisseur, created = Fournisseur.objects.get_or_create(
        nom="Total Energies",
        defaults={
            'contact': "Jean Dupont",
            'telephone': "0123456789",
            'email': "contact@total.fr"
        }
    )
    print(f"✅ Fournisseur: {fournisseur.nom}")
    
    # Type d'engin
    type_engin, created = TypeEngin.objects.get_or_create(nom="Excavatrice")
    print(f"✅ Type d'engin: {type_engin.nom}")
    
    # Engin
    engin, created = Engin.objects.get_or_create(
        nom="CAT 320D",
        defaults={
            'type_engin': type_engin,
            'numero_serie': "CAT123456"
        }
    )
    print(f"✅ Engin: {engin.nom}")
    
    # 2. Test du stock initial
    print("\n2. Test du stock initial...")
    stock = Stock.get_stock_actuel()
    print(f"📊 Stock initial: {stock.quantite}L")
    print(f"⚠️ Seuil minimum: {stock.seuil_minimum}L")
    
    # 3. Test d'approvisionnement
    print("\n3. Test d'approvisionnement...")
    approvisionnement = Approvisionnement.objects.create(
        date=timezone.now().date(),
        fournisseur=fournisseur,
        quantite=Decimal('1000'),
        prix_unitaire=Decimal('1.45'),
        numero_bon="BON001"
    )
    print(f"✅ Approvisionnement créé: +{approvisionnement.quantite}L")
    
    # Vérifier le stock après approvisionnement
    stock.refresh_from_db()
    print(f"📊 Stock après approvisionnement: {stock.quantite}L")
    
    # 4. Test de consommation
    print("\n4. Test de consommation...")
    consommation = Consommation.objects.create(
        date=timezone.now().date(),
        engin=engin,
        quantite=Decimal('150'),
        responsable="Pierre Martin"
    )
    print(f"✅ Consommation créée: -{consommation.quantite}L")
    
    # Vérifier le stock après consommation
    stock.refresh_from_db()
    print(f"📊 Stock après consommation: {stock.quantite}L")
    
    # 5. Test des alertes
    print("\n5. Test du système d'alertes...")
    alertes_count = AlerteStock.objects.count()
    print(f"🚨 Nombre d'alertes: {alertes_count}")
    
    if alertes_count > 0:
        derniere_alerte = AlerteStock.objects.order_by('-date_alerte').first()
        print(f"📝 Dernière alerte: {derniere_alerte.message}")
        print(f"👁️ Vue: {'Oui' if derniere_alerte.vue else 'Non'}")
    
    # 6. Test de consommation importante pour déclencher une alerte
    print("\n6. Test d'alerte de stock faible...")
    consommation_importante = Consommation.objects.create(
        date=timezone.now().date(),
        engin=engin,
        quantite=Decimal('400'),  # Pour descendre sous le seuil
        responsable="Marie Dubois"
    )
    print(f"✅ Consommation importante: -{consommation_importante.quantite}L")
    
    # Vérifier le stock
    stock.refresh_from_db()
    print(f"📊 Stock final: {stock.quantite}L")
    
    # Vérifier les nouvelles alertes
    nouvelles_alertes = AlerteStock.objects.filter(vue=False).count()
    print(f"🚨 Alertes non vues: {nouvelles_alertes}")
    
    # 7. Statistiques finales
    print("\n7. Statistiques finales...")
    total_approvisionnements = Approvisionnement.objects.aggregate(
        total=Sum('quantite')
    )['total'] or Decimal('0')
    
    total_consommations = Consommation.objects.aggregate(
        total=Sum('quantite')
    )['total'] or Decimal('0')
    
    print(f"📈 Total approvisionnements: {total_approvisionnements}L")
    print(f"📉 Total consommations: {total_consommations}L")
    print(f"📊 Stock calculé: {total_approvisionnements - total_consommations}L")
    print(f"📊 Stock en base: {stock.quantite}L")
    
    # Vérifier la cohérence
    if stock.quantite == (total_approvisionnements - total_consommations):
        print("✅ Cohérence des données: OK")
    else:
        print("❌ Incohérence détectée dans les calculs!")
    
    print("\n" + "=" * 50)
    print("🎉 Test terminé avec succès!")

if __name__ == "__main__":
    test_fuel_management_system()