from django.db import models
from customers.models import Client, Chantier
from formulas.models import FormuleBeton

class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    chantier = models.ForeignKey(Chantier, on_delete=models.CASCADE, null=True, blank=True)
    date_commande = models.DateField(auto_now_add=True)
    date_livraison_souhaitee = models.DateField()
    heure_livraison_souhaitee = models.TimeField(null=True, blank=True)  # heure de livraison souhaitée
    statut = models.CharField(max_length=20, choices=[('en_attente', 'En attente'), ('validee', 'Validée'), ('en_production', 'En production'), ('livree', 'Livrée'), ('annulee', 'Annulée')], default='en_attente')

    def __str__(self):
        return f"Commande {self.id} - {self.client}"

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, related_name='lignes', on_delete=models.CASCADE)
    formule = models.ForeignKey(FormuleBeton, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Ligne de commande pour {self.commande.id}"
