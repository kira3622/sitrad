from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum


class Fournisseur(models.Model):
    """Modèle pour les fournisseurs de gasoil"""
    nom = models.CharField(max_length=100, help_text="Nom du fournisseur")
    contact = models.CharField(max_length=100, blank=True, help_text="Personne de contact")
    telephone = models.CharField(max_length=20, blank=True, help_text="Numéro de téléphone")
    email = models.EmailField(blank=True, help_text="Adresse email")
    adresse = models.TextField(blank=True, help_text="Adresse du fournisseur")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']


class TypeEngin(models.Model):
    """Types d'engins (mixer, camion toupie, chargeur, etc.)"""
    nom = models.CharField(max_length=50, unique=True, help_text="Type d'engin")
    consommation_moyenne = models.DecimalField(
        max_digits=6, decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Consommation moyenne en litres/heure"
    )
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Type d'engin"
        verbose_name_plural = "Types d'engins"
        ordering = ['nom']


class Engin(models.Model):
    """Modèle pour les engins/machines"""
    nom = models.CharField(max_length=100, help_text="Nom/Identifiant de l'engin")
    type_engin = models.ForeignKey(TypeEngin, on_delete=models.CASCADE, help_text="Type d'engin")
    numero_serie = models.CharField(max_length=50, blank=True, help_text="Numéro de série")
    immatriculation = models.CharField(max_length=20, blank=True, help_text="Plaque d'immatriculation")
    marque = models.CharField(max_length=50, blank=True, help_text="Marque de l'engin")
    modele = models.CharField(max_length=50, blank=True, help_text="Modèle de l'engin")
    annee = models.PositiveIntegerField(null=True, blank=True, help_text="Année de fabrication")
    
    actif = models.BooleanField(default=True, help_text="Engin en service")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nom} ({self.type_engin})"
    
    def consommation_totale(self, date_debut=None, date_fin=None):
        """Calcule la consommation totale pour une période donnée"""
        queryset = self.consommations.all()
        if date_debut:
            queryset = queryset.filter(date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date__lte=date_fin)
        
        total = queryset.aggregate(total=Sum('quantite'))['total']
        return total or Decimal('0')
    
    class Meta:
        verbose_name = "Engin"
        verbose_name_plural = "Engins"
        ordering = ['nom']


class Approvisionnement(models.Model):
    """Modèle pour les entrées de gasoil"""
    date = models.DateField(default=timezone.now, help_text="Date de livraison")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, help_text="Fournisseur")
    quantite = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantité en litres"
    )
    prix_unitaire = models.DecimalField(
        max_digits=8, decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Prix par litre en DH"
    )
    montant_total = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Montant total en DH"
    )
    numero_bon = models.CharField(max_length=50, blank=True, help_text="Numéro de bon de livraison")
    numero_facture = models.CharField(max_length=50, blank=True, help_text="Numéro de facture")
    
    notes = models.TextField(blank=True, help_text="Notes ou observations")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calcul automatique du montant total
        self.montant_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
        
        # Mise à jour du stock après sauvegarde
        self.mettre_a_jour_stock()
    
    def mettre_a_jour_stock(self):
        """Met à jour le stock après un approvisionnement"""
        stock, created = Stock.objects.get_or_create(
            defaults={'quantite': Decimal('0'), 'seuil_minimum': Decimal('500')}
        )
        stock.recalculer_stock()
    
    def __str__(self):
        return f"Approvisionnement {self.date} - {self.fournisseur} ({self.quantite}L)"
    
    class Meta:
        verbose_name = "Approvisionnement"
        verbose_name_plural = "Approvisionnements"
        ordering = ['-date', '-date_creation']


class Consommation(models.Model):
    """Modèle pour les sorties de gasoil"""
    date = models.DateField(default=timezone.now, help_text="Date de consommation")
    engin = models.ForeignKey(Engin, on_delete=models.CASCADE, related_name='consommations', help_text="Engin concerné")
    quantite = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantité consommée en litres"
    )
    responsable = models.CharField(max_length=100, help_text="Responsable de l'opération")
    heures_fonctionnement = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Heures de fonctionnement (optionnel)"
    )
    kilometrage = models.PositiveIntegerField(null=True, blank=True, help_text="Kilométrage (pour véhicules)")
    
    notes = models.TextField(blank=True, help_text="Notes ou observations")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Mise à jour du stock après sauvegarde
        self.mettre_a_jour_stock()
    
    def mettre_a_jour_stock(self):
        """Met à jour le stock après une consommation"""
        stock, created = Stock.objects.get_or_create(
            defaults={'quantite': Decimal('0'), 'seuil_minimum': Decimal('500')}
        )
        stock.recalculer_stock()
    
    def consommation_par_heure(self):
        """Calcule la consommation par heure si les heures sont renseignées"""
        if self.heures_fonctionnement and self.heures_fonctionnement > 0:
            return self.quantite / self.heures_fonctionnement
        return None
    
    def __str__(self):
        return f"{self.date} - {self.engin} ({self.quantite}L)"
    
    class Meta:
        verbose_name = "Consommation"
        verbose_name_plural = "Consommations"
        ordering = ['-date', '-date_creation']


class Stock(models.Model):
    """Modèle pour le stock de gasoil (singleton)"""
    quantite = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0'),
        help_text="Quantité actuelle en stock (litres)"
    )
    seuil_minimum = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=Decimal('500'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Seuil d'alerte minimum (litres)"
    )
    
    date_derniere_maj = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Assurer qu'il n'y ait qu'un seul enregistrement de stock
        if not self.pk and Stock.objects.exists():
            raise ValueError("Il ne peut y avoir qu'un seul enregistrement de stock")
        super().save(*args, **kwargs)
    
    def recalculer_stock(self):
        """Recalcule le stock basé sur les approvisionnements et consommations"""
        total_approvisionnements = Approvisionnement.objects.aggregate(
            total=Sum('quantite')
        )['total'] or Decimal('0')
        
        total_consommations = Consommation.objects.aggregate(
            total=Sum('quantite')
        )['total'] or Decimal('0')
        
        self.quantite = total_approvisionnements - total_consommations
        self.save()
    
    def est_en_alerte(self):
        """Vérifie si le stock est en dessous du seuil minimum"""
        return self.quantite <= self.seuil_minimum
    
    def pourcentage_stock(self):
        """Calcule le pourcentage par rapport au seuil minimum"""
        if self.seuil_minimum > 0:
            return (self.quantite / self.seuil_minimum) * Decimal('100')
        return Decimal('0')
    
    @classmethod
    def get_stock_actuel(cls):
        """Récupère ou crée l'instance unique de stock"""
        stock, created = cls.objects.get_or_create(
            defaults={'quantite': Decimal('0'), 'seuil_minimum': Decimal('500')}
        )
        if created:
            stock.recalculer_stock()
        return stock
    
    def __str__(self):
        status = "⚠️ ALERTE" if self.est_en_alerte() else "✅ OK"
        return f"Stock Gasoil: {self.quantite}L {status}"
    
    class Meta:
        verbose_name = "Stock de gasoil"
        verbose_name_plural = "Stock de gasoil"


class AlerteStock(models.Model):
    """Modèle pour l'historique des alertes de stock"""
    date_alerte = models.DateTimeField(auto_now_add=True)
    quantite_stock = models.DecimalField(max_digits=10, decimal_places=2)
    seuil_minimum = models.DecimalField(max_digits=8, decimal_places=2)
    message = models.TextField()
    
    vue = models.BooleanField(default=False, help_text="Alerte vue par un utilisateur")
    
    def __str__(self):
        return f"Alerte {self.date_alerte.strftime('%d/%m/%Y %H:%M')} - Stock: {self.quantite_stock}L"
    
    class Meta:
        verbose_name = "Alerte de stock"
        verbose_name_plural = "Alertes de stock"
        ordering = ['-date_alerte']
