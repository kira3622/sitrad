#!/usr/bin/env python
"""
Script de test pour diagnostiquer les statistiques du tableau de bord
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from customers.models import Client
from orders.models import Commande
from production.models import OrdreProduction
from logistics.models import Livraison

def test_dashboard_stats():
    """Test des calculs des statistiques du tableau de bord"""
    print("🔍 Test des statistiques du tableau de bord")
    print("=" * 50)
    
    # Date de début du mois actuel
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    print(f"📅 Début du mois: {debut_mois}")
    print(f"📅 Date actuelle: {timezone.now()}")
    print()
    
    # Test 1: Total des clients
    try:
        total_clients = Client.objects.count()
        print(f"👥 Total clients: {total_clients}")
        
        # Afficher quelques clients pour debug
        clients = Client.objects.all()[:5]
        for client in clients:
            print(f"   - {client.nom} (ID: {client.id})")
    except Exception as e:
        print(f"❌ Erreur clients: {e}")
    
    print()
    
    # Test 2: Total des commandes ce mois
    try:
        total_commandes = Commande.objects.filter(
            date_commande__gte=debut_mois
        ).count()
        print(f"📋 Commandes ce mois: {total_commandes}")
        
        # Afficher toutes les commandes pour debug
        commandes = Commande.objects.all()
        print(f"   Total commandes (toutes): {commandes.count()}")
        for commande in commandes[:5]:
            print(f"   - Commande {commande.id}: {commande.date_commande} - {commande.statut}")
    except Exception as e:
        print(f"❌ Erreur commandes: {e}")
    
    print()
    
    # Test 3: Productions en cours
    try:
        productions_en_cours = OrdreProduction.objects.filter(
            statut='en_cours'
        ).count()
        print(f"🏭 Productions en cours: {productions_en_cours}")
        
        # Afficher toutes les productions pour debug
        productions = OrdreProduction.objects.all()
        print(f"   Total productions (toutes): {productions.count()}")
        for prod in productions[:5]:
            print(f"   - Production {prod.id}: {prod.statut}")
    except Exception as e:
        print(f"❌ Erreur productions: {e}")
    
    print()
    
    # Test 4: Livraisons prévues
    try:
        livraisons_prevues = Commande.objects.filter(
            statut__in=['confirmee', 'en_production']
        ).count()
        print(f"🚚 Livraisons prévues: {livraisons_prevues}")
        
        # Afficher les statuts des commandes
        statuts = Commande.objects.values('statut').annotate(count=Count('statut'))
        print("   Répartition des statuts:")
        for statut in statuts:
            print(f"   - {statut['statut']}: {statut['count']}")
    except Exception as e:
        print(f"❌ Erreur livraisons: {e}")
    
    print()
    print("✅ Test terminé")

if __name__ == "__main__":
    test_dashboard_stats()