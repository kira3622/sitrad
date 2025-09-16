from django.db import models

class MatierePremiere(models.Model):
    nom = models.CharField(max_length=100)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    unite = models.CharField(max_length=50)

    def __str__(self):
        return self.nom
