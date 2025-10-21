from decimal import Decimal
from typing import Dict, Optional, Tuple
from django.utils import timezone
from django.db.models import Q

from .models import CoûtMatierePremiere, CoûtMainOeuvre, CoûtFraisGeneraux
from formulas.models import FormuleBeton


def _default_prix_unitaire(matiere_nom: str, unite: str) -> Decimal:
    """Renvoie un prix unitaire par défaut basé sur le nom de la matière.
    Les prix sont exprimés par l'unité de la matière (kg, litre, m³, etc.).
    """
    nom = (matiere_nom or "").lower()
    if "ciment" in nom:
        return Decimal("0.12")  # EUR / kg
    if "sable" in nom:
        return Decimal("0.02")  # EUR / kg
    if any(x in nom for x in ["gravier", "gravillon", "granulat"]):
        return Decimal("0.015")  # EUR / kg
    if "eau" in nom:
        return Decimal("0.001")  # EUR / litre
    if any(x in nom for x in ["plastifiant", "adjuvant"]):
        return Decimal("3.0")  # EUR / litre
    # Par défaut, pas de coût si inconnu
    return Decimal("0")


def _get_prix_unitaire_matiere(matiere, date: Optional[timezone.datetime]) -> Decimal:
    """Essaye de récupérer le coût actif depuis la base, sinon prix par défaut.
    """
    aujourd_hui = (date or timezone.now()).date()
    cost = (
        CoûtMatierePremiere.objects.filter(
            matiere_premiere=matiere,
            actif=True,
            date_debut__lte=aujourd_hui,
        ).filter(Q(date_fin__isnull=True) | Q(date_fin__gte=aujourd_hui)).first()
    )
    if cost:
        return Decimal(cost.prix_total_unitaire)
    return _default_prix_unitaire(matiere.nom, matiere.unite_mesure)


def _compute_matieres_cost(formule: FormuleBeton, quantite: Decimal) -> Tuple[Decimal, Dict[str, Decimal]]:
    """Calcule le coût des matières à partir de la composition et renvoie le détail.
    Retourne (coût_total, details_par_matiere).
    """
    total = Decimal("0")
    details: Dict[str, Decimal] = {}

    for comp in formule.composition.all():
        # Quantité nécessaire proportionnelle à la quantité calculée
        quantite_necessaire = (comp.quantite * quantite) / (formule.quantite_produite_reference or Decimal("1"))
        prix_unitaire = _get_prix_unitaire_matiere(comp.matiere_premiere, timezone.now())
        cout = (quantite_necessaire * prix_unitaire).quantize(Decimal("0.01"))
        total += cout
        details[comp.matiere_premiere.nom] = cout

    return (total, details)


def _compute_main_oeuvre_cost(quantite: Decimal, defaults: Dict[str, Decimal]) -> Decimal:
    """Calcule la main d'œuvre via DB ou via défauts."""
    aujourd_hui = timezone.now().date()
    mo = (
        CoûtMainOeuvre.objects.filter(
            type_activite="production",
            actif=True,
            date_debut__lte=aujourd_hui,
        ).filter(Q(date_fin__isnull=True) | Q(date_fin__gte=aujourd_hui)).first()
    )
    if mo:
        heures = quantite * Decimal("0.5")  # hypothèse par m³
        return (heures * mo.coût_horaire_total).quantize(Decimal("0.01"))

    # Fallback avec les defaults
    cout_horaire = Decimal(defaults.get("cout_main_oeuvre_production", Decimal("25.0")))
    heures_prod = Decimal(defaults.get("heures_production", Decimal("1.0")))
    charges_pct = Decimal(defaults.get("charges_sociales", Decimal("45.0")))
    heures = quantite * heures_prod
    total_horaire = cout_horaire * (Decimal("1") + (charges_pct / Decimal("100")))
    return (heures * total_horaire).quantize(Decimal("0.01"))


def _compute_frais_generaux_cost(quantite: Decimal, base_mo_mat: Decimal, defaults: Dict[str, Decimal]) -> Decimal:
    """Calcule les frais généraux (DB sinon defaults)."""
    aujourd_hui = timezone.now().date()
    total = Decimal("0")
    frais_par_m3 = CoûtFraisGeneraux.objects.filter(
        type_repartition="par_m3",
        actif=True,
        date_debut__lte=aujourd_hui,
    ).filter(Q(date_fin__isnull=True) | Q(date_fin__gte=aujourd_hui))
    for frais in frais_par_m3:
        total += (quantite * frais.valeur)

    if total > 0:
        return total.quantize(Decimal("0.01"))

    # Fallback: fixe + amortissement + assurance + pourcentage variable
    frais_fixes = Decimal(defaults.get("frais_fixes", Decimal("50.0")))
    amortissement = Decimal(defaults.get("amortissement", Decimal("20.0")))
    assurance = Decimal(defaults.get("assurance", Decimal("15.0")))
    var_pct = Decimal(defaults.get("frais_variables_pct", Decimal("5.0")))
    variables = (base_mo_mat * (var_pct / Decimal("100")))
    total = frais_fixes + amortissement + assurance + variables
    return total.quantize(Decimal("0.01"))


def _compute_transport_cost(defaults: Dict[str, Decimal]) -> Decimal:
    """Calcule le transport (DB sinon defaults)."""
    aujourd_hui = timezone.now().date()
    frais_transport = CoûtFraisGeneraux.objects.filter(
        categorie__type_categorie="transport",
        type_repartition="par_commande",
        actif=True,
        date_debut__lte=aujourd_hui,
    ).filter(Q(date_fin__isnull=True) | Q(date_fin__gte=aujourd_hui)).first()

    if frais_transport:
        return Decimal(frais_transport.valeur).quantize(Decimal("0.01"))

    # Fallback defaults (distance * coût/km + frais fixes)
    distance = Decimal(defaults.get("distance_livraison", Decimal("10.0")))
    cout_km = Decimal(defaults.get("cout_km", Decimal("1.5")))
    frais_fixes = Decimal(defaults.get("frais_livraison_fixes", Decimal("25.0")))
    return (distance * cout_km + frais_fixes).quantize(Decimal("0.01"))


def calculer_cout_revient_module(formule: FormuleBeton, quantite: Decimal, defaults: Optional[Dict[str, Decimal]] = None) -> Dict:
    """
    Calcule un coût de revient à partir d'une formule et d'une quantité en combinant:
    - Coûts de matières (DB si dispo, sinon heuristiques par défaut)
    - Main d'œuvre (DB si dispo, sinon valeurs par défaut)
    - Frais généraux (DB si dispo, sinon valeurs par défaut)
    - Transport (DB si dispo, sinon valeurs par défaut)

    Retourne un dict similaire à la réponse JSON du endpoint `simulation_calcul`.
    """
    defaults = defaults or {}

    cout_matieres, details_matieres = _compute_matieres_cost(formule, quantite)
    cout_mo = _compute_main_oeuvre_cost(quantite, defaults)
    cout_fg = _compute_frais_generaux_cost(quantite, cout_matieres + cout_mo, defaults)
    cout_transport = _compute_transport_cost(defaults)

    total = (cout_matieres + cout_mo + cout_fg + cout_transport).quantize(Decimal("0.01"))

    return {
        "success": True,
        "calcul": {
            "quantite": float(quantite),
            "unite_mesure": "m3",
            "formule_nom": formule.nom,
            "cout_matieres": float(cout_matieres),
            "cout_main_oeuvre": float(cout_mo),
            "cout_frais_generaux": float(cout_fg),
            "cout_transport": float(cout_transport),
            "cout_total": float(total),
            "cout_unitaire": float((total / quantite) if quantite > 0 else Decimal("0")),
            "details_matieres": {k: float(v) for k, v in details_matieres.items()},
        },
    }