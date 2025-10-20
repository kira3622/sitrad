from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from .models import Commande, LigneCommande
from customers.models import Chantier

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 1

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'chantier', 'date_commande', 'date_livraison_souhaitee', 'heure_livraison_souhaitee', 'statut')
    list_filter = ('statut', 'date_commande', 'client')
    search_fields = ('client__nom', 'chantier__nom')
    inlines = [LigneCommandeInline]
    
    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['filter_chantiers_js'] = True
        return super().change_view(request, object_id, form_url, extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['filter_chantiers_js'] = True
        return super().add_view(request, form_url, extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ajax/filter-chantiers/', self.admin_site.admin_view(self.filter_chantiers), name='filter_chantiers'),
        ]
        return custom_urls + urls
    
    def filter_chantiers(self, request):
        """Vue AJAX pour filtrer les chantiers par client"""
        client_id = request.GET.get('client_id')
        if client_id:
            chantiers = Chantier.objects.filter(client_id=client_id).values('id', 'nom')
            return JsonResponse({'chantiers': list(chantiers)})
        return JsonResponse({'chantiers': []})
