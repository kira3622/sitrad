"""Planning des livraisons prévues.

Deux écrans :
- la consultation du planning (jour par jour + calendrier mensuel) construite à partir
  des commandes et de leurs ordres de production ;
- la planification d'une livraison (date, heure, véhicule, statut) enregistrée dans
  ``logistics.Livraison``.
"""
import calendar
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from customers.models import Client
from orders.models import Commande
from .models import Livraison, SaisiePlanning
from notifications.whatsapp import envoyer_message_groupe, message_nouvelle_saisie

# Statuts de commande considérés comme « à livrer »
STATUTS_A_LIVRER = ('en_attente', 'validee', 'en_production')

CHOIX_FILTRE_STATUT = [
    ('a_livrer', 'À livrer'),
    ('livree', 'Livrées'),
    ('annulee', 'Annulées'),
    ('toutes', 'Toutes'),
]

LIBELLES_STATUT = {
    'planifiee': 'Planifiée',
    'en_cours': 'En cours',
    'livree': 'Livrée',
    'annulee': 'Annulée',
    'en_attente': 'En attente',
    'validee': 'Validée',
    'en_production': 'En production',
}

MOIS_FRANCAIS = [
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
]

JOURS_FRANCAIS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']


class LivraisonForm(forms.ModelForm):
    """Planification d'une livraison : date, heure, véhicule, statut et adresse."""

    class Meta:
        model = Livraison
        fields = ('date_livraison', 'heure_livraison', 'vehicule', 'statut', 'adresse_livraison')
        widgets = {
            'date_livraison': forms.DateInput(attrs={'type': 'date'}),
            'heure_livraison': forms.TimeInput(attrs={'type': 'time'}),
            'adresse_livraison': forms.Textarea(attrs={'rows': 2, 'cols': 60}),
        }


def _date_demandee(valeur, defaut):
    """Convertit une date « AAAA-MM-JJ » de l'URL, sinon renvoie la valeur par défaut."""
    if valeur:
        try:
            return datetime.strptime(valeur, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return defaut
    return defaut


def _filtres(request):
    """Filtres de la barre de recherche : période, client et statut."""
    aujourdhui = timezone.localdate()
    date_debut = _date_demandee(request.GET.get('date_debut'), aujourdhui - timedelta(days=7))
    date_fin = _date_demandee(request.GET.get('date_fin'), aujourdhui + timedelta(days=30))
    if date_fin < date_debut:
        date_debut, date_fin = date_fin, date_debut

    statut = request.GET.get('statut') or 'a_livrer'
    if statut not in dict(CHOIX_FILTRE_STATUT):
        statut = 'a_livrer'

    client = request.GET.get('client') or ''
    if not str(client).isdigit():
        client = ''

    return {
        'date_debut': date_debut,
        'date_fin': date_fin,
        'statut': statut,
        'client': client,
    }


def _commandes(filtres, debut=None, fin=None):
    """Commandes à afficher dans le planning."""
    commandes = Commande.objects.filter(
        date_livraison_souhaitee__range=[debut or filtres['date_debut'], fin or filtres['date_fin']]
    ).select_related('client', 'chantier').prefetch_related('lignes__formule', 'ordreproduction_set')

    if filtres['client']:
        commandes = commandes.filter(client_id=filtres['client'])

    if filtres['statut'] == 'a_livrer':
        commandes = commandes.filter(statut__in=STATUTS_A_LIVRER)
    elif filtres['statut'] in ('livree', 'annulee'):
        commandes = commandes.filter(statut=filtres['statut'])

    return commandes.order_by('date_livraison_souhaitee', 'heure_livraison_souhaitee', 'id')


def _adresse_par_defaut(commande):
    """Adresse proposée par défaut : celle du chantier, sinon celle du client."""
    if commande.chantier is not None and commande.chantier.adresse:
        return commande.chantier.adresse
    return commande.client.adresse or ''


def _cle_tri(ligne):
    """Tri d'une journée : heures croissantes, livraisons sans heure en dernier."""
    return (ligne['heure'] is None, ligne['heure'] or time(0, 0))


def _ligne_planning(commande):
    """Prépare les informations d'une commande pour le planning."""
    livraison = commande.livraison_set.order_by('date_livraison', 'id').first()
    lignes = list(commande.lignes.all())
    ordres = list(commande.ordreproduction_set.all())

    quantite = Decimal('0.00')
    for ligne in lignes:
        if ligne.quantite:
            quantite += ligne.quantite

    heure = commande.heure_livraison_souhaitee
    if livraison is not None and livraison.heure_livraison:
        heure = livraison.heure_livraison

    statut_code = livraison.statut if livraison is not None else commande.statut

    if livraison is not None and livraison.adresse_livraison:
        adresse = livraison.adresse_livraison
    else:
        adresse = _adresse_par_defaut(commande)

    return {
        'commande': commande,
        'livraison': livraison,
        'date': commande.date_livraison_souhaitee,
        'heure': heure,
        'quantite': quantite,
        'formules': [ligne.formule.nom for ligne in lignes],
        'ordres': ordres,
        'vehicule': livraison.vehicule if livraison is not None else None,
        'statut_code': statut_code,
        'statut_label': LIBELLES_STATUT.get(statut_code, statut_code),
        'planifiee': livraison is not None,
        'adresse': adresse,
    }


@staff_member_required
def planning_livraisons(request):
    """Planning des livraisons prévues : liste jour par jour et calendrier mensuel."""
    filtres = _filtres(request)
    onglet = request.GET.get('onglet') or 'liste'
    aujourdhui = timezone.localdate()

    # --- Liste jour par jour ------------------------------------------------
    lignes = [_ligne_planning(commande) for commande in _commandes(filtres)]

    par_jour = {}
    for ligne in lignes:
        par_jour.setdefault(ligne['date'], []).append(ligne)

    jours = []
    for jour in sorted(par_jour):
        lignes_jour = sorted(par_jour[jour], key=_cle_tri)
        jours.append({
            'date': jour,
            'libelle': f"{JOURS_FRANCAIS[jour.weekday()]} {jour.strftime('%d/%m/%Y')}",
            'lignes': lignes_jour,
            'nb': len(lignes_jour),
            'quantite': sum((ligne['quantite'] for ligne in lignes_jour), Decimal('0.00')),
        })

    total_quantite = sum((jour['quantite'] for jour in jours), Decimal('0.00'))
    total_livraisons = sum(jour['nb'] for jour in jours)

    # --- Calendrier mensuel -------------------------------------------------
    mois = request.GET.get('mois') or aujourdhui.strftime('%Y-%m')
    try:
        annee, numero_mois = (int(partie) for partie in mois.split('-'))
        premier_jour_mois = date(annee, numero_mois, 1)
    except (TypeError, ValueError):
        premier_jour_mois = aujourdhui.replace(day=1)
        annee, numero_mois = premier_jour_mois.year, premier_jour_mois.month

    dernier_jour_mois = date(annee, numero_mois, calendar.monthrange(annee, numero_mois)[1])

    par_jour_mois = {}
    for commande in _commandes(filtres, debut=premier_jour_mois, fin=dernier_jour_mois):
        ligne = _ligne_planning(commande)
        par_jour_mois.setdefault(ligne['date'], []).append(ligne)

    semaines = []
    for semaine in calendar.Calendar(firstweekday=0).monthdatescalendar(annee, numero_mois):
        jours_semaine = []
        for jour in semaine:
            lignes_jour = sorted(par_jour_mois.get(jour, []), key=_cle_tri)
            jours_semaine.append({
                'date': jour,
                'dans_le_mois': jour.month == numero_mois,
                'aujourdhui': jour == aujourdhui,
                'lignes': lignes_jour,
                'quantite': sum((ligne['quantite'] for ligne in lignes_jour), Decimal('0.00')),
            })
        semaines.append(jours_semaine)

    context = {
        **filtres,
        'title': "Planning des livraisons prévues",
        'onglet': onglet,
        'jours': jours,
        'total_livraisons': total_livraisons,
        'total_quantite': total_quantite,
        'semaines': semaines,
        'mois_label': f"{MOIS_FRANCAIS[numero_mois - 1]} {annee}",
        'mois_precedent': (premier_jour_mois - timedelta(days=1)).strftime('%Y-%m'),
        'mois_suivant': (dernier_jour_mois + timedelta(days=1)).strftime('%Y-%m'),
        'aujourdhui': aujourdhui,
        'clients': Client.objects.order_by('nom'),
        'statuts': CHOIX_FILTRE_STATUT,
        'retour_filtres': request.GET.urlencode(),
    }
    return render(request, 'planning/livraisons.html', context)


@staff_member_required
def planifier_livraison(request, commande_id):
    """Planifie (ou modifie) la livraison prévue d'une commande."""
    commande = get_object_or_404(
        Commande.objects.select_related('client', 'chantier'), pk=commande_id)
    livraison = commande.livraison_set.order_by('date_livraison', 'id').first()
    retour = request.POST.get('retour') or request.GET.get('retour') or ''
    url_retour = reverse('planning:livraisons')

    if request.method == 'POST':
        form = LivraisonForm(request.POST, instance=livraison)
        if form.is_valid():
            livraison = form.save(commit=False)
            livraison.commande = commande
            if not livraison.adresse_livraison:
                livraison.adresse_livraison = _adresse_par_defaut(commande)
            livraison.save()
            messages.success(
                request,
                f"Livraison du {livraison.date_livraison.strftime('%d/%m/%Y')} enregistrée "
                f"pour {commande.client.nom}.",
            )
            return redirect(f'{url_retour}?{retour}' if retour else url_retour)
    else:
        initial = {}
        if livraison is None:
            initial = {
                'date_livraison': commande.date_livraison_souhaitee,
                'heure_livraison': commande.heure_livraison_souhaitee,
                'adresse_livraison': _adresse_par_defaut(commande),
                'statut': 'planifiee',
            }
        form = LivraisonForm(instance=livraison, initial=initial)

    context = {
        'title': "Planifier une livraison prévue",
        'commande': commande,
        'livraison': livraison,
        'form': form,
        'lignes': commande.lignes.select_related('formule'),
        'ordres': commande.ordreproduction_set.all(),
        'retour': retour,
    }
    return render(request, 'planning/planifier.html', context)


class SaisiePlanningForm(forms.ModelForm):
    """Saisie libre d'une livraison planifiée (sans commande)."""

    class Meta:
        model = SaisiePlanning
        fields = ('date_livraison', 'heure_livraison', 'client', 'chantier', 'formule',
                  'quantite', 'vehicule', 'adresse', 'statut', 'observation')
        widgets = {
            'date_livraison': forms.DateInput(attrs={'type': 'date'}),
            'heure_livraison': forms.TimeInput(attrs={'type': 'time'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'cols': 60}),
            'observation': forms.Textarea(attrs={'rows': 2, 'cols': 60}),
        }


def _url_saisie(filtres):
    """URL de la page de saisie en conservant la période affichée."""
    return (
        f"{reverse('planning:saisie')}"
        f"?date_debut={filtres['date_debut']}&date_fin={filtres['date_fin']}"
    )


@staff_member_required
def saisie_plannings(request):
    """Page dédiée : saisie libre des livraisons planifiées (hors commande)."""
    filtres = _filtres(request)

    instance = None
    identifiant = request.POST.get('id') or request.GET.get('edit')
    if identifiant and str(identifiant).isdigit():
        instance = get_object_or_404(SaisiePlanning, pk=identifiant)

    if request.method == 'POST':
        if request.POST.get('action') == 'supprimer' and instance is not None:
            instance.delete()
            messages.success(request, "Livraison planifiée supprimée.")
            return redirect(_url_saisie(filtres))
        form = SaisiePlanningForm(request.POST, instance=instance)
        if form.is_valid():
            enregistree = form.save()
            messages.success(
                request,
                f"Livraison planifiée du {enregistree.date_livraison.strftime('%d/%m/%Y')} "
                f"pour {enregistree.client} enregistrée.",
            )
            if instance is None:
                ok, detail = envoyer_message_groupe(message_nouvelle_saisie(enregistree))
                if ok:
                    messages.info(request, "Message envoyé au groupe WhatsApp.")
                else:
                    messages.warning(request, f"Envoi WhatsApp non effectué : {detail}")
            return redirect(_url_saisie(filtres))
    else:
        initial = {}
        if instance is None:
            initial = {'date_livraison': timezone.localdate(), 'statut': 'planifiee'}
        form = SaisiePlanningForm(instance=instance, initial=initial)

    entrees = list(
        SaisiePlanning.objects.filter(
            date_livraison__range=[filtres['date_debut'], filtres['date_fin']]
        ).select_related('vehicule').order_by('date_livraison', 'heure_livraison', 'id')
    )
    total_quantite = sum((entree.quantite for entree in entrees), Decimal('0.00'))

    context = {
        'title': "Saisie des plannings",
        **filtres,
        'form': form,
        'instance': instance,
        'entrees': entrees,
        'total_entrees': len(entrees),
        'total_quantite': total_quantite,
        'retour_filtres': request.GET.urlencode(),
    }
    return render(request, 'planning/saisie.html', context)
