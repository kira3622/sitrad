from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Client, Chantier, CommercialDashboard, AgentCommercial
from django.shortcuts import redirect
from django.urls import reverse

class ClientForm(forms.ModelForm):
    id = forms.IntegerField(
        required=False,
        help_text="Laissez vide pour génération automatique ou entrez un ID personnalisé",
        label="ID Client"
    )
    
    class Meta:
        model = Client
        fields = ['id', 'nom', 'adresse', 'telephone', 'email']
    
    def clean_id(self):
        """Validation personnalisée pour l'ID"""
        id_value = self.cleaned_data.get('id')
        
        # Si l'ID est vide, Django générera automatiquement
        if not id_value:
            return id_value
            
        # Vérifier si l'ID existe déjà (sauf pour l'objet actuel)
        if self.instance and self.instance.pk:
            # Modification d'un objet existant
            existing = Client.objects.filter(id=id_value).exclude(pk=self.instance.pk).first()
        else:
            # Création d'un nouvel objet
            existing = Client.objects.filter(id=id_value).first()
            
        if existing:
            raise forms.ValidationError(f"Un client avec l'ID {id_value} existe déjà.")
            
        return id_value
    
    def save(self, commit=True):
        """Sauvegarde personnalisée pour gérer la modification d'ID"""
        # Si c'est une modification et que l'ID a changé
        if self.instance.pk and self.cleaned_data.get('id') and self.cleaned_data.get('id') != self.instance.pk:
            new_id = self.cleaned_data.get('id')
            old_instance = self.instance
            
            if commit:
                # Créer un nouvel objet avec le nouvel ID
                new_instance = Client(
                    id=new_id,
                    nom=self.cleaned_data.get('nom'),
                    adresse=self.cleaned_data.get('adresse'),
                    telephone=self.cleaned_data.get('telephone'),
                    email=self.cleaned_data.get('email')
                )
                new_instance.save()
                
                # Mettre à jour les relations (chantiers, etc.)
                old_instance.chantiers.all().update(client=new_instance)
                
                # Supprimer l'ancien objet
                old_instance.delete()
                
                return new_instance
            else:
                # Mode sans commit, retourner l'instance modifiée
                instance = super().save(commit=False)
                instance.pk = new_id
                instance.id = new_id
                return instance
        
        # Cas normal : pas de changement d'ID
        return super().save(commit=commit)

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
    
    def get_readonly_fields(self, request, obj=None):
        """Permet l'édition de l'ID même sur les objets existants"""
        # Retourne une liste vide pour permettre l'édition de tous les champs
        return []
    
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
        return obj.nombre_commandes()
    nombre_commandes_display.short_description = "Nb commandes"

    def statut_chantier_display(self, obj):
        return obj.statut_chantier()
    statut_chantier_display.short_description = "Statut"

    def derniere_commande_display(self, obj):
        derniere = obj.derniere_commande()
        if derniere:
            try:
                return f"{derniere.date_commande} ({derniere.get_statut_display()})"
            except Exception:
                return str(derniere)
        return "-"
    derniere_commande_display.short_description = "Dernière commande"


@admin.register(CommercialDashboard)
class CommercialDashboardAdmin(admin.ModelAdmin):
    """Entrée d'admin pour le tableau de bord commercial.
    Redirige vers la vue frontend 'commercial_dashboard'.
    """
    list_display = ()
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        # Ne pas afficher d'objets dans la liste
        return Client.objects.none()

    def changelist_view(self, request, extra_context=None):
        # Rediriger vers la vue du dashboard commercial
        try:
            return redirect(reverse('commercial_dashboard'))
        except Exception:
            return redirect('/customers/commercial/')


@admin.register(AgentCommercial)
class AgentCommercialAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email', 'actif', 'nombre_clients_display')
    search_fields = ('nom', 'telephone', 'email')
    list_filter = ('actif',)
    filter_horizontal = ('clients',)

    def nombre_clients_display(self, obj):
        try:
            return obj.clients.count()
        except Exception:
            return 0
    nombre_clients_display.short_description = "Nb clients"
    
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
