from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Stock, AlerteStock, Approvisionnement, Consommation
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Approvisionnement)
def update_stock_after_approvisionnement(sender, instance, created, **kwargs):
    """
    Met à jour le stock après un approvisionnement
    """
    if created:
        try:
            stock = Stock.get_stock_actuel()
            stock.recalculer_stock()
            
            # Vérifier si l'alerte de stock faible peut être résolue
            check_and_resolve_low_stock_alert(stock)
            
            logger.info(f"Stock mis à jour après approvisionnement: +{instance.quantite}L")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du stock après approvisionnement: {e}")

@receiver(post_save, sender=Consommation)
def update_stock_after_consommation(sender, instance, created, **kwargs):
    """
    Met à jour le stock après une consommation
    """
    if created:
        try:
            stock = Stock.get_stock_actuel()
            stock.recalculer_stock()
            
            # Vérifier si une alerte de stock faible doit être créée
            check_and_create_low_stock_alert(stock)
            
            logger.info(f"Stock mis à jour après consommation: -{instance.quantite}L")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du stock après consommation: {e}")

def check_and_create_low_stock_alert(stock):
    """
    Vérifie si le stock est en dessous du seuil et crée une alerte si nécessaire
    """
    try:
        if stock.quantite <= stock.seuil_minimum:
            # Vérifier s'il n'y a pas déjà une alerte récente (moins de 1 heure)
            recent_alert = AlerteStock.objects.filter(
                vue=False,
                date_alerte__gte=timezone.now() - timezone.timedelta(hours=1)
            ).first()
            
            if not recent_alert:
                # Créer une nouvelle alerte
                alerte = AlerteStock.objects.create(
                    quantite_stock=stock.quantite,
                    seuil_minimum=stock.seuil_minimum,
                    message=f"Stock de gasoil faible: {stock.quantite:.0f}L (seuil: {stock.seuil_minimum:.0f}L)",
                    vue=False
                )
                
                # Envoyer une notification par email si configuré
                send_low_stock_notification(alerte, stock)
                
                logger.warning(f"Alerte de stock faible créée: {stock.quantite}L")
                
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du stock faible: {e}")

def check_and_resolve_low_stock_alert(stock):
    """
    Résout automatiquement les alertes de stock faible si le stock est suffisant
    """
    try:
        if stock.quantite > stock.seuil_minimum:
            # Marquer toutes les alertes de stock faible comme vues
            alertes_resolues = AlerteStock.objects.filter(
                vue=False
            ).update(vue=True)
            
            if alertes_resolues > 0:
                logger.info(f"{alertes_resolues} alerte(s) de stock faible résolue(s)")
                
    except Exception as e:
        logger.error(f"Erreur lors de la résolution des alertes de stock: {e}")

def send_low_stock_notification(alerte, stock):
    """
    Envoie une notification par email pour les alertes de stock faible
    """
    try:
        # Récupérer les utilisateurs administrateurs
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        admin_emails = [user.email for user in admin_users if user.email]
        
        if admin_emails and hasattr(settings, 'EMAIL_HOST'):
            niveau = 'CRITIQUE' if stock.quantite <= stock.seuil_minimum * 0.5 else 'MOYEN'
            subject = f"🚨 Alerte Stock Gasoil - Niveau {niveau}"
            
            message = f"""
Bonjour,

Une alerte de stock faible a été générée:

📊 Stock actuel: {stock.quantite:.0f} litres
⚠️ Seuil minimum: {stock.seuil_minimum:.0f} litres
🔴 Niveau d'urgence: {niveau}

Message: {alerte.message}

Date de l'alerte: {alerte.date_alerte.strftime('%d/%m/%Y à %H:%M')}

Veuillez prendre les mesures nécessaires pour réapprovisionner le stock.

---
Système de Gestion du Gasoil
            """
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                    recipient_list=admin_emails,
                    fail_silently=False,
                )
                logger.info(f"Notification email envoyée à {len(admin_emails)} administrateur(s)")
                
            except Exception as email_error:
                logger.error(f"Erreur lors de l'envoi de l'email: {email_error}")
                
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la notification: {e}")

@receiver(post_delete, sender=Approvisionnement)
def update_stock_after_approvisionnement_delete(sender, instance, **kwargs):
    """
    Met à jour le stock après suppression d'un approvisionnement
    """
    try:
        stock = Stock.get_stock_actuel()
        stock.recalculer_stock()
        
        # Vérifier si une alerte de stock faible doit être créée
        check_and_create_low_stock_alert(stock)
        
        logger.info(f"Stock mis à jour après suppression d'approvisionnement: -{instance.quantite}L")
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du stock après suppression: {e}")

@receiver(post_delete, sender=Consommation)
def update_stock_after_consommation_delete(sender, instance, **kwargs):
    """
    Met à jour le stock après suppression d'une consommation
    """
    try:
        stock = Stock.get_stock_actuel()
        stock.recalculer_stock()
        
        # Vérifier si l'alerte de stock faible peut être résolue
        check_and_resolve_low_stock_alert(stock)
        
        logger.info(f"Stock mis à jour après suppression de consommation: +{instance.quantite}L")
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du stock après suppression: {e}")

def create_manual_alert(message):
    """
    Fonction utilitaire pour créer manuellement des alertes
    """
    try:
        stock = Stock.get_stock_actuel()
        alerte = AlerteStock.objects.create(
            quantite_stock=stock.quantite,
            seuil_minimum=stock.seuil_minimum,
            message=message,
            vue=False
        )
        logger.info(f"Alerte manuelle créée: {message}")
        return alerte
        
    except Exception as e:
        logger.error(f"Erreur lors de la création d'alerte manuelle: {e}")
        return None

def check_stock_rupture():
    """
    Fonction pour vérifier si le stock est en rupture (0 ou négatif)
    """
    try:
        stock = Stock.get_stock_actuel()
        if stock.quantite <= 0:
            # Vérifier s'il n'y a pas déjà une alerte de rupture récente
            recent_rupture_alert = AlerteStock.objects.filter(
                vue=False,
                message__icontains='RUPTURE',
                date_alerte__gte=timezone.now() - timezone.timedelta(hours=1)
            ).first()
            
            if not recent_rupture_alert:
                alerte = AlerteStock.objects.create(
                    quantite_stock=stock.quantite,
                    seuil_minimum=stock.seuil_minimum,
                    message=f"RUPTURE DE STOCK: {stock.quantite:.0f}L - Réapprovisionnement urgent requis!",
                    vue=False
                )
                
                # Envoyer une notification urgente
                send_rupture_stock_notification(alerte, stock)
                
                logger.critical(f"RUPTURE DE STOCK détectée: {stock.quantite}L")
                
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de rupture de stock: {e}")

def send_rupture_stock_notification(alerte, stock):
    """
    Envoie une notification urgente pour rupture de stock
    """
    try:
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        admin_emails = [user.email for user in admin_users if user.email]
        
        if admin_emails and hasattr(settings, 'EMAIL_HOST'):
            subject = "🚨🚨 RUPTURE DE STOCK GASOIL - ACTION URGENTE REQUISE"
            
            message = f"""
ALERTE CRITIQUE - RUPTURE DE STOCK

🚨 STOCK ACTUEL: {stock.quantite:.0f} litres
⚠️ SEUIL MINIMUM: {stock.seuil_minimum:.0f} litres

SITUATION: RUPTURE DE STOCK DÉTECTÉE
ACTION REQUISE: RÉAPPROVISIONNEMENT IMMÉDIAT

Date de l'alerte: {alerte.date_alerte.strftime('%d/%m/%Y à %H:%M')}

VEUILLEZ PRENDRE DES MESURES IMMÉDIATES POUR ÉVITER L'ARRÊT DES OPÉRATIONS.

---
Système de Gestion du Gasoil - Alerte Automatique
            """
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                    recipient_list=admin_emails,
                    fail_silently=False,
                )
                logger.critical(f"Notification de rupture envoyée à {len(admin_emails)} administrateur(s)")
                
            except Exception as email_error:
                logger.error(f"Erreur lors de l'envoi de l'email de rupture: {email_error}")
                
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la notification de rupture: {e}")