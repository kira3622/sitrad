from django.contrib import admin
from .models import Vehicule, Livraison, Chauffeur

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'modele', 'capacite', 'chauffeur')
    search_fields = ('immatriculation', 'modele', 'chauffeur__nom')

@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'numero_permis', 'actif')
    search_fields = ('nom', 'telephone', 'numero_permis')

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('commande', 'vehicule', 'date_livraison', 'statut')
    list_filter = ('date_livraison', 'statut', 'vehicule')
    search_fields = ('commande__client__nom', 'commande__id')
