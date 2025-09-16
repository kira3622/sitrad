from django.contrib import admin
from .models import OrdreProduction, LotProduction

class LotProductionInline(admin.TabularInline):
    model = LotProduction
    extra = 0

@admin.register(OrdreProduction)
class OrdreProductionAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'formule', 'quantite_produire', 'date_production', 'statut')
    list_filter = ('statut', 'date_production')
    search_fields = ('commande__client__nom', 'formule__nom')
    inlines = [LotProductionInline]
