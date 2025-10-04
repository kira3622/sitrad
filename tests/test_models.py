"""
Tests pour les modèles Django
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from customers.models import Client, Chantier
from orders.models import Commande, LigneCommande
from formulas.models import FormuleBeton, CompositionFormule
from inventory.models import MatierePremiere
from stock.models import MouvementStock
from production.models import OrdreProduction, LotProduction


@pytest.mark.unit
class TestCustomerModels:
    """Tests pour les modèles de clients"""
    
    def test_client_creation(self, db):
        """Test de création d'un client"""
        client = Client.objects.create(
            nom="Test Client",
            adresse="123 Test Street",
            telephone="0123456789",
            email="test@example.com"
        )
        
        assert client.nom == "Test Client"
        assert client.adresse == "123 Test Street"
        assert client.telephone == "0123456789"
        assert client.email == "test@example.com"
        assert str(client) == "Test Client"
    
    def test_client_email_validation(self, db):
        """Test de validation de l'email du client"""
        # Email valide
        client = Client(
            nom="Test Client",
            adresse="123 Test Street",
            telephone="0123456789",
            email="valid@example.com"
        )
        client.full_clean()  # Ne devrait pas lever d'exception
        
        # Email invalide
        client_invalid = Client(
            nom="Test Client",
            adresse="123 Test Street",
            telephone="0123456789",
            email="invalid-email"
        )
        
        with pytest.raises(ValidationError):
            client_invalid.full_clean()
    
    def test_chantier_creation(self, db, sample_data):
        """Test de création d'un chantier"""
        client = sample_data['client']
        
        chantier = Chantier.objects.create(
            nom="Test Chantier",
            adresse="456 Test Avenue",
            client=client
        )
        
        assert chantier.nom == "Test Chantier"
        assert chantier.adresse == "456 Test Avenue"
        assert chantier.client == client
        # Le __str__ peut inclure le nom du client
        assert "Test Chantier" in str(chantier)
    
    def test_chantier_client_relationship(self, db, sample_data):
        """Test de la relation chantier-client"""
        client = sample_data['client']
        
        # Créer plusieurs chantiers pour le même client
        chantier1 = Chantier.objects.create(
            nom="Chantier 1",
            adresse="Adresse 1",
            client=client
        )
        
        chantier2 = Chantier.objects.create(
            nom="Chantier 2",
            adresse="Adresse 2",
            client=client
        )
        
        # Vérifier la relation inverse avec le nom correct
        chantiers = Chantier.objects.filter(client=client)
        assert chantier1 in chantiers
        assert chantier2 in chantiers
        assert chantiers.count() >= 2


@pytest.mark.unit
class TestInventoryModels:
    """Tests pour les modèles d'inventaire"""
    
    def test_matiere_premiere_creation(self, db):
        """Test de création d'une matière première"""
        matiere = MatierePremiere.objects.create(
            nom="Ciment Portland",
            unite_mesure="kg",
            seuil_critique=100,
            seuil_bas=200
        )
        
        assert matiere.nom == "Ciment Portland"
        assert matiere.unite_mesure == "kg"
        assert matiere.seuil_critique == 100
        assert matiere.seuil_bas == 200
        assert str(matiere) == "Ciment Portland"
    
    def test_matiere_premiere_stock_calculation(self, db):
        """Test du calcul du stock actuel"""
        matiere = MatierePremiere.objects.create(
            nom="Test Matiere",
            unite_mesure="kg",
            seuil_critique=50,
            seuil_bas=100
        )
        
        # Créer des mouvements de stock
        MouvementStock.objects.create(
            matiere_premiere=matiere,
            quantite=500,
            type_mouvement='entree',
            description="Livraison initiale"
        )
        
        MouvementStock.objects.create(
            matiere_premiere=matiere,
            quantite=150,
            type_mouvement='sortie',
            description="Consommation production"
        )
        
        # Le stock actuel devrait être 500 - 150 = 350
        assert matiere.stock_actuel == 350
    
    def test_matiere_premiere_statut_stock(self, db):
        """Test du calcul du statut de stock"""
        matiere = MatierePremiere.objects.create(
            nom="Test Matiere",
            unite_mesure="kg",
            seuil_critique=50,
            seuil_bas=100
        )
        
        # Stock critique (< seuil_critique)
        MouvementStock.objects.create(
            matiere_premiere=matiere,
            quantite=30,
            type_mouvement='entree',
            description="Stock critique"
        )
        assert matiere.statut_stock == 'critique'
        
        # Stock bas (entre seuil_critique et seuil_bas)
        MouvementStock.objects.create(
            matiere_premiere=matiere,
            quantite=50,
            type_mouvement='entree',
            description="Stock bas"
        )
        assert matiere.statut_stock == 'bas'
        
        # Stock normal (> seuil_bas)
        MouvementStock.objects.create(
            matiere_premiere=matiere,
            quantite=100,
            type_mouvement='entree',
            description="Stock normal"
        )
        assert matiere.statut_stock == 'normal'


@pytest.mark.unit
class TestFormulaModels:
    """Tests pour les modèles de formules"""
    
    def test_formule_beton_creation(self, db):
        """Test de création d'une formule de béton"""
        formule = FormuleBeton.objects.create(
            nom="Béton C25/30",
            description="Béton de résistance 25 MPa",
            resistance_requise=25.0,
            quantite_produite_reference=1.0
        )
        
        assert formule.nom == "Béton C25/30"
        assert formule.description == "Béton de résistance 25 MPa"
        assert formule.resistance_requise == 25.0
        assert formule.quantite_produite_reference == 1.0
        assert str(formule) == "Béton C25/30"
    
    def test_composition_formule_creation(self, db, sample_data):
        """Test de création d'une composition de formule"""
        formule = sample_data['formule']
        matiere = sample_data['matiere']
        
        composition = CompositionFormule.objects.create(
            formule=formule,
            matiere_premiere=matiere,
            quantite=350.0
        )
        
        assert composition.formule == formule
        assert composition.matiere_premiere == matiere
        assert composition.quantite == 350.0


@pytest.mark.unit
class TestOrderModels:
    """Tests pour les modèles de commandes"""
    
    def test_commande_creation(self, db, sample_data):
        """Test de création d'une commande"""
        from datetime import date, timedelta
        
        commande = Commande.objects.create(
            client=sample_data['client'],
            chantier=sample_data['chantier'],
            date_livraison_souhaitee=date.today() + timedelta(days=7),
            statut='en_attente'
        )
        
        assert commande.client == sample_data['client']
        assert commande.chantier == sample_data['chantier']
        assert commande.statut == 'en_attente'
        assert commande.date_commande is not None
        assert commande.date_livraison_souhaitee is not None
    
    def test_ligne_commande_creation(self, db, sample_data):
        """Test de création d'une ligne de commande"""
        from datetime import date, timedelta
        
        commande = Commande.objects.create(
            client=sample_data['client'],
            chantier=sample_data['chantier'],
            date_livraison_souhaitee=date.today() + timedelta(days=7),
            statut='en_attente'
        )
        
        ligne = LigneCommande.objects.create(
            commande=commande,
            formule=sample_data['formule'],
            quantite=5.0
        )
        
        assert ligne.commande == commande
        assert ligne.formule == sample_data['formule']
        assert ligne.quantite == 5.0


@pytest.mark.unit
class TestProductionModels:
    """Tests pour les modèles de production"""
    
    def test_ordre_production_creation(self, db, sample_data):
        """Test de création d'un ordre de production"""
        from datetime import date, timedelta
        
        commande = Commande.objects.create(
            client=sample_data['client'],
            chantier=sample_data['chantier'],
            date_livraison_souhaitee=date.today() + timedelta(days=7),
            statut='en_attente'
        )
        
        ordre = OrdreProduction.objects.create(
            commande=commande,
            formule=sample_data['formule'],
            quantite_produire=3.0,
            date_production=date.today(),
            statut='planifie'
        )
        
        assert ordre.commande == commande
        assert ordre.formule == sample_data['formule']
        assert ordre.quantite_produire == 3.0
        assert ordre.statut == 'planifie'
        assert ordre.numero_bon is not None
        assert ordre.date_production is not None
    
    def test_numero_bon_generation(self, db, sample_data):
        """Test de génération automatique du numéro de bon"""
        from datetime import date, timedelta
        
        commande = Commande.objects.create(
            client=sample_data['client'],
            chantier=sample_data['chantier'],
            date_livraison_souhaitee=date.today() + timedelta(days=7),
            statut='en_attente'
        )
        
        ordre1 = OrdreProduction.objects.create(
            commande=commande,
            formule=sample_data['formule'],
            quantite_produire=3.0,
            date_production=date.today(),
            statut='planifie'
        )
        
        ordre2 = OrdreProduction.objects.create(
            commande=commande,
            formule=sample_data['formule'],
            quantite_produire=2.0,
            date_production=date.today(),
            statut='planifie'
        )
        
        # Les numéros de bon doivent être différents
        assert ordre1.numero_bon != ordre2.numero_bon
        assert ordre1.numero_bon.startswith('BP')
        assert ordre2.numero_bon.startswith('BP')