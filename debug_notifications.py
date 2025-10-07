#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier la configuration des notifications
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

def debug_notifications():
    """Diagnostic complet de l'application notifications"""
    
    print("=== DIAGNOSTIC NOTIFICATIONS ===\n")
    
    # 1. Vérifier les settings
    print("1. Vérification des settings...")
    from django.conf import settings
    
    if 'notifications' in settings.INSTALLED_APPS:
        print("   ✓ 'notifications' est dans INSTALLED_APPS")
    else:
        print("   ✗ 'notifications' n'est PAS dans INSTALLED_APPS")
        return False
    
    # 2. Vérifier l'importation des modèles
    print("\n2. Vérification des modèles...")
    try:
        from notifications.models import Notification
        print("   ✓ Modèle Notification importé avec succès")
        print(f"   ✓ Champs du modèle: {[f.name for f in Notification._meta.fields]}")
    except Exception as e:
        print(f"   ✗ Erreur d'importation du modèle: {e}")
        return False
    
    # 3. Vérifier les vues
    print("\n3. Vérification des vues...")
    try:
        from notifications.views import NotificationViewSet
        print("   ✓ NotificationViewSet importé avec succès")
    except Exception as e:
        print(f"   ✗ Erreur d'importation des vues: {e}")
        return False
    
    # 4. Vérifier les sérialiseurs
    print("\n4. Vérification des sérialiseurs...")
    try:
        from notifications.serializers import NotificationSerializer
        print("   ✓ NotificationSerializer importé avec succès")
    except Exception as e:
        print(f"   ✗ Erreur d'importation des sérialiseurs: {e}")
        return False
    
    # 5. Vérifier les URLs
    print("\n5. Vérification des URLs...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        # Tester la résolution des URLs
        client = Client()
        
        # Test de l'URL de base des notifications
        try:
            response = client.get('/api/v1/notifications/')
            print(f"   ✓ URL /api/v1/notifications/ résolue (status: {response.status_code})")
        except Exception as e:
            print(f"   ✗ Erreur de résolution URL: {e}")
            return False
            
    except Exception as e:
        print(f"   ✗ Erreur de test des URLs: {e}")
        return False
    
    # 6. Vérifier la base de données
    print("\n6. Vérification de la base de données...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%notification%';")
            tables = cursor.fetchall()
            if tables:
                print(f"   ✓ Tables notifications trouvées: {[t[0] for t in tables]}")
            else:
                print("   ⚠️ Aucune table notification trouvée")
    except Exception as e:
        print(f"   ✗ Erreur de vérification BDD: {e}")
    
    # 7. Test de création d'une notification
    print("\n7. Test de création d'une notification...")
    try:
        from django.contrib.auth.models import User
        
        # Créer un utilisateur de test s'il n'existe pas
        user, created = User.objects.get_or_create(
            username='test_notifications',
            defaults={'email': 'test@example.com'}
        )
        
        # Créer une notification de test
        notification = Notification.objects.create(
            user=user,
            title="Test de diagnostic",
            message="Notification créée lors du diagnostic",
            type="info"
        )
        
        print(f"   ✓ Notification créée avec succès (ID: {notification.id})")
        
        # Nettoyer
        notification.delete()
        if created:
            user.delete()
            
    except Exception as e:
        print(f"   ✗ Erreur de création de notification: {e}")
        return False
    
    print("\n✅ DIAGNOSTIC NOTIFICATIONS RÉUSSI")
    return True

if __name__ == "__main__":
    success = debug_notifications()
    sys.exit(0 if success else 1)