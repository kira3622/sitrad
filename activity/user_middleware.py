import threading
from django.contrib.auth.models import AnonymousUser

# Thread local storage pour stocker l'utilisateur actuel
_thread_locals = threading.local()


def get_current_user():
    """Récupère l'utilisateur actuel depuis le thread local"""
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """Définit l'utilisateur actuel dans le thread local"""
    _thread_locals.user = user


class CurrentUserMiddleware:
    """
    Middleware pour stocker l'utilisateur actuel dans le thread local
    afin de pouvoir l'utiliser dans les signaux Django
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Stocker l'utilisateur actuel
        user = getattr(request, 'user', AnonymousUser())
        set_current_user(user)
        
        response = self.get_response(request)
        
        # Nettoyer après la requête
        set_current_user(None)
        
        return response


# Mixin pour les modèles qui veulent enregistrer l'utilisateur actuel
class UserTrackingMixin:
    """
    Mixin pour les modèles qui veulent automatiquement
    enregistrer leurs modifications dans ActivityLog
    """
    
    def save(self, *args, **kwargs):
        # Injecter l'utilisateur actuel dans l'instance
        current_user = get_current_user()
        if current_user and current_user.is_authenticated:
            self._current_user = current_user
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Injecter l'utilisateur actuel dans l'instance
        current_user = get_current_user()
        if current_user and current_user.is_authenticated:
            self._current_user = current_user
        super().delete(*args, **kwargs)