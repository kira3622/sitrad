from django.contrib import admin
from .models import Client, Chantier

class ChantierInline(admin.TabularInline):
    model = Chantier
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [ChantierInline]
    list_display = ('nom', 'adresse', 'telephone', 'email')
    search_fields = ('nom', 'adresse', 'email')

@admin.register(Chantier)
class ChantierAdmin(admin.ModelAdmin):
    list_display = ('nom', 'client', 'adresse')
    list_filter = ('client',)
    search_fields = ('nom', 'adresse')
