from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Rapport, ConfigurationSeuilsStock

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
