from django.db import models

class MatierePremiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    unite_mesure = models.CharField(max_length=20)  # e.g., 'kg', 'm³', 'litre'

    def __str__(self):
        return self.nom
