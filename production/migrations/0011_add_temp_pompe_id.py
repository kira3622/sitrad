# Generated manually to add temporary field for pompe ID mapping
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0010_create_pompes_and_migrate_data'),
    ]

    operations = [
        # Ajouter un champ temporaire pour stocker l'ID de la pompe
        migrations.AddField(
            model_name='ordreproduction',
            name='pompe_temp_id',
            field=models.BigIntegerField(blank=True, null=True, help_text='Temporary field for pompe ID mapping'),
        ),
    ]