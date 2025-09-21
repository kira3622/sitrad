from django.core.management.base import BaseCommand
from django.db.models import Sum
from fuel_management.models import *
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test complet du système de gestion du gasoil'

    def handle(self, *args, **options):
        """Test complet du système de gestion du gasoil"""
        
        self.stdout.write("🧪 Test du système de gestion du gasoil")
        self.stdout.write("=" * 50)
        
        # 1. Créer les données de base
        self.stdout.write("\n1. Création des données de base...")
        
        # Fournisseur
        fournisseur, created = Fournisseur.objects.get_or_create(
            nom="Total Energies",
            defaults={
                'contact': "Jean Dupont",
                'telephone': "0123456789",
                'email': "contact@total.fr"
            }
        )
        self.stdout.write(f"✅ Fournisseur: {fournisseur.nom}")
        
        # Type d'engin
        type_engin, created = TypeEngin.objects.get_or_create(
            nom="Excavatrice",
            defaults={'consommation_moyenne': Decimal('25.5')}
        )
        self.stdout.write(f"✅ Type d'engin: {type_engin.nom}")
        
        # Engin
        engin, created = Engin.objects.get_or_create(
            nom="CAT 320D",
            defaults={
                'type_engin': type_engin,
                'numero_serie': "CAT123456"
            }
        )
        self.stdout.write(f"✅ Engin: {engin.nom}")
        
        # 2. Test du stock initial
        self.stdout.write("\n2. Test du stock initial...")
        stock = Stock.get_stock_actuel()
        self.stdout.write(f"📊 Stock initial: {stock.quantite}L")
        self.stdout.write(f"⚠️ Seuil minimum: {stock.seuil_minimum}L")
        
        # 3. Test d'approvisionnement
        self.stdout.write("\n3. Test d'approvisionnement...")
        approvisionnement = Approvisionnement.objects.create(
            date=timezone.now().date(),
            fournisseur=fournisseur,
            quantite=Decimal('1000'),
            prix_unitaire=Decimal('1.45'),
            numero_bon="BON001"
        )
        self.stdout.write(f"✅ Approvisionnement créé: +{approvisionnement.quantite}L")
        
        # Vérifier le stock après approvisionnement
        stock.refresh_from_db()
        self.stdout.write(f"📊 Stock après approvisionnement: {stock.quantite}L")
        
        # 4. Test de consommation
        self.stdout.write("\n4. Test de consommation...")
        consommation = Consommation.objects.create(
            date=timezone.now().date(),
            engin=engin,
            quantite=Decimal('150'),
            responsable="Pierre Martin"
        )
        self.stdout.write(f"✅ Consommation créée: -{consommation.quantite}L")
        
        # Vérifier le stock après consommation
        stock.refresh_from_db()
        self.stdout.write(f"📊 Stock après consommation: {stock.quantite}L")
        
        # 5. Test des alertes
        self.stdout.write("\n5. Test du système d'alertes...")
        alertes_count = AlerteStock.objects.count()
        self.stdout.write(f"🚨 Nombre d'alertes: {alertes_count}")
        
        if alertes_count > 0:
            derniere_alerte = AlerteStock.objects.order_by('-date_alerte').first()
            self.stdout.write(f"📝 Dernière alerte: {derniere_alerte.message}")
            self.stdout.write(f"👁️ Vue: {'Oui' if derniere_alerte.vue else 'Non'}")
        
        # 6. Test de consommation importante pour déclencher une alerte
        self.stdout.write("\n6. Test d'alerte de stock faible...")
        consommation_importante = Consommation.objects.create(
            date=timezone.now().date(),
            engin=engin,
            quantite=Decimal('400'),  # Pour descendre sous le seuil
            responsable="Marie Dubois"
        )
        self.stdout.write(f"✅ Consommation importante: -{consommation_importante.quantite}L")
        
        # Vérifier le stock
        stock.refresh_from_db()
        self.stdout.write(f"📊 Stock final: {stock.quantite}L")
        
        # Vérifier les nouvelles alertes
        nouvelles_alertes = AlerteStock.objects.filter(vue=False).count()
        self.stdout.write(f"🚨 Alertes non vues: {nouvelles_alertes}")
        
        # 7. Statistiques finales
        self.stdout.write("\n7. Statistiques finales...")
        total_approvisionnements = Approvisionnement.objects.aggregate(
            total=Sum('quantite')
        )['total'] or Decimal('0')
        
        total_consommations = Consommation.objects.aggregate(
            total=Sum('quantite')
        )['total'] or Decimal('0')
        
        self.stdout.write(f"📈 Total approvisionnements: {total_approvisionnements}L")
        self.stdout.write(f"📉 Total consommations: {total_consommations}L")
        self.stdout.write(f"📊 Stock calculé: {total_approvisionnements - total_consommations}L")
        self.stdout.write(f"📊 Stock en base: {stock.quantite}L")
        
        # Vérifier la cohérence
        if stock.quantite == (total_approvisionnements - total_consommations):
            self.stdout.write(self.style.SUCCESS("✅ Cohérence des données: OK"))
        else:
            self.stdout.write(self.style.ERROR("❌ Incohérence détectée dans les calculs!"))
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("🎉 Test terminé avec succès!"))