"""
Configuration globale pour les tests pytest
"""
import pytest

@pytest.fixture
def api_client():
    """Client pour les tests API"""
    from django.test import Client
    return Client()

@pytest.fixture
def admin_user(db):
    """Utilisateur administrateur pour les tests"""
    from django.contrib.auth.models import User
    return User.objects.create_superuser(
        username='admin_test',
        email='admin@test.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Client authentifié pour les tests avec JWT"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    # Générer un token JWT pour l'utilisateur
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    
    # Ajouter le token JWT dans les headers
    api_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    return api_client

@pytest.fixture
def sample_data(db):
    """Données de test de base"""
    from customers.models import Client, Chantier
    from inventory.models import MatierePremiere
    from formulas.models import FormuleBeton
    
    # Créer un client de test
    client = Client.objects.create(
        nom="Client Test",
        adresse="123 Rue Test",
        telephone="0123456789",
        email="client@test.com"
    )
    
    # Créer un chantier de test
    chantier = Chantier.objects.create(
        nom="Chantier Test",
        adresse="456 Avenue Test",
        client=client
    )
    
    # Créer une matière première de test
    matiere = MatierePremiere.objects.create(
        nom="Ciment Test",
        unite_mesure="kg",
        seuil_critique=100,
        seuil_bas=200
    )
    
    # Créer une formule de test
    formule = FormuleBeton.objects.create(
        nom="Formule Test",
        description="Formule de test",
        resistance_requise=25.0,
        quantite_produite_reference=1.0
    )
    
    return {
        'client': client,
        'chantier': chantier,
        'matiere': matiere,
        'formule': formule
    }