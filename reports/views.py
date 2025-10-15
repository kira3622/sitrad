from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import Sum, Count, Avg, Q, Max
from django.db.models.functions import TruncMonth
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
    ).select_related('client', 'chantier').prefetch_related('lignes__formule')
    
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
    ca_mensuel = factures.annotate(
        mois=TruncMonth('date_facturation')
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
    """Rapport de stock avec niveaux, mouvements et alertes (seuils par matière)"""
    # Stock actuel de toutes les matières premières avec leurs seuils individuels
    matieres_premieres = MatierePremiere.objects.all()
    stocks_actuels = []
    
    for matiere in matieres_premieres:
        stock_actuel = matiere.stock_actuel
        niveau_alerte = matiere.statut_stock  # Utilise la méthode du modèle
        
        stocks_actuels.append({
            'matiere': matiere,
            'stock_actuel': stock_actuel,
            'niveau_alerte': niveau_alerte,
            'seuil_critique': matiere.seuil_critique,
            'seuil_bas': matiere.seuil_bas,
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
    
    # Statistiques des seuils
    stats_seuils = {
        'total_matieres': len(stocks_actuels),
        'matieres_critiques': len([s for s in stocks_actuels if s['niveau_alerte'] == 'critique']),
        'matieres_bas': len([s for s in stocks_actuels if s['niveau_alerte'] == 'bas']),
        'matieres_normales': len([s for s in stocks_actuels if s['niveau_alerte'] == 'normal']),
    }
    
    context = {
        'title': 'Rapport de Stock',
        'stocks_actuels': stocks_actuels,
        'mouvements_recents': mouvements_recents[:20],  # Limiter l'affichage
        'stats_mouvements': stats_mouvements,
        'mouvements_par_matiere': mouvements_par_matiere,
        'evolution_stock': evolution_stock,
        'alertes': alertes,
        'stats_seuils': stats_seuils,
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
    
    # Statistiques financières de base
    ca_total = factures.aggregate(total=Sum('montant_total'))['total'] or 0
    ca_paye = factures.filter(statut='payee').aggregate(total=Sum('montant_total'))['total'] or 0
    ca_en_attente = factures.filter(statut='envoyee').aggregate(total=Sum('montant_total'))['total'] or 0
    ca_brouillon = factures.filter(statut='brouillon').aggregate(total=Sum('montant_total'))['total'] or 0
    nombre_factures = factures.count()
    factures_payees = factures.filter(statut='payee').count()
    factures_en_attente = factures.filter(statut='envoyee').count()
    
    # Calculs supplémentaires pour les KPI
    montant_moyen = ca_total / nombre_factures if nombre_factures > 0 else 0
    taux_paiement = (factures_payees / nombre_factures * 100) if nombre_factures > 0 else 0
    pourcentage_en_attente = (ca_en_attente / ca_total * 100) if ca_total > 0 else 0
    
    # Factures en retard de paiement (envoyées depuis plus de 30 jours)
    date_limite_paiement = timezone.now().date() - timedelta(days=30)
    factures_en_retard_qs = factures.filter(
        statut='envoyee',
        date_facturation__lt=date_limite_paiement
    )
    
    # Ajouter le calcul des jours de retard pour chaque facture
    factures_en_retard_list = []
    for facture in factures_en_retard_qs:
        jours_retard = (timezone.now().date() - facture.date_facturation).days
        facture.jours_retard = jours_retard
        factures_en_retard_list.append(facture)
    
    # Délai de paiement moyen (approximation basée sur les factures payées)
    delai_paiement_moyen = 15  # Valeur par défaut, peut être calculée plus précisément
    
    # Statistiques complètes pour le template
    stats_factures = {
        'total_factures': nombre_factures,
        'ca_total': ca_total,
        'ca_paye': ca_paye,
        'ca_en_attente': ca_en_attente,
        'ca_brouillon': ca_brouillon,
        'nombre_factures': nombre_factures,
        'factures_payees': factures_payees,
        'factures_en_attente': factures_en_attente,
        'factures_en_retard': factures_en_retard_qs.count(),
        'montant_moyen': montant_moyen,
        'taux_paiement': taux_paiement,
        'delai_paiement_moyen': delai_paiement_moyen,
        'pourcentage_en_attente': pourcentage_en_attente,
    }
    
    # Répartition par statut avec pourcentages
    factures_par_statut_raw = factures.values('statut').annotate(
        nombre=Count('id'),
        montant_total=Sum('montant_total')
    ).order_by('statut')
    
    repartition_statut = []
    for statut_data in factures_par_statut_raw:
        pourcentage = (statut_data['montant_total'] / ca_total * 100) if ca_total > 0 else 0
        repartition_statut.append({
            'statut': statut_data['statut'],
            'nombre': statut_data['nombre'],
            'montant_total': statut_data['montant_total'],
            'pourcentage': pourcentage
        })
    
    # Top clients avec CA moyen et dernière facture
    top_clients_raw = factures.values(
        'commande__client__nom'
    ).annotate(
        ca_total=Sum('montant_total'),
        ca_paye=Sum('montant_total', filter=Q(statut='payee')),
        nombre_factures=Count('id'),
        derniere_facture=Max('date_facturation')
    ).order_by('-ca_total')[:10]
    
    top_clients = []
    for client_data in top_clients_raw:
        ca_moyen = client_data['ca_total'] / client_data['nombre_factures'] if client_data['nombre_factures'] > 0 else 0
        top_clients.append({
            'commande__client__nom': client_data['commande__client__nom'],
            'ca_total': client_data['ca_total'],
            'ca_paye': client_data['ca_paye'],
            'nombre_factures': client_data['nombre_factures'],
            'ca_moyen': ca_moyen,
            'derniere_facture': client_data['derniere_facture']
        })
    
    # Évolution du CA mensuel avec calcul d'évolution
    ca_mensuel_raw = factures.annotate(
        mois=TruncMonth('date_facturation')
    ).values('mois').annotate(
        ca_mensuel=Sum('montant_total'),
        ca_paye=Sum('montant_total', filter=Q(statut='payee')),
        nombre_factures=Count('id')
    ).order_by('mois')
    
    evolution_ca = []
    ca_precedent = None
    for i, mois_data in enumerate(ca_mensuel_raw):
        evolution = None
        if ca_precedent and ca_precedent > 0:
            evolution = ((mois_data['ca_mensuel'] - ca_precedent) / ca_precedent * 100)
        
        # Convertir la chaîne de mois en date pour l'affichage
        try:
            mois_date = datetime.strptime(mois_data['mois'], '%Y-%m').date()
        except:
            mois_date = timezone.now().date()
        
        evolution_ca.append({
            'mois': mois_date,
            'ca_mensuel': mois_data['ca_mensuel'],
            'ca_paye': mois_data['ca_paye'],
            'nombre_factures': mois_data['nombre_factures'],
            'evolution': evolution
        })
        ca_precedent = mois_data['ca_mensuel']
    
    # Analyse de trésorerie
    date_30j_avant = timezone.now().date() - timedelta(days=30)
    date_30j_apres = timezone.now().date() + timedelta(days=30)
    
    encaissements_30j = Facture.objects.filter(
        statut='payee',
        date_facturation__gte=date_30j_avant
    ).aggregate(total=Sum('montant_total'))['total'] or 0
    
    previsions_30j = factures.filter(
        statut='envoyee',
        date_facturation__lte=date_30j_apres
    ).aggregate(total=Sum('montant_total'))['total'] or 0
    
    creances_totales = factures.filter(statut='envoyee').aggregate(total=Sum('montant_total'))['total'] or 0
    
    # Âge moyen des créances (approximation)
    age_moyen_creances = 20  # Valeur par défaut, peut être calculée plus précisément
    
    tresorerie = {
        'encaissements_30j': encaissements_30j,
        'previsions_30j': previsions_30j,
        'creances_totales': creances_totales,
        'age_moyen_creances': age_moyen_creances
    }
    
    context = {
        'title': 'Rapport Financier',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'stats_factures': stats_factures,  # Nom correct pour le template
        'repartition_statut': repartition_statut,
        'top_clients': top_clients,
        'evolution_ca': evolution_ca,
        'factures_en_retard': factures_en_retard_list,
        'tresorerie': tresorerie,
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

# ==================== RAPPORTS MATIÈRES PAR M³ ====================

def rapport_ratios_m3(request):
    """Rapport des ratios de chaque matière première par mètre cube produit.

    - Section 1: Théorique par formule (composition normalisée par m³)
    - Section 2: Consommation réelle par m³ sur une période (sorties stock / m³ produits)
    """
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

    # Section 1: Théorique par Matière
    from inventory.models import MatierePremiere
    matieres = MatierePremiere.objects.prefetch_related('compositionformule_set__formule').all()
    matieres_theorique_data = []
    for matiere in matieres:
        formules_usage = []
        for comp in matiere.compositionformule_set.all():
            formule = comp.formule
            quantite_ref = formule.quantite_produite_reference or Decimal('1')
            if quantite_ref > 0:
                par_m3 = comp.quantite / quantite_ref
            else:
                par_m3 = Decimal('0')
            
            formules_usage.append({
                'formule_nom': formule.nom,
                'ratio': par_m3
            })
        
        if formules_usage:
            matieres_theorique_data.append({
                'matiere_nom': matiere.nom,
                'unite': matiere.unite_mesure,
                'formules_usage': formules_usage
            })

    # Section 2: Consommation réelle par m³ (période)
    # Utiliser les lots produits pendant la période (par date réelle de production)
    lots_produits = LotProduction.objects.filter(
        date_heure_production__date__range=[date_debut, date_fin]
    )
    total_m3_produits = lots_produits.aggregate(total=Sum('quantite_produite'))['total'] or Decimal('0')

    mouvements_sorties = MouvementStock.objects.filter(
        type_mouvement='sortie',
        date_mouvement__date__range=[date_debut, date_fin]
    )

    ratios_reels = []
    if total_m3_produits and total_m3_produits > 0:
        agr = mouvements_sorties.values(
            'matiere_premiere__nom', 'matiere_premiere__unite_mesure'
        ).annotate(total_sorties=Sum('quantite')).order_by('matiere_premiere__nom')
        for item in agr:
            total_sorties = item['total_sorties'] or Decimal('0')
            ratio = total_sorties / total_m3_produits if total_m3_produits > 0 else Decimal('0')
            ratios_reels.append({
                'matiere': item['matiere_premiere__nom'],
                'unite': item['matiere_premiere__unite_mesure'],
                'ratio_par_m3': ratio,
                'total_sorties': total_sorties,
            })

    context = {
        'title': 'Ratios Matières par m³',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'matieres_theorique_data': matieres_theorique_data,
        'total_m3_produits': total_m3_produits,
        'ratios_reels': ratios_reels,
    }

    return render(request, 'reports/ratios_m3.html', context)

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


def rapport_mouvements_par_jour(request):
    """
    Vue pour le rapport détaillé des mouvements par matière première par jour
    """
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from stock.models import MouvementStock
    from inventory.models import MatierePremiere
    
    # Récupération des paramètres de filtrage
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    matiere_id = request.GET.get('matiere_premiere')
    
    # Dates par défaut (30 derniers jours)
    if not date_fin:
        date_fin = timezone.now().date()
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    if not date_debut:
        date_debut = date_fin - timedelta(days=30)
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    
    # Filtrage des mouvements
    mouvements_query = MouvementStock.objects.filter(
        date_mouvement__date__gte=date_debut,
        date_mouvement__date__lte=date_fin
    ).select_related('matiere_premiere')
    
    if matiere_id:
        mouvements_query = mouvements_query.filter(matiere_premiere_id=matiere_id)
    
    # Regroupement par jour et matière première
    mouvements_par_jour = {}
    for mouvement in mouvements_query.order_by('date_mouvement'):
        jour = mouvement.date_mouvement.date()
        matiere = mouvement.matiere_premiere.nom
        
        if jour not in mouvements_par_jour:
            mouvements_par_jour[jour] = {}
        
        if matiere not in mouvements_par_jour[jour]:
            mouvements_par_jour[jour][matiere] = {
                'entrees': 0,
                'sorties': 0,
                'mouvements': [],
                'solde_debut': 0,
                'solde_fin': 0
            }
        
        if mouvement.type_mouvement == 'entree':
            mouvements_par_jour[jour][matiere]['entrees'] += mouvement.quantite
        else:
            mouvements_par_jour[jour][matiere]['sorties'] += mouvement.quantite
        
        mouvements_par_jour[jour][matiere]['mouvements'].append(mouvement)
    
    # Calcul des soldes quotidiens
    for jour in sorted(mouvements_par_jour.keys()):
        for matiere in mouvements_par_jour[jour]:
            data = mouvements_par_jour[jour][matiere]
            data['solde_fin'] = data['solde_debut'] + data['entrees'] - data['sorties']
    
    # Statistiques générales
    stats_data = mouvements_query.aggregate(
        total_entrees=Sum('quantite', filter=Q(type_mouvement='entree')) or 0,
        total_sorties=Sum('quantite', filter=Q(type_mouvement='sortie')) or 0,
        total_mouvements=Count('id')
    )
    
    # Calcul du solde net
    stats_data['solde_net'] = (stats_data['total_entrees'] or 0) - (stats_data['total_sorties'] or 0)
    
    # Résumé par matière première
    resume_par_matiere_data = mouvements_query.values('matiere_premiere__nom').annotate(
        total_entrees=Sum('quantite', filter=Q(type_mouvement='entree')) or 0,
        total_sorties=Sum('quantite', filter=Q(type_mouvement='sortie')) or 0,
        nb_mouvements=Count('id')
    ).order_by('matiere_premiere__nom')
    
    # Formatage du résumé par matière avec calcul du solde net
    resume_par_matiere = []
    for item in resume_par_matiere_data:
        resume_par_matiere.append({
            'matiere': item['matiere_premiere__nom'],
            'nb_mouvements': item['nb_mouvements'],
            'total_entrees': item['total_entrees'] or 0,
            'total_sorties': item['total_sorties'] or 0,
            'solde_net': (item['total_entrees'] or 0) - (item['total_sorties'] or 0)
        })
    
    # Liste des matières premières pour le filtre
    matieres_premieres = MatierePremiere.objects.all().order_by('nom')
    
    # Liste des mouvements pour l'affichage
    mouvements = mouvements_query.order_by('-date_mouvement')
    
    context = {
        'title': 'Mouvements par Matière Première par Jour',
        'date_debut': date_debut,
        'date_fin': date_fin,
        'matiere_id': matiere_id,
        'mouvements': mouvements,
        'stats': stats_data,
        'resume_par_matiere': resume_par_matiere,
        'matieres': matieres_premieres,
    }
    
    return render(request, 'reports/mouvements_par_jour.html', context)
