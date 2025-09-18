from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import OrdreProduction

@login_required
@require_POST
def calculer_sorties_ordre(request, ordre_id):
    """
    Vue pour calculer automatiquement les sorties de matières pour un ordre de production spécifique.
    """
    ordre = get_object_or_404(OrdreProduction, id=ordre_id)
    force = request.POST.get('force', 'false').lower() == 'true'
    
    try:
        resultat = ordre.creer_mouvements_stock(force=force)
        
        if resultat['success']:
            messages.success(request, resultat['message'])
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': resultat['message'],
                    'mouvements_count': len(resultat['mouvements'])
                })
        else:
            messages.error(request, resultat['message'])
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': resultat['message'],
                    'matieres_insuffisantes': resultat.get('matieres_insuffisantes', [])
                })
    
    except Exception as e:
        messages.error(request, f"Erreur lors du calcul des sorties : {str(e)}")
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': f"Erreur : {str(e)}"
            })
    
    return redirect('admin:production_ordreproduction_changelist')

@login_required
def preview_sorties_ordre(request, ordre_id):
    """
    Vue pour prévisualiser les sorties de matières sans les créer.
    """
    ordre = get_object_or_404(OrdreProduction, id=ordre_id)
    
    try:
        # Calculer les sorties prévues
        sorties_prevues = ordre.calculer_sorties_matieres()
        verification_stock = ordre.verifier_stock_disponible()
        
        context = {
            'ordre': ordre,
            'sorties_prevues': sorties_prevues,
            'verification_stock': verification_stock,
            'total_matieres': len(sorties_prevues)
        }
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': True,
                'sorties_prevues': [
                    {
                        'matiere_nom': sortie['matiere_premiere'].nom,
                        'matiere_unite': sortie['matiere_premiere'].unite_mesure,
                        'quantite_necessaire': float(sortie['quantite_necessaire']),
                        'quantite_formule': float(sortie['quantite_formule']),
                        'facteur': float(sortie['facteur'])
                    }
                    for sortie in sorties_prevues
                ],
                'verification_stock': {
                    'stock_suffisant': verification_stock['stock_suffisant'],
                    'matieres_insuffisantes': [
                        {
                            'matiere_nom': mat['matiere'].nom,
                            'stock_actuel': float(mat['stock_actuel']),
                            'quantite_necessaire': float(mat['quantite_necessaire']),
                            'manque': float(mat['manque'])
                        }
                        for mat in verification_stock['matieres_insuffisantes']
                    ]
                }
            })
        
        return render(request, 'production/preview_sorties.html', context)
    
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': f"Erreur : {str(e)}"
            })
        messages.error(request, f"Erreur lors de la prévisualisation : {str(e)}")
        return redirect('admin:production_ordreproduction_changelist')

@login_required
@require_POST
@transaction.atomic
def calculer_sorties_batch(request):
    """
    Vue pour calculer les sorties de matières pour plusieurs ordres de production en lot.
    """
    ordre_ids = request.POST.getlist('ordre_ids')
    force = request.POST.get('force', 'false').lower() == 'true'
    
    if not ordre_ids:
        messages.error(request, "Aucun ordre de production sélectionné.")
        return redirect('admin:production_ordreproduction_changelist')
    
    resultats = {
        'success': 0,
        'errors': 0,
        'details': []
    }
    
    for ordre_id in ordre_ids:
        try:
            ordre = OrdreProduction.objects.get(id=ordre_id)
            resultat = ordre.creer_mouvements_stock(force=force)
            
            if resultat['success']:
                resultats['success'] += 1
                resultats['details'].append({
                    'ordre_id': ordre_id,
                    'status': 'success',
                    'message': resultat['message']
                })
            else:
                resultats['errors'] += 1
                resultats['details'].append({
                    'ordre_id': ordre_id,
                    'status': 'error',
                    'message': resultat['message']
                })
        
        except OrdreProduction.DoesNotExist:
            resultats['errors'] += 1
            resultats['details'].append({
                'ordre_id': ordre_id,
                'status': 'error',
                'message': 'Ordre de production non trouvé'
            })
        except Exception as e:
            resultats['errors'] += 1
            resultats['details'].append({
                'ordre_id': ordre_id,
                'status': 'error',
                'message': str(e)
            })
    
    # Messages de résumé
    if resultats['success'] > 0:
        messages.success(request, f"{resultats['success']} ordre(s) traité(s) avec succès.")
    if resultats['errors'] > 0:
        messages.error(request, f"{resultats['errors']} ordre(s) en erreur.")
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(resultats)
    
    return redirect('admin:production_ordreproduction_changelist')
