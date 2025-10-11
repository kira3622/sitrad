from django.shortcuts import render
from django.apps import apps
from django.db.models import Sum, Count
from django.utils import timezone


def commercial_dashboard(request):
    """Tableau de bord commercial: clients, commandes, factures, KPIs."""
    # Récupération sûre des modèles (évite les import errors si module déplacé)
    Client = apps.get_model('customers', 'Client')
    Commande = apps.get_model('orders', 'Commande') if apps.is_installed('orders') else None
    Facture = apps.get_model('billing', 'Facture') if apps.is_installed('billing') else None

    # KPIs de base
    clients_count = Client.objects.count() if Client else 0
    commandes_count = Commande.objects.count() if Commande else 0
    factures_count = Facture.objects.count() if Facture else 0

    montant_total_factures = 0
    if Facture:
        try:
            montant_total_factures = Facture.objects.aggregate(total=Sum('montant_total'))['total'] or 0
        except Exception:
            montant_total_factures = 0

    # Top clients par nombre de commandes
    top_clients_commandes = []
    if Client and Commande and hasattr(Commande, 'client'):
        try:
            top_clients_commandes = (
                Client.objects
                .annotate(nb_commandes=Count('commande'))
                .order_by('-nb_commandes')[:10]
            )
        except Exception:
            top_clients_commandes = []

    # Top clients par montant facturé
    top_clients_factures = []
    if Client and Facture and hasattr(Facture, 'client'):
        try:
            top_clients_factures = (
                Client.objects
                .annotate(total_factures=Sum('facture__montant_total'))
                .order_by('-total_factures')[:10]
            )
        except Exception:
            top_clients_factures = []

    context = {
        'now': timezone.now(),
        'clients_count': clients_count,
        'commandes_count': commandes_count,
        'factures_count': factures_count,
        'montant_total_factures': montant_total_factures,
        'top_clients_commandes': top_clients_commandes,
        'top_clients_factures': top_clients_factures,
    }

    return render(request, 'customers/commercial_dashboard.html', context)

# Create your views here.
