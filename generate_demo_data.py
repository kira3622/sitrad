#!/usr/bin/env python
"""
Script de génération de données de démonstration pour Béton App
Ce script crée des données réalistes pour tester l'application
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from customers.models import Client, Chantier
from formulas.models import FormuleBeton, CompositionFormule
from inventory.models import MatierePremiere
from orders.models import Commande, LigneCommande
from stock.models import MouvementStock
from production.models import OrdreProduction, LotProduction
from logistics.models import Livraison
from billing.models import Facture, LigneFacture
from fuel_management.models import Fournisseur, Engin, Approvisionnement

def create_matieres_premieres():
    """Créer les matières premières de base"""
    print("Création des matières premières...")
    
    matieres = [
        {'nom': 'Ciment Portland CEM I 52.5', 'unite_mesure': 'kg', 'seuil_critique': 500, 'seuil_bas': 2000},
        {'nom': 'Sable 0/4', 'unite_mesure': 'kg', 'seuil_critique': 1000, 'seuil_bas': 5000},
        {'nom': 'Gravier 4/20', 'unite_mesure': 'kg', 'seuil_critique': 1500, 'seuil_bas': 7000},
        {'nom': 'Gravier 8/16', 'unite_mesure': 'kg', 'seuil_critique': 1000, 'seuil_bas': 5000},
        {'nom': 'Eau', 'unite_mesure': 'litre', 'seuil_critique': 200, 'seuil_bas': 1000},
        {'nom': 'Adjuvant plastifiant', 'unite_mesure': 'litre', 'seuil_critique': 10, 'seuil_bas': 50},
        {'nom': 'Adjuvant retardateur', 'unite_mesure': 'litre', 'seuil_critique': 5, 'seuil_bas': 25},
        {'nom': 'Fibres polypropylène', 'unite_mesure': 'kg', 'seuil_critique': 20, 'seuil_bas': 100},
    ]
    
    for matiere_data in matieres:
        matiere, created = MatierePremiere.objects.get_or_create(
            nom=matiere_data['nom'],
            defaults=matiere_data
        )
        if created:
            print(f"  ✓ {matiere.nom}")

def create_formules_beton():
    """Créer les formules de béton standard"""
    print("Création des formules de béton...")
    
    # Récupérer les matières premières
    ciment = MatierePremiere.objects.get(nom='Ciment Portland CEM I 52.5')
    sable = MatierePremiere.objects.get(nom='Sable 0/4')
    gravier_4_20 = MatierePremiere.objects.get(nom='Gravier 4/20')
    gravier_8_16 = MatierePremiere.objects.get(nom='Gravier 8/16')
    eau = MatierePremiere.objects.get(nom='Eau')
    plastifiant = MatierePremiere.objects.get(nom='Adjuvant plastifiant')
    
    formules = [
        {
            'nom': 'Béton C25/30 Standard',
            'description': 'Béton standard pour fondations et dalles',
            'resistance_requise': 'C25/30',
            'quantite_produite_reference': Decimal('1.00'),
            'composition': [
                (ciment, Decimal('350')),
                (sable, Decimal('680')),
                (gravier_4_20, Decimal('550')),
                (gravier_8_16, Decimal('550')),
                (eau, Decimal('175')),
                (plastifiant, Decimal('1.75')),
            ]
        },
        {
            'nom': 'Béton C30/37 Haute Résistance',
            'description': 'Béton haute résistance pour structures',
            'resistance_requise': 'C30/37',
            'quantite_produite_reference': Decimal('1.00'),
            'composition': [
                (ciment, Decimal('400')),
                (sable, Decimal('650')),
                (gravier_4_20, Decimal('500')),
                (gravier_8_16, Decimal('600')),
                (eau, Decimal('160')),
                (plastifiant, Decimal('2.00')),
            ]
        },
        {
            'nom': 'Béton C20/25 Économique',
            'description': 'Béton économique pour travaux courants',
            'resistance_requise': 'C20/25',
            'quantite_produite_reference': Decimal('1.00'),
            'composition': [
                (ciment, Decimal('300')),
                (sable, Decimal('700')),
                (gravier_4_20, Decimal('600')),
                (gravier_8_16, Decimal('500')),
                (eau, Decimal('180')),
                (plastifiant, Decimal('1.50')),
            ]
        }
    ]
    
    for formule_data in formules:
        composition = formule_data.pop('composition')
        formule, created = FormuleBeton.objects.get_or_create(
            nom=formule_data['nom'],
            defaults=formule_data
        )
        
        if created:
            print(f"  ✓ {formule.nom}")
            # Ajouter la composition
            for matiere, quantite in composition:
                CompositionFormule.objects.create(
                    formule=formule,
                    matiere_premiere=matiere,
                    quantite=quantite
                )

def create_clients_and_chantiers():
    """Créer des clients et leurs chantiers"""
    print("Création des clients et chantiers...")
    
    clients_data = [
        {
            'nom': 'Entreprise Bouygues Construction',
            'adresse': '32 Avenue Hoche, 75008 Paris',
            'telephone': '01.30.60.33.00',
            'email': 'contact@bouygues-construction.com',
            'chantiers': [
                {'nom': 'Résidence Les Jardins', 'adresse': '15 Rue des Lilas, 92100 Boulogne'},
                {'nom': 'Centre Commercial Westfield', 'adresse': '4 Place de la Pyramide, 92800 Puteaux'},
            ]
        },
        {
            'nom': 'VINCI Construction',
            'adresse': '1 Cours Ferdinand de Lesseps, 92500 Rueil-Malmaison',
            'telephone': '01.47.16.35.00',
            'email': 'info@vinci-construction.com',
            'chantiers': [
                {'nom': 'Tour Horizon', 'adresse': '50 Avenue de la Grande Armée, 75017 Paris'},
                {'nom': 'Pont de Neuilly Rénovation', 'adresse': 'Pont de Neuilly, 92200 Neuilly-sur-Seine'},
            ]
        },
        {
            'nom': 'Eiffage Construction',
            'adresse': '3-7 Place de l\'Europe, 78140 Vélizy-Villacoublay',
            'telephone': '01.34.65.89.89',
            'email': 'contact@eiffage.com',
            'chantiers': [
                {'nom': 'Écoquartier Clichy-Batignolles', 'adresse': 'Rue Cardinet, 75017 Paris'},
                {'nom': 'Stade Jean Bouin Rénovation', 'adresse': '26 Avenue du Général Sarrail, 75016 Paris'},
            ]
        },
        {
            'nom': 'Particulier - M. Martin',
            'adresse': '12 Rue de la Paix, 78000 Versailles',
            'telephone': '06.12.34.56.78',
            'email': 'martin.jean@email.com',
            'chantiers': [
                {'nom': 'Maison individuelle Martin', 'adresse': '12 Rue de la Paix, 78000 Versailles'},
            ]
        },
        {
            'nom': 'SAS Immobilier Développement',
            'adresse': '45 Boulevard Saint-Germain, 75005 Paris',
            'telephone': '01.43.25.67.89',
            'email': 'contact@sas-immo-dev.fr',
            'chantiers': [
                {'nom': 'Résidence Étudiante Sorbonne', 'adresse': '23 Rue des Écoles, 75005 Paris'},
                {'nom': 'Bureaux Défense 2000', 'adresse': '110 Esplanade du Général de Gaulle, 92400 Courbevoie'},
            ]
        }
    ]
    
    for client_data in clients_data:
        chantiers_data = client_data.pop('chantiers')
        client, created = Client.objects.get_or_create(
            nom=client_data['nom'],
            defaults=client_data
        )
        
        if created:
            print(f"  ✓ Client: {client.nom}")
            
            for chantier_data in chantiers_data:
                chantier = Chantier.objects.create(
                    client=client,
                    **chantier_data
                )
                print(f"    ✓ Chantier: {chantier.nom}")

def create_fournisseurs():
    """Créer des fournisseurs"""
    print("Création des fournisseurs...")
    
    fournisseurs_data = [
        {
            'nom': 'Total Energies',
            'contact': 'Service Commercial',
            'adresse': '2 Place Jean Millier, 92400 Courbevoie',
            'telephone': '01.47.44.45.46',
            'email': 'commercial@totalenergies.fr'
        },
        {
            'nom': 'Shell France',
            'contact': 'Département B2B',
            'adresse': '37 Place de la Madeleine, 75008 Paris',
            'telephone': '01.44.71.40.40',
            'email': 'b2b@shell.fr'
        },
        {
            'nom': 'Esso Express',
            'contact': 'Ventes Professionnelles',
            'adresse': '1 Avenue de la Liberté, 92500 Rueil-Malmaison',
            'telephone': '01.47.16.35.00',
            'email': 'pro@esso.fr'
        }
    ]
    
    for fournisseur_data in fournisseurs_data:
        fournisseur, created = Fournisseur.objects.get_or_create(
            nom=fournisseur_data['nom'],
            defaults=fournisseur_data
        )
        if created:
            print(f"  ✓ {fournisseur.nom}")

def create_engins():
    """Créer des types d'engins et des engins"""
    print("Création des engins...")
    
    # D'abord créer les types d'engins
    from fuel_management.models import TypeEngin
    
    types_engins_data = [
        {'nom': 'Camion Malaxeur', 'consommation_moyenne': Decimal('25.00')},
        {'nom': 'Pompe à Béton', 'consommation_moyenne': Decimal('30.00')},
        {'nom': 'Centrale à Béton', 'consommation_moyenne': Decimal('15.00')},
        {'nom': 'Chargeur', 'consommation_moyenne': Decimal('20.00')},
    ]
    
    for type_data in types_engins_data:
        type_engin, created = TypeEngin.objects.get_or_create(
            nom=type_data['nom'],
            defaults=type_data
        )
        if created:
            print(f"  ✓ Type: {type_engin.nom}")
    
    # Ensuite créer les engins
    type_malaxeur = TypeEngin.objects.get(nom='Camion Malaxeur')
    type_pompe = TypeEngin.objects.get(nom='Pompe à Béton')
    type_centrale = TypeEngin.objects.get(nom='Centrale à Béton')
    type_chargeur = TypeEngin.objects.get(nom='Chargeur')
    
    engins_data = [
        {
            'nom': 'Malaxeur 001',
            'type_engin': type_malaxeur,
            'immatriculation': 'AB-123-CD',
            'marque': 'Mercedes',
            'modele': 'Arocs 3240',
            'annee': 2020
        },
        {
            'nom': 'Malaxeur 002',
            'type_engin': type_malaxeur,
            'immatriculation': 'EF-456-GH',
            'marque': 'Volvo',
            'modele': 'FMX 420',
            'annee': 2019
        },
        {
            'nom': 'Pompe Mobile 001',
            'type_engin': type_pompe,
            'immatriculation': 'IJ-789-KL',
            'marque': 'Putzmeister',
            'modele': 'BSF 36-4.16H',
            'annee': 2021
        },
        {
            'nom': 'Centrale Principale',
            'type_engin': type_centrale,
            'numero_serie': 'CENTRALE-001',
            'marque': 'Liebherr',
            'modele': 'Mobilmix 2.5',
            'annee': 2018
        },
        {
            'nom': 'Chargeur 001',
            'type_engin': type_chargeur,
            'immatriculation': 'CH-001-FR',
            'marque': 'Caterpillar',
            'modele': '950M',
            'annee': 2020
        }
    ]
    
    for engin_data in engins_data:
        engin, created = Engin.objects.get_or_create(
            nom=engin_data['nom'],
            defaults=engin_data
        )
        if created:
            print(f"  ✓ Engin: {engin.nom}")

def create_stock_movements():
    """Créer des mouvements de stock pour avoir du stock initial"""
    print("Création des mouvements de stock...")
    
    matieres = MatierePremiere.objects.all()
    
    for matiere in matieres:
        # Créer un approvisionnement initial important
        quantite_initiale = random.randint(5000, 15000)
        if matiere.unite_mesure == 'litre':
            quantite_initiale = random.randint(500, 2000)
        elif 'Adjuvant' in matiere.nom:
            quantite_initiale = random.randint(100, 500)
        elif 'Fibres' in matiere.nom:
            quantite_initiale = random.randint(200, 800)
            
        # Créer le mouvement d'entrée initial
        mouvement_entree = MouvementStock(
            matiere_premiere=matiere,
            type_mouvement='entree',
            quantite=Decimal(str(quantite_initiale)),
            description=f'Stock initial de démonstration - Réf: APPRO-INIT-{matiere.id:03d}'
        )
        # Modifier la date manuellement après création
        mouvement_entree.save()
        mouvement_entree.date_mouvement = datetime.now() - timedelta(days=30)
        mouvement_entree.save()
        
        # Créer quelques sorties pour simuler la consommation
        for i in range(random.randint(3, 8)):
            quantite_sortie = random.randint(50, 500)
            if matiere.unite_mesure == 'litre':
                quantite_sortie = random.randint(10, 100)
            elif 'Adjuvant' in matiere.nom:
                quantite_sortie = random.randint(5, 50)
                
            mouvement_sortie = MouvementStock(
                matiere_premiere=matiere,
                type_mouvement='sortie',
                quantite=Decimal(str(quantite_sortie)),
                description=f'Consommation production - Réf: PROD-{random.randint(1000, 9999)}'
            )
            mouvement_sortie.save()
            mouvement_sortie.date_mouvement = datetime.now() - timedelta(days=random.randint(1, 25))
            mouvement_sortie.save()
        
        print(f"  ✓ Stock {matiere.nom}: {matiere.stock_actuel} {matiere.unite_mesure}")

def create_commandes():
    """Créer des commandes avec différents statuts"""
    print("Création des commandes...")
    
    chantiers = list(Chantier.objects.all())
    formules = list(FormuleBeton.objects.all())
    statuts = ['en_attente', 'validee', 'en_production', 'livree']
    
    for i in range(15):
        chantier = random.choice(chantiers)
        date_commande = datetime.now() - timedelta(days=random.randint(1, 60))
        date_livraison = date_commande + timedelta(days=random.randint(1, 14))
        
        commande = Commande.objects.create(
            client=chantier.client,
            chantier=chantier,
            date_livraison_souhaitee=date_livraison.date(),
            statut=random.choice(statuts)
        )
        
        # Ajouter 1-3 lignes de commande
        nb_lignes = random.randint(1, 3)
        for j in range(nb_lignes):
            formule = random.choice(formules)
            quantite = Decimal(str(random.randint(5, 50)))
            
            LigneCommande.objects.create(
                commande=commande,
                formule=formule,
                quantite=quantite
            )
        
        print(f"  ✓ Commande {commande.id} - {commande.client.nom} ({commande.statut})")

def create_productions():
    """Créer des ordres de production basés sur les commandes validées"""
    print("Création des ordres de production...")
    
    commandes_validees = Commande.objects.filter(statut__in=['validee', 'en_production'])
    
    for commande in commandes_validees[:8]:  # Limiter à 8 productions
        for ligne in commande.lignes.all():
            date_production = datetime.now() - timedelta(days=random.randint(0, 10))
            
            ordre_production = OrdreProduction.objects.create(
                commande=commande,
                formule=ligne.formule,
                quantite_produire=ligne.quantite,
                date_production=date_production.date(),
                heure_production=date_production.time(),
                statut=random.choice(['planifie', 'en_cours', 'termine'])
            )
            
            # Créer un lot de production
            LotProduction.objects.create(
                ordre_production=ordre_production,
                quantite_produite=ligne.quantite * Decimal(str(random.uniform(0.95, 1.05)))
            )
            
            print(f"  ✓ Ordre de production {ordre_production.numero_bon} - {ligne.formule.nom}")

def main():
    """Fonction principale pour générer toutes les données de démonstration"""
    print("🚀 Génération des données de démonstration pour Béton App")
    print("=" * 60)
    
    try:
        create_matieres_premieres()
        create_formules_beton()
        create_fournisseurs()
        create_engins()
        create_clients_and_chantiers()
        create_stock_movements()
        create_commandes()
        create_productions()
        
        print("\n" + "=" * 60)
        print("✅ Génération des données de démonstration terminée avec succès!")
        print("\nRésumé des données créées:")
        print(f"  • {MatierePremiere.objects.count()} matières premières")
        print(f"  • {FormuleBeton.objects.count()} formules de béton")
        print(f"  • {Client.objects.count()} clients")
        print(f"  • {Chantier.objects.count()} chantiers")
        print(f"  • {Fournisseur.objects.count()} fournisseurs")
        print(f"  • {Engin.objects.count()} engins")
        print(f"  • {Commande.objects.count()} commandes")
        print(f"  • {OrdreProduction.objects.count()} ordres de production")
        print(f"  • {MouvementStock.objects.count()} mouvements de stock")
        
        print("\n📱 Vous pouvez maintenant tester l'application mobile avec des données réalistes!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des données: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()