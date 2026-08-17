from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import MouvementStock, SaisieEntreeLie, Fournisseur


class MouvementStockTypeFilter(admin.SimpleListFilter):
    title = _('type de mouvement')
    parameter_name = 'type_mouvement'

    def lookups(self, request, model_admin):
        return (
            ('entree', _('Entrées')),
            ('sortie', _('Sorties')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'entree':
            return queryset.filter(type_mouvement='entree')
        if self.value() == 'sortie':
            return queryset.filter(type_mouvement='sortie')
        return queryset


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'type_mouvement_badge',
        'matiere_premiere',
        'unite_mesure',
        'quantite_display',
        'description_abr',
        'origine',
        'lien_saisie_entree',
        'date_mouvement',
    )
    list_display_links = ('id', 'date_mouvement')
    list_filter = (
        MouvementStockTypeFilter,
        ('matiere_premiere', admin.RelatedOnlyFieldListFilter),
        ('date_mouvement', admin.DateFieldListFilter),
    )
    search_fields = (
        'id',
        'matiere_premiere__nom',
        'description',
        'saisieentreelie__fournisseur__nom',
        'saisieentreelie__numero_facture',
    )
    autocomplete_fields = ('matiere_premiere',)
    date_hierarchy = 'date_mouvement'
    list_select_related = ('matiere_premiere', 'saisieentreelie', 'saisieentreelie__fournisseur')
    ordering = ('-date_mouvement', '-id')
    list_per_page = 50

    readonly_fields = (
        'type_mouvement_badge',
        'quantite_display',
        'unite_mesure',
        'origine',
        'lien_saisie_entree',
        'stock_apres_mouvement',
        'description',
        'date_mouvement',
    )

    fieldsets = (
        (_('Mouvement'), {
            'fields': (
                'type_mouvement',
                'type_mouvement_badge',
                'matiere_premiere',
                'unite_mesure',
                'quantite',
                'quantite_display',
                'date_mouvement',
            )
        }),
        (_('Origine & traçabilité'), {
            'fields': (
                'origine',
                'lien_saisie_entree',
                'description',
            )
        }),
        (_('Stock'), {
            'fields': ('stock_apres_mouvement',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'matiere_premiere',
            'saisieentreelie',
            'saisieentreelie__fournisseur',
        ).prefetch_related('matiere_premiere__mouvementstock_set')

    def type_mouvement_badge(self, obj):
        if obj.type_mouvement == 'entree':
            color = 'background:#dcfce7;color:#166534;'
            label = _('Entrée')
            arrow = '↗'
        else:
            color = 'background:#fee2e2;color:#991b1b;'
            label = _('Sortie')
            arrow = '↘'
        return format_html(
            '<span style="padding:3px 8px;border-radius:999px;font-weight:600;{}">{} {}</span>',
            color, arrow, label
        )
    type_mouvement_badge.short_description = _('Type')
    type_mouvement_badge.admin_order_field = 'type_mouvement'

    def unite_mesure(self, obj):
        if obj.matiere_premiere and obj.matiere_premiere.unite_mesure:
            return obj.matiere_premiere.unite_mesure
        return '-'
    unite_mesure.short_description = _('Unité')
    unite_mesure.admin_order_field = 'matiere_premiere__unite_mesure'

    def quantite_display(self, obj):
        unite = self.unite_mesure(obj)
        qty = obj.quantite
        if qty is None:
            return '-'
        return format_html(
            '<strong>{}</strong> <span style="color:#6b7280;">{}</span>',
            f"{qty:.2f}", unite
        )
    quantite_display.short_description = _('Quantité')
    quantite_display.admin_order_field = 'quantite'

    def description_abr(self, obj):
        txt = (obj.description or '').strip()
        if len(txt) == 0:
            return format_html('<em style="color:#9ca3af;">—</em>')
        if len(txt) <= 60:
            return format_html('{}', txt)
        return format_html('{}…', txt[:57])
    description_abr.short_description = _('Description')
    description_abr.admin_order_field = 'description'

    def origine(self, obj):
        try:
            entree = obj.saisieentreelie
        except MouvementStock.saisieentreelie.RelatedObjectDoesNotExist:
            entree = None
        if entree is not None:
            pieces = []
            if entree.fournisseur:
                pieces.append(str(entree.fournisseur))
            if entree.numero_facture:
                pieces.append(_("Fact. {}").format(entree.numero_facture))
            if entree.date_facture:
                pieces.append(entree.date_facture.isoformat())
            if pieces:
                return format_html(
                    '<span style="color:#065f46;">{}</span>',
                    ' · '.join(pieces)
                )
        desc = (obj.description or '').lower()
        if 'ordre de production' in desc or 'lot' in desc or 'production' in desc:
            return format_html(
                '<span style="color:#7c2d12;">{}</span>',
                _('Production')
            )
        if obj.type_mouvement == 'entree':
            return format_html('<span style="color:#334155;">{}</span>', _('Entrée manuelle'))
        return format_html('<span style="color:#334155;">{}</span>', _('Sortie manuelle'))
    origine.short_description = _('Origine')

    def lien_saisie_entree(self, obj):
        try:
            entree = obj.saisieentreelie
        except MouvementStock.saisieentreelie.RelatedObjectDoesNotExist:
            return format_html('<em style="color:#9ca3af;">—</em>')
        from django.urls import reverse
        url = reverse('admin:stock_saisieentreelie_change', args=(entree.id,))
        return format_html(
            '<a href="{}" style="font-weight:600;">#{} &raquo;</a>',
            url, entree.id
        )
    lien_saisie_entree.short_description = _('Saisie liée')

    def stock_apres_mouvement(self, obj):
        if not (obj.matiere_premiere_id and obj.date_mouvement and obj.id):
            return '-'
        from django.db.models import Sum, Q
        mp = obj.matiere_premiere
        qs = mp.mouvementstock_set.filter(
            Q(date_mouvement__lt=obj.date_mouvement)
            | Q(date_mouvement=obj.date_mouvement, id__lte=obj.id)
        )
        entrees = qs.filter(type_mouvement='entree').aggregate(t=Sum('quantite'))['t'] or 0
        sorties = qs.filter(type_mouvement='sortie').aggregate(t=Sum('quantite'))['t'] or 0
        stock = entrees - sorties
        unite = mp.unite_mesure or ''
        return format_html(
            '<strong>{}</strong> <span style="color:#6b7280;">{}</span>',
            f"{stock:.2f}", unite
        )
    stock_apres_mouvement.short_description = _('Stock après mouvement')


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'contact', 'telephone', 'email', 'actif', 'date_creation']
    list_filter = ['actif', 'date_creation']
    search_fields = ['nom', 'contact', 'telephone', 'email']
    list_editable = ['actif']
    readonly_fields = ['date_creation', 'date_modification']
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'contact', 'actif')
        }),
        ('Contact', {
            'fields': ('telephone', 'email', 'adresse')
        }),
        ('Informations système', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SaisieEntreeLie)
class SaisieEntreeLieAdmin(admin.ModelAdmin):
    list_display = ['fournisseur', 'matiere_premiere', 'quantite_display', 'prix_achat_ht_display', 'montant_ttc_display', 'montant_total_ttc_display', 'numero_facture', 'date_facture', 'date_creation']
    list_filter = ['matiere_premiere', 'date_creation', 'date_facture']
    search_fields = ['fournisseur', 'numero_facture', 'matiere_premiere__nom']
    date_hierarchy = 'date_creation'
    readonly_fields = ['date_creation', 'date_modification', 'montant_ttc_display', 'montant_tva_display', 'montant_total_ttc_display']
    autocomplete_fields = ['matiere_premiere', 'fournisseur']
    fieldsets = (
        ('Informations générales', {
            'fields': ('fournisseur', 'matiere_premiere', 'quantite', 'numero_facture', 'date_facture')
        }),
        ('Détails financiers', {
            'fields': ('prix_achat_ht', 'taux_tva', 'montant_tva_display', 'montant_ttc_display', 'montant_total_ttc_display')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Informations système', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    
    
    def quantite_display(self, obj):
        if obj.quantite and obj.matiere_premiere:
            return f"{obj.quantite} {obj.matiere_premiere.unite_mesure}"
        elif obj.quantite:
            return f"{obj.quantite}"
        else:
            return "-"
    quantite_display.short_description = "Quantité"
    
    def prix_achat_ht_display(self, obj):
        if obj.prix_achat_ht:
            return format_html('<span>{} MAD</span>', '{:.4f}'.format(obj.prix_achat_ht))
        return "-"
    prix_achat_ht_display.short_description = "Prix d'achat HT"
    
    def montant_ttc_display(self, obj):
        if obj.montant_ttc:
            return format_html('<span style="font-weight: bold;">{} MAD</span>', '{:.4f}'.format(obj.montant_ttc))
        return "-"
    montant_ttc_display.short_description = "Montant TTC"
    
    def montant_tva_display(self, obj):
        if obj.montant_tva:
            return format_html('<span>{} MAD</span>', '{:.4f}'.format(obj.montant_tva))
        return "-"
    montant_tva_display.short_description = "Montant TVA"
    
    def montant_total_ttc_display(self, obj):
        if obj.montant_total_ttc:
            return format_html('<span style="font-weight: bold; color: #28a745;">{} MAD</span>', '{:.4f}'.format(obj.montant_total_ttc))
        return "-"
    montant_total_ttc_display.short_description = "Montant Total TTC"
