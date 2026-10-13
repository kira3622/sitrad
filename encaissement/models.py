from django.db import models
from decimal import Decimal
from django.utils import timezone
from customers.models import Client
from production.models import OrdreProduction


class Encaissement(models.Model):
    """
    Encaissement d'un paiement pour un client.
    - Peut etre lie a un bon de livraison (ordre_production) ou etre un encaissement global client.
    - Plusieurs encaissements peuvent etre saisis pour le meme client.
    """

    MODE_REGLEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement'),
        ('carte', 'Carte bancaire'),
        ('traite', 'Traite'),
        ('effet', 'Effet de commerce'),
        ('autre', 'Autre'),
    ]

    # Relations
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='encaissements',
        verbose_name="Client",
    )
    ordre_production = models.ForeignKey(
        OrdreProduction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encaissements',
        verbose_name="Bon de livraison (Ordre de production)",
        help_text="Laisser vide pour un encaissement global sur le client.",
    )

    # Informations de base
    reference = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name="Référence encaissement",
        help_text="Générée automatiquement si vide.",
    )
    date_encaissement = models.DateField(
        default=timezone.now,
        verbose_name="Date d'encaissement",
    )

    # Montant
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant encaissé (MAD)",
    )

    # Règlement
    mode_reglement = models.CharField(
        max_length=20,
        choices=MODE_REGLEMENT_CHOICES,
        default='virement',
        verbose_name="Mode de règlement",
    )
    numero_reglement = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="N° de règlement",
        help_text="Numéro de chèque, virement, traite, etc.",
    )

    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes")

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_encaissement', '-id']
        verbose_name = "Encaissement"
        verbose_name_plural = "Encaissements"

    def __str__(self):
        bon = f" - Bon {self.ordre_production.numero_bon}" if self.ordre_production else ""
        return f"{self.reference} - {self.client.nom}{bon} - {self.montant} MAD"

    def save(self, *args, **kwargs):
        # Générer une référence automatique si elle n'existe pas
        if not self.reference:
            from datetime import datetime
            annee = timezone.now().year

            dernier = Encaissement.objects.filter(
                reference__startswith=f"ENC{annee}"
            ).order_by('-reference').first()

            if dernier:
                try:
                    sequence = int(dernier.reference[-6:]) + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1

            self.reference = f"ENC{annee}{sequence:06d}"

        super().save(*args, **kwargs)

    @property
    def numero_bon(self):
        """Retourne le numero de bon si lie a un ordre de production."""
        if self.ordre_production:
            return self.ordre_production.numero_bon
        return "-"

    @property
    def montant_bon_lie(self):
        """Retourne le montant du bon de livraison lie (quantite x PU) si disponible."""
        if self.ordre_production:
            op = self.ordre_production
            qte = op.quantite_produire or Decimal('0.00')
            pu = op.prix_vente_unitaire or Decimal('0.00')
            return qte * pu
        return Decimal('0.00')
