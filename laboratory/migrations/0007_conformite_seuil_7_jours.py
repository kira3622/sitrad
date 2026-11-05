"""Recalcule la conformité des essais d'écrasement à 7 jours.

Le critère appliqué aux éprouvettes écrasées à 7 jours est désormais
une résistance ≥ 18 MPa (et non plus le fck contractuel, atteint seulement
à 28 jours).
"""
from decimal import Decimal

from django.db import migrations

SEUIL_7J_MPA = Decimal('18')

FCK_MAP = {
    'C16/20': 16,
    'C20/25': 20,
    'C25/30': 25,
    'C30/37': 30,
    'C35/45': 35,
    'C40/50': 40,
    'C45/55': 45,
    'C50/60': 50,
}


def appliquer_seuil_7_jours(apps, schema_editor):
    """Conformité à 7 jours = résistance ≥ 18 MPa."""
    EssaiEcrasement = apps.get_model('laboratory', 'EssaiEcrasement')
    essais = (
        EssaiEcrasement.objects
        .filter(eprouvette__age_jours=7, resistance_mpa__isnull=False)
        .select_related('eprouvette')
    )
    a_mettre_a_jour = []
    for essai in essais:
        conforme = essai.resistance_mpa >= SEUIL_7J_MPA
        if essai.conforme != conforme:
            essai.conforme = conforme
            a_mettre_a_jour.append(essai)
    if a_mettre_a_jour:
        EssaiEcrasement.objects.bulk_update(a_mettre_a_jour, ['conforme'])


def retour_fck(apps, schema_editor):
    """Retour arrière : conformité à 7 jours vis-à-vis du fck contractuel."""
    EssaiEcrasement = apps.get_model('laboratory', 'EssaiEcrasement')
    essais = (
        EssaiEcrasement.objects
        .filter(eprouvette__age_jours=7, resistance_mpa__isnull=False)
        .select_related('eprouvette__prelevement')
    )
    a_mettre_a_jour = []
    for essai in essais:
        fck = FCK_MAP.get(essai.eprouvette.prelevement.classe_resistance)
        if fck is None:
            continue
        conforme = essai.resistance_mpa >= Decimal(fck)
        if essai.conforme != conforme:
            essai.conforme = conforme
            a_mettre_a_jour.append(essai)
    if a_mettre_a_jour:
        EssaiEcrasement.objects.bulk_update(a_mettre_a_jour, ['conforme'])


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0006_essaiequivalentsable_fournisseur_and_more'),
    ]

    operations = [
        migrations.RunPython(appliquer_seuil_7_jours, retour_fck),
    ]
