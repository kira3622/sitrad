"""Envoi de messages vers un groupe WhatsApp via UltraMsg.

Configuration (variables d'environnement) :
- ``ULTRAMSG_INSTANCE_ID`` : identifiant de l'instance UltraMsg (ex. ``instance123456``)
- ``ULTRAMSG_TOKEN`` : jeton de l'instance UltraMsg
- ``WHATSAPP_GROUP_ID`` : identifiant du groupe, se terminant par ``@g.us``
- ``ULTRAMSG_BASE_URL`` : optionnel (par défaut ``https://api.ultramsg.com``)

Tant que ces variables ne sont pas renseignées, l'envoi est ignoré
(``est_configure()`` renvoie ``False``) sans jamais faire échouer l'enregistrement.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TIMEOUT = 15


def est_configure():
    """Indique si les identifiants UltraMsg et le groupe sont renseignés."""
    return bool(
        getattr(settings, 'ULTRAMSG_INSTANCE_ID', '')
        and getattr(settings, 'ULTRAMSG_TOKEN', '')
        and getattr(settings, 'WHATSAPP_GROUP_ID', '')
    )


def envoyer_message_groupe(message):
    """Envoie un message texte au groupe WhatsApp configuré.

    Retourne ``(ok, detail)``. Ne lève jamais d'exception : une erreur réseau
    ou de configuration est renvoyée sous forme de message.
    """
    if not est_configure():
        return False, (
            "WhatsApp non configuré : renseignez ULTRAMSG_INSTANCE_ID, "
            "ULTRAMSG_TOKEN et WHATSAPP_GROUP_ID."
        )

    url = f"{settings.ULTRAMSG_BASE_URL}/{settings.ULTRAMSG_INSTANCE_ID}/messages/chat"
    donnees = {
        'token': settings.ULTRAMSG_TOKEN,
        'to': settings.WHATSAPP_GROUP_ID,
        'body': message,
    }
    try:
        reponse = requests.post(url, data=donnees, timeout=TIMEOUT)
    except requests.RequestException as exc:
        logger.warning("Envoi WhatsApp impossible : %s", exc)
        return False, f"Erreur réseau : {exc}"

    if reponse.status_code != 200:
        logger.warning("UltraMsg a répondu %s : %s", reponse.status_code, reponse.text[:200])
        return False, f"HTTP {reponse.status_code} : {reponse.text[:200]}"

    try:
        charge = reponse.json()
    except ValueError:
        return True, reponse.text[:200]

    if str(charge.get('sent', '')).lower() == 'true':
        return True, reponse.text[:200]
    detail = charge.get('message') or charge.get('error') or reponse.text[:200]
    logger.warning("UltraMsg a refusé l'envoi : %s", detail)
    return False, str(detail)


def message_nouvelle_saisie(saisie):
    """Construit le texte du message pour une nouvelle livraison planifiée."""
    lignes = ["📅 Nouvelle livraison planifiée"]
    if saisie.heure_livraison:
        lignes.append(f"🗓️ {saisie.date_livraison.strftime('%d/%m/%Y')} à {saisie.heure_livraison.strftime('%H:%M')}")
    else:
        lignes.append(f"🗓️ {saisie.date_livraison.strftime('%d/%m/%Y')}")
    lignes.append(f"👤 Client : {saisie.client}")
    if saisie.chantier:
        lignes.append(f"🏗️ Chantier : {saisie.chantier}")
    if saisie.formule:
        lignes.append(f"🧱 Formule : {saisie.formule}")
    if saisie.quantite:
        lignes.append(f"📦 Quantité : {saisie.quantite} m³")
    if saisie.vehicule:
        lignes.append(f"🚚 Véhicule : {saisie.vehicule.immatriculation}")
    if saisie.adresse:
        lignes.append(f"📍 Adresse : {saisie.adresse}")
    if saisie.observation:
        lignes.append(f"📝 Observation : {saisie.observation}")
    return "\n".join(lignes)
