from django.db import models
from orders.models import Commande

class Pompe(models.Model):
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_service', 'En service'),
        ('maintenance', 'En maintenance'),
        ('hors_service', 'Hors service'),
    ]
    
    nom = models.CharField(max_length=100, verbose_name="Nom de la pompe")
    immatriculation = models.CharField(max_length=20, blank=True, verbose_name="Immatriculation")
    numero_serie = models.CharField(max_length=50, unique=True, verbose_name="Numéro de série")
    marque = models.CharField(max_length=100, verbose_name="Marque")
    modele = models.CharField(max_length=100, verbose_name="Modèle")
    debit_max = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Débit maximum (m³/h)")
    portee_max = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Portée maximale (m)")
    hauteur_max = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Hauteur maximale (m)")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible', verbose_name="Statut")
    date_acquisition = models.DateField(verbose_name="Date d'acquisition")
    date_derniere_maintenance = models.DateField(null=True, blank=True, verbose_name="Dernière maintenance")
    operateur = models.ForeignKey('Chauffeur', on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='pompes_operees', verbose_name="Opérateur")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Pompe"
        verbose_name_plural = "Pompes"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.marque} {self.modele})"
    
    def est_disponible(self):
        """Vérifie si la pompe est disponible pour une mission"""
        return self.actif and self.statut == 'disponible'
    
    def jours_depuis_maintenance(self):
        """Calcule le nombre de jours depuis la dernière maintenance"""
        if self.date_derniere_maintenance:
            from datetime import date
            return (date.today() - self.date_derniere_maintenance).days
        return None

class Chauffeur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    numero_permis = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=20, unique=True)
    modele = models.CharField(max_length=100)
    capacite = models.DecimalField(max_digits=10, decimal_places=2)  # en m³
    chauffeur = models.ForeignKey('Chauffeur', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicules')

    def __str__(self):
        return f"{self.modele} ({self.immatriculation})"

class Livraison(models.Model):
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True)
    date_livraison = models.DateField()
    heure_livraison = models.TimeField(null=True, blank=True, verbose_name="Heure de livraison")
    adresse_livraison = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')

    def __str__(self):
        return f"Livraison pour {self.commande.client} le {self.date_livraison}"


class PlanningLivraisons(Livraison):
    """Proxy pour exposer le module « Planning des livraisons prévues » dans l'admin.
    Aucun enregistrement n'est affiché : sert uniquement de point d'entrée vers le planning.
    """
    class Meta:
        proxy = True
        verbose_name = "Planning des livraisons prévues"
        verbose_name_plural = "Planning des livraisons prévues"


class SaisiePlanning(models.Model):
    """Livraison planifiée saisie librement, sans être rattachée à une commande."""
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    date_livraison = models.DateField(verbose_name="Date de livraison")
    heure_livraison = models.TimeField(null=True, blank=True, verbose_name="Heure de livraison")
    client = models.CharField(max_length=200, verbose_name="Client")
    chantier = models.CharField(max_length=200, blank=True, verbose_name="Chantier / lieu")
    formule = models.CharField(max_length=200, blank=True, verbose_name="Formule")
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                   verbose_name="Quantité (m³)")
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="Véhicule")
    adresse = models.TextField(blank=True, verbose_name="Adresse de livraison")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee',
                              verbose_name="Statut")
    observation = models.TextField(blank=True, verbose_name="Observation")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Livraison planifiée (saisie)"
        verbose_name_plural = "Livraisons planifiées (saisie)"
        ordering = ['date_livraison', 'heure_livraison', 'id']

    def __str__(self):
        return f"{self.client} - {self.date_livraison}"


class SaisiePlanningModule(SaisiePlanning):
    """Proxy pour exposer l'entrée de menu « Saisie des plannings » dans l'admin."""
    class Meta:
        proxy = True
        verbose_name = "Saisie des plannings"
        verbose_name_plural = "Saisie des plannings"
