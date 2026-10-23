from collections import OrderedDict

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa

from .models import (
    Prelevement, Eprouvette,
    EssaiGranulometrie, EssaiEquivalentSable, EssaiBleuMethylene, EssaiTeneurEnEau,
)


def _eprouvettes_en_attente():
    return Eprouvette.objects.filter(ecrasement__isnull=True).select_related(
        'prelevement', 'prelevement__ordre_production', 'prelevement__ordre_production__commande__client'
    )


def _courbe_resistance(eprouvettes):
    """Moyenne de résistance (MPa) par âge d'échéance, pour le graphique de montée en résistance."""
    data = OrderedDict()
    for ep in eprouvettes:
        ecrasement = getattr(ep, 'ecrasement', None)
        if not ecrasement or ecrasement.resistance_mpa is None:
            continue
        data.setdefault(ep.age_jours, []).append(float(ecrasement.resistance_mpa))
    ages = sorted(data.keys())
    return {
        'ages': [f"{a} j" for a in ages],
        'moyennes': [round(sum(data[a]) / len(data[a]), 2) for a in ages],
    }


@staff_member_required
def dashboard(request):
    """Tableau de bord laboratoire : alertes d'écrasement et suivi statistique."""
    aujourdhui = timezone.localdate()
    en_attente = _eprouvettes_en_attente()

    a_ecraser = en_attente.filter(date_echeance__date=aujourdhui).order_by('date_echeance')
    en_retard = en_attente.filter(date_echeance__date__lt=aujourdhui).order_by('date_echeance')
    a_venir = en_attente.filter(date_echeance__date__gt=aujourdhui).order_by('date_echeance')[:50]

    ecrasees = Eprouvette.objects.filter(ecrasement__isnull=False).select_related('ecrasement')
    non_conformes = ecrasees.filter(ecrasement__conforme=False).count()

    courbe = _courbe_resistance(ecrasees)

    context = {
        'title': "Suivi de laboratoire",
        'a_ecraser': a_ecraser,
        'en_retard': en_retard,
        'a_venir': a_venir,
        'nb_a_ecraser': a_ecraser.count(),
        'nb_en_retard': en_retard.count(),
        'nb_a_venir': en_attente.filter(date_echeance__date__gt=aujourdhui).count(),
        'nb_ecrasees': ecrasees.count(),
        'nb_non_conformes': non_conformes,
        'courbe': courbe,
        'nb_prelevements': Prelevement.objects.count(),
        'nb_granulometrie': EssaiGranulometrie.objects.count(),
        'nb_equiv_sable': EssaiEquivalentSable.objects.count(),
        'nb_bleu': EssaiBleuMethylene.objects.count(),
        'nb_teneur_eau': EssaiTeneurEnEau.objects.count(),
        'derniers_prelevements': Prelevement.objects.select_related(
            'ordre_production', 'ordre_production__commande__client'
        )[:15],
    }
    return render(request, 'laboratory/dashboard.html', context)


@staff_member_required
def prelevement_detail(request, pk):
    """Fiche de suivi d'un prélèvement : éprouvettes, écrasements et montée en résistance."""
    prelevement = get_object_or_404(
        Prelevement.objects.select_related('ordre_production', 'ordre_production__commande__client', 'ordre_production__formule'),
        pk=pk,
    )
    eprouvettes = list(prelevement.eprouvettes.select_related('ecrasement').order_by('age_jours'))
    courbe = _courbe_resistance(eprouvettes)

    context = {
        'title': f"Suivi laboratoire - {prelevement.numero_bl or prelevement.pk}",
        'prelevement': prelevement,
        'eprouvettes': eprouvettes,
        'courbe': courbe,
    }
    return render(request, 'laboratory/prelevement_detail.html', context)


@staff_member_required
def pv_pdf(request, pk):
    """Génère le PV d'essai / rapport de conformité PDF d'un prélèvement."""
    prelevement = get_object_or_404(
        Prelevement.objects.select_related('ordre_production', 'ordre_production__commande__client', 'ordre_production__commande__chantier'),
        pk=pk,
    )
    eprouvettes = prelevement.eprouvettes.select_related('ecrasement').order_by('age_jours')

    lignes = []
    for ep in eprouvettes:
        ec = getattr(ep, 'ecrasement', None)
        lignes.append({
            'code': ep.code or ep.id,
            'forme': ep.get_forme_display(),
            'age': ep.age_jours,
            'echeance': ep.date_echeance,
            'statut': ep.statut_label,
            'poids': ec.poids_kg if ec else None,
            'force': ec.force_rupture_kn if ec else None,
            'section': ec.surface_mm2 if ec else None,
            'resistance': ec.resistance_mpa if ec else None,
            'masse_vol': ec.masse_volumique_kg_m3 if ec else None,
            'rupture': ec.get_type_rupture_display() if ec else '',
            'conforme': ec.conforme if ec else None,
        })

    context = {
        'prelevement': prelevement,
        'lignes': lignes,
        'date_edition': timezone.now(),
        'fck': prelevement.fck_mpa,
    }
    template = get_template('laboratory/pv_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PV_{prelevement.numero_bl or prelevement.pk}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf-8')
    if pisa_status.err:
        return HttpResponse('<h1>Erreur de génération du PDF</h1>', status=500)
    return response


@staff_member_required
def json_resistance(request):
    """Données JSON de la montée en résistance (toutes éprouvettes écrasées)."""
    ecrasees = Eprouvette.objects.filter(ecrasement__isnull=False).select_related('ecrasement')
    return JsonResponse(_courbe_resistance(ecrasees))
