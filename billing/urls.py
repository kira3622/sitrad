from django.urls import path
from . import views

urlpatterns = [
    path('<int:facture_id>/pdf/', views.facture_pdf, name='facture_pdf'),
]