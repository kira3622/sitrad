from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import Sum, Count, Avg, Q, Max
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Import des modèles
from .models import Rapport
from production.models import OrdreProduction, LotProduction
from orders.models import Commande, LigneCommande
from customers.models import Client, Chantier
from stock.models import MouvementStock
from inventory.models import MatierePremiere
from billing.models import Facture, LigneFacture
from formulas.models import FormuleBeton, CompositionFormule

# Vue principale des rapports
def dashboard_reports(request):
    """Vue principale du tableau de bord des rapports"""
    context = {
        'title': 'Tableau de Bord - Rapports',
    }
    return render(request, 'reports/dashboard.html', context)

# ==================== RAPPORTS DE PRODUCTION ====================

def rapport_production(request):
    """Rapport de production avec quantités, formules et efficacité"""
    # Filtres de date
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if not date_debut:
        date_debut = (timezone.now() - timedelta(days=30)).date()
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    
    if not date_fin:
        date_fin = timezone.now().date()
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Ordres de production dans la période
    ordres = OrdreProduction.objects.filter(
        date_production__range=[date_debut, date_fin]
    ).select_related('commande', 'formule')
    
    # Calcul de la quantité produite : utiliser les lots s'ils existent, sinon les ordres terminés
    quantite_lots = LotProduction.objects.filter(
        ordre_production__in=ordres
    ).aggregate(total=Sum('quantite_produite'))['total'] or 0
    
    # Si aucun lot n'existe, utiliser la quantité des ordres terminés
    if quantite_lots == 0:
        quantite_produite = ordres.filter(statut='termine').aggregate(
            total=Sum('quantite_produire')
        )['total'] or 0
    else:
        quantite_produite = quantite_lots
    
    # Statistiques de production
    stats_production = {
        'total_ordres': ordres.count(),
        'ordres_termines': ordres.filter(statut='termine').count(),
        'ordres_en_cours': ordres.filter(statut='en_cours').count(),
        'quantite_totale_planifiee': ordres.aggregate(total=Sum('quantite_produire'))['total'] or 0,
        'quantite_totale_produite': quantite_produite,
    }
    
    # Efficacité de production
    if stats_production['quantite_totale_planifiee'] > 0:
        stats_production['efficacite'] = (
            stats_production['quantite_totale_produite'] / 
            stats_production['quantite_totale_planifiee'] * 100
        )
    else:
        stats_production['efficacite'] = 0
    
    # Production par formule
    production_par_formule = ordres.values(
        'formule__nom', 'formule__resistance_requise'
    ).annotate(
        quantite_planifiee=Sum('quantite_produire'),
        nombre_ordres=Count('id')
    ).order_by('-quantite_planifiee')
    
    # Production quotidienne
    production_quotidienne = ordres.extra(
        select={'jour': 'date(date_production)'}
    ).values('jour').annotate(
        quantite=Sum('quantite_produire'),
        nombre_ordres=Count('id')
    ).order_by('jour')
    
    context = {
        'title': 'Rapport de Production',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'stats_production': stats_production,
        'ordres': ordres,
        'production_par_formule': production_par_formule,
        'production_quotidienne': production_quotidienne,
    }
    
    return render(request, 'reports/production.html', context)

# ==================== RAPPORTS DE COMMANDES ====================

def rapport_commandes(request):
    """Rapport des commandes avec statuts, délais et clients"""
    # Filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    statut_filtre = request.GET.get('statut')
    
    if not date_debut:
        date_debut = (timezone.now() - timedelta(days=30)).date()
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    
    if not date_fin:
        date_fin = timezone.now().date()
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Commandes dans la période
    commandes = Commande.objects.filter(
        date_commande__range=[date_debut, date_fin]
    ).select_related('client', 'chantier')
    
    if statut_filtre:
        commandes = commandes.filter(statut=statut_filtre)
    
    # Statistiques des commandes
    stats_commandes = {
        'total_commandes': commandes.count(),
        'en_attente': commandes.filter(statut='en_attente').count(),
        'validees': commandes.filter(statut='validee').count(),
        'en_production': commandes.filter(statut='en_production').count(),
        'livrees': commandes.filter(statut='livree').count(),
        'annulees': commandes.filter(statut='annulee').count(),
    }
    
    # Délais de livraison
    commandes_avec_delais = []
    for commande in commandes:
        delai = (commande.date_livraison_souhaitee - commande.date_commande).days
        commandes_avec_delais.append({
            'commande': commande,
            'delai_souhaite': delai,
            'en_retard': commande.date_livraison_souhaitee < timezone.now().date() and commande.statut != 'livree'
        })
    
    # Top clients
    top_clients = commandes.values(
        'client__nom'
    ).annotate(
        nombre_commandes=Count('id')
    ).order_by('-nombre_commandes')[:10]
    
    # Commandes par statut et par jour
    commandes_quotidiennes = commandes.extra(
        select={'jour': 'date(date_commande)'}
    ).values('jour', 'statut').annotate(
        nombre=Count('id')
    ).order_by('jour')
    
    context = {
        'title': 'Rapport des Commandes',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'statut_filtre': statut_filtre,
        'stats_commandes': stats_commandes,
        'commandes_avec_delais': commandes_avec_delais,
        'top_clients': top_clients,
        'commandes_quotidiennes': commandes_quotidiennes,
        'statuts_choices': Commande._meta.get_field('statut').choices,
    }
    
    return render(request, 'reports/commandes.html', context)

# ==================== RAPPORTS COMMERCIAUX & CLIENTS ====================

def rapport_commercial(request):
    """Rapport commercial avec CA, fidélité et géographie"""
    # Filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if not date_debut:
        date_debut = (timezone.now() - timedelta(days=30)).date()
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    
    if not date_fin:
        date_fin = timezone.now().date()
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Factures dans la période
    factures = Facture.objects.filter(
        date_facturation__range=[date_debut, date_fin]
    ).select_related('commande__client')
    
    # Chiffre d'affaires
    ca_stats = {
        'ca_total': factures.aggregate(total=Sum('montant_total'))['total'] or 0,
        'ca_paye': factures.filter(statut='payee').aggregate(total=Sum('montant_total'))['total'] or 0,
        'ca_en_attente': factures.exclude(statut='payee').aggregate(total=Sum('montant_total'))['total'] or 0,
        'nombre_factures': factures.count(),
        'factures_payees': factures.filter(statut='payee').count(),
    }
    
    # CA par client
    ca_par_client = factures.values(
        'commande__client__nom'
    ).annotate(
        ca_total=Sum('montant_total'),
        nombre_factures=Count('id')
    ).order_by('-ca_total')[:10]
    
    # Analyse de fidélité des clients
    clients_fidelite = Client.objects.annotate(
        nombre_commandes=Count('commande'),
        ca_total=Sum('commande__facture__montant_total'),
        derniere_commande=Max('commande__date_commande')
    ).filter(nombre_commandes__gt=0).order_by('-ca_total')
    
    # CA mensuel
    ca_mensuel = factures.extra(
        select={'mois': "strftime('%%Y-%%m', date_facturation)"}
    ).values('mois').annotate(
        ca=Sum('montant_total'),
        nombre_factures=Count('id')
    ).order_by('mois')
    
    # Répartition géographique (par ville des clients)
    repartition_geo = factures.values(
        'commande__client__adresse'
    ).annotate(
        ca=Sum('montant_total'),
        nombre_commandes=Count('id')
    ).order_by('-ca')
    
    context = {
        'title': 'Rapport Commercial',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'ca_stats': ca_stats,
        'ca_par_client': ca_par_client,
        'clients_fidelite': clients_fidelite,
        'ca_mensuel': ca_mensuel,
        'repartition_geo': repartition_geo,
    }
    
    return render(request, 'reports/commercial.html', context)

# ==================== RAPPORTS DE STOCK ====================

def rapport_stock(request):
    """Rapport de stock avec niveaux, mouvements et alertes"""
    # Seuils d'alerte (peuvent être configurés)
    seuil_critique = Decimal('10.0')
    seuil_bas = Decimal('50.0')
    
    # Stock actuel de toutes les matières premières
    matieres_premieres = MatierePremiere.objects.all()
    stocks_actuels = []
    
    for matiere in matieres_premieres:
        stock_actuel = matiere.stock_actuel
        niveau_alerte = 'normal'
        
        if stock_actuel <= seuil_critique:
            niveau_alerte = 'critique'
        elif stock_actuel <= seuil_bas:
            niveau_alerte = 'bas'
        
        stocks_actuels.append({
            'matiere': matiere,
            'stock_actuel': stock_actuel,
            'niveau_alerte': niveau_alerte
        })
    
    # Mouvements récents (30 derniers jours)
    date_limite = timezone.now() - timedelta(days=30)
    mouvements_recents = MouvementStock.objects.filter(
        date_mouvement__gte=date_limite
    ).select_related('matiere_premiere').order_by('-date_mouvement')
    
    # Statistiques des mouvements
    stats_mouvements = {
        'total_entrees': mouvements_recents.filter(type_mouvement='entree').aggregate(
            total=Sum('quantite'))['total'] or 0,
        'total_sorties': mouvements_recents.filter(type_mouvement='sortie').aggregate(
            total=Sum('quantite'))['total'] or 0,
        'nombre_mouvements': mouvements_recents.count(),
    }
    
    # Mouvements par matière première
    mouvements_par_matiere = mouvements_recents.values(
        'matiere_premiere__nom'
    ).annotate(
        entrees=Sum('quantite', filter=Q(type_mouvement='entree')),
        sorties=Sum('quantite', filter=Q(type_mouvement='sortie')),
        nombre_mouvements=Count('id')
    ).order_by('-nombre_mouvements')
    
    # Évolution du stock (par jour)
    evolution_stock = mouvements_recents.extra(
        select={'jour': 'date(date_mouvement)'}
    ).values('jour', 'type_mouvement').annotate(
        quantite_totale=Sum('quantite')
    ).order_by('jour')
    
    # Alertes de stock
    alertes = [stock for stock in stocks_actuels if stock['niveau_alerte'] in ['critique', 'bas']]
    
    context = {
        'title': 'Rapport de Stock',
        'stocks_actuels': stocks_actuels,
        'mouvements_recents': mouvements_recents[:20],  # Limiter l'affichage
        'stats_mouvements': stats_mouvements,
        'mouvements_par_matiere': mouvements_par_matiere,
        'evolution_stock': evolution_stock,
        'alertes': alertes,
        'seuil_critique': seuil_critique,
        'seuil_bas': seuil_bas,
    }
    
    return render(request, 'reports/stock.html', context)

# ==================== RAPPORTS FINANCIERS ====================

def rapport_financier(request):
    """Rapport financier avec factures, paiements et rentabilité"""
    # Filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if not date_debut:
        date_debut = (timezone.now() - timedelta(days=30)).date()
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    
    if not date_fin:
        date_fin = timezone.now().date()
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Factures dans la période
    factures = Facture.objects.filter(
        date_facturation__range=[date_debut, date_fin]
    ).select_related('commande__client')
    
    # Statistiques financières
    stats_financieres = {
        'ca_total': factures.aggregate(total=Sum('montant_total'))['total'] or 0,
        'ca_facture': factures.aggregate(total=Sum('montant_total'))['total'] or 0,
        'ca_paye': factures.filter(statut='payee').aggregate(total=Sum('montant_total'))['total'] or 0,
        'ca_en_attente': factures.filter(statut='envoyee').aggregate(total=Sum('montant_total'))['total'] or 0,
        'ca_brouillon': factures.filter(statut='brouillon').aggregate(total=Sum('montant_total'))['total'] or 0,
        'nombre_factures': factures.count(),
        'factures_payees': factures.filter(statut='payee').count(),
        'factures_en_attente': factures.filter(statut='envoyee').count(),
    }
    
    # Taux de recouvrement
    if stats_financieres['ca_facture'] > 0:
        stats_financieres['taux_recouvrement'] = (
            stats_financieres['ca_paye'] / stats_financieres['ca_facture'] * 100
        )
    else:
        stats_financieres['taux_recouvrement'] = 0
    
    # Factures par statut
    factures_par_statut = factures.values('statut').annotate(
        nombre=Count('id'),
        montant_total=Sum('montant_total')
    ).order_by('statut')
    
    # Évolution du CA mensuel
    ca_mensuel = factures.extra(
        select={'mois': "strftime('%%Y-%%m', date_facturation)"}
    ).values('mois').annotate(
        ca_facture=Sum('montant_total'),
        ca_paye=Sum('montant_total', filter=Q(statut='payee')),
        nombre_factures=Count('id')
    ).order_by('mois')
    
    # Top clients par CA
    top_clients_ca = factures.values(
        'commande__client__nom'
    ).annotate(
        ca_total=Sum('montant_total'),
        ca_paye=Sum('montant_total', filter=Q(statut='payee')),
        nombre_factures=Count('id')
    ).order_by('-ca_total')[:10]
    
    # Factures en retard de paiement (envoyées depuis plus de 30 jours)
    date_limite_paiement = timezone.now().date() - timedelta(days=30)
    factures_en_retard = factures.filter(
        statut='envoyee',
        date_facturation__lt=date_limite_paiement
    )
    
    context = {
        'title': 'Rapport Financier',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'stats_financieres': stats_financieres,
        'factures_par_statut': factures_par_statut,
        'ca_mensuel': ca_mensuel,
        'top_clients_ca': top_clients_ca,
        'factures_en_retard': factures_en_retard,
        'factures': factures,
    }
    
    return render(request, 'reports/financier.html', context)

# ==================== EXPORT PDF ====================

def export_rapport_pdf(request, type_rapport):
    """Export d'un rapport en PDF"""
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse("La bibliothèque xhtml2pdf n'est pas installée.", status=500)
    
    # Déterminer le template et les données selon le type de rapport
    # Dans la fonction export_rapport_pdf, ligne ~436
    if type_rapport == 'production':
        context = _get_production_data(request)
        template_path = 'reports/pdf/production_pdf.html'
        filename = f'rapport_production_{timezone.now().strftime("%Y%m%d")}.pdf'
    elif type_rapport == 'commandes':
        context = _get_commandes_data(request)
        template_path = 'reports/pdf/commandes_pdf.html'
        filename = f'rapport_commandes_{timezone.now().strftime("%Y%m%d")}.pdf'
    elif type_rapport == 'commercial':
        context = _get_commercial_data(request)
        template_path = 'reports/pdf/commercial_pdf.html'
        filename = f'rapport_commercial_{timezone.now().strftime("%Y%m%d")}.pdf'
    elif type_rapport == 'stock':
        context = _get_stock_data(request)
        template_path = 'reports/pdf/stock_pdf.html'
        filename = f'rapport_stock_{timezone.now().strftime("%Y%m%d")}.pdf'
    elif type_rapport == 'financier':
        context = _get_financier_data(request)
        template_path = 'reports/pdf/financier_pdf.html'
        filename = f'rapport_financier_{timezone.now().strftime("%Y%m%d")}.pdf'
    else:
        return HttpResponse("Type de rapport non reconnu.", status=400)
    
    # Créer la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Rendre le template
    template = get_template(template_path)
    html = template.render(context)
    
    # Créer le PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    
    return response

# Fonctions utilitaires pour récupérer les données
def _get_production_data(request):
    """Récupère les données de production pour l'export PDF"""
    # Filtres de date
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if not date_debut:
        date_debut = (timezone.now() - timedelta(days=30)).date()
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    
    if not date_fin:
        date_fin = timezone.now().date()
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Ordres de production dans la période
    ordres = OrdreProduction.objects.filter(
        date_production__range=[date_debut, date_fin]
    ).select_related('commande', 'formule')
    
    # Calcul de la quantité produite : utiliser les lots s'ils existent, sinon les ordres terminés
    quantite_lots = LotProduction.objects.filter(
        ordre_production__in=ordres
    ).aggregate(total=Sum('quantite_produite'))['total'] or 0
    
    # Si aucun lot n'existe, utiliser la quantité des ordres terminés
    if quantite_lots == 0:
        quantite_produite = ordres.filter(statut='termine').aggregate(
            total=Sum('quantite_produire')
        )['total'] or 0
    else:
        quantite_produite = quantite_lots
    
    # Statistiques de production
    stats_production = {
        'total_ordres': ordres.count(),
        'ordres_termines': ordres.filter(statut='termine').count(),
        'ordres_en_cours': ordres.filter(statut='en_cours').count(),
        'quantite_totale_planifiee': ordres.aggregate(total=Sum('quantite_produire'))['total'] or 0,
        'quantite_totale_produite': quantite_produite,
    }
    
    # Efficacité de production
    if stats_production['quantite_totale_planifiee'] > 0:
        stats_production['efficacite'] = (
            stats_production['quantite_totale_produite'] / 
            stats_production['quantite_totale_planifiee'] * 100
        )
    else:
        stats_production['efficacite'] = 0
    
    # Production par formule
    production_par_formule = ordres.values(
        'formule__nom', 'formule__resistance_requise'
    ).annotate(
        quantite_planifiee=Sum('quantite_produire'),
        nombre_ordres=Count('id')
    ).order_by('-quantite_planifiee')
    
    return {
        'title': 'Rapport de Production',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'stats_production': stats_production,
        'ordres': ordres,
        'production_par_formule': production_par_formule,
    }

def _get_commandes_data(request):
    # Logique similaire à rapport_commandes mais simplifiée pour PDF
    pass

def _get_commercial_data(request):
    # Logique similaire à rapport_commercial mais simplifiée pour PDF
    pass

def _get_stock_data(request):
    # Logique similaire à rapport_stock mais simplifiée pour PDF
    pass

def _get_financier_data(request):
    # Logique similaire à rapport_financier mais simplifiée pour PDF
    pass
