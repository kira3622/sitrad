"""Contrôle d'accès aux rapports, par utilisateur.

Deux mécanismes complémentaires accordent l'accès :
- les permissions Django natives (case cochée dans « Available user permissions »,
  ex. ``reports.voir_rapport_consommation_matieres``) ;
- le profil « Accès aux rapports » (inline sur la fiche utilisateur).

Règle appliquée :
- un superutilisateur accède à tous les rapports actifs ;
- un utilisateur sans profil d'accès configuré accède à tous les rapports
  (son accès reste donc inchangé tant qu'aucune restriction n'est choisie) ;
- dès qu'un profil existe, seuls les rapports cochés sont accessibles,
  sauf si « Accès à tous les rapports » est coché ;
- dans tous les cas, une permission Django native cochée accorde l'accès au
  rapport correspondant.
"""
from functools import wraps

from django.core.exceptions import PermissionDenied

from .models import AccesRapport

# Préfixe des permissions natives : reports.voir_rapport_<code>
PREFIXE_PERMISSION = 'reports.voir_rapport_'


def codes_rapports_autorises(user):
    """Renvoie l'ensemble des codes de rapports accessibles par ``user``."""
    if not getattr(user, 'is_authenticated', False):
        return set()

    tous_les_codes = set(AccesRapport.objects.filter(actif=True).values_list('code', flat=True))

    if user.is_superuser:
        return tous_les_codes

    # Permissions Django natives explicitement cochées pour cet utilisateur.
    codes_permissions = {
        perm[len(PREFIXE_PERMISSION):]
        for perm in user.get_all_permissions()
        if perm.startswith(PREFIXE_PERMISSION)
    }

    profil = getattr(user, 'profil_rapports', None)

    # Aucun mécanisme configuré : accès complet (compatibilité ascendante).
    if profil is None and not codes_permissions:
        return tous_les_codes

    if profil is not None and profil.acces_total:
        return tous_les_codes | codes_permissions

    codes_profil = set(profil.rapports.values_list('code', flat=True)) if profil is not None else set()
    return codes_profil | codes_permissions


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


# ---------------------------------------------------------------------------
# Consultation des prix de vente unitaires (accès strict, sans droit par défaut)
# ---------------------------------------------------------------------------

CODE_PRIX_VENTE = 'prix_vente_unitaire'
PERMISSION_PRIX_VENTE = PREFIXE_PERMISSION + CODE_PRIX_VENTE


def peut_voir_prix_vente(user):
    """Autorisation stricte (opt-in) pour consulter les prix de vente unitaires.

    Contrairement aux autres rapports, aucun accès n'est accordé par défaut :
    il faut être superutilisateur, détenir la permission native
    ``reports.voir_rapport_prix_vente_unitaire``, ou avoir le rapport
    « prix_vente_unitaire » coché dans son profil d'accès aux rapports.
    """
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    if PERMISSION_PRIX_VENTE in user.get_all_permissions():
        return True
    profil = getattr(user, 'profil_rapports', None)
    if profil is None:
        return False
    if profil.acces_total:
        return True
    return profil.rapports.filter(code=CODE_PRIX_VENTE).exists()


def prix_vente_requis(vue):
    """Décorateur de vue : réserve l'accès aux prix de vente unitaires."""
    @wraps(vue)
    def enveloppe(request, *args, **kwargs):
        if not peut_voir_prix_vente(request.user):
            raise PermissionDenied(
                "Vous n'êtes pas autorisé à consulter les prix de vente unitaires."
            )
        return vue(request, *args, **kwargs)
    return enveloppe
