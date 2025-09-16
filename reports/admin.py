from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Rapport

@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation', 'view_reports_link')
    search_fields = ('nom',)

    def view_reports_link(self, obj):
        url = reverse('report_list')
        return format_html('<a href="{url}">Voir les rapports</a>', url=url)
    view_reports_link.short_description = "Rapports"
