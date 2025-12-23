from django.db import models
from decimal import Decimal
from django.db.models import Avg
from formulas.models import FormuleBeton, CompositionFormule
from stock.models import SaisieEntreeLie
from inventory.models import MatierePremiere

class Rapport(models.Model):
    nom = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    contenu = models.TextField()

    def __str__(self):
        return self.nom


class ConfigurationSeuilsStock(models.Model):
    """Configuration des seuils d'alerte pour le stock"""
    
    seuil_critique = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('10.0'),
        help_text="Seuil en dessous duquel le stock est considéré comme critique"
    )
    
    seuil_bas = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('50.0'),
        help_text="Seuil en dessous duquel le stock est considéré comme bas"
    )
    
    date_modification = models.DateTimeField(auto_now=True)
    modifie_par = models.CharField(
        max_length=150, 
        blank=True, 
        null=True,
        help_text="Utilisateur qui a modifié la configuration"
    )
    
    class Meta:
        verbose_name = "Configuration des seuils de stock"
        verbose_name_plural = "Configuration des seuils de stock"
    
    def __str__(self):
        return f"Seuils: Critique ≤ {self.seuil_critique}, Bas ≤ {self.seuil_bas}"
    
    @classmethod
    def get_seuils(cls):
        """Récupère les seuils configurés ou crée une configuration par défaut"""
        config, created = cls.objects.get_or_create(
            pk=1,  # Une seule configuration
            defaults={
                'seuil_critique': Decimal('10.0'),
                'seuil_bas': Decimal('50.0')
            }
        )
        return config
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule configuration
        self.pk = 1
        super().save(*args, **kwargs)


class RapportCoutFormule(models.Model):
    """Rapport de coût de formule béton avec calcul des prix moyens"""
    
    formule = models.ForeignKey(FormuleBeton, on_delete=models.CASCADE, verbose_name="Formule béton")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    cout_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Coût total", null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Rapport de coût de formule"
        verbose_name_plural = "Rapports de coût de formule"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Coût {self.formule.nom} - {self.date_debut} au {self.date_fin}"
    
    def calculer_cout_matiere_premiere(self, matiere_premiere):
        """Calcule le prix moyen TTC d'une matière première sur la période"""
        # Calculer le prix HT moyen
        prix_ht_moyen = SaisieEntreeLie.objects.filter(
            matiere_premiere=matiere_premiere,
            date_facture__range=[self.date_debut, self.date_fin],
            prix_achat_ht__isnull=False,
            quantite__isnull=False,
            quantite__gt=0
        ).aggregate(
            prix_moyen=Avg('prix_achat_ht')
        )['prix_moyen'] or Decimal('0.00')
        
        # Calculer le taux TVA moyen
        taux_tva_moyen = SaisieEntreeLie.objects.filter(
            matiere_premiere=matiere_premiere,
            date_facture__range=[self.date_debut, self.date_fin],
            prix_achat_ht__isnull=False,
            taux_tva__isnull=False,
            quantite__isnull=False,
            quantite__gt=0
        ).aggregate(
            taux_moyen=Avg('taux_tva')
        )['taux_moyen'] or Decimal('20.00')
        
        # Calculer le prix TTC
        prix_ttc_moyen = prix_ht_moyen * (1 + taux_tva_moyen / 100)
        
        return prix_ttc_moyen
    
    def calculer_cout_total(self):
        """Calcule le coût total de la formule"""
        cout_total = Decimal('0.00')
        
        # Obtenir toutes les compositions de la formule
        compositions = CompositionFormule.objects.filter(formule=self.formule)
        
        for composition in compositions:
            # Calculer le prix moyen de la matière première
            prix_unitaire = self.calculer_cout_matiere_premiere(composition.matiere_premiere)
            
            # Calculer le coût pour cette matière première
            cout_matiere = prix_unitaire * composition.quantite
            
            # Ajouter au coût total
            cout_total += cout_matiere
        
        self.cout_total = cout_total
        self.save()
        
        return cout_total
    
    def get_details_cout(self):
        """Retourne les détails du coût par matière première"""
        details = []
        compositions = CompositionFormule.objects.filter(formule=self.formule)
        
        for composition in compositions:
            prix_unitaire = self.calculer_cout_matiere_premiere(composition.matiere_premiere)
            cout_total_matiere = prix_unitaire * composition.quantite
            
            details.append({
                'matiere_premiere': composition.matiere_premiere,
                'quantite': composition.quantite,
                'prix_unitaire': prix_unitaire,
                'cout_total': cout_total_matiere,
                'pourcentage': (cout_total_matiere / self.cout_total * 100) if self.cout_total > 0 else 0
            })
        
        return sorted(details, key=lambda x: x['cout_total'], reverse=True)


class DetailCoutFormule(models.Model):
    """Détail du coût par matière première pour un rapport"""
    
    rapport = models.ForeignKey(RapportCoutFormule, on_delete=models.CASCADE, related_name='details')
    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE, verbose_name="Matière première")
    quantite = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Quantité")
    prix_unitaire_moyen = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire moyen")
    cout_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Coût total")
    nombre_saisies = models.IntegerField(verbose_name="Nombre de saisies utilisées", default=0)
    
    class Meta:
        verbose_name = "Détail coût matière première"
        verbose_name_plural = "Détails coût matière première"
        unique_together = ('rapport', 'matiere_premiere')
    
    def __str__(self):
        return f"{self.matiere_premiere.nom} - {self.cout_total} MAD"
