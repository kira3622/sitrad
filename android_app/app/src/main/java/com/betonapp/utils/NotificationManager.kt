package com.betonapp.utils

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.betonapp.R
import com.betonapp.ui.MainActivity
import com.betonapp.data.models.ApiNotification

/**
 * Gestionnaire des notifications pour l'application Béton
 */
class BetonNotificationManager(private val context: Context) {

    companion object {
        // IDs des canaux de notification
        const val CHANNEL_ORDERS = "orders_channel"
        const val CHANNEL_PRODUCTION = "production_channel"
        const val CHANNEL_INVENTORY = "inventory_channel"
        const val CHANNEL_GENERAL = "general_channel"
        
        // IDs des notifications
        const val NOTIFICATION_NEW_ORDER = 1001
        const val NOTIFICATION_PRODUCTION_UPDATE = 1002
        const val NOTIFICATION_INVENTORY_LOW = 1003
        const val NOTIFICATION_DELIVERY = 1004
        const val NOTIFICATION_GENERAL = 1005
    }

    private val notificationManager = NotificationManagerCompat.from(context)

    init {
        createNotificationChannels()
    }

    /**
     * Crée les canaux de notification pour Android 8.0+
     */
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channels = listOf(
                NotificationChannel(
                    CHANNEL_ORDERS,
                    "Commandes",
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "Notifications pour les nouvelles commandes et mises à jour"
                    enableVibration(true)
                    enableLights(true)
                },
                
                NotificationChannel(
                    CHANNEL_PRODUCTION,
                    "Production",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Notifications pour les mises à jour de production"
                    enableVibration(true)
                },
                
                NotificationChannel(
                    CHANNEL_INVENTORY,
                    "Inventaire",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Notifications pour les alertes d'inventaire"
                    enableVibration(true)
                },
                
                NotificationChannel(
                    CHANNEL_GENERAL,
                    "Général",
                    NotificationManager.IMPORTANCE_LOW
                ).apply {
                    description = "Notifications générales de l'application"
                }
            )

            val systemNotificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            channels.forEach { channel ->
                systemNotificationManager.createNotificationChannel(channel)
            }
        }
    }

    /**
     * Affiche une notification pour une nouvelle commande
     */
    fun showNewOrderNotification(orderNumber: String, clientName: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "orders")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_ORDERS)
            .setSmallIcon(R.drawable.ic_orders)
            .setContentTitle("Nouvelle commande")
            .setContentText("Commande #$orderNumber de $clientName")
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("Une nouvelle commande #$orderNumber a été reçue de $clientName. Cliquez pour voir les détails."))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setVibrate(longArrayOf(0, 500, 250, 500))
            .build()

        notificationManager.notify(NOTIFICATION_NEW_ORDER, notification)
    }

    /**
     * Affiche une notification pour une mise à jour de production
     */
    fun showProductionUpdateNotification(productionId: String, status: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "production")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_PRODUCTION)
            .setSmallIcon(R.drawable.ic_production)
            .setContentTitle("Mise à jour production")
            .setContentText("Production #$productionId: $status")
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("La production #$productionId a été mise à jour. Nouveau statut: $status"))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(NOTIFICATION_PRODUCTION_UPDATE, notification)
    }

    /**
     * Affiche une notification pour un stock faible
     */
    fun showLowInventoryNotification(materialName: String, currentStock: Double, minThreshold: Double) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "inventory")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_INVENTORY)
            .setSmallIcon(R.drawable.ic_inventory)
            .setContentTitle("Stock faible")
            .setContentText("$materialName: ${currentStock}kg (seuil: ${minThreshold}kg)")
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("Le stock de $materialName est faible: ${currentStock}kg restant (seuil minimum: ${minThreshold}kg). Pensez à réapprovisionner."))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setColor(context.getColor(android.R.color.holo_orange_dark))
            .build()

        notificationManager.notify(NOTIFICATION_INVENTORY_LOW, notification)
    }

    /**
     * Affiche une notification pour une livraison
     */
    fun showDeliveryNotification(orderNumber: String, deliveryTime: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "orders")
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_ORDERS)
            .setSmallIcon(R.drawable.ic_orders)
            .setContentTitle("Livraison programmée")
            .setContentText("Commande #$orderNumber - $deliveryTime")
            .setStyle(NotificationCompat.BigTextStyle()
                .bigText("La livraison de la commande #$orderNumber est programmée pour $deliveryTime."))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setVibrate(longArrayOf(0, 300, 200, 300))
            .build()

        notificationManager.notify(NOTIFICATION_DELIVERY, notification)
    }

    /**
     * Affiche une notification générale
     */
    fun showGeneralNotification(title: String, message: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_GENERAL)
            .setSmallIcon(R.drawable.ic_notifications)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(NOTIFICATION_GENERAL, notification)
    }

    /**
     * Annule toutes les notifications
     */
    fun cancelAllNotifications() {
        notificationManager.cancelAll()
    }

    /**
     * Annule une notification spécifique
     */
    fun cancelNotification(notificationId: Int) {
        notificationManager.cancel(notificationId)
    }

    /**
     * Vérifie si les notifications sont activées
     */
    fun areNotificationsEnabled(): Boolean {
        return notificationManager.areNotificationsEnabled()
    }

    /**
     * Affiche une notification provenant de l'API
     */
    fun showApiNotification(apiNotification: ApiNotification) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("navigate_to", "notifications")
            putExtra("notification_id", apiNotification.id)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // Déterminer le canal et l'icône selon le type de notification
        val (channelId, iconRes) = when (apiNotification.type.lowercase()) {
            "commande", "order" -> CHANNEL_ORDERS to R.drawable.ic_orders
            "production" -> CHANNEL_PRODUCTION to R.drawable.ic_production
            "inventaire", "inventory", "stock" -> CHANNEL_INVENTORY to R.drawable.ic_inventory
            else -> CHANNEL_GENERAL to R.drawable.ic_notifications
        }

        // Déterminer la priorité selon le niveau de priorité de l'API
        val priority = when (apiNotification.priority?.lowercase()) {
            "high", "haute", "urgent" -> NotificationCompat.PRIORITY_HIGH
            "medium", "moyenne", "normal" -> NotificationCompat.PRIORITY_DEFAULT
            "low", "basse", "faible" -> NotificationCompat.PRIORITY_LOW
            else -> NotificationCompat.PRIORITY_DEFAULT
        }

        val notification = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(iconRes)
            .setContentTitle(apiNotification.title)
            .setContentText(apiNotification.message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(apiNotification.message))
            .setPriority(priority)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setWhen(apiNotification.timestamp)
            .setShowWhen(true)
            .apply {
                // Ajouter vibration pour les notifications haute priorité
                if (priority == NotificationCompat.PRIORITY_HIGH) {
                    setVibrate(longArrayOf(0, 500, 250, 500))
                }
                
                // Ajouter couleur selon le type
                when (apiNotification.type.lowercase()) {
                    "commande", "order" -> setColor(context.getColor(android.R.color.holo_blue_dark))
                    "production" -> setColor(context.getColor(android.R.color.holo_green_dark))
                    "inventaire", "inventory", "stock" -> setColor(context.getColor(android.R.color.holo_orange_dark))
                    else -> setColor(context.getColor(android.R.color.holo_blue_light))
                }
            }
            .build()

        // Utiliser l'ID de la notification API comme ID de notification système
        val notificationId = apiNotification.id.hashCode()
        notificationManager.notify(notificationId, notification)
    }
}