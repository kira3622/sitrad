from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Rapport

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
            'financier': reverse('reports:financier'),
        }
        return super().changelist_view(request, extra_context=extra_context)
