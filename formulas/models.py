from django.db import models
from inventory.models import MatierePremiere

class FormuleBeton(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    resistance_requise = models.CharField(max_length=50)  # e.g., 'C25/30'

    def __str__(self):
        return self.nom

class CompositionFormule(models.Model):
    formule = models.ForeignKey(FormuleBeton, related_name='composition', on_delete=models.CASCADE)
    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ('formule', 'matiere_premiere')

    def __str__(self):
        return f'{self.formule.nom} - {self.matiere_premiere.nom}: {self.quantite}'
