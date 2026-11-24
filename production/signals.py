import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.whatsapp import envoyer_message_groupe, message_nouvel_ordre

from .models import LotProduction, OrdreProduction
from stock.models import MouvementStock

logger = logging.getLogger(__name__)


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


@receiver(post_save, sender=OrdreProduction)
def notifier_whatsapp_nouvel_ordre(sender, instance, created, **kwargs):
    """Envoie un message WhatsApp au groupe à la création d'un ordre de production."""
    if not created:
        return

    def envoyer():
        # Une notification ne doit jamais faire échouer l'enregistrement de l'ordre.
        try:
            ok, detail = envoyer_message_groupe(message_nouvel_ordre(instance))
        except Exception as exc:  # pragma: no cover - filet de sécurité
            logger.warning("Notification WhatsApp impossible (ordre %s) : %s", instance.pk, exc)
            return
        if not ok:
            logger.warning("Notification WhatsApp non envoyée (ordre %s) : %s", instance.pk, detail)

    # Envoi après validation de la transaction pour ne jamais notifier un ordre annulé.
    transaction.on_commit(envoyer)