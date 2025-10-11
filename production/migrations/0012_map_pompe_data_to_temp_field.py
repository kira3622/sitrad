# Generated manually to map pompe data to temporary field
from django.db import migrations


def map_pompe_data_to_temp_field(apps, schema_editor):
    """
    Mapper les données du champ pompe (CharField) vers pompe_temp_id (BigIntegerField)
    """
    OrdreProduction = apps.get_model('production', 'OrdreProduction')
    Pompe = apps.get_model('logistics', 'Pompe')
    
    # Mapping des anciennes valeurs vers les noms des pompes
    pompe_name_mapping = {
        'Aucune': None,
        'Pompe mobile': 'Pompe Mobile Standard',
        'Pompe stationnaire': 'Pompe Stationnaire Standard',
        'Tremie': 'Trémie Standard'
    }
    
    # Récupérer les pompes créées
    pompe_objects = {}
    for old_value, pompe_name in pompe_name_mapping.items():
        if pompe_name is None:
            pompe_objects[old_value] = None
        else:
            try:
                pompe_obj = Pompe.objects.get(nom=pompe_name)
                pompe_objects[old_value] = pompe_obj
                print(f"Trouvé pompe: {pompe_name} (ID: {pompe_obj.id})")
            except Pompe.DoesNotExist:
                print(f"ERREUR: Pompe non trouvée: {pompe_name}")
                pompe_objects[old_value] = None
    
    # Mapper les données
    updated_count = 0
    for ordre in OrdreProduction.objects.all():
        if ordre.pompe in pompe_objects:
            pompe_obj = pompe_objects[ordre.pompe]
            if pompe_obj:
                ordre.pompe_temp_id = pompe_obj.id
            else:
                ordre.pompe_temp_id = None
            ordre.save(update_fields=['pompe_temp_id'])
            updated_count += 1
        else:
            print(f"ATTENTION: Valeur pompe inconnue: '{ordre.pompe}' pour ordre {ordre.id}")
    
    print(f"Mapping terminé. {updated_count} ordres mis à jour.")


def reverse_map_pompe_data_to_temp_field(apps, schema_editor):
    """
    Annuler le mapping (vider le champ temporaire)
    """
    OrdreProduction = apps.get_model('production', 'OrdreProduction')
    OrdreProduction.objects.update(pompe_temp_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0011_add_temp_pompe_id'),
    ]

    operations = [
        migrations.RunPython(
            map_pompe_data_to_temp_field,
            reverse_map_pompe_data_to_temp_field
        ),
    ]