from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('commercial/', views.commercial_dashboard, name='commercial_dashboard'),
]