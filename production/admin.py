from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html
from .models import OrdreProduction, LotProduction
from orders.models import Commande

class LotProductionInline(admin.TabularInline):
    model = LotProduction
    extra = 0

class OrdreProductionAdmin(admin.ModelAdmin):
    list_display = (
        'numero_bon', 'id', 'commande', 'formule', 'quantite_produire', 'prix_vente_unitaire', 'prix_deplacement_pompe', 'prix_deplacement_camion', 'date_production', 'heure_production',
        'chauffeur', 'vehicule', 'classe_exposition', 'classe_consistance', 'classe_teneur_chlorure', 'd_max',
        'ciment_type_classe', 'adjuvant_type', 'rapport_e_c', 'teneur_en_air', 'temperature_beton', 'teneur_en_ciment',
        'masse_volumique', 'transporteur', 'pompe_display', 'statut', 'matieres_sorties_calculees', 'actions_sorties'
    )
    list_filter = (
        'statut', 'date_production', 'matieres_sorties_calculees', 'chauffeur', 'vehicule',
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
