from django.db import models
from django.db import transaction
from orders.models import Commande
from formulas.models import FormuleBeton

class OrdreProduction(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    formule = models.ForeignKey(FormuleBeton, on_delete=models.CASCADE)
    quantite_produire = models.DecimalField(max_digits=10, decimal_places=2)
    date_production = models.DateField()
    statut = models.CharField(max_length=20, choices=[('planifie', 'Planifié'), ('en_cours', 'En cours'), ('termine', 'Terminé'), ('annule', 'Annulé')], default='planifie')
    matieres_sorties_calculees = models.BooleanField(default=False)  # Pour éviter les doublons

    def __str__(self):
        return f"Ordre de production {self.id} pour la commande {self.commande.id}"

    def calculer_sorties_matieres(self):
        """
        Calcule les quantités de matières premières nécessaires pour cet ordre de production
        basé sur la formule et la quantité à produire.
        """
        sorties_calculees = []
        
        # Récupérer la composition de la formule
        compositions = self.formule.composition.all()
        
        for composition in compositions:
            # Calculer la quantité nécessaire proportionnellement
            quantite_reference = self.formule.quantite_produite_reference
            facteur_multiplication = self.quantite_produire / quantite_reference
            quantite_necessaire = composition.quantite * facteur_multiplication
            
            sorties_calculees.append({
                'matiere_premiere': composition.matiere_premiere,
                'quantite_necessaire': quantite_necessaire,
                'quantite_formule': composition.quantite,
                'facteur': facteur_multiplication
            })
        
        return sorties_calculees

    def verifier_stock_disponible(self):
        """
        Vérifie si le stock disponible est suffisant pour cet ordre de production.
        Retourne un dictionnaire avec les matières en rupture.
        """
        sorties = self.calculer_sorties_matieres()
        matieres_insuffisantes = []
        
        for sortie in sorties:
            matiere = sortie['matiere_premiere']
            quantite_necessaire = sortie['quantite_necessaire']
            stock_actuel = matiere.stock_actuel
            
            if stock_actuel < quantite_necessaire:
                matieres_insuffisantes.append({
                    'matiere': matiere,
                    'stock_actuel': stock_actuel,
                    'quantite_necessaire': quantite_necessaire,
                    'manque': quantite_necessaire - stock_actuel
                })
        
        return {
            'stock_suffisant': len(matieres_insuffisantes) == 0,
            'matieres_insuffisantes': matieres_insuffisantes
        }

    @transaction.atomic
    def creer_mouvements_stock(self, force=False):
        """
        Crée automatiquement les mouvements de stock (sorties) pour cet ordre de production.
        
        Args:
            force (bool): Si True, crée les mouvements même si le stock est insuffisant
        
        Returns:
            dict: Résultat de l'opération avec les mouvements créés ou les erreurs
        """
        from stock.models import MouvementStock
        
        # Éviter les doublons
        if self.matieres_sorties_calculees and not force:
            return {
                'success': False,
                'message': 'Les sorties de matières ont déjà été calculées pour cet ordre.'
            }
        
        # Vérifier le stock disponible
        verification_stock = self.verifier_stock_disponible()
        if not verification_stock['stock_suffisant'] and not force:
            return {
                'success': False,
                'message': 'Stock insuffisant pour certaines matières.',
                'matieres_insuffisantes': verification_stock['matieres_insuffisantes']
            }
        
        # Calculer les sorties nécessaires
        sorties = self.calculer_sorties_matieres()
        mouvements_crees = []
        
        for sortie in sorties:
            mouvement = MouvementStock.objects.create(
                matiere_premiere=sortie['matiere_premiere'],
                quantite=sortie['quantite_necessaire'],
                type_mouvement='sortie',
                description=f"Sortie automatique pour ordre de production #{self.id} - {self.formule.nom}"
            )
            mouvements_crees.append(mouvement)
        
        # Marquer comme traité
        self.matieres_sorties_calculees = True
        self.save()
        
        return {
            'success': True,
            'message': f'{len(mouvements_crees)} mouvements de stock créés avec succès.',
            'mouvements': mouvements_crees
        }

class LotProduction(models.Model):
    ordre_production = models.ForeignKey(OrdreProduction, related_name='lots', on_delete=models.CASCADE)
    quantite_produite = models.DecimalField(max_digits=10, decimal_places=2)
    date_heure_production = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lot {self.id} de l'ordre {self.ordre_production.id}"
