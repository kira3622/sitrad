from django.urls import path
from . import views

app_name = 'activity'

urlpatterns = [
    path('recent/', views.recent_activities, name='recent_activities'),
    path('api/', views.activity_api, name='activity_api'),
    path('widget/', views.activity_widget, name='activity_widget'),
]