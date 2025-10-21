from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """
    Modèle pour les notifications de l'application
    """
    TYPE_CHOICES = [
        ('NEW_ORDER', 'Nouvelle commande'),
        ('PRODUCTION_UPDATE', 'Mise à jour production'),
        ('LOW_INVENTORY', 'Stock faible'),
        ('DELIVERY', 'Livraison'),
        ('GENERAL', 'Général'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevé'),
        ('urgent', 'Urgent'),
    ]
    
    # Champs de base
    title = models.CharField(max_length=255, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='GENERAL',
        verbose_name="Type"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name="Priorité"
    )
    
    # Métadonnées
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    
    # Relations optionnelles
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Utilisateur"
    )
    related_object_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="ID objet lié"
    )
    related_object_type = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        verbose_name="Type objet lié"
    )
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.title} - {self.get_type_display()}"

    def mark_as_read(self):
        """Marque la notification comme lue"""
        self.is_read = True
        self.save()
    
    @classmethod
    def create_notification(cls, title, message, notification_type='GENERAL', 
                          priority='normal', user=None, related_object_id=None, 
                          related_object_type=None):
        """
        Méthode utilitaire pour créer une notification
        """
        obj = cls.objects.create(
            title=title,
            message=message,
            type=notification_type,
            priority=priority,
            user=user,
            related_object_id=related_object_id,
            related_object_type=related_object_type
        )
        # Envoi Web Push (non bloquant si pywebpush indisponible)
        if user is not None:
            try:
                from .utils import broadcast_webpush_to_user
                payload = {
                    'title': title,
                    'message': message,
                    'type': notification_type,
                    'priority': priority,
                    'notificationId': obj.id,
                }
                broadcast_webpush_to_user(user, payload)
            except Exception:
                # Ignorer silencieusement en cas d'erreur pour ne pas bloquer la création
                pass
        return obj


class WebPushSubscription(models.Model):
    """
    Abonnement aux notifications Web Push (Chrome/Android, Firefox, etc.)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='webpush_subscriptions')
    endpoint = models.URLField(unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    browser = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'active']),
            models.Index(fields=['endpoint']),
        ]
        verbose_name = "Abonnement Web Push"
        verbose_name_plural = "Abonnements Web Push"

    def __str__(self):
        owner = self.user.username if self.user else 'anonymous'
        return f"{owner} - {self.browser}"
