from django.shortcuts import render, get_object_or_404
from .models import Facture
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from num2words import num2words

def facture_pdf(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    total_en_lettres = num2words(facture.montant_total, lang='fr')
    template_path = 'billing/facture_pdf.html'
    context = {
        'facture': facture,
        'total_en_lettres': total_en_lettres
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.id}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
