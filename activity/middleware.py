import json
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import ActivityLog


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ActivityLogMiddleware:
    """
    Middleware pour enregistrer les activités des utilisateurs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Traitement avant la vue
        response = self.get_response(request)
        
        # Traitement après la vue
        if hasattr(request, 'user') and request.user.is_authenticated:
            self.log_view_activity(request)
            
        return response
    
    def log_view_activity(self, request):
        """Enregistre les activités de consultation"""
        # Ne pas enregistrer les requêtes AJAX, les fichiers statiques, etc.
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if (is_ajax or 
            request.path.startswith('/static/') or 
            request.path.startswith('/media/') or
            request.path.startswith('/admin/jsi18n/') or
            request.path.endswith('.js') or
            request.path.endswith('.css') or
            request.path.endswith('.ico')):
            return
            
        # Ne pas enregistrer les consultations trop fréquentes du même utilisateur
        last_activity = ActivityLog.objects.filter(
            user=request.user,
            action='view'
        ).first()
        
        if (last_activity and 
            (timezone.now() - last_activity.timestamp).seconds < 30):
            return
            
        # Enregistrer l'activité de consultation
        try:
            ActivityLog.objects.create(
                user=request.user,
                action='view',
                description=f"Consultation de {request.path}",
                details={
                    'path': request.path,
                    'method': request.method,
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
                },
                ip_address=get_client_ip(request)
            )
        except Exception:
            # En cas d'erreur, ne pas interrompre le processus
            pass


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Enregistre les connexions d'utilisateurs"""
    try:
        ActivityLog.objects.create(
            user=user,
            action='login',
            description=f"Connexion de {user.username}",
            details={
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
            },
            ip_address=get_client_ip(request)
        )
    except Exception:
        pass


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Enregistre les déconnexions d'utilisateurs"""
    if user:
        try:
            ActivityLog.objects.create(
                user=user,
                action='logout',
                description=f"Déconnexion de {user.username}",
                details={
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
                },
                ip_address=get_client_ip(request)
            )
        except Exception:
            pass


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Enregistre les créations et modifications d'objets"""
    # Éviter les boucles infinies avec ActivityLog
    if sender == ActivityLog:
        return
        
    # Éviter d'enregistrer certains modèles système
    excluded_models = [
        'Session', 'LogEntry', 'Permission', 'Group', 
        'ContentType', 'Migration'
    ]
    
    if sender.__name__ in excluded_models:
        return
        
    # Récupérer l'utilisateur actuel depuis le thread local
    user = getattr(instance, '_current_user', None)
    if not user or not user.is_authenticated:
        return
        
    try:
        content_type = ContentType.objects.get_for_model(sender)
        action = 'create' if created else 'update'
        action_text = 'Création' if created else 'Modification'
        
        ActivityLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.pk,
            description=f"{action_text} de {sender._meta.verbose_name}: {str(instance)}",
            details={
                'model': sender.__name__,
                'app': sender._meta.app_label,
                'created': created
            }
        )
    except Exception:
        pass


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Enregistre les suppressions d'objets"""
    # Éviter les boucles infinies avec ActivityLog
    if sender == ActivityLog:
        return
        
    # Éviter d'enregistrer certains modèles système
    excluded_models = [
        'Session', 'LogEntry', 'Permission', 'Group', 
        'ContentType', 'Migration'
    ]
    
    if sender.__name__ in excluded_models:
        return
        
    # Récupérer l'utilisateur actuel depuis le thread local
    user = getattr(instance, '_current_user', None)
    if not user or not user.is_authenticated:
        return
        
    try:
        content_type = ContentType.objects.get_for_model(sender)
        
        ActivityLog.objects.create(
            user=user,
            action='delete',
            content_type=content_type,
            object_id=instance.pk,
            description=f"Suppression de {sender._meta.verbose_name}: {str(instance)}",
            details={
                'model': sender.__name__,
                'app': sender._meta.app_label,
                'deleted_object': str(instance)
            }
        )
    except Exception:
        pass