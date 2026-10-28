from datetime import timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db import models
from django.utils import timezone


def _q(value, places='0.01'):
    """Arrondit un Decimal de façon fiable."""
    if value is None:
        return None
    return Decimal(value).quantize(Decimal(places), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Choix métier
# ---------------------------------------------------------------------------

ELEMENT_COULE_CHOICES = [
    ('poteau', 'Poteau'),
    ('voile', 'Voile'),
    ('dalle', 'Dalle'),
    ('semelle', 'Semelle'),
    ('radier', 'Radier'),
    ('longrine', 'Longrine'),
    ('poutre', 'Poutre'),
    ('plancher', 'Plancher'),
    ('dallage', 'Dallage'),
    ('massif', 'Massif'),
    ('autre', 'Autre'),
]

FORME_EPROUVETTE_CHOICES = [
    ('cylindrique_16x32', 'Cylindrique 16x32 (cm)'),
    ('cylindrique_11x22', 'Cylindrique 11x22 (cm)'),
    ('cubique_15x15', 'Cubique 15x15 (cm)'),
    ('cubique_10x10', 'Cubique 10x10 (cm)'),
]

# forme -> (surface de section en mm², volume en cm³)
FORME_EPROUVETTE_DIMENSIONS = {
    'cylindrique_16x32': (Decimal('20106.19'), Decimal('6433.98')),
    'cylindrique_11x22': (Decimal('9503.32'), Decimal('2090.73')),
    'cubique_15x15': (Decimal('22500.00'), Decimal('3375.00')),
    'cubique_10x10': (Decimal('10000.00'), Decimal('1000.00')),
}

AGE_CHOICES = [
    (3, '3 jours'),
    (7, '7 jours'),
    (14, '14 jours'),
    (28, '28 jours'),
    (60, '60 jours'),
]

TYPE_RUPTURE_CHOICES = [
    ('normale', 'Normale'),
    ('conique', 'Conique'),
    ('arase', "Défaillance d'arase"),
    ('autre', 'Autre'),
]

# classe de résistance contractuelle -> fck (MPa, résistance caractéristique cylindrique)
CLASSE_RESISTANCE_CHOICES = [
    ('C16/20', 'C16/20'),
    ('C20/25', 'C20/25'),
    ('C25/30', 'C25/30'),
    ('C30/37', 'C30/37'),
    ('C35/45', 'C35/45'),
    ('C40/50', 'C40/50'),
    ('C45/55', 'C45/55'),
    ('C50/60', 'C50/60'),
]

FCK_MAP = {
    'C16/20': 16,
    'C20/25': 20,
    'C25/30': 25,
    'C30/37': 30,
    'C35/45': 35,
    'C40/50': 40,
    'C45/55': 45,
    'C50/60': 50,
}

MATERIAU_CHOICES = [
    ('sable', 'Sable'),
    ('gravier_3_8', 'Gravier 3/8'),
    ('gravier_8_15', 'Gravier 8/15'),
    ('gravier_15_25', 'Gravier 15/25'),
    ('grave', 'Grave / GNT'),
    ('autre', 'Autre'),
]

TYPE_MATIERE_CHOICES = [
    ('normal', 'Normal'),
    ('special', 'Spécial'),
]

# Ouverture des tamis normalisés (mm), du plus grand au plus petit
TAMIS_STANDARD = [
    Decimal('31.5'), Decimal('25'), Decimal('20'), Decimal('16'), Decimal('12.5'),
    Decimal('10'), Decimal('8'), Decimal('6.3'), Decimal('5'), Decimal('2.5'),
    Decimal('1.25'), Decimal('0.63'), Decimal('0.315'), Decimal('0.16'), Decimal('0.08'),
]

# Tamis utilisés pour le module de finesse (NF EN 12620)
TAMIS_MODULE_FINESSE = [
    Decimal('0.08'), Decimal('0.16'), Decimal('0.315'), Decimal('0.63'),
    Decimal('1.25'), Decimal('2.5'), Decimal('5'),
]


# ---------------------------------------------------------------------------
# B. Prélèvements & Éprouvettes
# ---------------------------------------------------------------------------

class Prelevement(models.Model):
    """Prélèvement de béton frais effectué sur chantier."""

    ordre_production = models.ForeignKey(
        'production.OrdreProduction', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='prelevements', verbose_name="Ordre de production",
        help_text="Rattache le prélèvement à un bon de livraison / une production",
    )
    numero_bl = models.CharField(max_length=30, blank=True, help_text="N° de bon de livraison (auto si lié à un ordre)")
    centrale = models.CharField(max_length=100, blank=True, default='', help_text="Centrale à béton")
    date_prelevement = models.DateTimeField(default=timezone.now, help_text="Date et heure du prélèvement")

    element_coule = models.CharField(max_length=20, choices=ELEMENT_COULE_CHOICES, default='dalle', verbose_name="Élément coulé")
    element_coule_detail = models.CharField(max_length=150, blank=True, help_text="Précision (ex: Poteau P3 - niveau 2)")

    # Essai à l'état frais
    affaissement_mm = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True,
                                          verbose_name="Affaissement (cône d'Abrams, mm)")
    temperature_beton = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Température béton (°C)")
    temperature_ambiante = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Température ambiante (°C)")

    # Résistance contractuelle
    classe_resistance = models.CharField(max_length=10, choices=CLASSE_RESISTANCE_CHOICES, blank=True,
                                         verbose_name="Classe de résistance (fck)")

    observations = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_prelevement']
        verbose_name = 'Prélèvement'
        verbose_name_plural = 'Prélèvements'

    def __str__(self):
        return f"{self.numero_bl or 'Sans BL'} - {self.get_element_coule_display()} ({self.date_prelevement:%d/%m/%Y})"

    def save(self, *args, **kwargs):
        # Pré-remplissage depuis l'ordre de production lié
        if self.ordre_production:
            if not self.numero_bl and self.ordre_production.numero_bon:
                self.numero_bl = self.ordre_production.numero_bon
            if not self.classe_resistance:
                res = (getattr(self.ordre_production.formule, 'resistance_requise', '') or '')
                res = res.replace(' ', '').upper()
                if res in FCK_MAP:
                    self.classe_resistance = res
                else:
                    # Certaines formules enregistrent la résistance en valeur numérique (ex: '25.0')
                    try:
                        valeur = Decimal(res)
                    except (InvalidOperation, TypeError):
                        valeur = None
                    if valeur is not None:
                        for classe, fck in FCK_MAP.items():
                            if Decimal(fck) == valeur:
                                self.classe_resistance = classe
                                break
        if not self.centrale:
            self.centrale = 'Sitrad Web'
        super().save(*args, **kwargs)

    @property
    def client(self):
        try:
            return self.ordre_production.commande.client
        except AttributeError:
            return None

    @property
    def chantier(self):
        try:
            return self.ordre_production.commande.chantier
        except AttributeError:
            return None

    @property
    def formule(self):
        try:
            return self.ordre_production.formule
        except AttributeError:
            return None

    @property
    def fck_mpa(self):
        """Résistance caractéristique contractuelle en MPa."""
        if self.classe_resistance in FCK_MAP:
            return Decimal(FCK_MAP[self.classe_resistance])
        return None

    def nb_eprouvettes(self):
        return self.eprouvettes.count()

    nb_eprouvettes.short_description = "Nb éprouvettes"

    def generer_eprouvettes(self, forme='cylindrique_16x32', ages=None, par_echeance=1):
        """Crée automatiquement les éprouvettes et leurs dates d'échéance."""
        if ages is None:
            ages = [7, 28]
        created = []
        for age in ages:
            for _ in range(par_echeance):
                index = self.eprouvettes.count() + 1
                ep = Eprouvette.objects.create(
                    prelevement=self,
                    forme=forme,
                    age_jours=age,
                    code=f"{self.numero_bl or self.pk}-{index}",
                )
                created.append(ep)
        return created


class Eprouvette(models.Model):
    """Éprouvette de béton durci issue d'un prélèvement."""

    prelevement = models.ForeignKey(Prelevement, on_delete=models.CASCADE, related_name='eprouvettes')
    code = models.CharField(max_length=40, blank=True, help_text="Identifiant de l'éprouvette")
    forme = models.CharField(max_length=30, choices=FORME_EPROUVETTE_CHOICES, default='cylindrique_16x32', verbose_name="Forme / dimensions")
    age_jours = models.PositiveSmallIntegerField(choices=AGE_CHOICES, default=28, verbose_name="Échéance (âge)")
    date_fabrication = models.DateTimeField(null=True, blank=True, help_text="Date de fabrication (défaut = date du prélèvement)")
    date_echeance = models.DateTimeField(null=True, blank=True, help_text="Date prévue d'écrasement (auto)")

    class Meta:
        ordering = ['date_echeance', 'code']
        verbose_name = 'Éprouvette'
        verbose_name_plural = 'Éprouvettes'

    def __str__(self):
        return f"{self.code or 'Éprouvette #' + str(self.pk)} - {self.get_forme_display()} ({self.age_jours}j)"

    def save(self, *args, **kwargs):
        if not self.date_fabrication:
            self.date_fabrication = self.prelevement.date_prelevement if self.prelevement_id else timezone.now()
        if self.date_fabrication and self.age_jours:
            self.date_echeance = self.date_fabrication + timedelta(days=self.age_jours)
        if not self.code and self.prelevement_id:
            self.code = f"{self.prelevement.numero_bl or self.prelevement_id}-{Eprouvette.objects.filter(prelevement_id=self.prelevement_id).count() + 1}"
        super().save(*args, **kwargs)

    @property
    def section_mm2(self):
        return FORME_EPROUVETTE_DIMENSIONS.get(self.forme, (None, None))[0]

    @property
    def volume_cm3(self):
        return FORME_EPROUVETTE_DIMENSIONS.get(self.forme, (None, None))[1]

    @property
    def ecrasement_resultat(self):
        """Résultat d'écrasement s'il existe, sinon None (accès sûr en template)."""
        return getattr(self, 'ecrasement', None)

    @property
    def statut(self):
        """Statut de suivi : ecrase / en_retard / a_ecraser / a_venir."""
        if hasattr(self, 'ecrasement'):
            return 'ecrase'
        if not self.date_echeance:
            return 'a_venir'
        aujourdhui = timezone.localdate()
        echeance = timezone.localtime(self.date_echeance).date() if timezone.is_aware(self.date_echeance) else self.date_echeance.date()
        if echeance < aujourdhui:
            return 'en_retard'
        if echeance == aujourdhui:
            return 'a_ecraser'
        return 'a_venir'

    @property
    def statut_label(self):
        return {
            'ecrase': 'Écrasée',
            'en_retard': 'En retard',
            'a_ecraser': "À écraser aujourd'hui",
            'a_venir': 'À venir',
        }.get(self.statut, self.statut)

    @property
    def statut_couleur(self):
        return {
            'ecrase': '#065f46',
            'en_retard': '#991b1b',
            'a_ecraser': '#b45309',
            'a_venir': '#1e40af',
        }.get(self.statut, '#374151')


# ---------------------------------------------------------------------------
# C. Suivi des essais & écrasement
# ---------------------------------------------------------------------------

class EssaiEcrasement(models.Model):
    """Résultat d'écrasement d'une éprouvette (résistance à la compression)."""

    eprouvette = models.OneToOneField(Eprouvette, on_delete=models.CASCADE, related_name='ecrasement')
    date_essai = models.DateTimeField(default=timezone.now)
    poids_kg = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, verbose_name="Poids (kg)")
    force_rupture_kn = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Force de rupture (kN)")
    type_rupture = models.CharField(max_length=20, choices=TYPE_RUPTURE_CHOICES, default='normale', verbose_name="Type de rupture")

    # Champs calculés automatiquement
    surface_mm2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Section (mm²)")
    resistance_mpa = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Résistance (MPa)")
    masse_volumique_kg_m3 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Masse volumique (kg/m³)")
    conforme = models.BooleanField(null=True, blank=True, verbose_name="Conforme (≥ fck)")

    observation = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_essai']
        verbose_name = "Essai d'écrasement"
        verbose_name_plural = "Essais d'écrasement"

    def __str__(self):
        return f"Écrasement {self.eprouvette} - {self.resistance_mpa or '?'} MPa"

    def save(self, *args, **kwargs):
        # Surface automatique à partir de la forme de l'éprouvette
        section = self.eprouvette.section_mm2
        self.surface_mm2 = section

        # Résistance = Force (kN) * 1000 / section (mm²)  ->  N/mm² = MPa
        if self.force_rupture_kn and section:
            self.resistance_mpa = _q(Decimal(self.force_rupture_kn) * Decimal('1000') / Decimal(section))

        # Masse volumique = poids (kg) / volume (cm³) * 1 000 000  ->  kg/m³
        volume = self.eprouvette.volume_cm3
        if self.poids_kg and volume:
            self.masse_volumique_kg_m3 = _q(Decimal(self.poids_kg) / Decimal(volume) * Decimal('1000000'))

        # Conformité vis-à-vis de la résistance contractuelle
        fck = self.eprouvette.prelevement.fck_mpa
        if fck is not None and self.resistance_mpa is not None:
            self.conforme = self.resistance_mpa >= fck

        super().save(*args, **kwargs)

    @property
    def ecart_fck(self):
        """Écart relatif (%) par rapport au fck contractuel."""
        fck = self.eprouvette.prelevement.fck_mpa
        if not fck or self.resistance_mpa is None:
            return None
        return _q((Decimal(self.resistance_mpa) - fck) / fck * Decimal('100'))


# ---------------------------------------------------------------------------
# D. Autres essais de laboratoire
# ---------------------------------------------------------------------------

class EssaiGranulometrie(models.Model):
    """Analyse granulométrique d'un granulat (courbe + module de finesse)."""

    reference = models.CharField(max_length=50, blank=True, help_text="N° d'échantillon / référence")
    date_essai = models.DateField(default=timezone.localdate)
    materiau = models.CharField(max_length=20, choices=MATERIAU_CHOICES, default='sable')
    matiere_premiere = models.ForeignKey('inventory.MatierePremiere', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='essais_granulometrie', verbose_name="Matière première liée")
    designation = models.CharField(max_length=150, blank=True, help_text="Désignation libre du granulat")
    masse_echantillon_g = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Masse de l'échantillon (g)")
    module_finesse = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="Module de finesse")
    observations = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_essai']
        verbose_name = 'Essai de granulométrie'
        verbose_name_plural = 'Essais de granulométrie'

    def __str__(self):
        return f"Granulométrie {self.reference or self.pk} - {self.get_materiau_display()} ({self.date_essai:%d/%m/%Y})"

    def recalculer(self):
        """Recalcule refus cumulés, % refus, % tamisat et le module de finesse."""
        masse_totale = Decimal(self.masse_echantillon_g or 0)
        lignes = list(self.lignes.all().order_by('-diametre_mm'))
        refus_cumule = Decimal('0')
        for ligne in lignes:
            refus_cumule += Decimal(ligne.masse_refus_g or 0)
            ligne.refus_cumule_g = _q(refus_cumule)
            if masse_totale:
                ligne.pourcentage_refus = _q(refus_cumule / masse_totale * Decimal('100'))
                ligne.pourcentage_tamisat = _q(Decimal('100') - ligne.pourcentage_refus)
            ligne.save()

        # Module de finesse = somme des refus cumulés (%) sur les tamis normalisés / 100
        par_tamis = {ligne.diametre_mm: (ligne.pourcentage_refus or Decimal('0')) for ligne in lignes}
        somme = sum((par_tamis.get(d, Decimal('0')) for d in TAMIS_MODULE_FINESSE), Decimal('0'))
        self.module_finesse = _q(somme / Decimal('100'), '0.001')
        super().save(update_fields=['module_finesse'])


class TamisGranulometrie(models.Model):
    """Ligne d'analyse granulométrique pour un tamis donné."""

    essai = models.ForeignKey(EssaiGranulometrie, on_delete=models.CASCADE, related_name='lignes')
    diametre_mm = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Ouverture tamis (mm)")
    masse_refus_g = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Refus (g)")

    refus_cumule_g = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    pourcentage_refus = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, editable=False)
    pourcentage_tamisat = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, editable=False)

    class Meta:
        ordering = ['-diametre_mm']
        verbose_name = 'Tamis (granulométrie)'
        verbose_name_plural = 'Tamis (granulométrie)'

    def __str__(self):
        return f"{self.diametre_mm} mm - {self.masse_refus_g} g"


class EssaiEquivalentSable(models.Model):
    """Essai d'équivalent de sable (ES)."""

    reference = models.CharField(max_length=50, blank=True)
    date_essai = models.DateField(default=timezone.localdate)
    materiau = models.CharField(max_length=20, choices=MATERIAU_CHOICES, default='sable')
    matiere_premiere = models.ForeignKey('inventory.MatierePremiere', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='essais_equivalent_sable')
    hauteur_sable_mm = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Hauteur sable (h1, mm)")
    hauteur_floculat_mm = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Hauteur floculat (h2, mm)")
    valeur_es = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Équivalent de sable ES (%)")
    observations = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_essai']
        verbose_name = "Essai d'équivalent de sable"
        verbose_name_plural = "Essais d'équivalent de sable"

    def __str__(self):
        return f"ES {self.valeur_es or '?'}% - {self.date_essai:%d/%m/%Y}"

    def save(self, *args, **kwargs):
        if self.hauteur_floculat_mm:
            self.valeur_es = _q(Decimal(self.hauteur_sable_mm or 0) / Decimal(self.hauteur_floculat_mm) * Decimal('100'))
        super().save(*args, **kwargs)


class EssaiBleuMethylene(models.Model):
    """Essai au bleu de méthylène (valeur de bleu VB)."""

    reference = models.CharField(max_length=50, blank=True)
    date_essai = models.DateField(default=timezone.localdate)
    materiau = models.CharField(max_length=20, choices=MATERIAU_CHOICES, default='sable')
    matiere_premiere = models.ForeignKey('inventory.MatierePremiere', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='essais_bleu_methylene')
    type_matiere = models.CharField(max_length=20, choices=TYPE_MATIERE_CHOICES, default='normal', verbose_name="Type")
    masse_echantillon_g = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Masse échantillon (g)")
    volume_solution_ml = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Volume solution de bleu (ml)")
    valeur_bleu = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Valeur de bleu VB (ml/kg)")
    observations = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_essai']
        verbose_name = 'Essai au bleu de méthylène'
        verbose_name_plural = 'Essais au bleu de méthylène'

    def __str__(self):
        return f"VB {self.valeur_bleu or '?'} - {self.date_essai:%d/%m/%Y}"

    def save(self, *args, **kwargs):
        # VB = volume de solution (ml) / masse sèche (kg)
        if self.masse_echantillon_g:
            self.valeur_bleu = _q(Decimal(self.volume_solution_ml or 0) / (Decimal(self.masse_echantillon_g) / Decimal('1000')))
        super().save(*args, **kwargs)


class EssaiTeneurEnEau(models.Model):
    """Détermination de la teneur en eau d'un granulat."""

    reference = models.CharField(max_length=50, blank=True)
    date_essai = models.DateField(default=timezone.localdate)
    materiau = models.CharField(max_length=20, choices=MATERIAU_CHOICES, default='sable')
    matiere_premiere = models.ForeignKey('inventory.MatierePremiere', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='essais_teneur_eau')
    masse_humide_g = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Masse humide (g)")
    masse_seche_g = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Masse sèche (g)")
    teneur_eau_pourcent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Teneur en eau (%)")
    observations = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_essai']
        verbose_name = 'Essai de teneur en eau'
        verbose_name_plural = 'Essais de teneur en eau'

    def __str__(self):
        return f"Teneur en eau {self.teneur_eau_pourcent or '?'}% - {self.date_essai:%d/%m/%Y}"

    def save(self, *args, **kwargs):
        if self.masse_seche_g:
            self.teneur_eau_pourcent = _q(
                (Decimal(self.masse_humide_g or 0) - Decimal(self.masse_seche_g)) / Decimal(self.masse_seche_g) * Decimal('100')
            )
        super().save(*args, **kwargs)
