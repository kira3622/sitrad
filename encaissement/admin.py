from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils.html import format_html
from .models import Encaissement
from .forms import EncaissementForm
from production.models import OrdreProduction


@admin.register(Encaissement)
class EncaissementAdmin(admin.ModelAdmin):
    form = EncaissementForm

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
    autocomplete_fields = ('client',)
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

    class Media:
        js = ('admin/js/encaissement_admin.js',)

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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'bons-par-client/<int:client_id>/',
                self.admin_site.admin_view(self.bons_par_client_view),
                name='encaissement_bons_par_client',
            ),
        ]
        return custom_urls + urls

    def bons_par_client_view(self, request, client_id):
        """Retourne la liste des bons de livraison (OrdreProduction) d'un client, triés par numéro de bon."""
        bons = OrdreProduction.objects.filter(
            commande__client_id=client_id
        ).order_by('numero_bon').select_related('formule')

        data = [
            {
                'id': bon.id,
                'numero_bon': bon.numero_bon or f'#{bon.id}',
                'label': f"{bon.numero_bon or '#'+str(bon.id)} - {bon.formule.nom if bon.formule else '-'} ({bon.quantite_produire} m³)",
            }
            for bon in bons
        ]
        return JsonResponse({'bons': data})
