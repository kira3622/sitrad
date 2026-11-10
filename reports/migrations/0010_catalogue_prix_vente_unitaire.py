"""Ajout du rapport « Prix de Vente Unitaire » au catalogue des rapports autorisables.

Le rapport est ensuite cochable utilisateur par utilisateur (inline « Accès aux
rapports ») et sa consultation est strictement réservée aux utilisateurs autorisés.
"""
from django.db import migrations

CATALOGUE = [
    # code, titre, categorie, url_name, ordre
    ('prix_vente_unitaire', 'Prix de Vente Unitaire (Ordres de Production)',
     'Commercial', 'reports:prix_vente_unitaire', 145),
]


def creer_catalogue(apps, schema_editor):
    AccesRapport = apps.get_model('reports', 'AccesRapport')
    for code, titre, categorie, url_name, ordre in CATALOGUE:
        AccesRapport.objects.update_or_create(
            code=code,
            defaults={
                'titre': titre,
                'categorie': categorie,
                'url_name': url_name,
                'ordre': ordre,
                'actif': True,
            },
        )


def supprimer_catalogue(apps, schema_editor):
    AccesRapport = apps.get_model('reports', 'AccesRapport')
    AccesRapport.objects.filter(code__in=[ligne[0] for ligne in CATALOGUE]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_alter_accesrapport_options'),
    ]

    operations = [
        migrations.RunPython(creer_catalogue, supprimer_catalogue),
    ]
