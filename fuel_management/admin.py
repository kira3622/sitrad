from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from .models import Fournisseur, TypeEngin, Engin, Approvisionnement, Consommation, Stock, AlerteStock


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'contact', 'telephone', 'email']
    search_fields = ['nom', 'contact', 'telephone', 'email']


@admin.register(TypeEngin)
class TypeEnginAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(Engin)
class EnginAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_engin', 'numero_serie', 'consommation_totale']
    list_filter = ['type_engin']
    search_fields = ['nom', 'numero_serie']
    
    def consommation_totale(self, obj):
        total = Consommation.objects.filter(engin=obj).aggregate(
            total=Sum('quantite')
        )['total'] or 0
        return f"{total} L"
    consommation_totale.short_description = "Consommation totale"


@admin.register(Approvisionnement)
class ApprovisionnementAdmin(admin.ModelAdmin):
    list_display = ['date', 'fournisseur', 'quantite', 'prix_unitaire', 'montant_total_mad', 'numero_bon']
    list_filter = ['date', 'fournisseur']
    search_fields = ['numero_bon', 'fournisseur__nom']
    date_hierarchy = 'date'
    readonly_fields = ['montant_total']

    def montant_total_mad(self, obj):
        valeur = float(obj.montant_total or 0)
        return format_html(
            '<span style="color: #7c2d12; font-weight: 600;">{} MAD</span>',
            f"{valeur:.2f}"
        )
    montant_total_mad.short_description = "Montant Total (MAD)"

    class Media:
        js = ('admin/js/fuel_management_admin.js',)


@admin.register(Consommation)
class ConsommationAdmin(admin.ModelAdmin):
    list_display = ['date', 'numero_bon', 'engin', 'quantite', 'prix_unitaire', 'montant_total_mad', 'responsable']
    list_filter = ['date', 'engin__type_engin', 'responsable']
    search_fields = ['numero_bon', 'engin__nom', 'responsable']
    date_hierarchy = 'date'
    readonly_fields = ['montant_total']
    fieldsets = (
        (None, {
            'fields': ('date', 'numero_bon', 'engin', 'responsable')
        }),
        ('Quantité & Coût', {
            'fields': ('quantite', 'prix_unitaire', 'montant_total'),
            'description': 'Montant total = Quantité (L) × Prix unitaire (DH/L). Mis à jour automatiquement à la sauvegarde.'
        }),
        ('Informations complémentaires', {
            'fields': ('heures_fonctionnement', 'kilometrage', 'notes'),
            'classes': ('collapse',),
        }),
    )

    def montant_total_mad(self, obj):
        valeur = float(obj.montant_total or 0)
        return format_html(
            '<span style="color: #7c2d12; font-weight: 600;">{} MAD</span>',
            f"{valeur:.2f}"
        )
    montant_total_mad.short_description = "Montant Total (MAD)"

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        dernier_appro = Approvisionnement.objects.order_by('-date', '-date_creation').first()
        if dernier_appro and dernier_appro.prix_unitaire > 0:
            initial.setdefault('prix_unitaire', str(dernier_appro.prix_unitaire))
        return initial

    class Media:
        js = ('admin/js/fuel_management_admin.js',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['quantite', 'seuil_minimum', 'statut_stock_display', 'date_derniere_maj']
    readonly_fields = ['quantite', 'date_derniere_maj']
    
    def statut_stock_display(self, obj):
        statut = obj.statut_stock
        if statut == 'rupture':
            return format_html(
                '<span style="color: red; font-weight: bold;">🚨 RUPTURE</span>'
            )
        elif statut == 'faible':
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ STOCK FAIBLE</span>'
            )
        elif statut == 'attention':
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠️ ATTENTION</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ OK</span>'
            )
    statut_stock_display.short_description = "Statut"
    
    def has_add_permission(self, request):
        # Empêcher la création manuelle de stocks multiples
        return not Stock.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression du stock
        return False


@admin.register(AlerteStock)
class AlerteStockAdmin(admin.ModelAdmin):
    list_display = ['date_alerte', 'quantite_stock', 'seuil_minimum', 'message', 'vue', 'statut_alerte']
    list_filter = ['vue', 'date_alerte']
    search_fields = ['message']
    date_hierarchy = 'date_alerte'
    list_editable = ['vue']
    readonly_fields = ['date_alerte', 'quantite_stock', 'seuil_minimum']
    
    def statut_alerte(self, obj):
        if not obj.vue:
            return format_html(
                '<span style="color: red; font-weight: bold;">🔴 NON VUE</span>'
            )
        else:
            return format_html(
                '<span style="color: green;">✅ VUE</span>'
            )
    statut_alerte.short_description = "Statut"
    
    def has_add_permission(self, request):
        # Les alertes sont créées automatiquement
        return False


# Configuration du titre de l'admin
admin.site.site_header = "Gestion Central SITRAD"
admin.site.site_title = "Gestion Gasoil"
admin.site.index_title = "Home › Tableau de bord - Gestion Central SITRAD"
