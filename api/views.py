from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings

from customers.models import Client, Chantier
from orders.models import Commande
from production.models import OrdreProduction
from inventory.models import MatierePremiere
from logistics.models import Livraison
from billing.models import Facture
from fuel_management.models import Fournisseur, Engin, Approvisionnement, Stock
from formulas.models import FormuleBeton

from .serializers import (
    UserSerializer, ClientSerializer, ChantierSerializer, CommandeSerializer,
    OrdreProductionSerializer, MatierePremiereSerializer,
    LivraisonSerializer, FactureSerializer, FournisseurSerializer,
    EnginSerializer, ApprovisionnementSerializer, StockCarburantSerializer,
    FormuleBetonSerializer,
    DashboardStatsSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


class ChantierViewSet(viewsets.ModelViewSet):
    queryset = Chantier.objects.all().select_related('client')
    serializer_class = ChantierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Vérifier si request existe avant d'y accéder
        if hasattr(self, 'request') and self.request:
            client_id = self.request.query_params.get('client', None)
            if client_id:
                queryset = queryset.filter(client_id=client_id)
        return queryset


class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all().select_related('client')
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(statut=status_filter)
        return queryset


class OrdreProductionViewSet(viewsets.ModelViewSet):
    queryset = OrdreProduction.objects.all().select_related(
        'commande', 'formule', 'chauffeur', 'vehicule', 'pompe', 'pompe__operateur'
    )
    serializer_class = OrdreProductionSerializer
    permission_classes = [IsAuthenticated]


class MatierePremiereViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MatierePremiere.objects.all()
    serializer_class = MatierePremiereSerializer
    permission_classes = [IsAuthenticated]


class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all().select_related('commande__client')
    serializer_class = LivraisonSerializer
    permission_classes = [IsAuthenticated]


class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all().select_related('commande__client')
    serializer_class = FactureSerializer
    permission_classes = [IsAuthenticated]


class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [IsAuthenticated]


class EnginViewSet(viewsets.ModelViewSet):
    queryset = Engin.objects.all().select_related('type_engin')
    serializer_class = EnginSerializer
    permission_classes = [IsAuthenticated]


class ApprovisionnementViewSet(viewsets.ModelViewSet):
    queryset = Approvisionnement.objects.all().select_related('fournisseur')
    serializer_class = ApprovisionnementSerializer
    permission_classes = [IsAuthenticated]


class StockCarburantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockCarburantSerializer
    permission_classes = [IsAuthenticated]


class FormuleBetonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FormuleBeton.objects.all()
    serializer_class = FormuleBetonSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    API endpoint pour les statistiques du tableau de bord
    """
    try:
        # Période courante (mois en cours)
        maintenant = timezone.now()
        debut_mois = maintenant.replace(day=1)

        # Commandes
        commandes_total = Commande.objects.count()
        commandes_en_cours = Commande.objects.filter(statut='en_production').count()

        # Production mensuelle (somme des quantités à produire dans le mois)
        production_mensuelle = OrdreProduction.objects.filter(
            date_production__gte=debut_mois,
            date_production__lte=maintenant.date()
        ).aggregate(total=Sum('quantite_produire'))['total'] or 0

        # Chiffre d'affaires mensuel (factures du mois, statut payée)
        chiffre_affaires_mensuel = Facture.objects.filter(
            date_facturation__gte=debut_mois,
            date_facturation__lte=maintenant.date(),
            statut='payee'
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        # Stock critique (matières premières avec stock bas/critique)
        stock_critique = sum(
            1 for mp in MatierePremiere.objects.all()
            if mp.statut_stock in ['critique', 'bas']
        )

        # Consommation carburant mensuelle
        consommation_carburant_mensuelle = Approvisionnement.objects.filter(
            date__gte=debut_mois,
            date__lte=maintenant.date()
        ).aggregate(total=Sum('quantite'))['total'] or 0

        stats = {
            'commandes_total': commandes_total,
            'commandes_en_cours': commandes_en_cours,
            'production_mensuelle': production_mensuelle,
            'chiffre_affaires_mensuel': chiffre_affaires_mensuel,
            'stock_critique': stock_critique,
            'consommation_carburant_mensuelle': consommation_carburant_mensuelle,
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Statistiques de production (endpoint attendu par l'app Android)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def production_stats(request):
    """
    Retourne des statistiques de production sous la forme:
    {
      "production_quotidienne": [ {"date": "YYYY-MM-DD", "quantite": float}, ... ],
      "production_par_type": [ {"type_beton": str, "quantite_totale": float}, ... ]
    }
    
    Implémentation minimale pour éviter les 404; peut être enrichie ensuite.
    """
    data = {
        'production_quotidienne': [],
        'production_par_type': []
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def commandes_recentes(request):
    """
    API endpoint pour les commandes récentes
    """
    commandes = Commande.objects.select_related('client').order_by('-date_commande')[:10]
    serializer = CommandeSerializer(commandes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def production_en_cours(request):
    """
    API endpoint pour la production en cours
    """
    production = OrdreProduction.objects.select_related(
        'commande', 'formule', 'chauffeur', 'vehicule', 'pompe', 'pompe__operateur'
    ).filter(
        statut='en_cours'
    ).order_by('-date_production')[:10]
    serializer = OrdreProductionSerializer(production, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_notifications_endpoint(request):
    """Endpoint de test pour vérifier le déploiement des notifications"""
    return Response({
        'status': 'success',
        'message': 'Endpoint de test des notifications fonctionne',
        'notifications_app_loaded': 'notifications' in settings.INSTALLED_APPS,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_health_check(request):
    """Endpoint simple pour vérifier la connectivité API"""
    return Response({
        'status': 'ok',
        'message': 'API is running',
        'timestamp': timezone.now().isoformat()
    })


# ======== Web Push: exposer clé publique VAPID =========
@api_view(['GET'])
@permission_classes([AllowAny])
def webpush_public_key(request):
    key = getattr(settings, 'VAPID_PUBLIC_KEY', None) or settings.SECRETS.get('VAPID_PUBLIC_KEY') if hasattr(settings, 'SECRETS') else None
    return Response({
        'vapidPublicKey': key
    })

# ======== Web Push: envoi test =========
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webpush_test_send(request):
    """Envoie une notification Web Push de test aux abonnements de l'utilisateur."""
    payload = request.data or {}
    if 'title' not in payload:
        payload['title'] = 'Test Web Push'
    if 'message' not in payload:
        payload['message'] = 'Ceci est une notification de test.'
    try:
        from notifications.utils import broadcast_webpush_to_user
        result = broadcast_webpush_to_user(request.user, payload)
        return Response({'status': 'ok', 'result': result})
    except Exception as e:
        return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)