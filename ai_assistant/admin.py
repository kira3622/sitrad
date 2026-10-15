from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "contenu", "date_creation")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("titre", "user", "avec_donnees", "date_maj")
    list_filter = ("avec_donnees",)
    search_fields = ("titre", "user__username")
    inlines = [MessageInline]
