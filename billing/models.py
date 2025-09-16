from django.db import models
from orders.models import Commande

class Facture(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    date_facturation = models.DateField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')

    def __str__(self):
        return f"Facture {self.id} pour la commande {self.commande.id}"

class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, related_name='lignes', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ligne = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Ligne pour facture {self.facture.id}: {self.description}"
