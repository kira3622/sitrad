from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class ActivityLog(models.Model):
    """
    Modèle pour enregistrer toutes les activités des utilisateurs
    dans l'application, visible par tous les utilisateurs
    """
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('view', 'Consultation'),
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    action = models.CharField(
        max_length=20, 
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date et heure"
    )
    
    # Référence générique vers n'importe quel modèle
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Description de l'action
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    # Détails supplémentaires (JSON)
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Détails"
    )
    
    # Adresse IP de l'utilisateur
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="Adresse IP"
    )
    
    class Meta:
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activités"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        if self.content_object:
            return f"{self.user.username} - {self.get_action_display()} - {self.content_object} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    def get_object_name(self):
        """Retourne le nom de l'objet concerné par l'action"""
        if self.content_object:
            return str(self.content_object)
        return "N/A"
    
    def get_model_name(self):
        """Retourne le nom du modèle concerné par l'action"""
        if self.content_type:
            return self.content_type.model_class()._meta.verbose_name
        return "N/A"
    
    def get_app_name(self):
        """Retourne le nom de l'application concernée par l'action"""
        if self.content_type:
            return self.content_type.app_label
        return "N/A"
