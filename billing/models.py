from django.db import models
from orders.models import Commande
from decimal import Decimal
from django.utils import timezone

class Facture(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    MODE_REGLEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement'),
        ('carte', 'Carte bancaire'),
        ('traite', 'Traite'),
    ]
    
    # Relations
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    
    # Informations de base
    date_facturation = models.DateField(auto_now_add=True)
    reference = models.CharField(max_length=50, unique=True, blank=True, help_text="Référence de la facture")
    objet = models.CharField(max_length=255, default="Fourniture de béton", help_text="Objet de la facture")
    
    # Montants
    montant_ht = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Montant hors taxes")
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=20.00, help_text="Taux de TVA en %")
    montant_tva = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Montant de la TVA")
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0, help_text="Montant TTC")
    
    # Règlement
    mode_reglement = models.CharField(max_length=20, choices=MODE_REGLEMENT_CHOICES, default='virement')
    date_reglement = models.DateField(null=True, blank=True, help_text="Date prévue de règlement")
    numero_reglement = models.CharField(max_length=100, blank=True, help_text="Numéro de chèque, virement, etc.")
    delai_reglement = models.IntegerField(default=30, help_text="Délai de règlement en jours")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Générer une référence automatique si elle n'existe pas
        if not self.reference:
            from datetime import datetime
            annee = timezone.now().year
            
            # Trouver la dernière facture pour cette année
            dernieres_factures = Facture.objects.filter(
                reference__startswith=f"F{annee}"
            ).order_by('-reference')
            
            if dernieres_factures.exists():
                derniere_reference = dernieres_factures.first().reference
                # Extraire le numéro séquentiel (les 4 derniers chiffres)
                try:
                    sequence = int(derniere_reference[-4:]) + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
            
            self.reference = f"F{annee}{sequence:04d}"
        
        # Sauvegarder d'abord pour avoir un ID et que date_facturation soit définie
        super().save(*args, **kwargs)
        
        # Calculer la date de règlement si elle n'est pas définie
        if not self.date_reglement and self.delai_reglement and self.date_facturation:
            from datetime import timedelta
            self.date_reglement = self.date_facturation + timedelta(days=self.delai_reglement)
            # Sauvegarder à nouveau pour mettre à jour date_reglement
            super().save(update_fields=['date_reglement'])
        
        # Puis calculer et mettre à jour les montants
        self.calculer_montants()

    def calculer_montants(self):
        """Calcule tous les montants de la facture"""
        # Calculer le montant HT
        montant_ht = sum(ligne.montant_ligne for ligne in self.lignes.all())
        
        # Calculer la TVA
        montant_tva = montant_ht * (self.taux_tva / 100)
        
        # Calculer le montant TTC
        montant_ttc = montant_ht + montant_tva
        
        # Mettre à jour si nécessaire
        if (self.montant_ht != montant_ht or 
            self.montant_tva != montant_tva or 
            self.montant_total != montant_ttc):
            
            self.montant_ht = montant_ht
            self.montant_tva = montant_tva
            self.montant_total = montant_ttc
            super().save(update_fields=['montant_ht', 'montant_tva', 'montant_total'])

    def get_numero_facture(self):
        """Retourne le numéro de facture formaté"""
        return f"F{self.id:06d}"

    def __str__(self):
        return f"Facture {self.get_numero_facture()} - {self.commande.client.nom if hasattr(self.commande, 'client') else 'Client'}"

    class Meta:
        ordering = ['-date_facturation']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"


class LigneFacture(models.Model):
    UNITE_CHOICES = [
        ('m3', 'Mètre cube (m³)'),
        ('tonne', 'Tonne'),
        ('unite', 'Unité'),
        ('forfait', 'Forfait'),
    ]
    
    facture = models.ForeignKey(Facture, related_name='lignes', on_delete=models.CASCADE)
    description = models.CharField(max_length=255, help_text="Description de la prestation")
    unite = models.CharField(max_length=20, choices=UNITE_CHOICES, default='m3', help_text="Unité de mesure")
    quantite = models.DecimalField(max_digits=10, decimal_places=3, help_text="Quantité")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix unitaire HT")
    montant_ligne = models.DecimalField(max_digits=12, decimal_places=2, help_text="Montant de la ligne HT")
    
    # Ordre d'affichage
    ordre = models.PositiveIntegerField(default=1, help_text="Ordre d'affichage dans la facture")

    def save(self, *args, **kwargs):
        # Calculer automatiquement le montant de la ligne
        self.montant_ligne = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
        
        # Mettre à jour les montants de la facture
        if self.facture:
            self.facture.calculer_montants()

    def delete(self, *args, **kwargs):
        facture = self.facture
        super().delete(*args, **kwargs)
        # Recalculer les montants après suppression
        if facture:
            facture.calculer_montants()

    def __str__(self):
        return f"{self.description} - {self.quantite} {self.unite}"

    class Meta:
        ordering = ['ordre', 'id']
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
