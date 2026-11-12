from decimal import Decimal

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from stock.models import MouvementStock
from .models import MatierePremiere


class AjustementStockForm(forms.Form):
    """Formulaire d'ajustement manuel du stock d'une ou plusieurs matières premières."""

    SENS_CHOICES = [
        ('entree', 'Ajouter au stock (entrée)'),
        ('sortie', 'Retirer du stock (sortie)'),
    ]

    sens = forms.ChoiceField(
        choices=SENS_CHOICES,
        initial='entree',
        label="Sens de l'ajustement",
        widget=forms.RadioSelect,
    )
    quantite = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        label="Quantité à ajuster",
        help_text="Quantité ajoutée (entrée) ou retirée (sortie) du stock.",
    )
    description = forms.CharField(
        required=False,
        max_length=200,
        label="Motif",
        widget=forms.TextInput(attrs={'placeholder': "Ex : correction d'inventaire"}),
    )


@admin.register(MatierePremiere)
class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'unite_mesure', 'stock_actuel_display', 'seuil_critique', 'seuil_bas', 'statut_stock_display')
    search_fields = ('nom',)
    list_filter = ('unite_mesure',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'unite_mesure')
        }),
        ('Configuration des seuils', {
            'fields': ('seuil_critique', 'seuil_bas'),
            'description': 'Configurez les seuils d\'alerte pour cette matière première'
        }),
    )
    actions = ['action_ajuster_stock']

    def get_urls(self):
        urls = super().get_urls()
        urls_personnalisees = [
            path(
                'ajuster-stock/',
                self.admin_site.admin_view(self.ajuster_stock_view),
                name='inventory_matierepremiere_ajuster_stock',
            ),
        ]
        return urls_personnalisees + urls

    @admin.action(description="Corriger le stock (ajouter ou retirer une quantité)")
    def action_ajuster_stock(self, request, queryset):
        """Redirige vers le formulaire d'ajustement pour les matières sélectionnées."""
        ids = ','.join(str(pk) for pk in queryset.values_list('pk', flat=True))
        url = reverse('admin:inventory_matierepremiere_ajuster_stock')
        return redirect(f'{url}?ids={ids}')

    def ajuster_stock_view(self, request):
        """Ajuste le stock des matières sélectionnées : entrée ou sortie d'une quantité."""
        if not self.has_change_permission(request):
            raise PermissionDenied

        ids_bruts = request.POST.get('ids') or request.GET.get('ids') or ''
        ids = [identifiant for identifiant in ids_bruts.split(',') if identifiant.strip().isdigit()]
        matieres = list(MatierePremiere.objects.filter(pk__in=ids).order_by('nom'))

        if not matieres:
            self.message_user(
                request,
                "Aucune matière première sélectionnée : choisissez au moins une ligne "
                "puis relancez l'action « Corriger le stock ».",
                messages.WARNING,
            )
            return redirect(reverse('admin:inventory_matierepremiere_changelist'))

        if request.method == 'POST':
            form = AjustementStockForm(request.POST)
            if form.is_valid():
                sens = form.cleaned_data['sens']
                quantite = form.cleaned_data['quantite']
                motif = form.cleaned_data['description'].strip()
                description = f"Ajustement d'inventaire : {motif}" if motif else "Ajustement d'inventaire"

                ajustees = []
                refusees = []
                for matiere in matieres:
                    # Une sortie ne doit jamais rendre le stock négatif.
                    if sens == 'sortie' and matiere.stock_actuel < quantite:
                        refusees.append(matiere)
                        continue
                    MouvementStock.objects.create(
                        matiere_premiere=matiere,
                        quantite=quantite,
                        type_mouvement=sens,
                        description=description,
                    )
                    ajustees.append(matiere)

                libelle_sens = "Entrée" if sens == 'entree' else "Sortie"
                if ajustees:
                    self.message_user(
                        request,
                        f"{libelle_sens} de {quantite} enregistrée pour : "
                        + ", ".join(m.nom for m in ajustees),
                        messages.SUCCESS,
                    )
                if refusees:
                    self.message_user(
                        request,
                        "Stock insuffisant, aucun ajustement pour : "
                        + ", ".join(f"{m.nom} ({m.stock_actuel} {m.unite_mesure} en stock)" for m in refusees),
                        messages.ERROR,
                    )
                return redirect(reverse('admin:inventory_matierepremiere_changelist'))
        else:
            form = AjustementStockForm()

        context = {
            **self.admin_site.each_context(request),
            'title': "Corriger le stock des matières premières",
            'form': form,
            'matieres': matieres,
            'ids': ','.join(str(matiere.pk) for matiere in matieres),
            'opts': self.model._meta,
        }
        return render(request, 'admin/inventory/matierepremiere/ajuster_stock.html', context)

    def stock_actuel_display(self, obj):
        """Affiche le stock actuel avec l'unité de mesure"""
        return f"{obj.stock_actuel} {obj.unite_mesure}"
    stock_actuel_display.short_description = "Stock actuel"

    def statut_stock_display(self, obj):
        """Affiche le statut du stock avec des couleurs"""
        statut = obj.statut_stock
        if statut == 'critique':
            return format_html('<span style="color: red; font-weight: bold;">🔴 CRITIQUE</span>')
        elif statut == 'bas':
            return format_html('<span style="color: orange; font-weight: bold;">🟠 BAS</span>')
        else:
            return format_html('<span style="color: green;">🟢 NORMAL</span>')
    statut_stock_display.short_description = "Statut"
