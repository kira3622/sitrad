from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from .models import (
    Prelevement, Eprouvette, EssaiEcrasement,
    EssaiGranulometrie, TamisGranulometrie,
    EssaiEquivalentSable, EssaiBleuMethylene, EssaiTeneurEnEau,
)


class StatutEprouvetteFilter(admin.SimpleListFilter):
    """Filtre personnalisé sur le statut de suivi des éprouvettes."""
    title = "statut de suivi"
    parameter_name = 'statut'

    def lookups(self, request, model_admin):
        return (
            ('a_ecraser', "À écraser aujourd'hui"),
            ('en_retard', 'En retard'),
            ('a_venir', 'À venir'),
            ('ecrase', 'Écrasées'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        aujourdhui = timezone.localdate()
        if value == 'ecrase':
            return queryset.filter(ecrasement__isnull=False)
        queryset = queryset.filter(ecrasement__isnull=True)
        if value == 'a_ecraser':
            return queryset.filter(date_echeance__date=aujourdhui)
        if value == 'en_retard':
            return queryset.filter(date_echeance__date__lt=aujourdhui)
        if value == 'a_venir':
            return queryset.filter(date_echeance__date__gt=aujourdhui)
        return queryset


class EssaiEcrasementInline(admin.StackedInline):
    model = EssaiEcrasement
    extra = 0
    fields = ('date_essai', 'poids_kg', 'force_rupture_kn', 'type_rupture',
              'surface_mm2', 'resistance_mpa', 'masse_volumique_kg_m3', 'conforme', 'observation')
    readonly_fields = ('surface_mm2', 'resistance_mpa', 'masse_volumique_kg_m3', 'conforme')


class EprouvetteInline(admin.TabularInline):
    model = Eprouvette
    extra = 2
    fields = ('code', 'forme', 'age_jours', 'date_fabrication', 'date_echeance', 'statut_badge')
    readonly_fields = ('statut_badge',)

    def statut_badge(self, obj):
        if not obj.pk:
            return '—'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            obj.statut_couleur, obj.statut_label,
        )
    statut_badge.short_description = "Statut"


@admin.register(Prelevement)
class PrelevementAdmin(admin.ModelAdmin):
    list_display = (
        'numero_bl', 'date_prelevement', 'element_coule', 'element_coule_detail',
        'client_nom', 'classe_resistance', 'affaissement_mm', 'temperature_beton',
        'temperature_ambiante', 'nb_eprouvettes_col', 'lien_pv',
    )
    list_filter = ('element_coule', 'classe_resistance', 'centrale', 'date_prelevement')
    search_fields = ('numero_bl', 'element_coule_detail', 'observations',
                     'ordre_production__numero_bon', 'ordre_production__commande__client__nom')
    date_hierarchy = 'date_prelevement'
    readonly_fields = ('date_creation', 'lien_pv', 'liens_suivi', 'formule_composition')
    autocomplete_fields = ('ordre_production',)
    inlines = [EprouvetteInline]
    actions = ['action_generer_7_28', 'action_generer_7_28_60']

    fieldsets = (
        ("Rattachement", {
            'fields': ('ordre_production', 'numero_bl', 'centrale', 'date_prelevement')
        }),
        ("Formule du béton", {
            'fields': ('formule_composition',)
        }),
        ("Élément coulé", {
            'fields': ('element_coule', 'element_coule_detail')
        }),
        ("Essai à l'état frais", {
            'fields': ('affaissement_mm', 'temperature_beton', 'temperature_ambiante')
        }),
        ("Résistance contractuelle", {
            'fields': ('classe_resistance',)
        }),
        ("Divers", {
            'fields': ('observations', 'date_creation', 'liens_suivi')
        }),
    )

    def client_nom(self, obj):
        client = obj.client
        return client.nom if client else '—'
    client_nom.short_description = "Client"

    def nb_eprouvettes_col(self, obj):
        return obj.eprouvettes.count()
    nb_eprouvettes_col.short_description = "Éprouvettes"

    def lien_pv(self, obj):
        if not obj.pk:
            return '—'
        url = reverse('laboratory:pv_pdf', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">📄 PV d\'essai PDF</a>', url)
    lien_pv.short_description = "PV"

    def liens_suivi(self, obj):
        if not obj.pk:
            return '—'
        detail = reverse('laboratory:prelevement_detail', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">🔬 Voir la fiche de suivi laboratoire</a>', detail)
    liens_suivi.short_description = "Suivi"

    def formule_composition(self, obj):
        """Formule utilisée sur le bon de production et sa composition (dosages)."""
        ordre = getattr(obj, 'ordre_production', None)
        formule = getattr(ordre, 'formule', None) if ordre is not None else None
        if formule is None:
            return format_html(
                '<p style="margin:0; color:#6b7280;">'
                "Aucune formule rattachée : sélectionnez d'abord un ordre de production.</p>"
            )

        entete = format_html(
            '<p style="margin:0 0 6px 0;"><strong>Formule : {}</strong>'
            ' &nbsp;|&nbsp; Résistance requise : <strong>{}</strong>'
            ' &nbsp;|&nbsp; Quantité de référence : {} m³'
            ' &nbsp;|&nbsp; Prix de vente : {} MAD/m³</p>',
            formule.nom, formule.resistance_requise,
            formule.quantite_produite_reference, formule.prix_vente_unitaire,
        )

        lignes = list(
            formule.composition.select_related('matiere_premiere')
            .order_by('matiere_premiere__nom')
        )
        if not lignes:
            return format_html(
                '{}<p style="margin:0; color:#6b7280;">'
                "Cette formule n'a pas de composition définie.</p>",
                entete,
            )

        corps = format_html_join(
            '',
            '<tr>'
            '<td style="padding:4px 12px; border-bottom:1px solid #e5e7eb;">{}</td>'
            '<td style="padding:4px 12px; border-bottom:1px solid #e5e7eb; text-align:right;">{}</td>'
            '<td style="padding:4px 12px; border-bottom:1px solid #e5e7eb;">{}</td>'
            '</tr>',
            ((l.matiere_premiere.nom, l.quantite, l.matiere_premiere.unite_mesure) for l in lignes),
        )
        tableau = format_html(
            '<table style="border-collapse:collapse; background:#fff;">'
            '<thead><tr style="background:#f3f4f6;">'
            '<th style="padding:4px 12px; text-align:left;">Matière première</th>'
            '<th style="padding:4px 12px; text-align:right;">Quantité</th>'
            '<th style="padding:4px 12px; text-align:left;">Unité</th>'
            '</tr></thead><tbody>{}</tbody></table>',
            corps,
        )
        return format_html('{}{}', entete, tableau)
    formule_composition.short_description = "Liste des formules (composition)"

    @admin.action(description="Générer les éprouvettes (7j et 28j)")
    def action_generer_7_28(self, request, queryset):
        total = 0
        for prelevement in queryset:
            total += len(prelevement.generer_eprouvettes(ages=[7, 28]))
        self.message_user(request, f"{total} éprouvette(s) générée(s) (échéances 7j et 28j).")

    @admin.action(description="Générer les éprouvettes (3j, 7j, 14j, 28j, 60j)")
    def action_generer_7_28_60(self, request, queryset):
        total = 0
        for prelevement in queryset:
            total += len(prelevement.generer_eprouvettes(ages=[3, 7, 14, 28, 60]))
        self.message_user(request, f"{total} éprouvette(s) générée(s) (échéances 3/7/14/28/60 j).")


@admin.register(Eprouvette)
class EprouvetteAdmin(admin.ModelAdmin):
    list_display = ('code', 'prelevement', 'forme', 'age_jours', 'date_fabrication',
                    'date_echeance', 'statut_badge', 'resistance_col')
    list_filter = (StatutEprouvetteFilter, 'forme', 'age_jours')
    search_fields = ('code', 'prelevement__numero_bl', 'prelevement__ordre_production__commande__client__nom')
    date_hierarchy = 'date_echeance'
    autocomplete_fields = ('prelevement',)
    readonly_fields = ('date_echeance', 'statut_badge')
    inlines = [EssaiEcrasementInline]

    def statut_badge(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            obj.statut_couleur, obj.statut_label,
        )
    statut_badge.short_description = "Statut"

    def resistance_col(self, obj):
        ecrasement = getattr(obj, 'ecrasement', None)
        if not ecrasement or ecrasement.resistance_mpa is None:
            return '—'
        couleur = '#065f46' if ecrasement.conforme else '#991b1b'
        return format_html('<span style="color: {}; font-weight: bold;">{} MPa</span>', couleur, ecrasement.resistance_mpa)
    resistance_col.short_description = "Résistance"


@admin.register(EssaiEcrasement)
class EssaiEcrasementAdmin(admin.ModelAdmin):
    list_display = ('eprouvette', 'date_essai', 'poids_kg', 'force_rupture_kn',
                    'surface_mm2', 'resistance_mpa', 'masse_volumique_kg_m3', 'type_rupture', 'conforme')
    list_filter = ('type_rupture', 'conforme', 'date_essai')
    search_fields = ('eprouvette__code', 'eprouvette__prelevement__numero_bl')
    date_hierarchy = 'date_essai'
    autocomplete_fields = ('eprouvette',)
    readonly_fields = ('surface_mm2', 'resistance_mpa', 'masse_volumique_kg_m3', 'conforme')

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        eprouvette = request.GET.get('eprouvette')
        if eprouvette:
            initial['eprouvette'] = eprouvette
        return initial


class TamisGranulometrieInline(admin.TabularInline):
    model = TamisGranulometrie
    extra = 4
    fields = ('diametre_mm', 'masse_refus_g', 'refus_cumule_g', 'pourcentage_refus', 'pourcentage_tamisat')
    readonly_fields = ('refus_cumule_g', 'pourcentage_refus', 'pourcentage_tamisat')


@admin.register(EssaiGranulometrie)
class EssaiGranulometrieAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_essai', 'materiau', 'designation', 'masse_echantillon_g', 'module_finesse')
    list_filter = ('materiau', 'date_essai')
    search_fields = ('reference', 'designation')
    date_hierarchy = 'date_essai'
    readonly_fields = ('module_finesse',)
    autocomplete_fields = ('matiere_premiere',)
    inlines = [TamisGranulometrieInline]
    actions = ['action_recalculer']
    change_form_template = 'admin/laboratory/essaigranulometrie/change_form.html'

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if obj and obj.pk:
            lignes = list(obj.lignes.order_by('-diametre_mm'))
            context['courbe_granulometrie'] = {
                'tamis': [float(ligne.diametre_mm) for ligne in lignes],
                'tamisat': [float(ligne.pourcentage_tamisat or 0) for ligne in lignes],
            }
        return super().render_change_form(request, context, add, change, form_url, obj)

    @admin.action(description="Recalculer refus cumulés et module de finesse")
    def action_recalculer(self, request, queryset):
        for essai in queryset:
            essai.recalculer()
        self.message_user(request, f"{queryset.count()} essai(s) recalculé(s).")


@admin.register(EssaiEquivalentSable)
class EssaiEquivalentSableAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_essai', 'materiau', 'type_matiere', 'fournisseur', 'hauteur_sable_mm', 'hauteur_floculat_mm', 'valeur_es')
    list_filter = ('materiau', 'type_matiere', 'fournisseur', 'date_essai')
    search_fields = ('reference',)
    date_hierarchy = 'date_essai'
    readonly_fields = ('valeur_es',)
    autocomplete_fields = ('matiere_premiere', 'fournisseur')


@admin.register(EssaiBleuMethylene)
class EssaiBleuMethyleneAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_essai', 'materiau', 'type_matiere', 'fournisseur', 'masse_echantillon_g', 'volume_solution_ml', 'valeur_bleu')
    list_filter = ('materiau', 'type_matiere', 'fournisseur', 'date_essai')
    search_fields = ('reference',)
    date_hierarchy = 'date_essai'
    readonly_fields = ('valeur_bleu',)
    autocomplete_fields = ('matiere_premiere', 'fournisseur')


@admin.register(EssaiTeneurEnEau)
class EssaiTeneurEnEauAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_essai', 'materiau', 'masse_humide_g', 'masse_seche_g', 'teneur_eau_pourcent')
    list_filter = ('materiau', 'date_essai')
    search_fields = ('reference',)
    date_hierarchy = 'date_essai'
    readonly_fields = ('teneur_eau_pourcent',)
    autocomplete_fields = ('matiere_premiere',)
