# Generated manually to remove temporary pompe_temp_id field
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0014_transfer_temp_data_to_foreignkey'),
    ]

    operations = [
        # Supprimer le champ temporaire
        migrations.RemoveField(
            model_name='ordreproduction',
            name='pompe_temp_id',
        ),
    ]