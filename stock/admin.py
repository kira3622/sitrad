from django.contrib import admin
from .models import MouvementStock

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('matiere_premiere', 'quantite', 'type_mouvement', 'date_mouvement')
    list_filter = ('type_mouvement', 'matiere_premiere')
    search_fields = ('matiere_premiere__nom',)
    # date_hierarchy = 'date_mouvement'
    list_select_related = ('matiere_premiere',)
