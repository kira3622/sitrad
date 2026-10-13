from django.contrib import admin
from .models import Encaissement
from django.utils.html import format_html
from decimal import Decimal


@admin.register(Encaissement)
class EncaissementAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'client',
        'numero_bon_display',
        'montant_display',
        'mode_reglement',
        'numero_reglement',
        'date_encaissement',
    )
    list_filter = (
        'mode_reglement',
        'date_encaissement',
        'client',
    )
    search_fields = (
        'reference',
        'client__nom',
        'numero_reglement',
        'ordre_production__numero_bon',
        'notes',
    )
    autocomplete_fields = ('client', 'ordre_production')
    readonly_fields = ('reference', 'date_creation', 'date_modification')
    date_hierarchy = 'date_encaissement'

    fieldsets = (
        ('Informations générales', {
            'fields': ('reference', 'client', 'ordre_production', 'date_encaissement'),
        }),
        ('Montant et règlement', {
            'fields': ('montant', 'mode_reglement', 'numero_reglement'),
        }),
        ('Informations complémentaires', {
            'fields': ('notes',),
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',),
        }),
    )

    def numero_bon_display(self, obj):
        if obj.ordre_production and obj.ordre_production.numero_bon:
            return format_html(
                '<span style="color: #007cba; font-weight: 600;">{}</span>',
                obj.ordre_production.numero_bon,
            )
        return format_html('<span style="color: #999;">—</span>')
    numero_bon_display.short_description = "N° Bon"

    def montant_display(self, obj):
        montant_str = f"{obj.montant:.2f}"
        return format_html(
            '<span style="font-weight: 700; color: #166534;">{} MAD</span>',
            montant_str,
        )
    montant_display.short_description = "Montant"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client', 'ordre_production')
