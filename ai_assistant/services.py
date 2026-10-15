import json
import logging
import time

import requests
from django.conf import settings
from django.db.models import Count, Max, Min, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}"
STREAM_URL = GEMINI_BASE + ":streamGenerateContent?alt=sse"

SYSTEM_PROMPT = (
    "Tu es l'assistant IA de SITRAD, une centrale à béton. "
    "Tu aides les gestionnaires, commerciaux et opérateurs en proposant des idées, "
    "des analyses et des recommandations concrètes (production, ventes, encaissements, "
    "stock, coûts, organisation). Réponds toujours en français, de façon claire et structurée. "
    "Lorsque des données de l'entreprise sont fournies, appuie ton analyse sur ces chiffres. "
    "La date du jour te sera fournie : utilise-la comme référence absolue et ne considère jamais "
    "une date passée ou égale comme future. "
    "Ne prétends jamais disposer d'une information absente des données fournies : "
    "si un chiffre n'y figure pas, dis-le explicitement au lieu d'inventer une valeur."
)


def _money(value):
    try:
        return f"{float(value or 0):,.2f}".replace(",", " ")
    except (TypeError, ValueError):
        return "0.00"


def build_business_context():
    """Construit un instantané des données réelles de l'entreprise pour alimenter l'IA."""
    lines = []

    aujourd_hui = timezone.localdate()
    lines.append(
        "- Date du jour (référence absolue pour tes calculs) : "
        f"{aujourd_hui.strftime('%d/%m/%Y')} ({aujourd_hui.isoformat()})"
    )

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

        bornes = qs.aggregate(dmin=Min("date_production"), dmax=Max("date_production"))
        if bornes["dmin"] and bornes["dmax"]:
            lines.append(
                "- Période couverte par les productions : du "
                f"{bornes['dmin'].strftime('%d/%m/%Y')} au {bornes['dmax'].strftime('%d/%m/%Y')}"
            )

        par_jour = (
            qs.values("date_production")
            .annotate(nb=Count("id"), volume=Sum("quantite_produire"))
            .order_by("-date_production")[:15]
        )
        detail = " | ".join(
            f"{r['date_production'].strftime('%d/%m/%Y')} : "
            f"{_money(r['volume'])} m³ ({r['nb']} bons)"
            for r in par_jour if r["date_production"]
        )
        if detail:
            lines.append(f"- Production par jour (15 derniers jours produits) : {detail}")

        aujourd_hui_qs = qs.filter(date_production=aujourd_hui)
        lines.append(
            f"- Production du jour ({aujourd_hui.strftime('%d/%m/%Y')}) : "
            f"{_money(aujourd_hui_qs.aggregate(v=Sum('quantite_produire')).get('v'))} m³ "
            f"sur {aujourd_hui_qs.count()} bons"
        )
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


def _headers(api_key):
    return {"x-goog-api-key": api_key, "Content-Type": "application/json"}


def _extract_sse_text(lines):
    """Agrège le texte des réponses SSE de Gemini (en ignorant les 'thoughts')."""
    parts = []
    for line in lines:
        if isinstance(line, (bytes, bytearray)):
            line = line.decode("utf-8", "ignore")
        line = (line or "").strip()
        if not line.startswith("data: "):
            continue
        chunk = line[6:].strip()
        if not chunk or chunk == "[DONE]":
            continue
        try:
            data = json.loads(chunk)
        except ValueError:
            continue
        for cand in data.get("candidates") or []:
            content = cand.get("content") or {}
            for part in content.get("parts") or []:
                if part.get("text") and not part.get("thought"):
                    parts.append(part["text"])
    return "".join(parts).strip()


def _call_streaming(model, api_key, payload, timeout):
    """Appelle Gemini en streaming (SSE) pour éviter les timeouts de lecture.

    Renvoie (texte, status_code, corps_d_erreur).
    """
    url = STREAM_URL.format(model=model)
    resp = requests.post(
        url, headers=_headers(api_key), json=payload, stream=True,
        timeout=(10, timeout),
    )
    if resp.status_code != 200:
        body = resp.text[:400]
        resp.close()
        return None, resp.status_code, body
    try:
        text = _extract_sse_text(resp.iter_lines())
    finally:
        resp.close()
    return text, 200, ""


def call_gemini(contents, business_context=""):
    """Appelle l'API Google Gemini et renvoie (texte, erreur)."""
    api_key = getattr(settings, "GEMINI_API_KEY", "") or ""
    if not api_key:
        return None, "Clé API Gemini non configurée (GEMINI_API_KEY)."

    model = getattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
    timeout = getattr(settings, "GEMINI_TIMEOUT", 90)
    thinking_level = str(getattr(settings, "GEMINI_THINKING_LEVEL", "low")).strip().lower()
    if thinking_level not in ("minimal", "low", "medium", "high"):
        thinking_level = "low"

    system_text = SYSTEM_PROMPT
    if business_context:
        system_text = f"{SYSTEM_PROMPT}\n\n{business_context}"

    payload = {
        "systemInstruction": {"parts": [{"text": system_text}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1500,
            # Réduit le temps de "réflexion" (valeurs : minimal/low/medium/high, minuscules).
            "thinkingConfig": {"thinkingLevel": thinking_level},
        },
    }

    started = time.monotonic()
    logger.info("Gemini appel : model=%s thinking=%s", model, thinking_level)
    try:
        text, status_code, body = _call_streaming(model, api_key, payload, timeout)
        # Si le paramètre de réflexion est refusé, on réessaie sans.
        if status_code == 400 and "thinking" in body.lower():
            logger.warning("thinkingConfig refusé, essai sans : %s", body)
            payload["generationConfig"].pop("thinkingConfig", None)
            text, status_code, body = _call_streaming(model, api_key, payload, timeout)
    except requests.RequestException as exc:
        elapsed = time.monotonic() - started
        logger.error("Erreur réseau Gemini après %.1fs : %s", elapsed, exc)
        return None, "Le service IA met trop de temps à répondre. Réessayez dans un instant."

    elapsed = time.monotonic() - started
    logger.info("Gemini répondu en %.1fs (HTTP %s)", elapsed, status_code)

    if status_code != 200:
        logger.error("Gemini HTTP %s : %s", status_code, body)
        return None, f"Erreur du service IA (HTTP {status_code}) : {body[:200]}"

    if not text:
        return None, "L'IA n'a pas renvoyé de texte (réponse vide)."
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
