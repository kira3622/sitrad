from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuration du router pour l'API REST
router = DefaultRouter()
router.register(r'categories', views.CategorieCoûtViewSet)
router.register(r'couts-matieres', views.CoûtMatierePremierViewSet)
router.register(r'couts-main-oeuvre', views.CoûtMainOeuvreViewSet)
router.register(r'couts-frais-generaux', views.CoûtFraisGenerauxViewSet)
router.register(r'calculs', views.CalculCoûtRevientViewSet)

app_name = 'cost_calculation'

urlpatterns = [
    # Vues principales
    path('', views.dashboard_coûts, name='dashboard'),
    path('calculs/', views.liste_calculs_coûts, name='liste_calculs'),
    path('calculs/<int:calcul_id>/', views.detail_calcul_coût, name='detail_calcul'),
    path('calculs/nouveau/', views.nouveau_calcul_coût, name='nouveau_calcul'),
    
    # Gestion des coûts
    path('couts/matieres/', views.gestion_coûts_matieres, name='gestion_couts_matieres'),
    path('couts/main-oeuvre/', views.gestion_coûts_main_oeuvre, name='gestion_couts_main_oeuvre'),
    path('couts/frais-generaux/', views.gestion_frais_generaux, name='gestion_couts_frais_generaux'),
    
    # Export et rapports (à implémenter)
    # path('export/', views.export_calculs, name='export_calculs'),
    # path('rapports/', views.rapports, name='rapports'),
    
    # API REST
    path('api/', include(router.urls)),
    
    # API endpoints requis par le template
    path('api/simulate/', views.simulation_calcul, name='api_simulation'),
    path('api/commandes/', views.api_commandes, name='api_commandes'),
    path('api/ordres-production/', views.api_ordres_production, name='api_ordres_production'),
    path('api/formules/<int:formule_id>/composition/', views.api_formule_composition, name='api_formule_composition'),
    path('api/default-costs/', views.default_costs, name='api_default_costs'),
]