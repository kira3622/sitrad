# Generated manually to create Pompe objects and migrate data
from django.db import migrations


def create_pompes_and_migrate_data(apps, schema_editor):
    """
    Créer les objets Pompe correspondant aux anciennes valeurs CharField
    et préparer la migration des données
    """
    OrdreProduction = apps.get_model('production', 'OrdreProduction')
    Pompe = apps.get_model('logistics', 'Pompe')
    
    # Mapping des anciennes valeurs vers les nouvelles pompes
    pompe_mapping = {
        'Aucune': None,  # Pas de pompe
        'Pompe mobile': {
            'nom': 'Pompe Mobile Standard',
            'numero_serie': 'PM-001',
            'marque': 'Standard',
            'modele': 'Mobile-001',
            'debit_max': 50.0,
            'portee_max': 100.0,
            'hauteur_max': 30.0,
            'statut': 'disponible',
            'date_acquisition': '2024-01-01'
        },
        'Pompe stationnaire': {
            'nom': 'Pompe Stationnaire Standard',
            'numero_serie': 'PS-001',
            'marque': 'Standard',
            'modele': 'Stat-001',
            'debit_max': 80.0,
            'portee_max': 150.0,
            'hauteur_max': 50.0,
            'statut': 'disponible',
            'date_acquisition': '2024-01-01'
        },
        'Tremie': {
            'nom': 'Trémie Standard',
            'numero_serie': 'TR-001',
            'marque': 'Standard',
            'modele': 'Tremie-001',
            'debit_max': 30.0,
            'portee_max': 50.0,
            'hauteur_max': 20.0,
            'statut': 'disponible',
            'date_acquisition': '2024-01-01'
        }
    }
    
    # Créer les objets Pompe s'ils n'existent pas déjà
    created_pompes = {}
    
    for old_value, pompe_data in pompe_mapping.items():
        if pompe_data is None:
            created_pompes[old_value] = None
            continue
            
        # Vérifier si la pompe existe déjà
        existing_pompe = Pompe.objects.filter(nom=pompe_data['nom']).first()
        if existing_pompe:
            created_pompes[old_value] = existing_pompe
        else:
            # Créer la nouvelle pompe
            new_pompe = Pompe.objects.create(**pompe_data)
            created_pompes[old_value] = new_pompe
            print(f"Créé pompe: {new_pompe.nom}")
    
    # Stocker les mappings dans un champ temporaire pour la prochaine migration
    # (nous ne pouvons pas modifier le champ pompe maintenant car il est encore CharField)
    for ordre in OrdreProduction.objects.all():
        if ordre.pompe in created_pompes:
            # Stocker l'ID de la pompe dans un attribut temporaire
            # Nous utiliserons cela dans la prochaine migration
            if hasattr(ordre, '_pompe_temp_id'):
                continue  # Déjà traité
            
            pompe_obj = created_pompes[ordre.pompe]
            if pompe_obj:
                # Nous stockerons l'ID dans un champ temporaire dans la prochaine migration
                pass
    
    print(f"Migration des données terminée. Pompes créées: {len([p for p in created_pompes.values() if p is not None])}")


def reverse_create_pompes_and_migrate_data(apps, schema_editor):
    """
    Annuler la création des pompes (optionnel)
    """
    Pompe = apps.get_model('logistics', 'Pompe')
    
    # Supprimer les pompes créées par cette migration
    pompe_names = [
        'Pompe Mobile Standard',
        'Pompe Stationnaire Standard', 
        'Trémie Standard'
    ]
    
    for name in pompe_names:
        Pompe.objects.filter(nom=name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0009_revert_pompe_to_charfield'),
        ('logistics', '0003_pompe'),  # S'assurer que le modèle Pompe existe
    ]

    operations = [
        migrations.RunPython(
            create_pompes_and_migrate_data,
            reverse_create_pompes_and_migrate_data
        ),
    ]