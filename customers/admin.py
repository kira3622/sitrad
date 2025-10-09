from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Client, Chantier

class ClientForm(forms.ModelForm):
    id = forms.IntegerField(
        required=False,
        help_text="Laissez vide pour génération automatique ou entrez un ID personnalisé",
        label="ID Client"
    )
    
    class Meta:
        model = Client
        fields = ['id', 'nom', 'adresse', 'telephone', 'email']

class ChantierInline(admin.TabularInline):
    model = Chantier
    extra = 1
    readonly_fields = ('nombre_commandes_display', 'statut_chantier_display')
    
    def nombre_commandes_display(self, obj):
        if obj.pk:
            return obj.nombre_commandes()
        return "-"
    nombre_commandes_display.short_description = "Nb commandes"
    
    def statut_chantier_display(self, obj):
        if obj.pk:
            statut = obj.statut_chantier()
            if statut == "Actif":
                return format_html('<span style="color: green; font-weight: bold;">🟢 {}</span>', statut)
            elif statut == "Terminé":
                return format_html('<span style="color: orange; font-weight: bold;">🟠 {}</span>', statut)
            else:
                return format_html('<span style="color: gray;">⚪ {}</span>', statut)
        return "-"
    statut_chantier_display.short_description = "Statut"

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    inlines = [ChantierInline]
    list_display = ('id', 'nom', 'adresse', 'telephone', 'email', 'nombre_chantiers_display', 'chantiers_actifs_display')
    search_fields = ('nom', 'adresse', 'email')
    list_filter = ('chantiers__commande__statut',)
    fields = ('id', 'nom', 'adresse', 'telephone', 'email')
    
    def nombre_chantiers_display(self, obj):
        count = obj.nombre_chantiers()
        if count > 0:
            return format_html('<span style="font-weight: bold; color: #2196F3;">{}</span>', count)
        return "0"
    nombre_chantiers_display.short_description = "Nb chantiers"
    
    def chantiers_actifs_display(self, obj):
        actifs = obj.chantiers_actifs().count()
        if actifs > 0:
            return format_html('<span style="color: green; font-weight: bold;">🟢 {}</span>', actifs)
        return format_html('<span style="color: gray;">⚪ 0</span>')
    chantiers_actifs_display.short_description = "Chantiers actifs"

@admin.register(Chantier)
class ChantierAdmin(admin.ModelAdmin):
    list_display = ('nom', 'client', 'adresse', 'nombre_commandes_display', 'statut_chantier_display', 'derniere_commande_display')
    list_filter = ('client', 'commande__statut')
    search_fields = ('nom', 'adresse', 'client__nom')
    readonly_fields = ('nombre_commandes_display', 'statut_chantier_display', 'derniere_commande_display')
    
    def nombre_commandes_display(self, obj):
        count = obj.nombre_commandes()
        if count > 0:
            return format_html('<span style="font-weight: bold; color: #2196F3;">{}</span>', count)
        return "0"
    nombre_commandes_display.short_description = "Nb commandes"
    
    def statut_chantier_display(self, obj):
        statut = obj.statut_chantier()
        if statut == "Actif":
            return format_html('<span style="color: green; font-weight: bold;">🟢 {}</span>', statut)
        elif statut == "Terminé":
            return format_html('<span style="color: orange; font-weight: bold;">🟠 {}</span>', statut)
        else:
            return format_html('<span style="color: gray;">⚪ {}</span>', statut)
    statut_chantier_display.short_description = "Statut"
    
    def derniere_commande_display(self, obj):
        derniere = obj.derniere_commande()
        if derniere:
            return format_html('{} ({})', derniere.date_commande.strftime('%d/%m/%Y'), derniere.get_statut_display())
        return "Aucune"
    derniere_commande_display.short_description = "Dernière commande"
