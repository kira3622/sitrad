from django.contrib import admin
from .models import MatierePremiere

@admin.register(MatierePremiere)
class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'unite_mesure')
    search_fields = ('nom',)
