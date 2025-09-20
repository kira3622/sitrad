from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.liste_factures, name='liste_factures'),
    path('<int:facture_id>/pdf/', views.facture_pdf, name='facture_pdf'),
    path('<int:facture_id>/preview/', views.facture_preview, name='facture_preview'),
]