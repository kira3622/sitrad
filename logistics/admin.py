from django.contrib import admin
from .models import Vehicule, Livraison

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'modele', 'capacite')
    search_fields = ('immatriculation', 'modele')

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('commande', 'vehicule', 'date_livraison', 'statut')
    list_filter = ('date_livraison', 'statut', 'vehicule')
    search_fields = ('commande__client__nom', 'commande__id')
