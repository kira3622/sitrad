# Widget d'accès rapide aux rapports (context processor)

from .acces import codes_rapports_autorises


def quick_reports_widget(request):
    """Context processor : widget d'accès rapide et codes de rapports autorisés.

    Les entrées sans ``code`` (pages d'accueil des rapports) restent toujours
    visibles ; les rapports ne sont ajoutés que si l'utilisateur y a accès.
    """
    from django.urls import reverse

    codes_autorises = codes_rapports_autorises(getattr(request, 'user', None))

    # Rapports rapides disponibles
    quick_reports_tous = [
        {
            'code': None,
            'title': 'Accès Rapide',
            'icon': 'fas fa-bolt',
            'url': reverse('reports:acces_rapide'),
            'color': '#FF9800',
            'description': 'Tous les rapports'
        },
        {
            'code': 'production',
            'title': 'Production',
            'icon': 'fas fa-industry',
            'url': reverse('reports:production'),
            'color': '#4CAF50',
            'description': 'Rapports de production'
        },
        {
            'code': 'commandes',
            'title': 'Commandes',
            'icon': 'fas fa-clipboard-list',
            'url': reverse('reports:commandes'),
            'color': '#2196F3',
            'description': 'Rapports de commandes'
        },
        {
            'code': 'stock',
            'title': 'Stock',
            'icon': 'fas fa-boxes',
            'url': reverse('reports:stock'),
            'color': '#9C27B0',
            'description': 'Rapports de stock'
        },
        {
            'code': 'financier',
            'title': 'Financier',
            'icon': 'fas fa-euro-sign',
            'url': reverse('reports:financier'),
            'color': '#F44336',
            'description': 'Rapports financiers'
        },
        {
            'code': 'cout_formule',
            'title': 'Coût Formule',
            'icon': 'fas fa-calculator',
            'url': reverse('reports:cout_formule'),
            'color': '#795548',
            'description': 'Coût des formules béton'
        },
    ]

    quick_reports = [
        rapport for rapport in quick_reports_tous
        if rapport['code'] is None or rapport['code'] in codes_autorises
    ]

    return {
        'quick_reports': quick_reports,
        'has_quick_reports': bool(quick_reports),
        'codes_rapports': codes_autorises,
    }
