from django.contrib import admin
from .models import MouvementStock

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
