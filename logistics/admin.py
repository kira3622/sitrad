from django.contrib import admin
from .models import Vehicule, Livraison, Chauffeur, Pompe

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

@admin.register(Pompe)
class PompeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'marque', 'modele', 'statut', 'operateur', 'debit_max', 'actif', 'jours_depuis_maintenance_display')
    list_filter = ('statut', 'marque', 'actif', 'date_acquisition')
    search_fields = ('nom', 'numero_serie', 'marque', 'modele', 'operateur__nom')
    list_editable = ('statut', 'actif')
    readonly_fields = ('jours_depuis_maintenance_display',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'numero_serie', 'marque', 'modele', 'statut', 'actif')
        }),
        ('Caractéristiques techniques', {
            'fields': ('debit_max', 'portee_max', 'hauteur_max')
        }),
        ('Gestion', {
            'fields': ('operateur', 'date_acquisition', 'date_derniere_maintenance', 'jours_depuis_maintenance_display')
        }),
    )
    
    def jours_depuis_maintenance_display(self, obj):
        """Affiche le nombre de jours depuis la dernière maintenance"""
        jours = obj.jours_depuis_maintenance()
        if jours is not None:
            if jours > 365:
                return f"{jours} jours (⚠️ Maintenance requise)"
            elif jours > 180:
                return f"{jours} jours (⚠️ Maintenance recommandée)"
            else:
                return f"{jours} jours"
        return "Aucune maintenance enregistrée"
    
    jours_depuis_maintenance_display.short_description = "Jours depuis maintenance"
    
    def get_queryset(self, request):
        """Optimise les requêtes en incluant l'opérateur"""
        return super().get_queryset(request).select_related('operateur')
