from django.contrib import admin
from .models import Facture, LigneFacture
from django.urls import reverse
from django.utils.html import format_html

class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1
    readonly_fields = ('montant_ligne',)
    fields = ('description', 'quantite', 'prix_unitaire', 'montant_ligne')

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    def view_pdf_link(self, obj):
        if obj.id:
            url = reverse('facture_pdf', args=[obj.id])
            return format_html('<a href="{url}">Voir PDF</a>', url=url)
        return "Sauvegarder d'abord"
    view_pdf_link.short_description = "Facture PDF"
    
    list_display = ('id', 'commande', 'date_facturation', 'montant_total', 'statut', 'view_pdf_link')
    list_filter = ('date_facturation', 'statut')
    search_fields = ('commande__id', 'commande__client__nom')
    inlines = [LigneFactureInline]
    readonly_fields = ('montant_total', 'date_facturation', 'view_pdf_link')
    fields = ('commande', 'statut', 'date_facturation', 'montant_total')

    def save_model(self, request, obj, form, change):
        # Le calcul du montant total est maintenant automatique dans le modèle
        super().save_model(request, obj, form, change)

@admin.register(LigneFacture)
class LigneFactureAdmin(admin.ModelAdmin):
    list_display = ('facture', 'description', 'quantite', 'prix_unitaire', 'montant_ligne')
    readonly_fields = ('montant_ligne',)
