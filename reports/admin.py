from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from decimal import Decimal
from .models import Rapport, ConfigurationSeuilsStock, RapportCoutFormule, DetailCoutFormule

@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation', 'view_dashboard_link')
    search_fields = ('nom',)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='reports_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        from django.shortcuts import redirect
        return redirect('reports:dashboard')

    def view_dashboard_link(self, obj):
        url = reverse('reports:dashboard')
        return format_html('<a href="{url}" style="color: #007cba; font-weight: bold;">📊 Dashboard Rapports</a>', url=url)
    view_dashboard_link.short_description = "Dashboard"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['reports_links'] = {
            'dashboard': reverse('reports:dashboard'),
            'production': reverse('reports:production'),
            'commandes': reverse('reports:commandes'),
            'commercial': reverse('reports:commercial'),
            'stock': reverse('reports:stock'),
            'consommation_matieres': reverse('reports:consommation_matieres'),
            'financier': reverse('reports:financier'),
            'ratios_m3': reverse('reports:ratios_m3'),
            'clients_journalier': reverse('reports:clients_journalier'),
            'vehicules_journalier': reverse('reports:vehicules_journalier'),
            'cout_formule': reverse('reports:cout_formule'),
            'rapport_camion': reverse('reports:rapport_camion'),
        }
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ConfigurationSeuilsStock)
class ConfigurationSeuilsStockAdmin(admin.ModelAdmin):
    """Interface d'administration pour la configuration des seuils de stock"""
    
    list_display = ('__str__', 'date_modification', 'modifie_par')
    fields = ('seuil_critique', 'seuil_bas', 'modifie_par')
    readonly_fields = ('date_modification',)
    
    def has_add_permission(self, request):
        # Empêcher la création de multiples configurations
        return not ConfigurationSeuilsStock.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression de la configuration
        return False
    
    def save_model(self, request, obj, form, change):
        # Enregistrer l'utilisateur qui modifie
        if request.user.is_authenticated:
            obj.modifie_par = request.user.username
        super().save_model(request, obj, form, change)
    
    def changelist_view(self, request, extra_context=None):
        # S'assurer qu'une configuration existe
        ConfigurationSeuilsStock.get_seuils()
        return super().changelist_view(request, extra_context=extra_context)
    
    class Meta:
        verbose_name = "Configuration des seuils de stock"
        verbose_name_plural = "Configuration des seuils de stock"


class DetailCoutFormuleInline(admin.TabularInline):
    """Inline pour afficher les détails du coût par matière première"""
    model = DetailCoutFormule
    extra = 0
    readonly_fields = ('matiere_premiere', 'quantite', 'prix_unitaire_moyen', 'cout_total', 'nombre_saisies', 'pourcentage_display')
    fields = ('matiere_premiere', 'quantite', 'prix_unitaire_moyen', 'cout_total', 'nombre_saisies', 'pourcentage_display')
    
    def pourcentage_display(self, obj):
        if obj.rapport.cout_total and obj.rapport.cout_total > 0:
            pourcentage = (obj.cout_total / obj.rapport.cout_total * 100)
            return format_html('<span style="color: #28a745; font-weight: bold;">{:.1f}%</span>', pourcentage)
        return "-"
    pourcentage_display.short_description = "Pourcentage"


@admin.register(RapportCoutFormule)
class RapportCoutFormuleAdmin(admin.ModelAdmin):
    """Interface d'administration pour le rapport de coût de formule"""
    
    list_display = ('formule', 'date_debut', 'date_fin', 'cout_total_display', 'date_creation', 'generer_details_action')
    list_filter = ('date_creation', 'formule', 'date_debut', 'date_fin')
    search_fields = ('formule__nom',)
    readonly_fields = ('cout_total', 'date_creation', 'details_cout_display')
    fieldsets = (
        ('Informations générales', {
            'fields': ('formule', 'date_debut', 'date_fin')
        }),
        ('Résultats', {
            'fields': ('cout_total', 'details_cout_display')
        }),
        ('Informations système', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [DetailCoutFormuleInline]
    
    def cout_total_display(self, obj):
        if obj.cout_total:
            return format_html('<span style="font-weight: bold; color: #28a745; font-size: 1.1em;">{:.2f} MAD</span>', obj.cout_total)
        return format_html('<span style="color: #dc3545;">Non calculé</span>')
    cout_total_display.short_description = "Coût total"
    
    def details_cout_display(self, obj):
        if not obj.cout_total:
            return format_html('<span style="color: #dc3545;">Cliquez sur "Calculer le coût" pour générer les détails</span>')
        
        details = obj.get_details_cout()
        if not details:
            return format_html('<span style="color: #ffc107;">Aucune donnée de prix disponible pour cette période</span>')
        
        html = '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
        html += '<thead><tr style="background-color: #f8f9fa;">'
        html += '<th style="border: 1px solid #dee2e6; padding: 8px;">Matière première</th>'
        html += '<th style="border: 1px solid #dee2e6; padding: 8px;">Quantité</th>'
        html += '<th style="border: 1px solid #dee2e6; padding: 8px;">Prix unitaire moyen</th>'
        html += '<th style="border: 1px solid #dee2e6; padding: 8px;">Coût total</th>'
        html += '<th style="border: 1px solid #dee2e6; padding: 8px;">Pourcentage</th>'
        html += '</tr></thead><tbody>'
        
        for detail in details:
            html += '<tr>'
            html += f'<td style="border: 1px solid #dee2e6; padding: 8px;">{detail["matiere_premiere"].nom}</td>'
            html += f'<td style="border: 1px solid #dee2e6; padding: 8px;">{detail["quantite"]:.3f}</td>'
            html += f'<td style="border: 1px solid #dee2e6; padding: 8px;">{detail["prix_unitaire"]:.2f} MAD</td>'
            html += f'<td style="border: 1px solid #dee2e6; padding: 8px; font-weight: bold;">{detail["cout_total"]:.2f} MAD</td>'
            html += f'<td style="border: 1px solid #dee2e6; padding: 8px;">{detail["pourcentage"]:.1f}%</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return mark_safe(html)
    details_cout_display.short_description = "Détails du coût"
    
    def generer_details_action(self, obj):
        return format_html(
            '<a class="button" href="{}" style="background-color: #007cba; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Calculer le coût</a>',
            f'/admin/reports/rapportcoutformule/{obj.id}/calculer/'
        )
    generer_details_action.short_description = "Actions"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/calculer/', self.admin_site.admin_view(self.calculer_cout_view), name='rapportcoutformule_calculer'),
        ]
        return custom_urls + urls
    
    def calculer_cout_view(self, request, object_id):
        """Vue pour calculer le coût de la formule"""
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        
        rapport = get_object_or_404(RapportCoutFormule, pk=object_id)
        
        try:
            # Calculer le coût total
            cout_total = rapport.calculer_cout_total()
            
            # Créer ou mettre à jour les détails
            compositions = CompositionFormule.objects.filter(formule=rapport.formule)
            
            for composition in compositions:
                prix_unitaire = rapport.calculer_cout_matiere_premiere(composition.matiere_premiere)
                
                # Compter le nombre de saisies utilisées
                nombre_saisies = SaisieEntreeLie.objects.filter(
                    matiere_premiere=composition.matiere_premiere,
                    date_facture__range=[rapport.date_debut, rapport.date_fin],
                    prix_achat_ht__isnull=False,
                    quantite__isnull=False,
                    quantite__gt=0
                ).count()
                
                DetailCoutFormule.objects.update_or_create(
                    rapport=rapport,
                    matiere_premiere=composition.matiere_premiere,
                    defaults={
                        'quantite': composition.quantite,
                        'prix_unitaire_moyen': prix_unitaire,
                        'cout_total': prix_unitaire * composition.quantite,
                        'nombre_saisies': nombre_saisies
                    }
                )
            
            if cout_total > 0:
                messages.success(request, f'Coût calculé avec succès: {cout_total:.2f} MAD')
            else:
                messages.warning(request, 'Aucune donnée de prix disponible pour cette période')
                
        except Exception as e:
            messages.error(request, f'Erreur lors du calcul: {str(e)}')
        
        return redirect('admin:reports_rapportcoutformule_change', object_id)
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder le modèle et calculer automatiquement le coût si c'est une nouvelle instance"""
        super().save_model(request, obj, form, change)
        
        # Si c'est une nouvelle instance, calculer le coût automatiquement
        if not change:
            obj.calculer_cout_total()
