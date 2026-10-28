from django.db import migrations

# Ajout du rapport de laboratoire au catalogue des rapports autorisables.
CATALOGUE = [
    # code, titre, catégorie, nom d'URL, ordre
    ('laboratoire', 'Rapport de Laboratoire', 'Laboratoire', 'reports:laboratoire', 150),
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
        ('reports', '0007_alter_accesrapport_options'),
    ]

    operations = [
        migrations.RunPython(creer_catalogue, supprimer_catalogue),
    ]
