from django.db import models
from decimal import Decimal

class Rapport(models.Model):
    nom = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    contenu = models.TextField()

    def __str__(self):
        return self.nom


class ConfigurationSeuilsStock(models.Model):
    """Configuration des seuils d'alerte pour le stock"""
    
    seuil_critique = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('10.0'),
        help_text="Seuil en dessous duquel le stock est considéré comme critique"
    )
    
    seuil_bas = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('50.0'),
        help_text="Seuil en dessous duquel le stock est considéré comme bas"
    )
    
    date_modification = models.DateTimeField(auto_now=True)
    modifie_par = models.CharField(
        max_length=150, 
        blank=True, 
        null=True,
        help_text="Utilisateur qui a modifié la configuration"
    )
    
    class Meta:
        verbose_name = "Configuration des seuils de stock"
        verbose_name_plural = "Configuration des seuils de stock"
    
    def __str__(self):
        return f"Seuils: Critique ≤ {self.seuil_critique}, Bas ≤ {self.seuil_bas}"
    
    @classmethod
    def get_seuils(cls):
        """Récupère les seuils configurés ou crée une configuration par défaut"""
        config, created = cls.objects.get_or_create(
            pk=1,  # Une seule configuration
            defaults={
                'seuil_critique': Decimal('10.0'),
                'seuil_bas': Decimal('50.0')
            }
        )
        return config
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule configuration
        self.pk = 1
        super().save(*args, **kwargs)
