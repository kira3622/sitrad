from django.db import models
from inventory.models import MatierePremiere, FournisseurMatierePremiere

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

    def save(self, *args, **kwargs):
        """Vérifie que le mouvement de stock lié est bien une entrée"""
        super().save(*args, **kwargs)


class SaisieEntreeLie(models.Model):
    """Modèle pour lier les entrées de stock avec les fournisseurs"""
    fournisseur = models.ForeignKey(FournisseurMatierePremiere, on_delete=models.CASCADE, verbose_name="Fournisseur")
    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE, verbose_name="Matière première", null=True, blank=True)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité", null=True, blank=True)
    mouvement_stock = models.OneToOneField(MouvementStock, on_delete=models.CASCADE, verbose_name="Mouvement de stock", null=True, blank=True)
    numero_facture = models.CharField(max_length=50, blank=True, verbose_name="Numéro de facture")
    date_facture = models.DateField(null=True, blank=True, verbose_name="Date de facture")
    prix_achat_ht = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix d'achat HT")
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=20.0, verbose_name="Taux TVA (%)")
    notes = models.TextField(blank=True, verbose_name="Notes")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Saisie d'entrée liée"
        verbose_name_plural = "Saisies d'entrées liées"
        ordering = ['-date_creation']

    def __str__(self):
        if self.matiere_premiere and self.quantite:
            return f"Entrée de {self.quantite} {self.matiere_premiere.unite_mesure} de {self.matiere_premiere.nom} - {self.fournisseur.nom}"
        elif self.fournisseur:
            return f"Entrée de {self.fournisseur.nom}"
        else:
            return f"Entrée #{self.id}"

    def save(self, *args, **kwargs):
        """Crée automatiquement le mouvement de stock lors de la première sauvegarde"""
        # Ne créer le mouvement de stock que si tous les champs requis sont présents
        if not self.mouvement_stock and self.matiere_premiere and self.quantite and self.matiere_premiere_id and self.quantite > 0:
            # Créer un nouveau mouvement de stock pour cette entrée
            self.mouvement_stock = MouvementStock.objects.create(
                matiere_premiere=self.matiere_premiere,
                quantite=self.quantite,
                type_mouvement='entree',
                description=f"Entrée via facture {self.numero_facture} du fournisseur {self.fournisseur.nom}" if self.numero_facture else f"Entrée du fournisseur {self.fournisseur.nom}"
            )
        elif self.mouvement_stock and self.matiere_premiere and self.quantite and self.matiere_premiere_id and self.quantite > 0:
            # Si le mouvement existe déjà, mettre à jour la quantité et la matière première si nécessaire
            if self.mouvement_stock.matiere_premiere != self.matiere_premiere:
                self.mouvement_stock.matiere_premiere = self.matiere_premiere
            if self.mouvement_stock.quantite != self.quantite:
                self.mouvement_stock.quantite = self.quantite
            self.mouvement_stock.save()
        
        super().save(*args, **kwargs)

    @property
    def montant_ttc(self):
        """Calcule le montant TTC du prix d'achat"""
        if self.prix_achat_ht and self.taux_tva:
            return self.prix_achat_ht * (1 + self.taux_tva / 100)
        return None

    @property
    def montant_tva(self):
        """Calcule le montant de la TVA"""
        if self.prix_achat_ht and self.taux_tva:
            return self.prix_achat_ht * (self.taux_tva / 100)
        return None
    
    @property
    def montant_total_ttc(self):
        """Calcule le montant total TTC (quantité × prix unitaire TTC)"""
        if self.quantite and self.montant_ttc:
            return self.quantite * self.montant_ttc
        return None
