# Generated manually to force table creation on Render
from django.db import migrations, models, connection
import django.db.models.deletion


def create_table_if_not_exists(apps, schema_editor):
    """Create the table if it doesn't exist, compatible with both SQLite and PostgreSQL"""
    with connection.cursor() as cursor:
        # Check if table exists
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'stock_mouvementstock'
                );
            """)
        else:  # SQLite
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='stock_mouvementstock';
            """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists or (connection.vendor == 'postgresql' and not table_exists[0]):
            # Create the table using Django's model creation
            MouvementStock = apps.get_model('stock', 'MouvementStock')
            schema_editor.create_model(MouvementStock)


def reverse_create_table(apps, schema_editor):
    """Drop the table"""
    MouvementStock = apps.get_model('stock', 'MouvementStock')
    schema_editor.delete_model(MouvementStock)


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_table_if_not_exists, reverse_create_table),
    ]