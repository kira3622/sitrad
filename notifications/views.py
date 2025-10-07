from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from .models import Notification
from .serializers import (
    NotificationSerializer, 
    NotificationSummarySerializer,
    MarkAsReadSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retourne les notifications pour l'utilisateur connecté
        """
        queryset = Notification.objects.all()
        
        # Filtrer par utilisateur si spécifié
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user_id=user)
        
        # Filtrer par type si spécifié
        notification_type = self.request.query_params.get('type', None)
        if notification_type is not None:
            queryset = queryset.filter(type=notification_type)
        
        # Filtrer par statut de lecture
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retourne un résumé des notifications
        """
        queryset = self.get_queryset()
        
        summary_data = {
            'total_count': queryset.count(),
            'unread_count': queryset.filter(is_read=False).count(),
            'new_orders_count': queryset.filter(type='NEW_ORDER').count(),
            'production_updates_count': queryset.filter(type='PRODUCTION_UPDATE').count(),
            'low_inventory_count': queryset.filter(type='LOW_INVENTORY').count(),
            'delivery_count': queryset.filter(type='DELIVERY').count(),
        }
        
        serializer = NotificationSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marque une notification spécifique comme lue
        """
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Marque toutes les notifications comme lues
        """
        serializer = MarkAsReadSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            if data.get('mark_all', False):
                # Marquer toutes les notifications comme lues
                updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)
                return Response({
                    'message': f'{updated_count} notifications marquées comme lues',
                    'updated_count': updated_count
                })
            
            elif data.get('notification_ids'):
                # Marquer les notifications spécifiées comme lues
                notification_ids = data['notification_ids']
                updated_count = self.get_queryset().filter(
                    id__in=notification_ids,
                    is_read=False
                ).update(is_read=True)
                
                return Response({
                    'message': f'{updated_count} notifications marquées comme lues',
                    'updated_count': updated_count
                })
            
            else:
                return Response(
                    {'error': 'Aucune notification spécifiée'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def delete_read(self, request):
        """
        Supprime toutes les notifications lues
        """
        deleted_count, _ = self.get_queryset().filter(is_read=True).delete()
        return Response({
            'message': f'{deleted_count} notifications supprimées',
            'deleted_count': deleted_count
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Supprime une notification spécifique
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Notification supprimée avec succès'},
            status=status.HTTP_204_NO_CONTENT
        )
