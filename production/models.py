from django.db import models
from orders.models import Commande
from formulas.models import FormuleBeton

class OrdreProduction(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    formule = models.ForeignKey(FormuleBeton, on_delete=models.CASCADE)
    quantite_produire = models.DecimalField(max_digits=10, decimal_places=2)
    date_production = models.DateField()
    statut = models.CharField(max_length=20, choices=[('planifie', 'Planifié'), ('en_cours', 'En cours'), ('termine', 'Terminé'), ('annule', 'Annulé')], default='planifie')

    def __str__(self):
        return f"Ordre de production {self.id} pour la commande {self.commande.id}"

class LotProduction(models.Model):
    ordre_production = models.ForeignKey(OrdreProduction, related_name='lots', on_delete=models.CASCADE)
    quantite_produite = models.DecimalField(max_digits=10, decimal_places=2)
    date_heure_production = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lot {self.id} de l'ordre {self.ordre_production.id}"
