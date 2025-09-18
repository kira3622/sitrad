import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')

# Ajouter le répertoire du projet au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurer Django
django.setup()

from django.contrib.auth.models import User
from customers.models import Client, Chantier
from orders.models import Commande, LigneCommande
from production.models import OrdreProduction
from inventory.models import MatierePremiere
from stock.models import MouvementStock
from formulas.models import FormuleBeton, CompositionFormule
from decimal import Decimal
from datetime import date, timedelta

# Créer un superuser
user, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
)
if created:
    user.set_password('admin123')
    user.save()
    print("Superuser créé")

# Créer un client
client, created = Client.objects.get_or_create(
    nom="Client Test",
    defaults={
        'adresse': '123 Rue Test',
        'telephone': '0123456789',
        'email': 'client@test.com'
    }
)
print(f"Client {'créé' if created else 'existant'}: {client}")

# Créer un chantier
chantier, created = Chantier.objects.get_or_create(
    nom="Chantier Test",
    client=client,
    defaults={'adresse': '456 Avenue Chantier'}
)
print(f"Chantier {'créé' if created else 'existant'}: {chantier}")

# Créer des matières premières
ciment, created = MatierePremiere.objects.get_or_create(
    nom="Ciment",
    defaults={'unite_mesure': 'kg'}
)
print(f"Ciment {'créé' if created else 'existant'}: {ciment}")

sable, created = MatierePremiere.objects.get_or_create(
    nom="Sable",
    defaults={'unite_mesure': 'kg'}
)
print(f"Sable {'créé' if created else 'existant'}: {sable}")

gravier, created = MatierePremiere.objects.get_or_create(
    nom="Gravier",
    defaults={'unite_mesure': 'kg'}
)
print(f"Gravier {'créé' if created else 'existant'}: {gravier}")

eau, created = MatierePremiere.objects.get_or_create(
    nom="Eau",
    defaults={'unite_mesure': 'L'}
)
print(f"Eau {'créé' if created else 'existant'}: {eau}")

# Ajouter du stock initial pour les matières premières
matieres_stock = [
    (ciment, Decimal('1000')),
    (sable, Decimal('2000')),
    (gravier, Decimal('3000')),
    (eau, Decimal('500'))
]

for matiere, stock_initial in matieres_stock:
    # Vérifier s'il y a déjà du stock
    if matiere.stock_actuel == 0:
        MouvementStock.objects.create(
            matiere_premiere=matiere,
            quantite=stock_initial,
            type_mouvement='entree',
            description=f'Stock initial {matiere.nom}'
        )
        print(f"Stock initial ajouté pour {matiere.nom}: {stock_initial} {matiere.unite_mesure}")

# Créer une formule de béton
formule, created = FormuleBeton.objects.get_or_create(
    nom="Béton C25/30",
    defaults={'description': 'Béton standard pour construction'}
)
print(f"Formule {'créée' if created else 'existante'}: {formule}")

# Créer les compositions de la formule
compositions = [
    (ciment, Decimal('350')),
    (sable, Decimal('650')),
    (gravier, Decimal('1200')),
    (eau, Decimal('175'))
]

for matiere, quantite in compositions:
    comp, created = CompositionFormule.objects.get_or_create(
        formule=formule,
        matiere_premiere=matiere,
        defaults={'quantite': quantite}
    )
    print(f"Composition {matiere.nom}: {'créée' if created else 'existante'}")

# Créer une commande
commande, created = Commande.objects.get_or_create(
    client=client,
    chantier=chantier,
    defaults={
        'statut': 'validee',
        'date_livraison_souhaitee': date.today() + timedelta(days=7)
    }
)
print(f"Commande {'créée' if created else 'existante'}: {commande}")

# Créer une ligne de commande
ligne_commande, created = LigneCommande.objects.get_or_create(
    commande=commande,
    formule=formule,
    defaults={'quantite': Decimal('5')}  # 5 m³ de béton
)
print(f"Ligne de commande {'créée' if created else 'existante'}: {ligne_commande}")

# Créer un ordre de production
ordre_production, created = OrdreProduction.objects.get_or_create(
    commande=commande,
    formule=formule,
    defaults={
        'quantite_produire': Decimal('5'),
        'date_production': date.today(),
        'statut': 'planifie'
    }
)
print(f"Ordre de production {'créé' if created else 'existant'}: {ordre_production}")

# Tester le calcul des sorties de matières
print("\n=== Test du calcul des sorties de matières ===")
sorties = ordre_production.calculer_sorties_matieres()
print(f"Sorties calculées: {len(sorties)} matières")

for sortie in sorties:
    print(f"- {sortie['matiere_premiere'].nom}: {sortie['quantite_necessaire']} {sortie['matiere_premiere'].unite_mesure}")

# Vérifier le stock disponible
print("\n=== Vérification du stock ===")
verification = ordre_production.verifier_stock_disponible()
print(f"Stock suffisant: {verification['stock_suffisant']}")

if not verification['stock_suffisant']:
    print("Matières insuffisantes:")
    for matiere_info in verification['matieres_insuffisantes']:
        print(f"- {matiere_info['matiere']}: besoin {matiere_info['quantite_necessaire']}, disponible {matiere_info['stock_actuel']}")

# Créer les mouvements de stock
print("\n=== Création des mouvements de stock ===")
if not ordre_production.matieres_sorties_calculees:
    resultat = ordre_production.creer_mouvements_stock(force=True)
    print(f"Résultat: {resultat['message']}")
    
    if resultat['success']:
        print("Mouvements créés:")
        for mouvement in resultat['mouvements']:
            print(f"- {mouvement.matiere_premiere.nom}: -{mouvement.quantite} {mouvement.matiere_premiere.unite_mesure}")
else:
    print("Les sorties ont déjà été calculées pour cet ordre.")

# Vérifier les stocks après les mouvements
print("\n=== Stocks après les mouvements ===")
for matiere in [ciment, sable, gravier, eau]:
    matiere.refresh_from_db()
    print(f"- {matiere.nom}: {matiere.stock_actuel} {matiere.unite_mesure}")

print("\n=== Test terminé avec succès! ===")