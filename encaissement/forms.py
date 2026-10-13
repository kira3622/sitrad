from django import forms
from .models import Encaissement
from production.models import OrdreProduction


class EncaissementForm(forms.ModelForm):
    class Meta:
        model = Encaissement
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Déterminer le client sélectionné (instance existante ou données du formulaire)
        client_id = None
        if self.instance and self.instance.pk and self.instance.client_id:
            client_id = self.instance.client_id
        elif self.data:
            client_id = self.data.get('client')

        # Filtrer les bons de livraison (OrdreProduction) par client et trier par numéro de bon
        if client_id:
            self.fields['ordre_production'].queryset = OrdreProduction.objects.filter(
                commande__client_id=client_id
            ).order_by('numero_bon')
        else:
            # Aucun client sélectionné : liste vide
            self.fields['ordre_production'].queryset = OrdreProduction.objects.none()

        # Trier également la liste des clients par nom
        if 'client' in self.fields:
            from customers.models import Client
            self.fields['client'].queryset = Client.objects.all().order_by('nom')
