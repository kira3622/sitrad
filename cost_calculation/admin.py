from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    CategorieCoût, CoûtMatierePremiere, CoûtMainOeuvre, 
    CoûtFraisGeneraux, CalculCoûtRevient, DetailCoûtMatiere
)


@admin.register(CategorieCoût)
class CategorieCoûtAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_categorie', 'actif', 'date_creation')
    list_filter = ('type_categorie', 'actif', 'date_creation')
    search_fields = ('nom', 'description')
    ordering = ('type_categorie', 'nom')


@admin.register(CoûtMatierePremiere)
class CoûtMatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('matiere_premiere', 'prix_unitaire', 'coût_transport', 'coût_stockage', 'prix_total_unitaire', 'actif', 'date_debut')
    list_filter = ('actif', 'date_debut', 'date_fin', 'matiere_premiere')
    search_fields = ('matiere_premiere__nom', 'fournisseur', 'reference_fournisseur')
    ordering = ('-date_debut',)
    readonly_fields = ('prix_total_unitaire',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('matiere_premiere')


@admin.register(CoûtMainOeuvre)
class CoûtMainOeuvreAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_activite', 'coût_horaire_base', 'charges_sociales_pourcentage', 'coût_horaire_total', 'actif', 'date_debut')
    list_filter = ('type_activite', 'actif', 'date_debut', 'date_fin')
    search_fields = ('nom', 'type_activite', 'description')
    ordering = ('type_activite', 'nom')
    readonly_fields = ('coût_horaire_total',)


@admin.register(CoûtFraisGeneraux)
class CoûtFraisGenerauxAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'valeur', 'type_repartition', 'actif', 'date_debut')
    list_filter = ('actif', 'type_repartition', 'categorie', 'date_debut')
    search_fields = ('nom', 'description')
    ordering = ('categorie', 'nom')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categorie')


class DetailCoûtMatiereInline(admin.TabularInline):
    model = DetailCoûtMatiere
    extra = 0
    readonly_fields = ('prix_unitaire', 'coût_total_matiere')


@admin.register(CalculCoûtRevient)
class CalculCoûtRevientAdmin(admin.ModelAdmin):
    list_display = ('id', 'formule', 'quantite_calculee', 'unite_mesure', 'coût_total', 'coût_unitaire_total', 'date_calcul', 'view_link')
    list_filter = ('date_calcul', 'formule')
    search_fields = ('commande__id', 'ordre_production__id')
    ordering = ('-date_calcul',)
    readonly_fields = (
        'coût_matieres_premieres', 'coût_unitaire_matieres',
        'coût_main_oeuvre', 'coût_unitaire_main_oeuvre',
        'coût_frais_generaux', 'coût_unitaire_frais_generaux',
        'coût_transport', 'coût_unitaire_transport',
        'coût_total', 'coût_unitaire_total',
        'date_calcul', 'date_modification'
    )
    inlines = [DetailCoûtMatiereInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('commande', 'ordre_production', 'formule', 'quantite_calculee', 'unite_mesure')
        }),
        ('Matières premières', {
            'fields': ('coût_matieres_premieres', 'coût_unitaire_matieres'),
            'classes': ('collapse',)
        }),
        ('Main d\'œuvre', {
            'fields': ('coût_main_oeuvre', 'coût_unitaire_main_oeuvre'),
            'classes': ('collapse',)
        }),
        ('Frais généraux', {
            'fields': ('coût_frais_generaux', 'coût_unitaire_frais_generaux'),
            'classes': ('collapse',)
        }),
        ('Transport', {
            'fields': ('coût_transport', 'coût_unitaire_transport'),
            'classes': ('collapse',)
        }),
        ('Totaux', {
            'fields': ('coût_total', 'coût_unitaire_total'),
        }),
        ('Métadonnées', {
            'fields': ('date_calcul', 'date_modification', 'notes'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('commande', 'ordre_production', 'formule')

    def view_link(self, obj):
        url = reverse('cost_calculation:detail_calcul', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Voir détail</a>', url)
    view_link.short_description = 'Détail'


@admin.register(DetailCoûtMatiere)
class DetailCoûtMatiereAdmin(admin.ModelAdmin):
    list_display = ('calcul_coût', 'matiere_premiere', 'quantite_utilisee', 'prix_unitaire', 'coût_total_matiere')
    list_filter = ('calcul_coût__date_calcul', 'matiere_premiere')
    search_fields = ('calcul_coût__id', 'matiere_premiere__nom')
    ordering = ('-calcul_coût__date_calcul',)
    readonly_fields = ('coût_total_matiere',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('calcul_coût', 'matiere_premiere')
