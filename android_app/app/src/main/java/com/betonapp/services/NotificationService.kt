package com.betonapp.services

import android.content.Context
import androidx.work.*
import com.betonapp.data.repository.DashboardRepository
import com.betonapp.data.repository.InventoryRepository
import com.betonapp.data.repository.OrdersRepository
import com.betonapp.data.repository.ProductionRepository
import com.betonapp.data.repository.NotificationsRepository
import com.betonapp.data.local.entities.NotificationEntity
import com.betonapp.utils.BetonNotificationManager
import com.betonapp.di.ChildWorkerFactory
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import dagger.hilt.android.qualifiers.ApplicationContext
import androidx.work.ListenableWorker
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.concurrent.TimeUnit
import javax.inject.Inject

/**
 * Worker pour vérifier les mises à jour et envoyer des notifications
 */
class NotificationWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val ordersRepository: OrdersRepository,
    private val productionRepository: ProductionRepository,
    private val inventoryRepository: InventoryRepository,
    private val dashboardRepository: DashboardRepository,
    private val notificationsRepository: NotificationsRepository
) : CoroutineWorker(context, params) {

    @dagger.assisted.AssistedFactory
    interface Factory {
        fun create(context: Context, params: WorkerParameters): NotificationWorker
    }

    private val notificationManager = BetonNotificationManager(context)

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            // Récupérer les notifications depuis l'API
            fetchAndProcessApiNotifications()
            
            // Vérifier les nouvelles commandes (données réelles)
            checkNewOrders()
            
            // Vérifier les mises à jour de production (données réelles)
            checkProductionUpdates()
            
            // Vérifier les stocks faibles (données réelles)
            checkLowInventory()
            
            // Vérifier les livraisons programmées (données réelles)
            checkScheduledDeliveries()
            
            Result.success()
        } catch (e: Exception) {
            e.printStackTrace()
            Result.retry()
        }
    }

    /**
     * Récupère les notifications depuis l'API et les traite
     */
    private suspend fun fetchAndProcessApiNotifications() {
        try {
            // Récupérer les notifications non lues depuis l'API
            val apiResult = notificationsRepository.getNotificationsFromApi(isRead = false)
            
            if (apiResult.isSuccess) {
                val notifications = apiResult.getOrNull() ?: emptyList()
                
                // Traiter chaque notification de l'API
                notifications.forEach { apiNotification ->
                    // Afficher la notification système
                    notificationManager.showApiNotification(apiNotification)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private suspend fun checkNewOrders() {
        try {
            // Récupérer les commandes récentes (dernières 24h) depuis l'API
            val recentOrders = ordersRepository.getRecentOrders()
            
            // Vérifier s'il y a de nouvelles commandes non notifiées
            recentOrders.forEach { order ->
                // Afficher la notification système
                notificationManager.showNewOrderNotification(
                    orderNumber = order.numero ?: "N/A",
                    clientName = order.clientNom ?: "Client inconnu"
                )
                
                // Créer une notification locale pour l'historique
                val notification = NotificationEntity(
                    id = "order_${order.id}_${System.currentTimeMillis()}",
                    title = "Nouvelle commande",
                    message = "Commande ${order.numero} de ${order.clientNom ?: "Client inconnu"}",
                    type = "new_order",
                    timestamp = System.currentTimeMillis(),
                    isRead = false,
                    relatedObjectId = order.id.toString(),
                    relatedObjectType = "commande",
                    priority = "medium"
                )
                notificationsRepository.addNotification(notification)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private suspend fun checkProductionUpdates() {
        try {
            // Récupérer les productions avec des mises à jour récentes depuis l'API
            val recentProductions = productionRepository.getRecentProductionUpdates()
            
            recentProductions.forEach { production ->
                // Pour les productions prêtes, on vérifie le statut
                if (production.statut == "PRET") {
                    // Afficher la notification système
                    notificationManager.showProductionUpdateNotification(
                        productionId = production.id.toString(),
                        status = "PRET"
                    )
                    
                    // Créer une notification locale pour l'historique
                    val notification = NotificationEntity(
                        id = "production_${production.id}_${System.currentTimeMillis()}",
                        title = "Production prête",
                        message = "La production #${production.id} est prête pour livraison",
                        type = "production_update",
                        timestamp = System.currentTimeMillis(),
                        isRead = false,
                        relatedObjectId = production.id.toString(),
                        relatedObjectType = "production",
                        priority = "high"
                    )
                    notificationsRepository.addNotification(notification)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private suspend fun checkLowInventory() {
        try {
            // Récupérer les matières premières avec stock faible depuis l'API
            val lowStockItems = inventoryRepository.getLowStockItems()
            
            lowStockItems.forEach { item ->
                if (item.stockActuel <= item.stockMinimum) {
                    // Afficher la notification système
                    notificationManager.showLowInventoryNotification(
                        materialName = item.nom ?: "Article inconnu",
                        currentStock = item.stockActuel.toDouble(),
                        minThreshold = item.stockMinimum.toDouble()
                    )
                    
                    // Créer une notification locale pour l'historique
                    val notification = NotificationEntity(
                        id = "inventory_${item.id}_${System.currentTimeMillis()}",
                        title = "Stock critique",
                        message = "Stock faible pour ${item.nom ?: "Article inconnu"}: ${item.stockActuel}/${item.stockMinimum} ${item.unite ?: "unités"}",
                        type = "low_inventory",
                        timestamp = System.currentTimeMillis(),
                        isRead = false,
                        relatedObjectId = item.id.toString(),
                        relatedObjectType = "matiere_premiere",
                        priority = "high"
                    )
                    notificationsRepository.addNotification(notification)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private suspend fun checkScheduledDeliveries() {
        try {
            // Récupérer les livraisons programmées pour aujourd'hui depuis l'API
            val todayDeliveries = ordersRepository.getTodayDeliveries()
            
            todayDeliveries.forEach { order ->
                if (!order.deliveryNotified) {
                    // Afficher la notification système
                    notificationManager.showDeliveryNotification(
                        orderNumber = order.numero ?: "CMD-${order.id}",
                        deliveryTime = order.dateLivraisonPrevue ?: order.dateLivraisonSouhaitee
                    )
                    
                    // Créer une notification locale pour l'historique
                    val notification = NotificationEntity(
                        id = "delivery_${order.id}_${System.currentTimeMillis()}",
                        title = "Livraison programmée",
                        message = "Livraison de la commande ${order.numero ?: "CMD-${order.id}"} prévue aujourd'hui",
                        type = "delivery",
                        timestamp = System.currentTimeMillis(),
                        isRead = false,
                        relatedObjectId = order.id.toString(),
                        relatedObjectType = "commande",
                        priority = "medium"
                    )
                    notificationsRepository.addNotification(notification)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    companion object {
        const val WORK_NAME = "notification_check_work"
        
        /**
         * Programme le worker pour vérifier les notifications périodiquement
         */
        fun schedulePeriodicWork(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .setRequiresBatteryNotLow(true)
                .build()

            val periodicWorkRequest = PeriodicWorkRequestBuilder<NotificationWorker>(
                15, TimeUnit.MINUTES // Vérifier toutes les 15 minutes
            )
                .setConstraints(constraints)
                .setBackoffCriteria(
                    BackoffPolicy.LINEAR,
                    30000, // 30 secondes
                    TimeUnit.MILLISECONDS
                )
                .build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                periodicWorkRequest
            )
        }

        /**
         * Déclenche une exécution immédiate du worker pour validation.
         */
        fun runOnceNow(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val oneTimeWorkRequest = OneTimeWorkRequestBuilder<NotificationWorker>()
                .setConstraints(constraints)
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "${WORK_NAME}_one_shot",
                ExistingWorkPolicy.REPLACE,
                oneTimeWorkRequest
            )
        }

        /**
         * Annule le worker de notifications
         */
        fun cancelWork(context: Context) {
            WorkManager.getInstance(context).cancelUniqueWork(WORK_NAME)
        }
    }
}


