#!/usr/bin/env python
"""
Test simple pour diagnostiquer le problème avec ChantierViewSet
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

print("=== TEST IMPORT CHANTIER ===")

try:
    print("1. Import du modèle Chantier...")
    from customers.models import Chantier
    print("✅ Modèle Chantier importé")
    
    print("2. Import du serializer...")
    from api.serializers import ChantierSerializer
    print("✅ ChantierSerializer importé")
    
    print("3. Import du ViewSet...")
    from api.views import ChantierViewSet
    print("✅ ChantierViewSet importé")
    
    print("4. Test du routeur...")
    from api.urls import router
    registry_names = [item[0] for item in router.registry]
    print(f"Routes enregistrées: {registry_names}")
    if 'chantiers' in registry_names:
        print("✅ ChantierViewSet enregistré dans le routeur")
    else:
        print("❌ ChantierViewSet non trouvé dans le routeur")
    
    print("5. Test de la base de données...")
    count = Chantier.objects.count()
    print(f"✅ {count} chantiers dans la base de données")
    
    print("6. Test du ViewSet...")
    viewset = ChantierViewSet()
    queryset = viewset.get_queryset()
    print(f"✅ ViewSet fonctionnel: {queryset.count()} objets")
    
    print("\n✅ TOUS LES TESTS SONT PASSÉS")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()