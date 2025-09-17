from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_reports, name='dashboard'),
    
    # Rapports spécialisés
    path('production/', views.rapport_production, name='production'),
    path('commandes/', views.rapport_commandes, name='commandes'),
    path('commercial/', views.rapport_commercial, name='commercial'),
    path('stock/', views.rapport_stock, name='stock'),
    path('financier/', views.rapport_financier, name='financier'),
    
    # Export PDF
    path('export/<str:type_rapport>/', views.export_rapport_pdf, name='export_pdf'),
]