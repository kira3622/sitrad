from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from customers.models import Client
from orders.models import Commande
from production.models import OrdreProduction
from logistics.models import Livraison


def admin_dashboard_stats(request):
    """
    Context processor pour fournir les statistiques du tableau de bord admin
    """
    if not (request.user.is_authenticated and request.user.is_staff):
        return {}
    
    # Calculer les statistiques seulement pour les pages admin
    if not request.path.startswith('/admin/'):
        return {}
    
    try:
        # Date de début du mois actuel
        debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total des clients
        total_clients = Client.objects.count()
        
        # Total des commandes ce mois
        total_commandes = Commande.objects.filter(
            date_commande__gte=debut_mois
        ).count()
        
        # Productions en cours
        productions_en_cours = OrdreProduction.objects.filter(
            statut='en_cours'
        ).count()
        
        # Livraisons prévues (commandes confirmées non livrées)
        livraisons_prevues = Commande.objects.filter(
            statut__in=['confirmee', 'en_production']
        ).count()
        
        return {
            'total_clients': total_clients,
            'total_commandes': total_commandes,
            'productions_en_cours': productions_en_cours,
            'livraisons_prevues': livraisons_prevues,
        }
    
    except Exception as e:
        # En cas d'erreur, retourner des valeurs par défaut
        return {
            'total_clients': 0,
            'total_commandes': 0,
            'productions_en_cours': 0,
            'livraisons_prevues': 0,
        }