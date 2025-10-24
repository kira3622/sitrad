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
    path('mouvements-par-jour/', views.rapport_mouvements_par_jour, name='mouvements_par_jour'),
    path('financier/', views.rapport_financier, name='financier'),
    path('ratios-m3/', views.rapport_ratios_m3, name='ratios_m3'),
    path('clients-journalier/', views.rapport_journalier_clients, name='clients_journalier'),
    path('vehicules-journalier/', views.rapport_journalier_vehicules, name='vehicules_journalier'),
    
    # Export PDF
    path('export/<str:type_rapport>/', views.export_rapport_pdf, name='export_pdf'),
]