"""Contrôle d'accès aux rapports, par utilisateur.

Règle appliquée :
- un superutilisateur accède à tous les rapports actifs ;
- un utilisateur sans profil d'accès configuré accède à tous les rapports
  (son accès reste donc inchangé tant qu'aucune restriction n'est choisie) ;
- dès qu'un profil existe, seuls les rapports cochés sont accessibles,
  sauf si « Accès à tous les rapports » est coché.
"""
from functools import wraps

from django.core.exceptions import PermissionDenied

from .models import AccesRapport


def codes_rapports_autorises(user):
    """Renvoie l'ensemble des codes de rapports accessibles par ``user``."""
    if not getattr(user, 'is_authenticated', False):
        return set()

    tous_les_codes = set(AccesRapport.objects.filter(actif=True).values_list('code', flat=True))

    if user.is_superuser:
        return tous_les_codes

    profil = getattr(user, 'profil_rapports', None)
    if profil is None or profil.acces_total:
        return tous_les_codes

    return set(profil.rapports.values_list('code', flat=True))


def a_acces_rapport(user, code):
    """Indique si ``user`` peut consulter le rapport identifié par ``code``."""
    return code in codes_rapports_autorises(user)


def rapport_requis(code):
    """Décorateur de vue : refuse l'accès au rapport ``code`` si non autorisé."""
    def decorateur(vue):
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            if not a_acces_rapport(request.user, code):
                raise PermissionDenied("Vous n'avez pas accès à ce rapport.")
            return vue(request, *args, **kwargs)
        return enveloppe
    return decorateur
