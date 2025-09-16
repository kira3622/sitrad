from django.contrib import admin
from .models import Facture, LigneFacture
from django.urls import reverse
from django.utils.html import format_html

class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1
    readonly_fields = ('montant_ligne',)

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'date_facturation', 'montant_total', 'statut', 'view_pdf_link')
    list_filter = ('date_facturation', 'statut')
    search_fields = ('commande__id', 'commande__client__nom', 'reference')
    inlines = [LigneFactureInline]
    readonly_fields = ('montant_total',)

    def view_pdf_link(self, obj):
        url = reverse('facture_pdf', args=[obj.id])
        return format_html('<a href="{url}">Voir PDF</a>', url=url)
    view_pdf_link.short_description = "Facture PDF"
