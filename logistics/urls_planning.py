from django.urls import path

from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.planning_livraisons, name='livraisons'),
    path('planifier/<int:commande_id>/', views.planifier_livraison, name='planifier'),
]
