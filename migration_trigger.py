# Migration Trigger - 2025-10-11T11:20:33.244862
# Ce fichier force l'exécution des migrations lors du déploiement

FORCE_MIGRATION = True
MIGRATION_TIMESTAMP = "2025-10-11T11:20:33.244862"

# Commandes à exécuter:
# 1. python manage.py makemigrations production --name add_pompes_fields
# 2. python manage.py migrate --noinput
# 3. python manage.py collectstatic --noinput
