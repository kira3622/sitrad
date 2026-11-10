from datetime import timedelta

from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.html import format_html
from .models import OrdreProduction, LotProduction
from orders.models import Commande
from reports.acces import peut_voir_prix_vente


class PlageDatesFilter(admin.SimpleListFilter):
    """Filtre de période de production : l'utilisateur choisit la durée à consulter."""
    title = "Période de production"
    parameter_name = 'plage'

    def lookups(self, request, model_admin):
        return (
            ('aujourdhui', "Aujourd'hui"),
            ('7j', "7 derniers jours"),
            ('30j', "30 derniers jours"),
            ('mois', "Ce mois"),
            ('mois_precedent', "Mois précédent"),
            ('annee', "Cette année"),
        )

    def queryset(self, request, queryset):
        valeur = self.value()
        if not valeur:
            return queryset
        aujourdhui = timezone.localdate()
        if valeur == 'aujourdhui':
            return queryset.filter(date_production=aujourdhui)
        if valeur == '7j':
            return queryset.filter(date_production__gte=aujourdhui - timedelta(days=7))
        if valeur == '30j':
            return queryset.filter(date_production__gte=aujourdhui - timedelta(days=30))
        if valeur == 'mois':
            return queryset.filter(date_production__year=aujourdhui.year,
                                   date_production__month=aujourdhui.month)
        if valeur == 'mois_precedent':
            premier_du_mois = aujourdhui.replace(day=1)
            fin = premier_du_mois - timedelta(days=1)
            debut = fin.replace(day=1)
            return queryset.filter(date_production__range=[debut, fin])
        if valeur == 'annee':
            return queryset.filter(date_production__year=aujourdhui.year)
        return queryset


class LotProductionInline(admin.TabularInline):
    model = LotProduction
    extra = 0

class OrdreProductionAdmin(admin.ModelAdmin):
    change_list_template = 'admin/production/ordreproduction/change_list.html'

    list_display = (
        'numero_bon', 'id', 'commande', 'formule', 'quantite_produire', 'prix_vente_unitaire', 'prix_deplacement_pompe', 'prix_deplacement_camion', 'date_production', 'heure_production',
        'chauffeur', 'vehicule', 'classe_exposition', 'classe_consistance', 'classe_teneur_chlorure', 'd_max',
        'ciment_type_classe', 'adjuvant_type', 'rapport_e_c', 'teneur_en_air', 'temperature_beton', 'teneur_en_ciment',
        'masse_volumique', 'transporteur', 'pompe_display', 'statut', 'matieres_sorties_calculees', 'actions_sorties'
    )
    list_filter = (
        'statut', PlageDatesFilter, 'date_production', 'matieres_sorties_calculees', 'chauffeur', 'vehicule',
        'classe_exposition', 'classe_consistance', 'classe_teneur_chlorure', 'd_max',
        'ciment_type_classe', 'adjuvant_type', 'transporteur', 'pompe__statut', 'pompe__marque'
    )
    search_fields = ('numero_bon', 'commande__client__nom', 'formule__nom', 'chauffeur__nom', 'vehicule__immatriculation', 'pompe__nom', 'pompe__numero_serie')
    
    readonly_fields = ('delivery_note_link', 'actions_sorties')
    fields = (
        'numero_bon', 'commande', 'formule', 'quantite_produire', 'prix_vente_unitaire', 'prix_deplacement_pompe', 'prix_deplacement_camion', 'date_production', 'heure_production',
        'chauffeur', 'vehicule',
        'classe_exposition', 'classe_consistance', 'classe_teneur_chlorure', 'd_max',
        'ciment_type_classe', 'adjuvant_type', 'rapport_e_c', 'teneur_en_air', 'temperature_beton', 'teneur_en_ciment',
        'masse_volumique', 'transporteur', 'pompe', 'agent_commercial',
        'statut', 'matieres_sorties_calculees', 'actions_sorties', 'delivery_note_link'
    )
    
    inlines = [LotProductionInline]
    actions = ['calculer_sorties_batch_action']
    
    def get_queryset(self, request):
        """Optimiser les requêtes en incluant les relations"""
        return super().get_queryset(request).select_related(
            'commande', 'formule', 'chauffeur', 'vehicule', 'pompe', 'pompe__operateur'
        )

    def get_list_display(self, request):
        """Masquer la colonne « Prix de vente unitaire » aux utilisateurs non autorisés."""
        colonnes = list(super().get_list_display(request))
        if not peut_voir_prix_vente(request.user):
            colonnes = [colonne for colonne in colonnes if colonne != 'prix_vente_unitaire']
        return colonnes

    def get_fields(self, request, obj=None):
        """Masquer le champ « Prix de vente unitaire » du formulaire aux non autorisés."""
        champs = list(super().get_fields(request, obj))
        if not peut_voir_prix_vente(request.user):
            champs = [champ for champ in champs if champ != 'prix_vente_unitaire']
        return champs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['peut_voir_prix'] = peut_voir_prix_vente(request.user)
        return super().changelist_view(request, extra_context=extra_context)

    def pompe_display(self, obj):
        """Affiche les informations de la pompe de manière formatée"""
        if obj.pompe:
            statut_color = {
                'disponible': 'green',
                'en_service': 'blue', 
                'maintenance': 'orange',
                'hors_service': 'red'
            }.get(obj.pompe.statut, 'gray')
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span><br>'
                '<small>{} {} - Débit: {}m³/h</small>',
                statut_color,
                obj.pompe.nom,
                obj.pompe.marque,
                obj.pompe.modele,
                obj.pompe.debit_max
            )
        return "Aucune"
    pompe_display.short_description = "Pompe"
    pompe_display.admin_order_field = 'pompe__nom'
    
    def actions_sorties(self, obj):
        """Affiche les boutons d'action pour calculer les sorties de matières"""
        preview_url = reverse('production:preview_sorties_ordre', args=[obj.id])
        calculer_url = reverse('production:calculer_sorties_ordre', args=[obj.id])
        
        if obj.matieres_sorties_calculees:
            status_icon = "✅"
            status_text = "Calculées"
            button_class = "default"
            button_text = "Recalculer"
        else:
            status_icon = "⏳"
            status_text = "À calculer"
            button_class = "default"
            button_text = "Calculer"
        
        return format_html(
            '{} {} | <a href="{}" class="button {}">👁️ Prévisualiser</a> | '
            '<a href="#" onclick="calculerSorties({})" class="button {}">{} {}</a>',
            status_icon, status_text, preview_url, button_class, obj.id, button_class, status_icon, button_text
        )
    actions_sorties.short_description = "Actions Sorties Matières"
    
    def calculer_sorties_batch_action(self, request, queryset):
        """Action pour calculer les sorties de matières en lot"""
        ordre_ids = list(queryset.values_list('id', flat=True))
        
        # Rediriger vers la vue de traitement en lot
        url = reverse('production:calculer_sorties_batch')
        return HttpResponseRedirect(f"{url}?ordre_ids={','.join(map(str, ordre_ids))}")
    
    calculer_sorties_batch_action.short_description = "Calculer sorties matières (lot)"
    
    class Media:
        js = ('admin/js/production_admin.js',)
        css = {
            'all': ('admin/css/production_admin.css',)
        }
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        try:
            # Filtrer uniquement à l'ajout: exclure les commandes livrées
            if obj is None and 'commande' in form.base_fields:
                form.base_fields['commande'].queryset = Commande.objects.exclude(statut='livree')
        except Exception:
            # En cas d'erreur, ne pas bloquer le formulaire
            pass
        return form
    def actions_sorties(self, obj):
        """Affiche les boutons d'action pour calculer les sorties de matières.
        Sur la vue d'ajout (obj non défini), afficher un texte informatif.
        """
        if not obj or not getattr(obj, 'pk', None):
            return "Disponible après enregistrement"

        preview_url = reverse('production:preview_sorties_ordre', args=[obj.id])
        calculer_url = reverse('production:calculer_sorties_ordre', args=[obj.id])

        if obj.matieres_sorties_calculees:
            status_icon = "✅"
            status_text = "Calculées"
            button_class = "default"
            button_text = "Recalculer"
        else:
            status_icon = "⏳"
            status_text = "À calculer"
            button_class = "default"
            button_text = "Calculer"

        return format_html(
            '{} {} | <a href="{}" class="button {}">👁️ Prévisualiser</a> | '
            '<a href="#" onclick="calculerSorties({})" class="button {}">{} {}</a>',
            status_icon, status_text, preview_url, button_class, obj.id, button_class, status_icon, button_text
        )
    actions_sorties.short_description = "Actions Sorties Matières"
    
    def calculer_sorties_batch_action(self, request, queryset):
        """Action pour calculer les sorties de matières en lot"""
        ordre_ids = list(queryset.values_list('id', flat=True))
        
        # Rediriger vers la vue de traitement en lot
        url = reverse('production:calculer_sorties_batch')
        return HttpResponseRedirect(f"{url}?ordre_ids={','.join(map(str, ordre_ids))}")
    
    calculer_sorties_batch_action.short_description = "Calculer sorties matières (lot)"
    
    class Media:
        js = ('admin/js/production_admin.js',)
        css = {
            'all': ('admin/css/production_admin.css',)
        }
    def delivery_note_link(self, obj):
        if not obj.pk:
            return "Disponible après enregistrement"
        # Tentative de résolution du lien PDF avec namespace, puis sans, puis fallback chemin direct
        try:
            url = reverse('production:delivery_note_pdf', args=[obj.pk])
        except NoReverseMatch:
            try:
                url = reverse('delivery_note_pdf', args=[obj.pk])
            except NoReverseMatch:
                url = f"/production/orders/{obj.pk}/delivery-note.pdf"
        return format_html('<a class="button" href="{}" target="_blank">Télécharger Bon de Livraison (PDF)</a>', url)
    delivery_note_link.short_description = "Bon de Livraison"
admin.site.register(OrdreProduction, OrdreProductionAdmin)
