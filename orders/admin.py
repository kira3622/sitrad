from django.contrib import admin
from .models import Commande, LigneCommande

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 1

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'chantier', 'date_commande', 'date_livraison_souhaitee', 'statut')
    list_filter = ('statut', 'date_commande', 'client')
    search_fields = ('client__nom', 'chantier__nom')
    inlines = [LigneCommandeInline]
