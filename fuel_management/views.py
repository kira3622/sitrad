from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    Fournisseur, TypeEngin, Engin, Approvisionnement, 
    Consommation, Stock, AlerteStock
)


@login_required
def dashboard_fuel(request):
    """Dashboard principal du module de gestion du gasoil"""
    
    # Récupérer ou créer le stock
    stock, created = Stock.objects.get_or_create(pk=1)
    
    # Statistiques générales
    total_approvisionnements = Approvisionnement.objects.count()
    total_consommations = Consommation.objects.count()
    total_engins = Engin.objects.filter(actif=True).count()
    
    # Approvisionnements récents (7 derniers jours)
    date_limite = timezone.now() - timedelta(days=7)
    approvisionnements_recents = Approvisionnement.objects.filter(
        date__gte=date_limite
    ).order_by('-date')[:5]
    
    # Consommations récentes (7 derniers jours)
    consommations_recentes = Consommation.objects.filter(
        date__gte=date_limite
    ).order_by('-date')[:5]
    
    # Alertes non lues
    alertes_non_lues = AlerteStock.objects.filter(lu=False).order_by('-date_creation')[:5]
    
    # Top 5 des engins les plus consommateurs (30 derniers jours)
    date_limite_mois = timezone.now() - timedelta(days=30)
    top_engins = Engin.objects.filter(
        consommation__date__gte=date_limite_mois
    ).annotate(
        total_consommation=Sum('consommation__quantite')
    ).order_by('-total_consommation')[:5]
    
    # Données pour le graphique (consommation par jour sur 30 jours)
    consommations_par_jour = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        total_jour = Consommation.objects.filter(
            date__date=date
        ).aggregate(total=Sum('quantite'))['total'] or 0
        consommations_par_jour.append({
            'date': date.strftime('%d/%m'),
            'total': float(total_jour)
        })
    consommations_par_jour.reverse()
    
    context = {
        'stock': stock,
        'total_approvisionnements': total_approvisionnements,
        'total_consommations': total_consommations,
        'total_engins': total_engins,
        'approvisionnements_recents': approvisionnements_recents,
        'consommations_recentes': consommations_recentes,
        'alertes_non_lues': alertes_non_lues,
        'top_engins': top_engins,
        'consommations_par_jour': json.dumps(consommations_par_jour),
    }
    
    return render(request, 'fuel_management/dashboard.html', context)


@login_required
def stock_detail(request):
    """Vue détaillée du stock avec historique"""
    
    stock, created = Stock.objects.get_or_create(pk=1)
    
    # Historique des mouvements (approvisionnements et consommations)
    approvisionnements = Approvisionnement.objects.all().order_by('-date')[:20]
    consommations = Consommation.objects.all().order_by('-date')[:20]
    
    # Alertes liées au stock
    alertes = AlerteStock.objects.all().order_by('-date_creation')[:10]
    
    context = {
        'stock': stock,
        'approvisionnements': approvisionnements,
        'consommations': consommations,
        'alertes': alertes,
    }
    
    return render(request, 'fuel_management/stock_detail.html', context)


@login_required
def rapport_consommation_engin(request):
    """Rapport de consommation par engin"""
    
    # Filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    engin_id = request.GET.get('engin')
    
    # Query de base
    consommations = Consommation.objects.all()
    
    # Application des filtres
    if date_debut:
        consommations = consommations.filter(date__gte=date_debut)
    if date_fin:
        consommations = consommations.filter(date__lte=date_fin)
    if engin_id:
        consommations = consommations.filter(engin_id=engin_id)
    
    # Groupement par engin
    rapport_engins = Engin.objects.filter(
        consommation__in=consommations
    ).annotate(
        total_consommation=Sum('consommation__quantite'),
        nombre_utilisations=Count('consommation')
    ).order_by('-total_consommation')
    
    # Liste des engins pour le filtre
    engins = Engin.objects.filter(actif=True).order_by('nom')
    
    context = {
        'rapport_engins': rapport_engins,
        'engins': engins,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'engin_id': engin_id,
    }
    
    return render(request, 'fuel_management/rapport_consommation.html', context)


@login_required
def rapport_approvisionnement(request):
    """Rapport d'historique des approvisionnements"""
    
    # Filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    fournisseur_id = request.GET.get('fournisseur')
    
    # Query de base
    approvisionnements = Approvisionnement.objects.all()
    
    # Application des filtres
    if date_debut:
        approvisionnements = approvisionnements.filter(date__gte=date_debut)
    if date_fin:
        approvisionnements = approvisionnements.filter(date__lte=date_fin)
    if fournisseur_id:
        approvisionnements = approvisionnements.filter(fournisseur_id=fournisseur_id)
    
    approvisionnements = approvisionnements.order_by('-date')
    
    # Pagination
    paginator = Paginator(approvisionnements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_quantite = approvisionnements.aggregate(total=Sum('quantite'))['total'] or 0
    total_montant = sum(app.montant_total for app in approvisionnements)
    
    # Liste des fournisseurs pour le filtre
    fournisseurs = Fournisseur.objects.filter(actif=True).order_by('nom')
    
    context = {
        'page_obj': page_obj,
        'fournisseurs': fournisseurs,
        'total_quantite': total_quantite,
        'total_montant': total_montant,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'fournisseur_id': fournisseur_id,
    }
    
    return render(request, 'fuel_management/rapport_approvisionnement.html', context)


@login_required
def rapport_bilan_mensuel(request):
    """Bilan mensuel des entrées, sorties et solde"""
    
    # Paramètres de date
    mois = request.GET.get('mois', timezone.now().month)
    annee = request.GET.get('annee', timezone.now().year)
    
    try:
        mois = int(mois)
        annee = int(annee)
    except (ValueError, TypeError):
        mois = timezone.now().month
        annee = timezone.now().year
    
    # Dates de début et fin du mois
    date_debut = datetime(annee, mois, 1).date()
    if mois == 12:
        date_fin = datetime(annee + 1, 1, 1).date() - timedelta(days=1)
    else:
        date_fin = datetime(annee, mois + 1, 1).date() - timedelta(days=1)
    
    # Calculs pour le mois
    approvisionnements_mois = Approvisionnement.objects.filter(
        date__range=[date_debut, date_fin]
    )
    consommations_mois = Consommation.objects.filter(
        date__range=[date_debut, date_fin]
    )
    
    # Totaux
    total_entrees = approvisionnements_mois.aggregate(total=Sum('quantite'))['total'] or 0
    total_sorties = consommations_mois.aggregate(total=Sum('quantite'))['total'] or 0
    solde_mois = total_entrees - total_sorties
    
    # Montant total des approvisionnements
    montant_total = sum(app.montant_total for app in approvisionnements_mois)
    
    # Détail par jour
    bilan_par_jour = []
    current_date = date_debut
    while current_date <= date_fin:
        entrees_jour = approvisionnements_mois.filter(
            date__date=current_date
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        sorties_jour = consommations_mois.filter(
            date__date=current_date
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        bilan_par_jour.append({
            'date': current_date,
            'entrees': entrees_jour,
            'sorties': sorties_jour,
            'solde': entrees_jour - sorties_jour
        })
        
        current_date += timedelta(days=1)
    
    # Stock actuel
    stock = Stock.objects.first()
    
    context = {
        'mois': mois,
        'annee': annee,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'total_entrees': total_entrees,
        'total_sorties': total_sorties,
        'solde_mois': solde_mois,
        'montant_total': montant_total,
        'bilan_par_jour': bilan_par_jour,
        'stock': stock,
        'approvisionnements_mois': approvisionnements_mois,
        'consommations_mois': consommations_mois,
    }
    
    return render(request, 'fuel_management/rapport_bilan_mensuel.html', context)


@login_required
def marquer_alerte_lue(request, alerte_id):
    """Marquer une alerte comme lue"""
    if request.method == 'POST':
        alerte = get_object_or_404(AlerteStock, id=alerte_id)
        alerte.lu = True
        alerte.save()
        messages.success(request, 'Alerte marquée comme lue.')
    
    return redirect('fuel_management:dashboard')


@login_required
def api_stock_status(request):
    """API pour récupérer le statut du stock en JSON"""
    stock = Stock.objects.first()
    if stock:
        data = {
            'quantite_actuelle': float(stock.quantite_actuelle),
            'seuil_minimum': float(stock.seuil_minimum),
            'status': 'critique' if stock.quantite_actuelle <= stock.seuil_minimum else 'ok',
            'derniere_mise_a_jour': stock.derniere_mise_a_jour.isoformat()
        }
    else:
        data = {
            'quantite_actuelle': 0,
            'seuil_minimum': 100,
            'status': 'critique',
            'derniere_mise_a_jour': None
        }
    
    return JsonResponse(data)
