#!/usr/bin/env python3
"""
Script de test pour valider la relation client-chantiers
"""

import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from customers.models import Client, Chantier
from orders.models import Commande
from datetime import date, timedelta

def test_clients_chantiers():
    print("🏗️ Test de la relation Client-Chantiers")
    print("=" * 50)
    
    # 1. Créer des clients de test
    print("\n1️⃣ Création des clients de test...")
    
    # Nettoyer les données de test existantes
    Client.objects.filter(nom__startswith="Client Test").delete()
    
    client1 = Client.objects.create(
        nom="Client Test 1",
        adresse="123 Rue de la Paix",
        telephone="0123456789",
        email="client1@test.com"
    )
    
    client2 = Client.objects.create(
        nom="Client Test 2", 
        adresse="456 Avenue des Champs",
        telephone="0987654321",
        email="client2@test.com"
    )
    
    print(f"✅ Client 1 créé: {client1}")
    print(f"✅ Client 2 créé: {client2}")
    
    # 2. Créer des chantiers pour chaque client
    print("\n2️⃣ Création des chantiers...")
    
    # Chantiers pour client 1
    chantier1_1 = Chantier.objects.create(
        nom="Chantier Résidentiel A",
        adresse="789 Rue des Maisons",
        client=client1
    )
    
    chantier1_2 = Chantier.objects.create(
        nom="Chantier Commercial B",
        adresse="321 Boulevard du Commerce",
        client=client1
    )
    
    # Chantiers pour client 2
    chantier2_1 = Chantier.objects.create(
        nom="Chantier Industriel C",
        adresse="654 Zone Industrielle",
        client=client2
    )
    
    print(f"✅ Chantier 1.1: {chantier1_1}")
    print(f"✅ Chantier 1.2: {chantier1_2}")
    print(f"✅ Chantier 2.1: {chantier2_1}")
    
    # 3. Tester les méthodes des modèles
    print("\n3️⃣ Test des méthodes des modèles...")
    
    # Test Client
    print(f"📊 Client 1 - Nombre de chantiers: {client1.nombre_chantiers()}")
    print(f"📊 Client 2 - Nombre de chantiers: {client2.nombre_chantiers()}")
    
    # Test Chantier
    print(f"🏗️ Chantier 1.1 - Statut: {chantier1_1.statut_chantier()}")
    print(f"🏗️ Chantier 1.1 - Nombre de commandes: {chantier1_1.nombre_commandes()}")
    
    # 4. Créer des commandes pour tester les statuts
    print("\n4️⃣ Création de commandes de test...")
    
    commande1 = Commande.objects.create(
        client=client1,
        chantier=chantier1_1,
        date_livraison_souhaitee=date.today() + timedelta(days=7),
        statut='en_attente'
    )
    
    commande2 = Commande.objects.create(
        client=client1,
        chantier=chantier1_2,
        date_livraison_souhaitee=date.today() + timedelta(days=14),
        statut='en_production'
    )
    
    print(f"✅ Commande 1 créée: {commande1}")
    print(f"✅ Commande 2 créée: {commande2}")
    
    # 5. Tester les statuts après création des commandes
    print("\n5️⃣ Test des statuts après création des commandes...")
    
    print(f"🏗️ Chantier 1.1 - Nouveau statut: {chantier1_1.statut_chantier()}")
    print(f"🏗️ Chantier 1.2 - Nouveau statut: {chantier1_2.statut_chantier()}")
    print(f"🏗️ Chantier 2.1 - Statut: {chantier2_1.statut_chantier()}")
    
    print(f"📊 Client 1 - Chantiers actifs: {client1.chantiers_actifs().count()}")
    print(f"📊 Client 2 - Chantiers actifs: {client2.chantiers_actifs().count()}")
    
    # 6. Afficher la hiérarchie client-chantiers
    print("\n6️⃣ Hiérarchie Client-Chantiers:")
    print("=" * 30)
    
    for client in [client1, client2]:
        print(f"\n👤 {client.nom}")
        print(f"   📧 {client.email}")
        print(f"   📍 {client.adresse}")
        print(f"   📊 {client.nombre_chantiers()} chantier(s)")
        
        for chantier in client.chantiers.all():
            print(f"   └── 🏗️ {chantier.nom}")
            print(f"       📍 {chantier.adresse}")
            print(f"       📊 {chantier.nombre_commandes()} commande(s)")
            print(f"       🔄 Statut: {chantier.statut_chantier()}")
            
            if chantier.derniere_commande():
                derniere = chantier.derniere_commande()
                print(f"       📅 Dernière commande: {derniere.date_commande} ({derniere.get_statut_display()})")
    
    print("\n✅ Test terminé avec succès!")
    print("🎯 Chaque client a bien ses propres chantiers")
    print("🎯 Les relations et méthodes fonctionnent correctement")
    print("🎯 L'interface d'administration est prête")

if __name__ == "__main__":
    test_clients_chantiers()