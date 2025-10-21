from rest_framework import serializers
from .models import (
    CategorieCoût, CoûtMatierePremiere, CoûtMainOeuvre, 
    CoûtFraisGeneraux, CalculCoûtRevient, DetailCoûtMatiere
)
from inventory.models import MatierePremiere
from formulas.models import FormuleBeton
from orders.models import Commande
from production.models import OrdreProduction


class CategorieCoûtSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories de coûts"""
    type_categorie_display = serializers.CharField(source='get_type_categorie_display', read_only=True)
    
    class Meta:
        model = CategorieCoût
        fields = [
            'id', 'nom', 'type_categorie', 'type_categorie_display', 
            'description', 'actif', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['date_creation', 'date_modification']


class CoûtMatierePremierSerializer(serializers.ModelSerializer):
    """Serializer pour les coûts des matières premières"""
    matiere_premiere_nom = serializers.CharField(source='matiere_premiere.nom', read_only=True)
    matiere_premiere_unite = serializers.CharField(source='matiere_premiere.unite_mesure', read_only=True)
    prix_total_unitaire = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    class Meta:
        model = CoûtMatierePremiere
        fields = [
            'id', 'matiere_premiere', 'matiere_premiere_nom', 'matiere_premiere_unite',
            'prix_unitaire', 'devise', 'date_debut', 'date_fin', 
            'fournisseur', 'reference_fournisseur', 'coût_transport', 
            'coût_stockage', 'prix_total_unitaire', 'actif', 'date_creation'
        ]
        read_only_fields = ['date_creation', 'prix_total_unitaire']
    
    def validate(self, data):
        """Validation des données"""
        if data.get('date_fin') and data.get('date_debut'):
            if data['date_fin'] <= data['date_debut']:
                raise serializers.ValidationError("La date de fin doit être postérieure à la date de début")
        return data


class CoûtMainOeuvreSerializer(serializers.ModelSerializer):
    """Serializer pour les coûts de main d'œuvre"""
    type_activite_display = serializers.CharField(source='get_type_activite_display', read_only=True)
    coût_horaire_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CoûtMainOeuvre
        fields = [
            'id', 'nom', 'type_activite', 'type_activite_display',
            'coût_horaire_base', 'charges_sociales_pourcentage', 'coût_horaire_total',
            'date_debut', 'date_fin', 'actif', 'date_creation'
        ]
        read_only_fields = ['date_creation', 'coût_horaire_total']
    
    def validate(self, data):
        """Validation des données"""
        if data.get('date_fin') and data.get('date_debut'):
            if data['date_fin'] <= data['date_debut']:
                raise serializers.ValidationError("La date de fin doit être postérieure à la date de début")
        
        if data.get('charges_sociales_pourcentage', 0) < 0 or data.get('charges_sociales_pourcentage', 0) > 100:
            raise serializers.ValidationError("Le pourcentage de charges sociales doit être entre 0 et 100")
        
        return data


class CoûtFraisGenerauxSerializer(serializers.ModelSerializer):
    """Serializer pour les frais généraux"""
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    type_repartition_display = serializers.CharField(source='get_type_repartition_display', read_only=True)
    
    class Meta:
        model = CoûtFraisGeneraux
        fields = [
            'id', 'categorie', 'categorie_nom', 'nom', 'description',
            'type_repartition', 'type_repartition_display', 'valeur',
            'date_debut', 'date_fin', 'actif', 'date_creation'
        ]
        read_only_fields = ['date_creation']
    
    def validate(self, data):
        """Validation des données"""
        if data.get('date_fin') and data.get('date_debut'):
            if data['date_fin'] <= data['date_debut']:
                raise serializers.ValidationError("La date de fin doit être postérieure à la date de début")
        return data


class DetailCoûtMatiereSerializer(serializers.ModelSerializer):
    """Serializer pour les détails des coûts par matière"""
    matiere_premiere_nom = serializers.CharField(source='matiere_premiere.nom', read_only=True)
    matiere_premiere_unite = serializers.CharField(source='matiere_premiere.unite_mesure', read_only=True)
    
    class Meta:
        model = DetailCoûtMatiere
        fields = [
            'id', 'matiere_premiere', 'matiere_premiere_nom', 'matiere_premiere_unite',
            'quantite_utilisee', 'prix_unitaire', 'coût_total_matiere'
        ]


class CalculCoûtRevientSerializer(serializers.ModelSerializer):
    """Serializer pour les calculs de coûts de revient"""
    commande_numero = serializers.CharField(source='commande.id', read_only=True)
    ordre_production_numero = serializers.CharField(source='ordre_production.numero_bon', read_only=True)
    formule_nom = serializers.CharField(source='formule.nom', read_only=True)
    details_matieres = DetailCoûtMatiereSerializer(many=True, read_only=True)
    
    # Champs calculés en lecture seule
    coût_matieres_premieres = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    coût_main_oeuvre = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    coût_frais_generaux = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    coût_transport = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    coût_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    coût_unitaire_matieres = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    coût_unitaire_main_oeuvre = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    coût_unitaire_frais_generaux = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    coût_unitaire_transport = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    coût_unitaire_total = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    
    class Meta:
        model = CalculCoûtRevient
        fields = [
            'id', 'commande', 'commande_numero', 'ordre_production', 'ordre_production_numero',
            'formule', 'formule_nom', 'quantite_calculee', 'unite_mesure',
            'coût_matieres_premieres', 'coût_main_oeuvre', 'coût_frais_generaux', 
            'coût_transport', 'coût_total',
            'coût_unitaire_matieres', 'coût_unitaire_main_oeuvre', 
            'coût_unitaire_frais_generaux', 'coût_unitaire_transport', 'coût_unitaire_total',
            'date_calcul', 'date_modification', 'calculé_par', 'notes', 'details_matieres'
        ]
        read_only_fields = [
            'date_calcul', 'date_modification', 'coût_matieres_premieres', 
            'coût_main_oeuvre', 'coût_frais_generaux', 'coût_transport', 'coût_total',
            'coût_unitaire_matieres', 'coût_unitaire_main_oeuvre', 
            'coût_unitaire_frais_generaux', 'coût_unitaire_transport', 'coût_unitaire_total'
        ]
    
    def validate(self, data):
        """Validation des données"""
        if data.get('quantite_calculee', 0) <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        
        # Vérifier qu'au moins une commande ou un ordre de production est spécifié
        if not data.get('commande') and not data.get('ordre_production'):
            # Permettre les calculs sans commande/ordre pour les simulations
            pass
        
        return data
    
    def create(self, validated_data):
        """Création d'un calcul avec calcul automatique des coûts"""
        calcul = super().create(validated_data)
        calcul.calculer_coûts()
        calcul.save()
        return calcul


class CalculCoûtRevientDetailSerializer(CalculCoûtRevientSerializer):
    """Serializer détaillé pour les calculs de coûts de revient"""
    commande_details = serializers.SerializerMethodField()
    ordre_production_details = serializers.SerializerMethodField()
    formule_details = serializers.SerializerMethodField()
    
    class Meta(CalculCoûtRevientSerializer.Meta):
        fields = CalculCoûtRevientSerializer.Meta.fields + [
            'commande_details', 'ordre_production_details', 'formule_details'
        ]
    
    def get_commande_details(self, obj):
        """Détails de la commande associée"""
        if obj.commande:
            return {
                'id': obj.commande.id,
                'client_nom': obj.commande.client.nom if obj.commande.client else None,
                'date_creation': obj.commande.date_creation,
                'statut': obj.commande.statut
            }
        return None
    
    def get_ordre_production_details(self, obj):
        """Détails de l'ordre de production associé"""
        if obj.ordre_production:
            return {
                'id': obj.ordre_production.id,
                'numero_bon': obj.ordre_production.numero_bon,
                'date_creation': obj.ordre_production.date_creation,
                'statut': obj.ordre_production.statut
            }
        return None
    
    def get_formule_details(self, obj):
        """Détails de la formule utilisée"""
        return {
            'id': obj.formule.id,
            'nom': obj.formule.nom,
            'description': obj.formule.description,
            'quantite_reference': obj.formule.quantite_produite_reference,
            'resistance_requise': obj.formule.resistance_requise
        }


# Serializers simplifiés pour les listes déroulantes
class MatierePremierSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple pour les matières premières"""
    class Meta:
        model = MatierePremiere
        fields = ['id', 'nom', 'unite_mesure']


class FormuleBetonSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple pour les formules de béton"""
    class Meta:
        model = FormuleBeton
        fields = ['id', 'nom', 'description', 'quantite_produite_reference']


class CommandeSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple pour les commandes"""
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    
    class Meta:
        model = Commande
        fields = ['id', 'client_nom', 'date_creation', 'statut']


class OrdreProductionSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple pour les ordres de production"""
    class Meta:
        model = OrdreProduction
        fields = ['id', 'numero_bon', 'date_creation', 'statut']