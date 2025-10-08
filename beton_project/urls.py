"""
URL configuration for beton_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from production.views import delivery_note_pdf

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
    # Route explicite pour le PDF Bon de Livraison (assure la disponibilité en production)
    path('production/orders/<int:pk>/delivery-note.pdf', delivery_note_pdf, name='delivery_note_pdf'),
    
    # Applications web
    path('activity/', include('activity.urls')),
    path('reports/', include('reports.urls')),
    path('billing/', include('billing.urls')),
    path('production/', include('production.urls')),
    path('fuel/', include('fuel_management.urls')),
    
    # API REST
    path('api/v1/', include('api.urls')),
    
    # Interface de navigation de l'API (pour le développement)
    path('api-auth/', include('rest_framework.urls')),
]
