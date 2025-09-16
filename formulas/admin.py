from django.contrib import admin
from .models import FormuleBeton, CompositionFormule

class CompositionFormuleInline(admin.TabularInline):
    model = CompositionFormule
    extra = 1  # Number of extra forms to display

@admin.register(FormuleBeton)
class FormuleBetonAdmin(admin.ModelAdmin):
    inlines = [CompositionFormuleInline]
    list_display = ('nom', 'resistance_requise')
    search_fields = ('nom',)

# Optional: Register CompositionFormule if you want to manage it directly
# @admin.register(CompositionFormule)
# class CompositionFormuleAdmin(admin.ModelAdmin):
#     list_display = ('formule', 'matiere_premiere', 'quantite')
#     list_filter = ('formule', 'matiere_premiere')
