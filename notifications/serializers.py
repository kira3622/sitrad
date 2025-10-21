from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les notifications
    """
    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'type',
            'priority',
            'timestamp',
            'is_read',
            'user',
            'related_object_id',
            'related_object_type'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def to_representation(self, instance):
        """
        Personnalise la représentation pour correspondre au format attendu par l'app Android
        """
        data = super().to_representation(instance)
        
        # Convertir timestamp en millisecondes (format Unix timestamp)
        if data['timestamp']:
            from django.utils.dateparse import parse_datetime
            import time
            dt = parse_datetime(data['timestamp']) if isinstance(data['timestamp'], str) else instance.timestamp
            data['timestamp'] = int(dt.timestamp() * 1000)
        
        return data


class NotificationSummarySerializer(serializers.Serializer):
    """
    Serializer pour le résumé des notifications
    """
    total_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    new_orders_count = serializers.IntegerField()
    production_updates_count = serializers.IntegerField()
    low_inventory_count = serializers.IntegerField()
    delivery_count = serializers.IntegerField()


class MarkAsReadSerializer(serializers.Serializer):
    """
    Serializer pour marquer une notification comme lue
    """
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Liste des IDs des notifications à marquer comme lues"
    )
    mark_all = serializers.BooleanField(
        default=False,
        help_text="Marquer toutes les notifications comme lues"
    )


# ======== Web Push =========
from .models import WebPushSubscription

class WebPushSubscriptionSerializer(serializers.ModelSerializer):
    # Supporte le payload standard du navigateur: { endpoint, keys: { p256dh, auth } }
    keys = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = WebPushSubscription
        fields = ['id', 'user', 'endpoint', 'p256dh', 'auth', 'browser', 'active', 'created_at', 'updated_at', 'keys']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        keys = attrs.pop('keys', None)
        if keys:
            attrs['p256dh'] = keys.get('p256dh')
            attrs['auth'] = keys.get('auth')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        endpoint = validated_data['endpoint']
        defaults = {
            'user': user,
            'p256dh': validated_data.get('p256dh', ''),
            'auth': validated_data.get('auth', ''),
            'browser': validated_data.get('browser', ''),
            'active': True,
        }
        obj, _created = WebPushSubscription.objects.update_or_create(endpoint=endpoint, defaults=defaults)
        return obj