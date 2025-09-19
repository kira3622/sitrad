from django.contrib import admin
from django.utils.html import format_html
from .models import MatierePremiere

@admin.register(MatierePremiere)
class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'unite_mesure', 'stock_actuel_display', 'seuil_critique', 'seuil_bas', 'statut_stock_display')
    search_fields = ('nom',)
    list_filter = ('unite_mesure',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'unite_mesure')
        }),
        ('Configuration des seuils', {
            'fields': ('seuil_critique', 'seuil_bas'),
            'description': 'Configurez les seuils d\'alerte pour cette matière première'
        }),
    )

    def stock_actuel_display(self, obj):
        """Affiche le stock actuel avec l'unité de mesure"""
        return f"{obj.stock_actuel} {obj.unite_mesure}"
    stock_actuel_display.short_description = "Stock actuel"

    def statut_stock_display(self, obj):
        """Affiche le statut du stock avec des couleurs"""
        statut = obj.statut_stock
        if statut == 'critique':
            return format_html('<span style="color: red; font-weight: bold;">🔴 CRITIQUE</span>')
        elif statut == 'bas':
            return format_html('<span style="color: orange; font-weight: bold;">🟠 BAS</span>')
        else:
            return format_html('<span style="color: green;">🟢 NORMAL</span>')
    statut_stock_display.short_description = "Statut"
