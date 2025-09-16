from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nom

class Chantier(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='chantiers')

    def __str__(self):
        return f'{self.nom} ({self.client.nom})'
