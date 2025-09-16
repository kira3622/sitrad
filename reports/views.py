from django.shortcuts import render, get_object_or_404
from .models import Rapport
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def report_list(request):
    reports = Rapport.objects.all()
    return render(request, 'reports/report_list.html', {'reports': reports})

def report_detail(request, pk):
    report = get_object_or_404(Rapport, pk=pk)
    return render(request, 'reports/report_detail.html', {'report': report})

def report_pdf(request, pk):
    report = get_object_or_404(Rapport, pk=pk)
    template_path = 'reports/report_pdf.html'
    context = {'report': report}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.nom}.pdf"'
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
