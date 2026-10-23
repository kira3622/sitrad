from django.urls import path

from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('prelevement/<int:pk>/', views.prelevement_detail, name='prelevement_detail'),
    path('prelevement/<int:pk>/pv.pdf', views.pv_pdf, name='pv_pdf'),
    path('json/resistance/', views.json_resistance, name='json_resistance'),
]
