from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from .models import (
    Vehicule, Livraison, Chauffeur, Pompe, PlanningLivraisons, SaisiePlanningModule,
)

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
    list_display = ('commande', 'vehicule', 'date_livraison', 'heure_livraison', 'statut')
    list_filter = ('date_livraison', 'statut', 'vehicule')
    search_fields = ('commande__client__nom', 'commande__id')


@admin.register(PlanningLivraisons)
class PlanningLivraisonsAdmin(admin.ModelAdmin):
    """Entrée de menu « Planning des livraisons prévues ».
    Redirige vers la vue de planning (consultation + planification).
    """
    list_display = ()
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        # Aucun enregistrement à afficher : simple point d'entrée.
        return Livraison.objects.none()

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('planning:livraisons'))


@admin.register(SaisiePlanningModule)
class SaisiePlanningModuleAdmin(admin.ModelAdmin):
    """Entrée de menu « Saisie des plannings ».
    Redirige vers la page dédiée de saisie libre des livraisons planifiées.
    """
    list_display = ()
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        # Aucun enregistrement à afficher : simple point d'entrée.
        return SaisiePlanningModule.objects.none()

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('planning:saisie'))

@admin.register(Pompe)
class PompeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'immatriculation', 'marque', 'modele', 'statut', 'operateur', 'debit_max', 'actif', 'jours_depuis_maintenance_display')
    list_filter = ('statut', 'marque', 'actif', 'date_acquisition')
    search_fields = ('nom', 'immatriculation', 'numero_serie', 'marque', 'modele', 'operateur__nom')
    list_editable = ('statut', 'actif')
    readonly_fields = ('jours_depuis_maintenance_display',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'immatriculation', 'numero_serie', 'marque', 'modele', 'statut', 'actif')
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
