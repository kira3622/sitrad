from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chauffeur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('telephone', models.CharField(max_length=20, blank=True)),
                ('numero_permis', models.CharField(max_length=50, blank=True)),
                ('actif', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='vehicule',
            name='chauffeur',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehicules', to='logistics.chauffeur'),
        ),
    ]