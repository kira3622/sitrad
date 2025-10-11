# Generated manually to fix data type conflict
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0008_alter_ordreproduction_pompe'),
    ]

    operations = [
        # Revenir temporairement au CharField pour éviter les erreurs de type
        migrations.AlterField(
            model_name='ordreproduction',
            name='pompe',
            field=models.CharField(
                blank=True, 
                choices=[
                    ('Aucune', 'Aucune'), 
                    ('Pompe mobile', 'Pompe mobile'), 
                    ('Pompe stationnaire', 'Pompe stationnaire'), 
                    ('Tremie', 'Trémie')
                ], 
                help_text='Pompe', 
                max_length=20, 
                null=True
            ),
        ),
    ]