from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from inventory.models import MatierePremiere
from formulas.models import FormuleBeton
from production.models import OrdreProduction
from orders.models import Commande


class CategorieCoût(models.Model):
    """Catégories de coûts pour organiser les différents types de coûts"""
    TYPES_CHOICES = [
        ('matiere_premiere', 'Matière première'),
        ('main_oeuvre', 'Main d\'œuvre'),
        ('frais_generaux', 'Frais généraux'),
        ('transport', 'Transport'),
        ('energie', 'Énergie'),
        ('amortissement', 'Amortissement'),
        ('autre', 'Autre'),
    ]
    
    nom = models.CharField(max_length=100, unique=True)
    type_categorie = models.CharField(max_length=20, choices=TYPES_CHOICES)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_categorie_display()})"
    
    class Meta:
        verbose_name = "Catégorie de coût"
        verbose_name_plural = "Catégories de coûts"
        ordering = ['type_categorie', 'nom']


class CoûtMatierePremiere(models.Model):
    """Coûts des matières premières avec historique des prix"""
    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE, related_name='coûts')
    prix_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Prix par unité de mesure"
    )
    devise = models.CharField(max_length=3, default='EUR')
    
    # Période de validité
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(null=True, blank=True)
    
    # Informations fournisseur
    fournisseur = models.CharField(max_length=200, blank=True)
    reference_fournisseur = models.CharField(max_length=100, blank=True)
    
    # Coûts additionnels
    coût_transport = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Coût de transport par unité"
    )
    coût_stockage = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Coût de stockage par unité"
    )
    
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    @property
    def prix_total_unitaire(self):
        """Prix total incluant transport et stockage"""
        return self.prix_unitaire + self.coût_transport + self.coût_stockage
    
    def __str__(self):
        return f"{self.matiere_premiere.nom} - {self.prix_unitaire} {self.devise}/{self.matiere_premiere.unite_mesure}"
    
    class Meta:
        verbose_name = "Coût matière première"
        verbose_name_plural = "Coûts matières premières"
        ordering = ['-date_debut', 'matiere_premiere__nom']


class CoûtMainOeuvre(models.Model):
    """Coûts de main d'œuvre par type d'activité"""
    TYPES_ACTIVITE = [
        ('production', 'Production'),
        ('transport', 'Transport'),
        ('livraison', 'Livraison'),
        ('maintenance', 'Maintenance'),
        ('administration', 'Administration'),
        ('commercial', 'Commercial'),
    ]
    
    nom = models.CharField(max_length=100)
    type_activite = models.CharField(max_length=20, choices=TYPES_ACTIVITE)
    
    # Coûts horaires
    coût_horaire_base = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    charges_sociales_pourcentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=45.00,
        help_text="Pourcentage de charges sociales"
    )
    
    # Période de validité
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(null=True, blank=True)
    
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    @property
    def coût_horaire_total(self):
        """Coût horaire total avec charges sociales"""
        charges = self.coût_horaire_base * (self.charges_sociales_pourcentage / 100)
        return self.coût_horaire_base + charges
    
    def __str__(self):
        return f"{self.nom} - {self.coût_horaire_total:.2f} EUR/h"
    
    class Meta:
        verbose_name = "Coût main d'œuvre"
        verbose_name_plural = "Coûts main d'œuvre"
        ordering = ['type_activite', 'nom']


class CoûtFraisGeneraux(models.Model):
    """Frais généraux et coûts indirects"""
    TYPES_REPARTITION = [
        ('fixe', 'Montant fixe'),
        ('pourcentage_ca', 'Pourcentage du CA'),
        ('par_m3', 'Par m³ produit'),
        ('par_commande', 'Par commande'),
    ]
    
    categorie = models.ForeignKey(CategorieCoût, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    type_repartition = models.CharField(max_length=20, choices=TYPES_REPARTITION)
    valeur = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Période de validité
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(null=True, blank=True)
    
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} - {self.valeur} ({self.get_type_repartition_display()})"
    
    class Meta:
        verbose_name = "Frais généraux"
        verbose_name_plural = "Frais généraux"
        ordering = ['categorie', 'nom']


class CalculCoûtRevient(models.Model):
    """Calcul du coût de revient pour une commande ou un ordre de production"""
    # Relations
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, null=True, blank=True)
    ordre_production = models.ForeignKey(OrdreProduction, on_delete=models.CASCADE, null=True, blank=True)
    formule = models.ForeignKey(FormuleBeton, on_delete=models.CASCADE)
    
    # Quantités
    quantite_calculee = models.DecimalField(max_digits=10, decimal_places=2)
    unite_mesure = models.CharField(max_length=10, default='m³')
    
    # Coûts calculés
    coût_matieres_premieres = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coût_main_oeuvre = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coût_frais_generaux = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coût_transport = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coût_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Coûts unitaires
    coût_unitaire_matieres = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    coût_unitaire_main_oeuvre = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    coût_unitaire_frais_generaux = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    coût_unitaire_transport = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    coût_unitaire_total = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    # Métadonnées
    date_calcul = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    calculé_par = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    def calculer_coûts(self):
        """Calcule tous les coûts pour cette production"""
        self.coût_matieres_premieres = self._calculer_coût_matieres_premieres()
        self.coût_main_oeuvre = self._calculer_coût_main_oeuvre()
        self.coût_frais_generaux = self._calculer_coût_frais_generaux()
        self.coût_transport = self._calculer_coût_transport()
        
        self.coût_total = (
            self.coût_matieres_premieres + 
            self.coût_main_oeuvre + 
            self.coût_frais_generaux + 
            self.coût_transport
        )
        
        # Calcul des coûts unitaires
        if self.quantite_calculee > 0:
            self.coût_unitaire_matieres = self.coût_matieres_premieres / self.quantite_calculee
            self.coût_unitaire_main_oeuvre = self.coût_main_oeuvre / self.quantite_calculee
            self.coût_unitaire_frais_generaux = self.coût_frais_generaux / self.quantite_calculee
            self.coût_unitaire_transport = self.coût_transport / self.quantite_calculee
            self.coût_unitaire_total = self.coût_total / self.quantite_calculee
    
    def _calculer_coût_matieres_premieres(self):
        """Calcule le coût des matières premières"""
        coût_total = Decimal('0')
        
        for composition in self.formule.composition.all():
            # Quantité nécessaire pour la production
            quantite_necessaire = (composition.quantite * self.quantite_calculee) / self.formule.quantite_produite_reference
            
            # Récupérer le coût actuel de la matière première
            coût_matiere = CoûtMatierePremiere.objects.filter(
                matiere_premiere=composition.matiere_premiere,
                actif=True,
                date_debut__lte=timezone.now().date()
            ).filter(
                models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=timezone.now().date())
            ).first()
            
            if coût_matiere:
                coût_total += quantite_necessaire * coût_matiere.prix_total_unitaire
        
        return coût_total
    
    def _calculer_coût_main_oeuvre(self):
        """Calcule le coût de main d'œuvre (à personnaliser selon vos besoins)"""
        # Exemple : coût fixe par m³ pour la production
        coût_production = CoûtMainOeuvre.objects.filter(
            type_activite='production',
            actif=True,
            date_debut__lte=timezone.now().date()
        ).filter(
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=timezone.now().date())
        ).first()
        
        if coût_production:
            # Estimation : 0.5h de main d'œuvre par m³
            heures_estimees = self.quantite_calculee * Decimal('0.5')
            return heures_estimees * coût_production.coût_horaire_total
        
        return Decimal('0')
    
    def _calculer_coût_frais_generaux(self):
        """Calcule les frais généraux"""
        coût_total = Decimal('0')
        
        frais_par_m3 = CoûtFraisGeneraux.objects.filter(
            type_repartition='par_m3',
            actif=True,
            date_debut__lte=timezone.now().date()
        ).filter(
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=timezone.now().date())
        )
        
        for frais in frais_par_m3:
            coût_total += self.quantite_calculee * frais.valeur
        
        return coût_total
    
    def _calculer_coût_transport(self):
        """Calcule le coût de transport (à personnaliser)"""
        # Exemple simple : coût fixe par commande
        frais_transport = CoûtFraisGeneraux.objects.filter(
            categorie__type_categorie='transport',
            type_repartition='par_commande',
            actif=True,
            date_debut__lte=timezone.now().date()
        ).filter(
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=timezone.now().date())
        ).first()
        
        if frais_transport:
            return frais_transport.valeur
        
        return Decimal('0')
    
    def __str__(self):
        if self.commande:
            return f"Coût de revient - Commande {self.commande.id}"
        elif self.ordre_production:
            return f"Coût de revient - Ordre {self.ordre_production.numero_bon}"
        return f"Coût de revient - {self.formule.nom}"
    
    class Meta:
        verbose_name = "Calcul coût de revient"
        verbose_name_plural = "Calculs coûts de revient"
        ordering = ['-date_calcul']


class DetailCoûtMatiere(models.Model):
    """Détail des coûts par matière première pour un calcul"""
    calcul_coût = models.ForeignKey(CalculCoûtRevient, related_name='details_matieres', on_delete=models.CASCADE)
    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    quantite_utilisee = models.DecimalField(max_digits=10, decimal_places=3)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=4)
    coût_total_matiere = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.matiere_premiere.nom} - {self.coût_total_matiere} EUR"
    
    class Meta:
        verbose_name = "Détail coût matière"
        verbose_name_plural = "Détails coûts matières"
