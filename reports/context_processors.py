# Widget d'accès rapide aux rapports (context processor)

def quick_reports_widget(request):
    """Context processor pour ajouter le widget d'accès rapide à toutes les pages"""
    from django.urls import reverse
    
    # Rapports rapides disponibles
    quick_reports = [
        {
            'title': 'Production',
            'icon': 'fas fa-industry',
            'url': reverse('reports:production'),
            'color': '#4CAF50',
            'description': 'Rapports de production'
        },
        {
            'title': 'Commandes',
            'icon': 'fas fa-clipboard-list',
            'url': reverse('reports:commandes'),
            'color': '#2196F3',
            'description': 'Rapports de commandes'
        },
        {
            'title': 'Stock',
            'icon': 'fas fa-boxes',
            'url': reverse('reports:stock'),
            'color': '#9C27B0',
            'description': 'Rapports de stock'
        },
        {
            'title': 'Financier',
            'icon': 'fas fa-euro-sign',
            'url': reverse('reports:financier'),
            'color': '#F44336',
            'description': 'Rapports financiers'
        },
        {
            'title': 'Coût Formule',
            'icon': 'fas fa-calculator',
            'url': reverse('reports:cout_formule'),
            'color': '#795548',
            'description': 'Coût des formules béton'
        },
        {
            'title': 'Accès Rapide',
            'icon': 'fas fa-bolt',
            'url': reverse('reports:acces_rapide'),
            'color': '#FF9800',
            'description': 'Tous les rapports'
        }
    ]
    
    return {
        'quick_reports': quick_reports,
        'has_quick_reports': True
    }