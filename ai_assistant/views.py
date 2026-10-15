import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Conversation
from .services import generate_assistant_reply


def _get_or_create_conversation(user, conversation_id=None, avec_donnees=True):
    if conversation_id:
        conv = Conversation.objects.filter(id=conversation_id, user=user).first()
        if conv:
            return conv
    return Conversation.objects.create(user=user, avec_donnees=avec_donnees)


def _autotitle(conversation, user_text):
    if conversation.titre in ("", "Nouvelle conversation"):
        conversation.titre = user_text[:60]
        conversation.save(update_fields=["titre"])


@staff_member_required
def chat_page(request):
    conversations = Conversation.objects.filter(user=request.user)[:30]
    return render(request, "ai_assistant/chat.html", {"conversations": conversations})


@login_required
@require_POST
def chat_send(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Requête invalide."}, status=400)

    user_text = (payload.get("message") or "").strip()
    if not user_text:
        return JsonResponse({"error": "Message vide."}, status=400)

    avec_donnees = payload.get("avec_donnees", True)
    conversation = _get_or_create_conversation(
        request.user, payload.get("conversation_id"), avec_donnees
    )
    _autotitle(conversation, user_text)

    reply, error = generate_assistant_reply(conversation, user_text)
    if error:
        return JsonResponse({"error": error, "conversation_id": conversation.id}, status=502)

    return JsonResponse({
        "conversation_id": conversation.id,
        "reply": reply,
        "titre": conversation.titre,
    })


class AIChatView(APIView):
    """Endpoint REST pour l'application mobile Android."""

    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_text = (request.data.get("message") or "").strip()
        if not user_text:
            return Response({"error": "Message vide."}, status=status.HTTP_400_BAD_REQUEST)

        avec_donnees = request.data.get("avec_donnees", True)
        conversation = _get_or_create_conversation(
            request.user, request.data.get("conversation_id"), avec_donnees
        )
        _autotitle(conversation, user_text)

        reply, error = generate_assistant_reply(conversation, user_text)
        if error:
            return Response(
                {"error": error, "conversation_id": conversation.id},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            "conversation_id": conversation.id,
            "reply": reply,
            "titre": conversation.titre,
        })
