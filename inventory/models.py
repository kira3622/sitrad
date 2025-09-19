from django.db import models
from django.db.models import Sum

class MatierePremiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    unite_mesure = models.CharField(max_length=20)  # e.g., 'kg', 'm³', 'litre'
    
    # Seuils d'alerte pour cette matière première
    seuil_critique = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=10.00,
        help_text="Seuil en dessous duquel le stock est considéré comme critique"
    )
    seuil_bas = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=50.00,
        help_text="Seuil en dessous duquel le stock est considéré comme bas"
    )

    @property
    def stock_actuel(self):
        from stock.models import MouvementStock
        stock_entrees = MouvementStock.objects.filter(matiere_premiere=self, type_mouvement='entree').aggregate(total=Sum('quantite'))['total'] or 0
        stock_sorties = MouvementStock.objects.filter(matiere_premiere=self, type_mouvement='sortie').aggregate(total=Sum('quantite'))['total'] or 0
        return stock_entrees - stock_sorties

    @property
    def statut_stock(self):
        """Retourne le statut du stock selon les seuils configurés"""
        stock = self.stock_actuel
        if stock <= self.seuil_critique:
            return 'critique'
        elif stock <= self.seuil_bas:
            return 'bas'
        else:
            return 'normal'

    @property
    def stock_critique(self):
        """Vérifie si le stock est en niveau critique"""
        return self.stock_actuel <= self.seuil_critique

    @property
    def stock_bas(self):
        """Vérifie si le stock est en niveau bas"""
        return self.stock_actuel <= self.seuil_bas

    def __str__(self):
        return self.nom
