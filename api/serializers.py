from rest_framework import serializers
from django.contrib.auth.models import User
from customers.models import Client, Chantier
from orders.models import Commande
# No direct model imports to prevent circular dependencies
from production.models import OrdreProduction
from inventory.models import MatierePremiere
from logistics.models import Livraison
from billing.models import Facture
from fuel_management.models import Fournisseur, Engin, Approvisionnement, Stock
from formulas.models import FormuleBeton, CompositionFormule


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ChantierSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    
    class Meta:
        model = Chantier
        fields = '__all__'


class CommandeSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    clientId = serializers.IntegerField(source='client', write_only=True, required=False)
    chantierId = serializers.IntegerField(source='chantier', write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Commande
        fields = '__all__'
        extra_kwargs = {
            'client': {'write_only': True, 'required': False},
            'chantier': {'write_only': True, 'required': False},
        }
    
    def create(self, validated_data):
        # Gérer les champs clientId et chantierId envoyés par Android
        if 'clientId' in self.initial_data:
            validated_data['client_id'] = self.initial_data['clientId']
        if 'chantierId' in self.initial_data and self.initial_data['chantierId'] is not None:
            validated_data['chantier_id'] = self.initial_data['chantierId']
        
        return super().create(validated_data)


class OrdreProductionSerializer(serializers.ModelSerializer):
    commande_reference = serializers.CharField(source='commande.reference', read_only=True)
    
    class Meta:
        model = OrdreProduction
        fields = '__all__'


class MatierePremiereSerializer(serializers.ModelSerializer):
    stock_actuel = serializers.ReadOnlyField()
    statut_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = MatierePremiere
        fields = ['id', 'nom', 'unite_mesure', 'seuil_critique', 'seuil_bas', 'stock_actuel', 'statut_stock']


class LivraisonSerializer(serializers.ModelSerializer):
    commande_reference = serializers.CharField(source='commande.reference', read_only=True)
    client_nom = serializers.CharField(source='commande.client.nom', read_only=True)
    
    class Meta:
        model = Livraison
        fields = '__all__'


class FactureSerializer(serializers.ModelSerializer):
    client_nom = serializers.CharField(source='commande.client.nom', read_only=True)
    
    class Meta:
        model = Facture
        fields = '__all__'


class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'


class EnginSerializer(serializers.ModelSerializer):
    type_nom = serializers.CharField(source='type_engin.nom', read_only=True)
    
    class Meta:
        model = Engin
        fields = '__all__'


class ApprovisionnementSerializer(serializers.ModelSerializer):
    fournisseur_nom = serializers.CharField(source='fournisseur.nom', read_only=True)
    
    class Meta:
        model = Approvisionnement
        fields = '__all__'


class StockCarburantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


# ==================== FORMULES BÉTON ====================
class CompositionFormuleSerializer(serializers.ModelSerializer):
    matiere_nom = serializers.CharField(source='matiere_premiere.nom', read_only=True)

    class Meta:
        model = CompositionFormule
        fields = ['id', 'matiere_premiere', 'matiere_nom', 'quantite']


class FormuleBetonSerializer(serializers.ModelSerializer):
    composition = CompositionFormuleSerializer(many=True, read_only=True)

    class Meta:
        model = FormuleBeton
        fields = ['id', 'nom', 'description', 'resistance_requise', 'quantite_produite_reference', 'composition']


# Serializer pour les statistiques du dashboard (aligné avec l'app Android)
class DashboardStatsSerializer(serializers.Serializer):
    commandes_total = serializers.IntegerField()
    commandes_en_cours = serializers.IntegerField()
    production_mensuelle = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)
    chiffre_affaires_mensuel = serializers.DecimalField(max_digits=15, decimal_places=2, coerce_to_string=False)
    stock_critique = serializers.IntegerField()
    consommation_carburant_mensuelle = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)