from django.db import models
from inventory.models import MatierePremiere

class MouvementStock(models.Model):
    TYPE_MOUVEMENT_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ]

    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    type_mouvement = models.CharField(max_length=6, choices=TYPE_MOUVEMENT_CHOICES)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_type_mouvement_display()} de {self.quantite} {self.matiere_premiere.unite_mesure} de {self.matiere_premiere.nom}"
