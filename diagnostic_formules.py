#!/usr/bin/env python
"""
Script de diagnostic pour vérifier l'état des formules sur Render
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

def diagnostic_formules():
    print("=== DIAGNOSTIC FORMULES ===")
    
    # 1. Vérifier les imports
    print("\n1. Test des imports...")
    try:
        from formulas.models import FormuleBeton, CompositionFormule
        print("✅ Import des modèles FormuleBeton et CompositionFormule réussi")
    except Exception as e:
        print(f"❌ Erreur d'import des modèles: {e}")
        return
    
    try:
        from api.views import FormuleBetonViewSet
        print("✅ Import de FormuleBetonViewSet réussi")
    except Exception as e:
        print(f"❌ Erreur d'import de FormuleBetonViewSet: {e}")
        return
    
    try:
        from api.serializers import FormuleBetonSerializer
        print("✅ Import de FormuleBetonSerializer réussi")
    except Exception as e:
        print(f"❌ Erreur d'import de FormuleBetonSerializer: {e}")
        return
    
    # 2. Vérifier les tables en base
    print("\n2. Vérification des tables en base...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        
        # Vérifier si la table formulas_formulebeton existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='formulas_formulebeton';
        """)
        result = cursor.fetchone()
        
        if result:
            print("✅ Table formulas_formulebeton existe")
            
            # Compter les formules
            count = FormuleBeton.objects.count()
            print(f"✅ Nombre de formules en base: {count}")
            
            if count > 0:
                # Afficher quelques formules
                formules = FormuleBeton.objects.all()[:3]
                for formule in formules:
                    print(f"  - {formule.nom} ({formule.resistance_requise})")
        else:
            print("❌ Table formulas_formulebeton n'existe pas")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la base: {e}")
    
    # 3. Vérifier l'enregistrement dans le routeur
    print("\n3. Vérification du routeur API...")
    try:
        from api.urls import router
        
        # Lister toutes les routes enregistrées
        routes = []
        for pattern in router.urls:
            if hasattr(pattern, 'pattern') and hasattr(pattern.pattern, '_route'):
                routes.append(pattern.pattern._route)
        
        formules_routes = [r for r in routes if 'formules' in r]
        
        if formules_routes:
            print("✅ Routes formules trouvées:")
            for route in formules_routes:
                print(f"  - {route}")
        else:
            print("❌ Aucune route formules trouvée")
            print("Routes disponibles:")
            for route in routes[:10]:  # Afficher les 10 premières
                print(f"  - {route}")
                
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du routeur: {e}")
    
    # 4. Test du ViewSet
    print("\n4. Test du ViewSet...")
    try:
        viewset = FormuleBetonViewSet()
        queryset = viewset.get_queryset()
        print(f"✅ ViewSet accessible, queryset count: {queryset.count()}")
    except Exception as e:
        print(f"❌ Erreur du ViewSet: {e}")
    
    print("\n=== FIN DIAGNOSTIC ===")

if __name__ == "__main__":
    diagnostic_formules()