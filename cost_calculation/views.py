from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
from decimal import Decimal

from .models import (
    CategorieCoût, CoûtMatierePremiere, CoûtMainOeuvre, 
    CoûtFraisGeneraux, CalculCoûtRevient, DetailCoûtMatiere
)
from .serializers import (
    CategorieCoûtSerializer, CoûtMatierePremierSerializer, 
    CoûtMainOeuvreSerializer, CoûtFraisGenerauxSerializer,
    CalculCoûtRevientSerializer, DetailCoûtMatiereSerializer
)
from orders.models import Commande
from production.models import OrdreProduction
from formulas.models import FormuleBeton
from inventory.models import MatierePremiere
from .engine import calculer_cout_revient_module


# ============= VUES TEMPLATES =============

def dashboard_coûts(request):
    """Dashboard principal du module de calcul des coûts"""
    # Statistiques générales
    total_calculs = CalculCoûtRevient.objects.count()
    calculs_ce_mois = CalculCoûtRevient.objects.filter(
        date_calcul__month=timezone.now().month,
        date_calcul__year=timezone.now().year
    ).count()
    
    # Coût moyen par m³
    coût_moyen_m3 = CalculCoûtRevient.objects.aggregate(
        moyenne=Avg('coût_unitaire_total')
    )['moyenne'] or 0
    
    # Derniers calculs
    derniers_calculs = CalculCoûtRevient.objects.select_related(
        'commande', 'ordre_production', 'formule'
    ).order_by('-date_calcul')[:10]
    
    # Répartition des coûts (moyennes)
    repartition_coûts = CalculCoûtRevient.objects.aggregate(
        matieres=Avg('coût_unitaire_matieres'),
        main_oeuvre=Avg('coût_unitaire_main_oeuvre'),
        frais_generaux=Avg('coût_unitaire_frais_generaux'),
        transport=Avg('coût_unitaire_transport')
    )
    
    context = {
        'total_calculs': total_calculs,
        'calculs_ce_mois': calculs_ce_mois,
        'coût_moyen_m3': coût_moyen_m3,
        'derniers_calculs': derniers_calculs,
        'repartition_coûts': repartition_coûts,
    }
    
    return render(request, 'cost_calculation/dashboard.html', context)


def liste_calculs_coûts(request):
    """Liste des calculs de coûts avec filtres"""
    calculs = CalculCoûtRevient.objects.select_related(
        'commande', 'ordre_production', 'formule'
    ).order_by('-date_calcul')
    
    # Filtres
    search = request.GET.get('search', '')
    if search:
        calculs = calculs.filter(
            Q(commande__id__icontains=search) |
            Q(ordre_production__numero_bon__icontains=search) |
            Q(formule__nom__icontains=search)
        )
    
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    if date_debut:
        calculs = calculs.filter(date_calcul__date__gte=date_debut)
    if date_fin:
        calculs = calculs.filter(date_calcul__date__lte=date_fin)
    
    # Pagination
    paginator = Paginator(calculs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    
    return render(request, 'cost_calculation/liste_calculs.html', context)


def detail_calcul_coût(request, calcul_id):
    """Détail d'un calcul de coût"""
    calcul = get_object_or_404(CalculCoûtRevient, id=calcul_id)
    details_matieres = calcul.details_matieres.select_related('matiere_premiere').all()
    
    context = {
        'calcul': calcul,
        'details_matieres': details_matieres,
    }
    
    return render(request, 'cost_calculation/detail_calcul.html', context)


def nouveau_calcul_coût(request):
    """Formulaire pour créer un nouveau calcul de coût"""
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            commande_id = request.POST.get('commande_id')
            ordre_production_id = request.POST.get('ordre_production_id')
            formule_id = request.POST.get('formule_id')
            quantite = Decimal(request.POST.get('quantite', '0'))
            
            # Validation
            if not formule_id or quantite <= 0:
                messages.error(request, "Formule et quantité sont obligatoires")
                return redirect('cost_calculation:nouveau_calcul')
            
            # Création du calcul
            calcul = CalculCoûtRevient.objects.create(
                commande_id=commande_id if commande_id else None,
                ordre_production_id=ordre_production_id if ordre_production_id else None,
                formule_id=formule_id,
                quantite_calculee=quantite,
                calculé_par=request.user.username if request.user.is_authenticated else 'Système'
            )
            
            # Calcul automatique des coûts
            calcul.calculer_coûts()
            calcul.save()
            
            # Création des détails par matière
            _creer_details_matieres(calcul)
            
            messages.success(request, f"Calcul de coût créé avec succès (ID: {calcul.id})")
            return redirect('cost_calculation:detail_calcul', calcul_id=calcul.id)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du calcul: {str(e)}")
    
    # Données pour le formulaire
    commandes = Commande.objects.filter(statut__in=['confirmee', 'en_production']).order_by('-date_creation')[:50]
    ordres_production = OrdreProduction.objects.filter(statut__in=['planifie', 'en_cours']).order_by('-date_creation')[:50]
    formules = FormuleBeton.objects.filter(active=True).order_by('nom')
    
    context = {
        'commandes': commandes,
        'ordres_production': ordres_production,
        'formules': formules,
    }
    
    return render(request, 'cost_calculation/nouveau_calcul.html', context)


def gestion_coûts_matieres(request):
    """Gestion des coûts des matières premières"""
    coûts = CoûtMatierePremiere.objects.select_related('matiere_premiere').filter(actif=True).order_by('-date_debut')
    
    # Filtres
    matiere_id = request.GET.get('matiere')
    if matiere_id:
        coûts = coûts.filter(matiere_premiere_id=matiere_id)
    
    # Pagination
    paginator = Paginator(coûts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Matières premières pour le filtre
    matieres = MatierePremiere.objects.filter(actif=True).order_by('nom')
    
    context = {
        'page_obj': page_obj,
        'matieres': matieres,
        'matiere_selectionnee': matiere_id,
    }
    
    return render(request, 'cost_calculation/gestion_coûts_matieres.html', context)


def gestion_coûts_main_oeuvre(request):
    """Gestion des coûts de main d'œuvre"""
    coûts = CoûtMainOeuvre.objects.filter(actif=True).order_by('type_activite', 'nom')
    
    context = {
        'coûts': coûts,
    }
    
    return render(request, 'cost_calculation/gestion_coûts_main_oeuvre.html', context)


def gestion_frais_generaux(request):
    """Gestion des frais généraux"""
    frais = CoûtFraisGeneraux.objects.select_related('categorie').filter(actif=True).order_by('categorie__nom', 'nom')
    categories = CategorieCoût.objects.filter(actif=True).order_by('type_categorie', 'nom')
    
    context = {
        'frais': frais,
        'categories': categories,
    }
    
    return render(request, 'cost_calculation/gestion_frais_generaux.html', context)


# ============= FONCTIONS UTILITAIRES =============

def _creer_details_matieres(calcul):
    """Crée les détails des coûts par matière première"""
    for composition in calcul.formule.composition.all():
        # Quantité nécessaire
        quantite_necessaire = (composition.quantite * calcul.quantite_calculee) / calcul.formule.quantite_produite_reference
        
        # Coût actuel de la matière
        coût_matiere = CoûtMatierePremiere.objects.filter(
            matiere_premiere=composition.matiere_premiere,
            actif=True,
            date_debut__lte=timezone.now().date()
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__gte=timezone.now().date())
        ).first()
        
        if coût_matiere:
            DetailCoûtMatiere.objects.create(
                calcul_coût=calcul,
                matiere_premiere=composition.matiere_premiere,
                quantite_utilisee=quantite_necessaire,
                prix_unitaire=coût_matiere.prix_total_unitaire,
                coût_total_matiere=quantite_necessaire * coût_matiere.prix_total_unitaire
            )


# ============= API REST =============

class CategorieCoûtViewSet(viewsets.ModelViewSet):
    """API pour les catégories de coûts"""
    queryset = CategorieCoût.objects.filter(actif=True)
    serializer_class = CategorieCoûtSerializer
    permission_classes = [IsAuthenticated]


class CoûtMatierePremierViewSet(viewsets.ModelViewSet):
    """API pour les coûts des matières premières"""
    queryset = CoûtMatierePremiere.objects.select_related('matiere_premiere').filter(actif=True)
    serializer_class = CoûtMatierePremierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        matiere_id = self.request.query_params.get('matiere_id')
        if matiere_id:
            queryset = queryset.filter(matiere_premiere_id=matiere_id)
        return queryset.order_by('-date_debut')
    
    @action(detail=False, methods=['get'])
    def coûts_actuels(self, request):
        """Retourne les coûts actuels de toutes les matières premières"""
        coûts_actuels = []
        matieres = MatierePremiere.objects.filter(actif=True)
        
        for matiere in matieres:
            coût = CoûtMatierePremiere.objects.filter(
                matiere_premiere=matiere,
                actif=True,
                date_debut__lte=timezone.now().date()
            ).filter(
                Q(date_fin__isnull=True) | Q(date_fin__gte=timezone.now().date())
            ).first()
            
            if coût:
                coûts_actuels.append({
                    'matiere_id': matiere.id,
                    'matiere_nom': matiere.nom,
                    'prix_unitaire': coût.prix_total_unitaire,
                    'unite_mesure': matiere.unite_mesure,
                    'date_debut': coût.date_debut
                })
        
        return Response(coûts_actuels)


class CoûtMainOeuvreViewSet(viewsets.ModelViewSet):
    """API pour les coûts de main d'œuvre"""
    queryset = CoûtMainOeuvre.objects.filter(actif=True)
    serializer_class = CoûtMainOeuvreSerializer
    permission_classes = [IsAuthenticated]


class CoûtFraisGenerauxViewSet(viewsets.ModelViewSet):
    """API pour les frais généraux"""
    queryset = CoûtFraisGeneraux.objects.select_related('categorie').filter(actif=True)
    serializer_class = CoûtFraisGenerauxSerializer
    permission_classes = [IsAuthenticated]


class CalculCoûtRevientViewSet(viewsets.ModelViewSet):
    """API pour les calculs de coûts de revient"""
    queryset = CalculCoûtRevient.objects.select_related('commande', 'ordre_production', 'formule')
    serializer_class = CalculCoûtRevientSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculer_coût_simulation(self, request):
        """Simule un calcul de coût sans le sauvegarder"""
        try:
            formule_id = request.data.get('formule_id')
            quantite = Decimal(str(request.data.get('quantite', '0')))
            
            if not formule_id or quantite <= 0:
                return Response(
                    {'error': 'Formule et quantité sont obligatoires'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            formule = get_object_or_404(FormuleBeton, id=formule_id)
            
            # Création temporaire pour simulation
            calcul_temp = CalculCoûtRevient(
                formule=formule,
                quantite_calculee=quantite
            )
            
            # Calcul des coûts
            calcul_temp.calculer_coûts()
            
            # Détails des matières
            details_matieres = []
            for composition in formule.composition.all():
                quantite_necessaire = (composition.quantite * quantite) / formule.quantite_produite_reference
                
                coût_matiere = CoûtMatierePremiere.objects.filter(
                    matiere_premiere=composition.matiere_premiere,
                    actif=True,
                    date_debut__lte=timezone.now().date()
                ).filter(
                    Q(date_fin__isnull=True) | Q(date_fin__gte=timezone.now().date())
                ).first()
                
                if coût_matiere:
                    details_matieres.append({
                        'matiere_nom': composition.matiere_premiere.nom,
                        'quantite_utilisee': float(quantite_necessaire),
                        'prix_unitaire': float(coût_matiere.prix_total_unitaire),
                        'coût_total': float(quantite_necessaire * coût_matiere.prix_total_unitaire)
                    })
            
            return Response({
                'formule_nom': formule.nom,
                'quantite_calculee': float(quantite),
                'coût_matieres_premieres': float(calcul_temp.coût_matieres_premieres),
                'coût_main_oeuvre': float(calcul_temp.coût_main_oeuvre),
                'coût_frais_generaux': float(calcul_temp.coût_frais_generaux),
                'coût_transport': float(calcul_temp.coût_transport),
                'coût_total': float(calcul_temp.coût_total),
                'coût_unitaire_total': float(calcul_temp.coût_unitaire_total),
                'details_matieres': details_matieres
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def recalculer(self, request, pk=None):
        """Recalcule les coûts d'un calcul existant"""
        calcul = self.get_object()
        
        try:
            # Recalcul des coûts
            calcul.calculer_coûts()
            calcul.save()
            
            # Suppression et recréation des détails
            calcul.details_matieres.all().delete()
            _creer_details_matieres(calcul)
            
            return Response({
                'message': 'Calcul mis à jour avec succès',
                'coût_total': float(calcul.coût_total),
                'coût_unitaire_total': float(calcul.coût_unitaire_total)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du recalcul: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= API AJAX =============

@csrf_exempt
@require_http_methods(["GET"])
def api_formule_details(request, formule_id):
    """API pour récupérer les détails d'une formule"""
    try:
        formule = get_object_or_404(FormuleBeton, id=formule_id)
        
        compositions = []
        for comp in formule.composition.all():
            coût_actuel = CoûtMatierePremiere.objects.filter(
                matiere_premiere=comp.matiere_premiere,
                actif=True,
                date_debut__lte=timezone.now().date()
            ).filter(
                Q(date_fin__isnull=True) | Q(date_fin__gte=timezone.now().date())
            ).first()
            
            compositions.append({
                'matiere_nom': comp.matiere_premiere.nom,
                'quantite': float(comp.quantite),
                'unite_mesure': comp.matiere_premiere.unite_mesure,
                'prix_unitaire': float(coût_actuel.prix_total_unitaire) if coût_actuel else 0
            })
        
        return JsonResponse({
            'nom': formule.nom,
            'description': formule.description,
            'quantite_reference': float(formule.quantite_produite_reference),
            'compositions': compositions
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Endpoints supplémentaires requis par le template nouveau_calcul

@csrf_exempt
@require_http_methods(["GET"])
def api_commandes(request):
    """Liste simple des commandes pour sélection (dernieres 50)."""
    commandes = Commande.objects.order_by('-date_commande')[:50]
    data = []
    for cmd in commandes:
        try:
            client_nom = getattr(cmd, 'client_nom', None)
        except Exception:
            client_nom = None
        data.append({
            'id': cmd.id,
            'client_nom': client_nom
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def api_ordres_production(request):
    """Liste simple des ordres de production pour sélection (derniers 50)."""
    ordres = OrdreProduction.objects.order_by('-date_production')[:50]
    data = []
    for op in ordres:
        try:
            numero_bon = getattr(op, 'numero_bon', None)
        except Exception:
            numero_bon = None
        try:
            formule_obj = getattr(op, 'formule', None)
            formule_nom = getattr(formule_obj, 'nom', None) if formule_obj else None
            formule_id = getattr(formule_obj, 'id', None) if formule_obj else None
        except Exception:
            formule_nom = None
            formule_id = None
        data.append({
            'id': op.id,
            'numero_bon': numero_bon,
            'formule_nom': formule_nom,
            'formule_id': formule_id
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def api_formule_composition(request, formule_id):
    """Détail de composition d'une formule au format attendu par le JS."""
    try:
        formule = get_object_or_404(FormuleBeton, id=formule_id)
        compositions = []
        for comp in formule.composition.all():
            coût_actuel = CoûtMatierePremiere.objects.filter(
                matiere_premiere=comp.matiere_premiere,
                actif=True,
                date_debut__lte=timezone.now().date()
            ).filter(
                Q(date_fin__isnull=True) | Q(date_fin__gte=timezone.now().date())
            ).first()
            compositions.append({
                'matiere_premiere': {
                    'id': comp.matiere_premiere.id,
                    'nom': comp.matiere_premiere.nom,
                    'unite_mesure': comp.matiere_premiere.unite_mesure,
                    'prix_unitaire': float(coût_actuel.prix_total_unitaire) if coût_actuel else 0
                },
                'quantite': float(comp.quantite)
            })
        return JsonResponse({
            'id': formule.id,
            'nom': formule.nom,
            'compositions': compositions
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def simulation_calcul(request):
    """Simule un calcul de coût selon les champs du formulaire et retourne un aperçu."""
    try:
        # Lecture des paramètres du formulaire
        formule_id = request.POST.get('formule') or request.POST.get('formule_id')
        quantite_str = request.POST.get('quantite', '0')
        unite_mesure = request.POST.get('unite_mesure', 'm3')
        quantite = Decimal(str(quantite_str)) if quantite_str else Decimal('0')
        
        if not formule_id or quantite <= 0:
            return JsonResponse({'success': False, 'error': 'Formule et quantité sont obligatoires'}, status=400)
        
        formule = get_object_or_404(FormuleBeton, id=formule_id)
        
        # Création d'un calcul temporaire et exécution
        calcul_temp = CalculCoûtRevient(formule=formule, quantite_calculee=quantite)
        calcul_temp.calculer_coûts()
        
        # Fallback: si les coûts calculés sont nuls, utiliser le nouveau module
        if calcul_temp.coût_total == Decimal('0'):
            result = calculer_cout_revient_module(formule, quantite)
            return JsonResponse(result)
        
        data = {
            'success': True,
            'calcul': {
                'quantite': float(quantite),
                'unite_mesure': unite_mesure,
                'formule_nom': formule.nom,
                'cout_matieres': float(calcul_temp.coût_matieres_premieres),
                'cout_main_oeuvre': float(calcul_temp.coût_main_oeuvre),
                'cout_frais_generaux': float(calcul_temp.coût_frais_generaux),
                'cout_transport': float(calcul_temp.coût_transport),
                'cout_total': float(calcul_temp.coût_total),
                'cout_unitaire': float(calcul_temp.coût_unitaire_total) if quantite > 0 else 0.0,
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def default_costs(request):
    """Valeurs par défaut pour le formulaire de nouveau calcul."""
    return JsonResponse({
        'cout_main_oeuvre_production': 25.00,
        'heures_production': 1.0,
        'charges_sociales': 45.0,
        'frais_fixes': 50.00,
        'frais_variables_pct': 5.0,
        'amortissement': 20.00,
        'assurance': 15.00,
        'distance_livraison': 10.0,
        'cout_km': 1.50,
        'frais_livraison_fixes': 25.00
    })
