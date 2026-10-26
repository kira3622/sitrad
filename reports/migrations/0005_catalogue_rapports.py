from django.db import migrations

# Catalogue des rapports pouvant être autorisés utilisateur par utilisateur.
# Le code sert de clé de contrôle d'accès dans les vues et les templates.
CATALOGUE = [
    # code, titre, catégorie, nom d'URL, ordre
    ('production', 'Rapport de Production', 'Production', 'reports:production', 10),
    ('commandes', 'Rapport de Commandes', 'Commercial', 'reports:commandes', 20),
    ('commercial', 'Rapport Commercial', 'Commercial', 'reports:commercial', 30),
    ('rapport_client', 'Rapport Client', 'Commercial', 'reports:rapport_client', 40),
    ('stock', 'Rapport de Stock', 'Logistique', 'reports:stock', 50),
    ('mouvements_par_jour', 'Mouvements par jour', 'Logistique', 'reports:mouvements_par_jour', 60),
    ('rapport_camion', 'Rapport Camion', 'Logistique', 'reports:rapport_camion', 70),
    ('consommation_matieres', 'Consommation Matières Premières', 'Stock', 'reports:consommation_matieres', 80),
    ('entrees_matieres', 'Entrées Agrégats', 'Stock', 'reports:entrees_matieres', 90),
    ('financier', 'Rapport Financier', 'Finance', 'reports:financier', 100),
    ('ratios_m3', 'Ratios matières par m³', 'Analyse', 'reports:ratios_m3', 110),
    ('cout_formule', 'Coût de Formule Béton', 'Analyse', 'reports:cout_formule', 120),
    ('clients_journalier', 'Journalier Clients', 'Journalier', 'reports:clients_journalier', 130),
    ('vehicules_journalier', 'Journalier Véhicules', 'Journalier', 'reports:vehicules_journalier', 140),
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
        ('reports', '0004_accesrapport_profilrapports'),
    ]

    operations = [
        migrations.RunPython(creer_catalogue, supprimer_catalogue),
    ]
