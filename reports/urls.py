from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_reports, name='dashboard'),
    path('acces-rapide/', views.acces_rapide_reports, name='acces_rapide'),
    
    # Rapports spécialisés
    path('production/', views.rapport_production, name='production'),
    path('commandes/', views.rapport_commandes, name='commandes'),
    path('commercial/', views.rapport_commercial, name='commercial'),
    path('stock/', views.rapport_stock, name='stock'),
    path('consommation-matieres/', views.rapport_consommation_matieres, name='consommation_matieres'),
    path('mouvements-par-jour/', views.rapport_mouvements_par_jour, name='mouvements_par_jour'),
    path('financier/', views.rapport_financier, name='financier'),
    path('ratios-m3/', views.rapport_ratios_m3, name='ratios_m3'),
    path('clients-journalier/', views.rapport_journalier_clients, name='clients_journalier'),
    path('vehicules-journalier/', views.rapport_journalier_vehicules, name='vehicules_journalier'),
    path('cout-formule/', views.rapport_cout_formule, name='cout_formule'),
    
    # Endpoints JSON pour graphiques admin
    path('json/daily-production/', views.json_daily_production, name='json_daily_production'),
    path('json/daily-orders/', views.json_daily_orders, name='json_daily_orders'),
    path('json/daily-deliveries/', views.json_daily_deliveries, name='json_daily_deliveries'),
    
    # Export PDF
    path('export/<str:type_rapport>/', views.export_rapport_pdf, name='export_pdf'),
]