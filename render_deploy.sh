#!/bin/bash

# Script de déploiement pour Render avec diagnostic et migration forcée

echo "=== DÉPLOIEMENT RENDER - DIAGNOSTIC FORMULES ==="

# 1. Afficher les variables d'environnement importantes
echo "1. Variables d'environnement:"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..." # Afficher seulement le début pour la sécurité

# 2. Installer les dépendances
echo "2. Installation des dépendances..."
pip install -r requirements.txt

# 3. Collecter les fichiers statiques
echo "3. Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 4. Diagnostic avant migration
echo "4. Diagnostic avant migration..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

print('=== DIAGNOSTIC PRE-MIGRATION ===')
try:
    from formulas.models import FormuleBeton
    from api.views import FormuleBetonViewSet
    from api.serializers import FormuleBetonSerializer
    print('✅ Imports réussis')
except Exception as e:
    print(f'❌ Erreur import: {e}')

try:
    from api.urls import router
    registry = router.registry
    formules_registered = any('formules' in str(item) for item in registry)
    print(f'✅ Formules dans registry: {formules_registered}')
    print(f'Registry: {[item[0] for item in registry]}')
except Exception as e:
    print(f'❌ Erreur registry: {e}')
"

# 5. Afficher l'état des migrations
echo "5. État des migrations..."
python manage.py showmigrations

# 6. Créer les migrations si nécessaire
echo "6. Création des migrations..."
python manage.py makemigrations

# 7. Appliquer les migrations
echo "7. Application des migrations..."
python manage.py migrate

# 8. Diagnostic après migration
echo "8. Diagnostic après migration..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

print('=== DIAGNOSTIC POST-MIGRATION ===')
try:
    from formulas.models import FormuleBeton
    count = FormuleBeton.objects.count()
    print(f'✅ FormuleBeton accessible: {count} objets')
    
    # Test du ViewSet
    from api.views import FormuleBetonViewSet
    viewset = FormuleBetonViewSet()
    queryset = viewset.get_queryset()
    print(f'✅ ViewSet accessible: {queryset.count()} objets')
    
    # Test des routes
    from api.urls import router
    from django.urls import reverse
    print('✅ Routes disponibles:')
    for prefix, viewset_class, basename in router.registry:
        print(f'  - {prefix} -> {basename}')
        
except Exception as e:
    print(f'❌ Erreur diagnostic: {e}')
"

# 9. Test final de l'API
echo "9. Test final de l'API..."
python manage.py shell -c "
from django.test import Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Créer un utilisateur de test si nécessaire
user, created = User.objects.get_or_create(username='test_api', defaults={'email': 'test@example.com'})
if created:
    user.set_password('testpass123')
    user.save()

# Générer un token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

# Tester l'endpoint
client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

try:
    response = client.get('/api/v1/')
    print(f'✅ Index API accessible: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if 'formules' in str(data):
            print('✅ Endpoint formules trouvé dans l\\'index')
        else:
            print('❌ Endpoint formules absent de l\\'index')
            print(f'Endpoints disponibles: {list(data.keys()) if isinstance(data, dict) else data}')
    
    # Test direct de l'endpoint formules
    response = client.get('/api/v1/formules/')
    print(f'✅ Endpoint formules direct: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Données formules: {len(data.get(\"results\", data))} éléments')
    
except Exception as e:
    print(f'❌ Erreur test API: {e}')
"

echo "=== FIN DÉPLOIEMENT RENDER ==="