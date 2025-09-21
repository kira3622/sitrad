from django.core.management.base import BaseCommand
from django.utils import timezone
from fuel_management.models import Stock, AlerteStock
from fuel_management.signals import check_and_create_low_stock_alert, check_stock_rupture
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Vérifie et gère les alertes de stock de gasoil'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la vérification même si le stock semble suffisant',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affiche des informations détaillées',
        )

    def handle(self, *args, **options):
        """
        Fonction principale de vérification des alertes
        """
        try:
            self.stdout.write('🔍 Vérification des alertes de stock de gasoil...')
            
            # Obtenir le stock actuel
            stock = Stock.get_stock_actuel()
            if not stock:
                self.stdout.write(
                    self.style.ERROR('❌ Aucun stock trouvé. Veuillez initialiser le stock.')
                )
                return

            if options['verbose']:
                self.stdout.write(f"📊 Stock actuel: {stock.quantite}L")
                self.stdout.write(f"⚠️ Seuil minimum: {stock.seuil_minimum}L")

            # Vérifier les alertes existantes
            alertes_actives = AlerteStock.objects.filter(vue=False).count()
            if options['verbose']:
                self.stdout.write(f"🚨 Alertes actives: {alertes_actives}")

            # Forcer la vérification ou vérifier seulement si nécessaire
            if options['force'] or stock.quantite <= stock.seuil_minimum:
                
                # Vérifier rupture de stock (priorité absolue)
                if stock.quantite <= 0:
                    self.stdout.write(
                        self.style.ERROR('🚨 RUPTURE DE STOCK DÉTECTÉE!')
                    )
                    check_stock_rupture()
                
                # Vérifier le stock faible
                elif stock.quantite <= stock.seuil_minimum:
                    # Vérifier s'il n'y a pas déjà une alerte récente
                    recent_alert = AlerteStock.objects.filter(
                        vue=False,
                        date_alerte__gte=timezone.now() - timezone.timedelta(hours=1)
                    ).exists()
                    
                    if options['force'] or not recent_alert:
                        self.stdout.write(
                            self.style.WARNING('⚠️ Stock faible détecté, création d\'alerte...')
                        )
                        check_and_create_low_stock_alert(stock)
                    elif options['verbose']:
                        self.stdout.write('ℹ️ Alerte récente déjà existante')
                
                # Compter les nouvelles alertes
                nouvelles_alertes = AlerteStock.objects.filter(vue=False).count()
                alertes_creees = nouvelles_alertes - alertes_actives
                
                if alertes_creees > 0:
                    self.stdout.write(
                        self.style.WARNING(f'✅ {alertes_creees} nouvelle(s) alerte(s) créée(s)')
                    )
                elif options['verbose']:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Aucune nouvelle alerte nécessaire')
                    )
                    
            else:
                # Stock suffisant, vérifier si on peut résoudre des alertes
                alertes_resolues = AlerteStock.objects.filter(
                    vue=False
                ).update(vue=True)
                
                if alertes_resolues > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {alertes_resolues} alerte(s) résolue(s) automatiquement')
                    )
                elif options['verbose']:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Stock suffisant, aucune alerte active')
                    )

            # Afficher les statistiques si demandé
            if options['verbose']:
                self.afficher_statistiques()

            self.stdout.write(
                self.style.SUCCESS('✅ Vérification des alertes terminée')
            )

        except Exception as e:
            logger.error(f"Erreur lors de la vérification des alertes: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur: {e}')
            )

    def afficher_statistiques(self):
        """
        Affiche les statistiques des alertes
        """
        try:
            total_alertes = AlerteStock.objects.count()
            alertes_vues = AlerteStock.objects.filter(vue=True).count()
            alertes_non_vues = AlerteStock.objects.filter(vue=False).count()
            
            self.stdout.write('\n📈 Statistiques des alertes:')
            self.stdout.write(f'   Total: {total_alertes}')
            self.stdout.write(f'   Vues: {alertes_vues}')
            self.stdout.write(f'   Non vues: {alertes_non_vues}')
            
            # Alertes récentes (dernières 24h)
            alertes_recentes = AlerteStock.objects.filter(
                date_alerte__gte=timezone.now() - timezone.timedelta(days=1)
            ).count()
            
            if alertes_recentes > 0:
                self.stdout.write(f'   Dernières 24h: {alertes_recentes}')
            
            # Dernière alerte
            derniere_alerte = AlerteStock.objects.order_by('-date_alerte').first()
            if derniere_alerte:
                self.stdout.write(
                    f'   Dernière alerte: {derniere_alerte.date_alerte.strftime("%d/%m/%Y %H:%M")}'
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage des statistiques: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur statistiques: {e}')
            )

    def check_and_clean_old_alerts(self):
        """
        Nettoie les anciennes alertes (plus de 30 jours et déjà vues)
        """
        try:
            old_alerts = AlerteStock.objects.filter(
                vue=True,
                date_alerte__lt=timezone.now() - timezone.timedelta(days=30)
            )
            
            count = old_alerts.count()
            if count > 0:
                old_alerts.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'🧹 {count} ancienne(s) alerte(s) supprimée(s)')
                )
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des alertes: {e}")