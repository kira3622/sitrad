from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
    
    def nombre_chantiers(self):
        """Retourne le nombre de chantiers de ce client"""
        return self.chantiers.count()
    
    def chantiers_actifs(self):
        """Retourne les chantiers qui ont des commandes en cours"""
        from orders.models import Commande
        return self.chantiers.filter(
            commande__statut__in=['en_attente', 'validee', 'en_production']
        ).distinct()
    
    def dernier_chantier(self):
        """Retourne le dernier chantier créé pour ce client"""
        return self.chantiers.order_by('-id').first()
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

class Chantier(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='chantiers')

    def __str__(self):
        return f'{self.nom} ({self.client.nom})'
    
    def nombre_commandes(self):
        """Retourne le nombre de commandes pour ce chantier"""
        return self.commande_set.count()
    
    def commandes_actives(self):
        """Retourne les commandes actives pour ce chantier"""
        return self.commande_set.filter(
            statut__in=['en_attente', 'validee', 'en_production']
        )
    
    def derniere_commande(self):
        """Retourne la dernière commande pour ce chantier"""
        return self.commande_set.order_by('-date_commande').first()
    
    def statut_chantier(self):
        """Retourne le statut du chantier basé sur ses commandes"""
        commandes_actives = self.commandes_actives()
        if commandes_actives.exists():
            return "Actif"
        elif self.commande_set.exists():
            return "Terminé"
        else:
            return "Nouveau"
    
    class Meta:
        verbose_name = "Chantier"
        verbose_name_plural = "Chantiers"
