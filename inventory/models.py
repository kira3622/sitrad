from django.db import models
from django.db.models import Sum

class MatierePremiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    unite_mesure = models.CharField(max_length=20)  # e.g., 'kg', 'm³', 'litre'

    @property
    def stock_actuel(self):
        from stock.models import MouvementStock
        stock_entrees = MouvementStock.objects.filter(matiere_premiere=self, type_mouvement='entree').aggregate(total=Sum('quantite'))['total'] or 0
        stock_sorties = MouvementStock.objects.filter(matiere_premiere=self, type_mouvement='sortie').aggregate(total=Sum('quantite'))['total'] or 0
        return stock_entrees - stock_sorties

    def __str__(self):
        return self.nom
