from django.contrib.auth.models import User
from django.db import models


class Conversation(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ai_conversations",
        null=True, blank=True, verbose_name="Utilisateur",
    )
    titre = models.CharField(max_length=200, blank=True, default="Nouvelle conversation")
    avec_donnees = models.BooleanField(
        default=True, verbose_name="Utiliser les données de l'entreprise",
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_maj"]
        verbose_name = "Conversation IA"
        verbose_name_plural = "Conversations IA"

    def __str__(self):
        return self.titre or f"Conversation #{self.id}"


class Message(models.Model):
    ROLE_CHOICES = [("user", "Utilisateur"), ("model", "Assistant")]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_creation"]
        verbose_name = "Message IA"
        verbose_name_plural = "Messages IA"

    def __str__(self):
        return f"{self.get_role_display()}: {self.contenu[:50]}"
