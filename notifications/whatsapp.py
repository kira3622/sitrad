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


def _format_date(valeur):
    """Formate une date (objet ``date``/``datetime`` ou chaîne « AAAA-MM-JJ ») en jj/mm/aaaa."""
    if hasattr(valeur, 'strftime'):
        return valeur.strftime('%d/%m/%Y')
    return str(valeur)


def _format_heure(valeur):
    """Formate une heure (objet ``time``) en hh:mm."""
    if hasattr(valeur, 'strftime'):
        return valeur.strftime('%H:%M')
    return str(valeur)


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
        lignes.append(f"🗓️ {_format_date(saisie.date_livraison)} à {_format_heure(saisie.heure_livraison)}")
    else:
        lignes.append(f"🗓️ {_format_date(saisie.date_livraison)}")
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


def message_nouvel_ordre(ordre):
    """Construit le texte du message pour un nouvel ordre de production."""
    lignes = ["🏭 Nouvel ordre de production"]
    if ordre.numero_bon:
        lignes.append(f"🔖 Bon N° : {ordre.numero_bon}")
    commande = ordre.commande
    if commande is not None:
        lignes.append(f"👤 Client : {commande.client}")
        if commande.chantier:
            lignes.append(f"🏗️ Chantier : {commande.chantier}")
    if ordre.formule:
        lignes.append(f"🧱 Formule : {ordre.formule}")
    lignes.append(f"📦 Quantité : {ordre.quantite_produire} m³")
    if ordre.heure_production:
        lignes.append(
            f"🗓️ {_format_date(ordre.date_production)} à {_format_heure(ordre.heure_production)}"
        )
    else:
        lignes.append(f"🗓️ {_format_date(ordre.date_production)}")
    if ordre.vehicule:
        lignes.append(f"🚚 Véhicule : {ordre.vehicule.immatriculation}")
    if ordre.chauffeur:
        lignes.append(f"👷 Chauffeur : {ordre.chauffeur.nom}")
    if ordre.pompe:
        lignes.append(f"🚛 Pompe : {ordre.pompe}")
    lignes.append(f"📌 Statut : {ordre.get_statut_display()}")
    return "\n".join(lignes)
