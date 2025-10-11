# Generated manually to transfer data from temp field to ForeignKey
from django.db import migrations


def transfer_temp_data_to_foreignkey(apps, schema_editor):
    """
    Transférer les données du champ pompe_temp_id vers le nouveau champ pompe (ForeignKey)
    """
    OrdreProduction = apps.get_model('production', 'OrdreProduction')
    Pompe = apps.get_model('logistics', 'Pompe')
    
    updated_count = 0
    error_count = 0
    
    for ordre in OrdreProduction.objects.all():
        if ordre.pompe_temp_id:
            try:
                pompe_obj = Pompe.objects.get(id=ordre.pompe_temp_id)
                ordre.pompe = pompe_obj
                ordre.save(update_fields=['pompe'])
                updated_count += 1
            except Pompe.DoesNotExist:
                print(f"ERREUR: Pompe avec ID {ordre.pompe_temp_id} non trouvée pour ordre {ordre.id}")
                error_count += 1
        else:
            # pompe_temp_id est None, donc pompe reste None
            ordre.pompe = None
            ordre.save(update_fields=['pompe'])
            updated_count += 1
    
    print(f"Transfert terminé. {updated_count} ordres mis à jour, {error_count} erreurs.")


def reverse_transfer_temp_data_to_foreignkey(apps, schema_editor):
    """
    Annuler le transfert (vider le champ pompe ForeignKey)
    """
    OrdreProduction = apps.get_model('production', 'OrdreProduction')
    OrdreProduction.objects.update(pompe=None)


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0013_recreate_pompe_as_foreignkey'),
    ]

    operations = [
        migrations.RunPython(
            transfer_temp_data_to_foreignkey,
            reverse_transfer_temp_data_to_foreignkey
        ),
    ]