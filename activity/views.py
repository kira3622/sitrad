from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import ActivityLog


@login_required
def recent_activities(request):
    """
    Vue pour afficher les activités récentes de tous les utilisateurs
    """
    # Filtres
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    days_filter = request.GET.get('days', '7')
    
    # Requête de base
    activities = ActivityLog.objects.select_related('user', 'content_type')
    
    # Filtrage par période
    try:
        days = int(days_filter)
        if days > 0:
            start_date = timezone.now() - timedelta(days=days)
            activities = activities.filter(timestamp__gte=start_date)
    except ValueError:
        days = 7
        start_date = timezone.now() - timedelta(days=7)
        activities = activities.filter(timestamp__gte=start_date)
    
    # Filtrage par action
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    # Filtrage par utilisateur
    if user_filter:
        activities = activities.filter(
            Q(user__username__icontains=user_filter) |
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter)
        )
    
    # Pagination
    paginator = Paginator(activities, 50)  # 50 activités par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total_activities': activities.count(),
        'unique_users': activities.values('user').distinct().count(),
        'actions_breakdown': {}
    }
    
    # Répartition par type d'action
    for action, label in ActivityLog.ACTION_CHOICES:
        count = activities.filter(action=action).count()
        if count > 0:
            stats['actions_breakdown'][label] = count
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'days_filter': days_filter,
        'action_choices': ActivityLog.ACTION_CHOICES,
    }
    
    return render(request, 'activity/recent_activities.html', context)


@login_required
def activity_api(request):
    """
    API JSON pour récupérer les activités récentes
    Utilisée pour les widgets et les mises à jour en temps réel
    """
    limit = int(request.GET.get('limit', 10))
    action_filter = request.GET.get('action', '')
    
    activities = ActivityLog.objects.select_related('user', 'content_type')
    
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    activities = activities[:limit]
    
    data = []
    for activity in activities:
        data.append({
            'id': activity.id,
            'user': {
                'username': activity.user.username,
                'full_name': activity.user.get_full_name() or activity.user.username
            },
            'action': {
                'code': activity.action,
                'label': activity.get_action_display()
            },
            'timestamp': activity.timestamp.isoformat(),
            'description': activity.description,
            'object_name': activity.get_object_name(),
            'model_name': activity.get_model_name(),
            'app_name': activity.get_app_name(),
        })
    
    return JsonResponse({
        'activities': data,
        'count': len(data)
    })


@login_required
def activity_widget(request):
    """
    Vue pour le widget des activités récentes
    À intégrer dans l'interface d'administration
    """
    recent_activities = ActivityLog.objects.select_related(
        'user', 'content_type'
    )[:10]
    
    context = {
        'recent_activities': recent_activities
    }
    
    return render(request, 'activity/widget.html', context)
