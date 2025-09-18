from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    # Calcul automatique des sorties de matières
    path('ordre/<int:ordre_id>/calculer-sorties/', views.calculer_sorties_ordre, name='calculer_sorties_ordre'),
    path('ordre/<int:ordre_id>/preview-sorties/', views.preview_sorties_ordre, name='preview_sorties_ordre'),
    path('calculer-sorties-batch/', views.calculer_sorties_batch, name='calculer_sorties_batch'),
]