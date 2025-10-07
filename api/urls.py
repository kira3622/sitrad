from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views
from notifications.views import NotificationViewSet

# Configuration du router pour les ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'chantiers', views.ChantierViewSet)
router.register(r'commandes', views.CommandeViewSet)
router.register(r'production', views.OrdreProductionViewSet)
router.register(r'stock', views.MatierePremiereViewSet)
router.register(r'livraisons', views.LivraisonViewSet)
router.register(r'factures', views.FactureViewSet)
router.register(r'fournisseurs', views.FournisseurViewSet)
router.register(r'engins', views.EnginViewSet)
router.register(r'approvisionnements', views.ApprovisionnementViewSet)
router.register(r'stock-carburant', views.StockCarburantViewSet)
router.register(r'formules', views.FormuleBetonViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

app_name = 'api'

urlpatterns = [
    # Authentification JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints personnalisés
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/production-stats/', views.production_stats, name='production_stats'),
    path('commandes/recentes/', views.commandes_recentes, name='commandes_recentes'),
    path('production/en-cours/', views.production_en_cours, name='production_en_cours'),
    path('test-notifications/', views.test_notifications_endpoint, name='test_notifications'),
    
    # Routes automatiques des ViewSets (incluant notifications)
    path('', include(router.urls)),
]