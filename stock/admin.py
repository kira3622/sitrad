from django.contrib import admin
from django.utils.html import format_html
from .models import MouvementStock, SaisieEntreeLie, Fournisseur

# Temporairement désactivé pour débogage
# @admin.register(MouvementStock)
# class MouvementStockAdmin(admin.ModelAdmin):
#     list_display = ('matiere_premiere_id', 'quantite', 'type_mouvement', 'date_mouvement', 'description')
#     # list_filter = ('type_mouvement', 'matiere_premiere')
#     # search_fields = ('matiere_premiere__nom', 'description')
#     # date_hierarchy = 'date_mouvement'
#     # list_select_related = ('matiere_premiere',)

# Enregistrement basique temporaire
admin.site.register(MouvementStock)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'contact', 'telephone', 'email', 'actif', 'date_creation']
    list_filter = ['actif', 'date_creation']
    search_fields = ['nom', 'contact', 'telephone', 'email']
    list_editable = ['actif']
    readonly_fields = ['date_creation', 'date_modification']
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'contact', 'actif')
        }),
        ('Contact', {
            'fields': ('telephone', 'email', 'adresse')
        }),
        ('Informations système', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SaisieEntreeLie)
class SaisieEntreeLieAdmin(admin.ModelAdmin):
    list_display = ['fournisseur', 'matiere_premiere', 'quantite_display', 'prix_achat_ht_display', 'montant_ttc_display', 'montant_total_ttc_display', 'numero_facture', 'date_facture', 'date_creation']
    list_filter = ['matiere_premiere', 'date_creation', 'date_facture']
    search_fields = ['fournisseur', 'numero_facture', 'matiere_premiere__nom']
    date_hierarchy = 'date_creation'
    readonly_fields = ['date_creation', 'date_modification', 'montant_ttc_display', 'montant_tva_display', 'montant_total_ttc_display']
    autocomplete_fields = ['matiere_premiere', 'fournisseur']
    fieldsets = (
        ('Informations générales', {
            'fields': ('fournisseur', 'matiere_premiere', 'quantite', 'numero_facture', 'date_facture')
        }),
        ('Détails financiers', {
            'fields': ('prix_achat_ht', 'taux_tva', 'montant_tva_display', 'montant_ttc_display', 'montant_total_ttc_display')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Informations système', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    
    
    def quantite_display(self, obj):
        if obj.quantite and obj.matiere_premiere:
            return f"{obj.quantite} {obj.matiere_premiere.unite_mesure}"
        elif obj.quantite:
            return f"{obj.quantite}"
        else:
            return "-"
    quantite_display.short_description = "Quantité"
    
    def prix_achat_ht_display(self, obj):
        if obj.prix_achat_ht:
            return format_html('<span>{} MAD</span>', '{:.4f}'.format(obj.prix_achat_ht))
        return "-"
    prix_achat_ht_display.short_description = "Prix d'achat HT"
    
    def montant_ttc_display(self, obj):
        if obj.montant_ttc:
            return format_html('<span style="font-weight: bold;">{} MAD</span>', '{:.4f}'.format(obj.montant_ttc))
        return "-"
    montant_ttc_display.short_description = "Montant TTC"
    
    def montant_tva_display(self, obj):
        if obj.montant_tva:
            return format_html('<span>{} MAD</span>', '{:.4f}'.format(obj.montant_tva))
        return "-"
    montant_tva_display.short_description = "Montant TVA"
    
    def montant_total_ttc_display(self, obj):
        if obj.montant_total_ttc:
            return format_html('<span style="font-weight: bold; color: #28a745;">{} MAD</span>', '{:.4f}'.format(obj.montant_total_ttc))
        return "-"
    montant_total_ttc_display.short_description = "Montant Total TTC"
