from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from xhtml2pdf import pisa
from num2words import num2words
import logging
from .models import Facture

logger = logging.getLogger(__name__)

@login_required
def facture_pdf(request, facture_id):
    """Génère et retourne une facture en PDF"""
    try:
        facture = get_object_or_404(Facture, id=facture_id)
        
        # Vérifier que la facture a des lignes
        if not facture.lignes.exists():
            messages.error(request, "Cette facture n'a pas de lignes de détail.")
            raise Http404("Facture sans lignes de détail")
        
        # Convertir le montant total en lettres
        try:
            total_en_lettres = num2words(float(facture.montant_total), lang='fr')
            total_en_lettres = total_en_lettres.capitalize() + " dirhams"
        except Exception as e:
            logger.warning(f"Erreur conversion en lettres pour facture {facture_id}: {e}")
            total_en_lettres = "Montant non disponible"
        
        # Préparer le contexte pour le template
        context = {
            'facture': facture,
            'total_en_lettres': total_en_lettres,
            'date_generation': timezone.now(),
            'lignes': facture.lignes.all().order_by('ordre', 'id'),
        }
        
        # Charger le template
        template_path = 'billing/facture_pdf.html'
        template = get_template(template_path)
        html = template.render(context)
        
        # Créer la réponse PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{facture.get_numero_facture()}.pdf"'
        
        # Générer le PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        # Vérifier les erreurs
        if pisa_status.err:
            logger.error(f"Erreur génération PDF facture {facture_id}: {pisa_status.err}")
            return HttpResponse(
                f'<h1>Erreur de génération PDF</h1><pre>{html}</pre>',
                status=500
            )
        
        # Log de l'action
        logger.info(f"PDF généré avec succès pour facture {facture_id} par utilisateur {request.user}")
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur inattendue génération PDF facture {facture_id}: {e}")
        return HttpResponse(
            '<h1>Erreur</h1><p>Une erreur est survenue lors de la génération du PDF.</p>',
            status=500
        )

@login_required
def facture_preview(request, facture_id):
    """Affiche un aperçu HTML de la facture avant génération PDF"""
    facture = get_object_or_404(Facture, id=facture_id)
    
    try:
        total_en_lettres = num2words(float(facture.montant_total), lang='fr')
        total_en_lettres = total_en_lettres.capitalize() + " dirhams"
    except:
        total_en_lettres = "Montant non disponible"
    
    context = {
        'facture': facture,
        'total_en_lettres': total_en_lettres,
        'date_generation': timezone.now(),
        'lignes': facture.lignes.all().order_by('ordre', 'id'),
        'preview_mode': True,
    }
    
    return render(request, 'billing/facture_pdf.html', context)

@login_required
def liste_factures(request):
    """Liste toutes les factures"""
    factures = Facture.objects.select_related('commande').order_by('-date_facturation')
    
    # Filtrage par statut si demandé
    statut = request.GET.get('statut')
    if statut and statut in dict(Facture.STATUT_CHOICES):
        factures = factures.filter(statut=statut)
    
    context = {
        'factures': factures,
        'statuts': Facture.STATUT_CHOICES,
        'statut_filtre': statut,
    }
    
    return render(request, 'billing/liste_factures.html', context)
