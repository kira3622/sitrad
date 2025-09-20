from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp_display', 
        'user_display', 
        'action_display', 
        'model_display', 
        'object_display',
        'ip_address'
    )
    list_filter = (
        'action', 
        'timestamp', 
        'content_type',
        'user'
    )
    search_fields = (
        'user__username', 
        'user__first_name', 
        'user__last_name',
        'description'
    )
    readonly_fields = (
        'user', 
        'action', 
        'timestamp', 
        'content_type', 
        'object_id',
        'description', 
        'details', 
        'ip_address'
    )
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """Empêche l'ajout manuel d'entrées"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêche la modification des entrées"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permet seulement la suppression pour nettoyer les anciens logs"""
        return request.user.is_superuser
    
    def timestamp_display(self, obj):
        """Affiche la date et heure formatée"""
        return obj.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp_display.short_description = "Date et heure"
    timestamp_display.admin_order_field = 'timestamp'
    
    def user_display(self, obj):
        """Affiche l'utilisateur avec un lien vers son profil"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            full_name = obj.user.get_full_name() or obj.user.username
            return format_html('<a href="{}">{}</a>', url, full_name)
        return "Utilisateur supprimé"
    user_display.short_description = "Utilisateur"
    user_display.admin_order_field = 'user__username'
    
    def action_display(self, obj):
        """Affiche l'action avec une couleur"""
        colors = {
            'create': 'green',
            'update': 'orange', 
            'delete': 'red',
            'view': 'blue',
            'login': 'purple',
            'logout': 'gray'
        }
        color = colors.get(obj.action, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', 
            color, 
            obj.get_action_display()
        )
    action_display.short_description = "Action"
    action_display.admin_order_field = 'action'
    
    def model_display(self, obj):
        """Affiche le modèle concerné"""
        if obj.content_type:
            return obj.content_type.model_class()._meta.verbose_name.title()
        return "N/A"
    model_display.short_description = "Modèle"
    model_display.admin_order_field = 'content_type'
    
    def object_display(self, obj):
        """Affiche l'objet concerné avec un lien si possible"""
        if obj.content_object:
            try:
                # Essaie de créer un lien vers l'objet dans l'admin
                model_name = obj.content_type.model
                app_label = obj.content_type.app_label
                url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.object_id])
                return format_html('<a href="{}">{}</a>', url, str(obj.content_object)[:50])
            except:
                return str(obj.content_object)[:50]
        return "N/A"
    object_display.short_description = "Objet"
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related(
            'user', 'content_type'
        ).prefetch_related('content_object')
