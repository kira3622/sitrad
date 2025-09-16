from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LotProduction
from stock.models import MouvementStock

@receiver(post_save, sender=LotProduction)
def deduire_stock_apres_production(sender, instance, created, **kwargs):
    if created:
        ordre_production = instance.ordre_production
        formule = ordre_production.formule
        quantite_produite = instance.quantite_produite

        for composition in formule.composition.all():
            matiere_premiere = composition.matiere_premiere
            quantite_necessaire = (composition.quantite / formule.quantite_produite_reference) * quantite_produite

            MouvementStock.objects.create(
                matiere_premiere=matiere_premiere,
                quantite=quantite_necessaire,
                type_mouvement='sortie',
                description=f"Production du lot {instance.id} (Ordre {ordre_production.id})"
            )