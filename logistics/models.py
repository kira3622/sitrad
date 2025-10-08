from django.db import models
from orders.models import Commande

class Chauffeur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    numero_permis = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=20, unique=True)
    modele = models.CharField(max_length=100)
    capacite = models.DecimalField(max_digits=10, decimal_places=2)  # en m³
    chauffeur = models.ForeignKey('Chauffeur', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicules')

    def __str__(self):
        return f"{self.modele} ({self.immatriculation})"

class Livraison(models.Model):
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True)
    date_livraison = models.DateField()
    adresse_livraison = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')

    def __str__(self):
        return f"Livraison pour {self.commande.client} le {self.date_livraison}"
