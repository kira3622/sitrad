from django.db import models
from django.db import transaction
from orders.models import Commande
from formulas.models import FormuleBeton
from logistics.models import Chauffeur, Vehicule

class OrdreProduction(models.Model):
    numero_bon = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="Numéro de bon de production")
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    formule = models.ForeignKey(FormuleBeton, on_delete=models.CASCADE)
    quantite_produire = models.DecimalField(max_digits=10, decimal_places=2)
    date_production = models.DateField()
    heure_production = models.TimeField(null=True, blank=True, help_text="Heure prévue de production")
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordres_production')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordres_production')
    statut = models.CharField(max_length=20, choices=[('planifie', 'Planifié'), ('en_cours', 'En cours'), ('termine', 'Terminé'), ('annule', 'Annulé')], default='planifie')
    matieres_sorties_calculees = models.BooleanField(default=False)  # Pour éviter les doublons

    def save(self, *args, **kwargs):
        if not self.numero_bon:
            # Générer un numéro de bon automatique
            from datetime import datetime
            date_str = datetime.now().strftime("%Y%m%d")
            
            # Trouver le dernier numéro pour aujourd'hui
            derniers_ordres = OrdreProduction.objects.filter(
                numero_bon__startswith=f"BP{date_str}"
            ).order_by('-numero_bon')
            
            if derniers_ordres.exists():
                dernier_numero = derniers_ordres.first().numero_bon
                # Extraire le numéro séquentiel (les 3 derniers chiffres)
                try:
                    sequence = int(dernier_numero[-3:]) + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
            
            self.numero_bon = f"BP{date_str}{sequence:03d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bon {self.numero_bon} - Ordre de production {self.id} pour la commande {self.commande.id}"

    def calculer_sorties_matieres(self):
        """
        Calcule les quantités de matières premières nécessaires pour cet ordre de production
        basé sur la formule et la quantité à produire.
        """
        try:
            sorties_calculees = []
            
            # Vérifications préliminaires
            if not self.formule:
                raise ValueError("Aucune formule associée à cet ordre de production")
            
            if not self.quantite_produire or self.quantite_produire <= 0:
                raise ValueError("Quantité à produire invalide ou nulle")
            
            if not self.formule.quantite_produite_reference or self.formule.quantite_produite_reference <= 0:
                raise ValueError(f"Quantité de référence invalide pour la formule '{self.formule.nom}' (valeur: {self.formule.quantite_produite_reference})")
            
            # Récupérer la composition de la formule
            compositions = self.formule.composition.all()
            
            if not compositions.exists():
                raise ValueError(f"La formule '{self.formule.nom}' n'a pas de composition définie (aucune matière première)")
            
            # Calculer le facteur de multiplication
            quantite_reference = self.formule.quantite_produite_reference
            facteur_multiplication = self.quantite_produire / quantite_reference
            
            for composition in compositions:
                # Vérifications pour chaque composition
                if not composition.matiere_premiere:
                    continue  # Ignorer les compositions sans matière première
                
                if not composition.quantite or composition.quantite <= 0:
                    continue  # Ignorer les quantités nulles ou négatives
                
                # Calculer la quantité nécessaire proportionnellement
                quantite_necessaire = composition.quantite * facteur_multiplication
                
                sorties_calculees.append({
                    'matiere_premiere': composition.matiere_premiere,
                    'quantite_necessaire': quantite_necessaire,
                    'quantite_formule': composition.quantite,
                    'facteur': facteur_multiplication
                })
            
            if not sorties_calculees:
                raise ValueError("Aucune matière première valide trouvée dans la composition de la formule")
            
            return sorties_calculees
            
        except Exception as e:
            # Log l'erreur pour le débogage
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors du calcul des sorties pour l'ordre {self.id}: {str(e)}")
            
            # Relancer l'exception avec plus de contexte
            raise ValueError(f"Impossible de calculer les sorties de matières: {str(e)}")

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
