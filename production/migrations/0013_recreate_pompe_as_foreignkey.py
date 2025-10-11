# Generated manually to recreate pompe field as ForeignKey
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0003_pompe'),
        ('production', '0012_map_pompe_data_to_temp_field'),
    ]

    operations = [
        # Supprimer l'ancien champ pompe (CharField)
        migrations.RemoveField(
            model_name='ordreproduction',
            name='pompe',
        ),
        # Créer le nouveau champ pompe (ForeignKey)
        migrations.AddField(
            model_name='ordreproduction',
            name='pompe',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='logistics.pompe'
            ),
        ),
    ]