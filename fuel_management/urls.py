from django.urls import path
from . import views

app_name = 'fuel_management'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_fuel, name='dashboard'),
    
    # Gestion du stock
    path('stock/', views.stock_detail, name='stock_detail'),
    
    # Rapports
    path('rapports/consommation/', views.rapport_consommation_engin, name='rapport_consommation'),
    path('rapports/approvisionnement/', views.rapport_approvisionnement, name='rapport_approvisionnement'),
    path('rapports/bilan-mensuel/', views.rapport_bilan_mensuel, name='rapport_bilan_mensuel'),
    
    # Actions
    path('alertes/<int:alerte_id>/marquer-lue/', views.marquer_alerte_lue, name='marquer_alerte_lue'),
    
    # API
    path('api/stock-status/', views.api_stock_status, name='api_stock_status'),
]