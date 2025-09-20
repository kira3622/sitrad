from django.utils import timezone
from datetime import timedelta
from .models import ActivityLog


def recent_activities(request):
    """
    Context processor pour injecter les activités récentes dans tous les templates
    """
    if request.user.is_authenticated and request.user.is_staff:
        # Récupérer les 10 dernières activités des 24 dernières heures
        yesterday = timezone.now() - timedelta(days=1)
        activities = ActivityLog.objects.filter(
            timestamp__gte=yesterday
        ).select_related('user').order_by('-timestamp')[:10]
        
        return {
            'recent_activities': activities
        }
    
    return {
        'recent_activities': []
    }