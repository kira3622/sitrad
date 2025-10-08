from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import OrdreProduction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum
from django.conf import settings
import os
from django.templatetags.static import static

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
        
        # Préparer les données pour le template
        preview_data = {
            'matieres': [
                {
                    'nom': sortie['matiere_premiere'].nom,
                    'quantite_necessaire': sortie['quantite_necessaire'],
                    'unite': sortie['matiere_premiere'].unite_mesure,
                    'stock_actuel': sortie['matiere_premiere'].stock_actuel,
                    'stock_apres_deduction': sortie['matiere_premiere'].stock_actuel - sortie['quantite_necessaire'],
                    'stock_suffisant': sortie['matiere_premiere'].stock_actuel >= sortie['quantite_necessaire']
                }
                for sortie in sorties_prevues
            ],
            'stock_suffisant': verification_stock['stock_suffisant']
        }
        
        context = {
            'ordre': ordre,
            'preview_data': preview_data,
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
        # Préparer les données d'erreur pour le template
        preview_data = {
            'error': str(e),
            'matieres': None
        }
        
        context = {
            'ordre': ordre,
            'preview_data': preview_data
        }
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': f"Erreur : {str(e)}"
            })
        
        messages.error(request, f"Erreur lors de la prévisualisation : {str(e)}")
        return render(request, 'production/preview_sorties.html', context)

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

def delivery_note_pdf(request, pk):
    """Génère le Bon de Livraison PDF à partir des données d'OrdreProduction en rendant le template HTML."""
    op = get_object_or_404(OrdreProduction, pk=pk)

    # Helpers pour normaliser les champs saisis comme "300 kg/m³", "2400 kg/m³", "20°C", "3%"
    def _strip_suffix(value, suffixes):
        if not value:
            return ''
        v = str(value)
        for s in suffixes:
            v = v.replace(s, '')
        return v.strip()

    # Client & chantier
    client_obj = getattr(op.commande, 'client', None)
    chantier_obj = getattr(op.commande, 'chantier', None)

    # Quantités
    ordered_quantity = (op.commande.lignes.aggregate(total=Sum('quantite'))['total'] or 0) if hasattr(op.commande, 'lignes') else 0
    cumulative_quantity = OrdreProduction.objects.filter(commande=op.commande).aggregate(total=Sum('quantite_produire'))['total'] or 0

    # Contexte pour le template bon_livraison.html
    # Utiliser une URL absolue accessible par xhtml2pdf (HTTP) plutôt qu'un chemin fichier.
    logo_url = request.build_absolute_uri(static('images/sitrad_logo_real.png'))
    context = {
        'logo_url': logo_url,
        'bl': {
            'date': op.date_production,
            'number': op.numero_bon or f'OP-{op.id}',
            'site': getattr(chantier_obj, 'nom', '') or getattr(chantier_obj, 'adresse', ''),
            'command_number': op.commande.id,
            'ordered_quantity_m3': ordered_quantity,
            'cumulative_quantity_m3': cumulative_quantity,
            'notes': '',
        },
        'client': {
            'name': getattr(client_obj, 'nom', ''),
            'code': getattr(client_obj, 'id', ''),
        },
        'plant': {
            'name': 'SITRAD',
        },
        'concrete': {
            'volume_m3': op.quantite_produire,
            'code': op.formule.nom,
            'designation': op.formule.description or 'BÉTON',
            'resistance_class': op.formule.resistance_requise,
            'exposure_class': op.classe_exposition or '',
            'consistency': op.classe_consistance or '',
            'chloride_class': op.classe_teneur_chlorure or '',
            'dmax_mm': _strip_suffix(op.d_max, [' mm']) if op.d_max else '',
            'cement_type': op.ciment_type_classe or '',
            'additive_type': op.adjuvant_type or '',
            'ec_ratio': op.rapport_e_c or '',
            'air_content_percent': _strip_suffix(op.teneur_en_air, ['%']) if op.teneur_en_air else '',
            'density_kg_per_m3': _strip_suffix(op.masse_volumique, ['kg/m³', 'kg/m3']) if op.masse_volumique else '',
            'cement_content_kg_per_m3': _strip_suffix(op.teneur_en_ciment, ['kg/m³', 'kg/m3']) if op.teneur_en_ciment else '',
        },
        'quality': {
            'temperature_c': _strip_suffix(op.temperature_beton, ['°C']) if op.temperature_beton else '',
        },
        'transport': {
            'carrier': op.transporteur or '',
            'mixer_number': getattr(op.vehicule, 'immatriculation', ''),
            'driver': getattr(op.chauffeur, 'nom', ''),
            'services': op.pompe or '',
            'reference': op.numero_bon or f'OP-{op.id}',
            'first_time': '',
            'arrival_time': '',
            'start_time': op.heure_production.strftime('%H:%M') if op.heure_production else '',
            'end_time': '',
            'return_time': '',
        },
    }

    template = get_template('reports/bon_livraison.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="BL_{op.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    return response
    c.save()
    return resp
