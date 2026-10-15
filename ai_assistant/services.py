import logging

import requests
from django.conf import settings
from django.db.models import Count, Sum

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = (
    "Tu es l'assistant IA de SITRAD, une centrale à béton. "
    "Tu aides les gestionnaires, commerciaux et opérateurs en proposant des idées, "
    "des analyses et des recommandations concrètes (production, ventes, encaissements, "
    "stock, coûts, organisation). Réponds toujours en français, de façon claire et structurée. "
    "Lorsque des données de l'entreprise sont fournies, appuie ton analyse sur ces chiffres."
)


def _money(value):
    try:
        return f"{float(value or 0):,.2f}".replace(",", " ")
    except (TypeError, ValueError):
        return "0.00"


def build_business_context():
    """Construit un instantané des données réelles de l'entreprise pour alimenter l'IA."""
    lines = []

    try:
        from customers.models import Client
        lines.append(f"- Nombre de clients : {Client.objects.count()}")
    except Exception as exc:
        logger.warning("Contexte clients indisponible : %s", exc)

    try:
        from production.models import OrdreProduction
        qs = OrdreProduction.objects.all()

        def montant(o):
            return (o.quantite_produire or 0) * (o.prix_vente_unitaire or 0) \
                + (o.prix_deplacement_pompe or 0) + (o.prix_deplacement_camion or 0)

        total_montant = sum(montant(o) for o in qs)
        lines.append(f"- Nombre de bons de production : {qs.count()}")
        lines.append(
            f"- Volume total produit : "
            f"{_money(qs.aggregate(v=Sum('quantite_produire')).get('v'))} m³"
        )
        lines.append(f"- Montant total des bons : {_money(total_montant)} MAD")
    except Exception as exc:
        logger.warning("Contexte production indisponible : %s", exc)

    try:
        from encaissement.models import Encaissement
        qs = Encaissement.objects.all()
        lines.append(f"- Nombre d'encaissements : {qs.count()}")
        lines.append(
            f"- Total encaissé : {_money(qs.aggregate(m=Sum('montant')).get('m'))} MAD"
        )
    except Exception as exc:
        logger.warning("Contexte encaissements indisponible : %s", exc)

    try:
        from production.models import OrdreProduction
        top = (
            OrdreProduction.objects.values("commande__client__nom")
            .annotate(nb=Count("id")).order_by("-nb")[:5]
        )
        items = ", ".join(
            f"{t['commande__client__nom'] or 'Inconnu'} ({t['nb']})" for t in top
        )
        if items:
            lines.append(f"- Top clients par nombre de bons : {items}")
    except Exception as exc:
        logger.warning("Contexte top clients indisponible : %s", exc)

    if not lines:
        return ""
    return "Données actuelles de l'entreprise :\n" + "\n".join(lines)


def _convert_history(messages):
    contents = []
    for msg in messages:
        role = "user" if msg.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg.contenu}]})
    return contents


def _post_gemini(url, api_key, payload, timeout):
    return requests.post(
        url,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=timeout,
    )


def call_gemini(contents, business_context=""):
    """Appelle l'API Google Gemini et renvoie (texte, erreur)."""
    api_key = getattr(settings, "GEMINI_API_KEY", "") or ""
    if not api_key:
        return None, "Clé API Gemini non configurée (GEMINI_API_KEY)."

    model = getattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
    url = GEMINI_URL.format(model=model)
    timeout = getattr(settings, "GEMINI_TIMEOUT", 90)
    thinking_level = getattr(settings, "GEMINI_THINKING_LEVEL", "LOW")

    system_text = SYSTEM_PROMPT
    if business_context:
        system_text = f"{SYSTEM_PROMPT}\n\n{business_context}"

    generation_config = {
        "temperature": 0.7,
        "maxOutputTokens": 1500,
        # Réduit le temps de "réflexion" du modèle pour éviter les timeouts.
        "thinkingConfig": {"thinkingLevel": thinking_level},
    }
    payload = {
        "systemInstruction": {"parts": [{"text": system_text}]},
        "contents": contents,
        "generationConfig": generation_config,
    }

    try:
        resp = _post_gemini(url, api_key, payload, timeout)
        # Si le modèle ne supporte pas thinkingConfig, on réessaie sans.
        if resp.status_code == 400 and "thinking" in resp.text.lower():
            logger.warning("thinkingConfig refusé, nouvel essai sans : %s", resp.text[:300])
            generation_config.pop("thinkingConfig", None)
            resp = _post_gemini(url, api_key, payload, timeout)
    except requests.RequestException as exc:
        logger.error("Erreur réseau Gemini : %s", exc)
        return None, "Le service IA met trop de temps à répondre. Réessayez."

    if resp.status_code != 200:
        logger.error("Gemini HTTP %s : %s", resp.status_code, resp.text[:500])
        return None, f"Erreur du service IA (HTTP {resp.status_code})."

    try:
        data = resp.json()
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if p.get("text")).strip()
    except (KeyError, IndexError, ValueError) as exc:
        logger.error("Réponse Gemini inattendue : %s", exc)
        return None, "Réponse IA illisible."

    if not text:
        return None, "L'IA n'a pas renvoyé de texte."
    return text, None



def generate_assistant_reply(conversation, user_text):
    """Enregistre le message utilisateur, interroge Gemini et enregistre la réponse."""
    from .models import Message

    Message.objects.create(conversation=conversation, role="user", contenu=user_text)
    history = list(conversation.messages.order_by("date_creation"))
    contents = _convert_history(history)
    business_context = build_business_context() if conversation.avec_donnees else ""

    text, error = call_gemini(contents, business_context)
    if error:
        return None, error

    Message.objects.create(conversation=conversation, role="model", contenu=text)
    return text, None
