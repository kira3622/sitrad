package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.local.dao.NotificationDao
import com.betonapp.data.local.entities.NotificationEntity
import com.betonapp.data.models.ApiNotification
import com.betonapp.data.models.NotificationSummary
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NotificationsRepository @Inject constructor(
    private val notificationDao: NotificationDao,
    private val apiService: ApiService
) {

    // ==================== API METHODS ====================
    
    /**
     * Récupère les notifications depuis l'API
     */
    suspend fun getNotificationsFromApi(
        page: Int? = null,
        type: String? = null,
        isRead: Boolean? = null
    ): Result<List<ApiNotification>> {
        return try {
            val response = apiService.getNotifications(page, type, isRead)
            if (response.isSuccessful) {
                val notifications = response.body()?.results ?: emptyList()
                // Synchroniser avec la base de données locale
                syncNotificationsToLocal(notifications)
                Result.success(notifications)
            } else {
                Result.failure(Exception("Erreur API: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Récupère le résumé des notifications depuis l'API
     */
    suspend fun getNotificationsSummaryFromApi(): Result<NotificationSummary> {
        return try {
            val response = apiService.getNotificationsSummary()
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Erreur API: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Marque une notification comme lue via l'API
     */
    suspend fun markNotificationAsReadApi(id: String): Result<Unit> {
        return try {
            val response = apiService.markNotificationAsRead(id)
            if (response.isSuccessful) {
                // Mettre à jour la base de données locale
                notificationDao.markAsRead(id)
                Result.success(Unit)
            } else {
                Result.failure(Exception("Erreur API: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Marque toutes les notifications comme lues via l'API
     */
    suspend fun markAllNotificationsAsReadApi(): Result<Unit> {
        return try {
            val response = apiService.markAllNotificationsAsRead()
            if (response.isSuccessful) {
                // Mettre à jour la base de données locale
                notificationDao.markAllAsRead()
                Result.success(Unit)
            } else {
                Result.failure(Exception("Erreur API: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Supprime une notification via l'API
     */
    suspend fun deleteNotificationApi(id: String): Result<Unit> {
        return try {
            val response = apiService.deleteNotification(id)
            if (response.isSuccessful) {
                // Supprimer de la base de données locale
                val notification = notificationDao.getNotificationById(id)
                notification?.let { notificationDao.deleteNotification(it) }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Erreur API: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ==================== SYNCHRONIZATION ====================
    
    /**
     * Synchronise les notifications de l'API vers la base de données locale
     */
    private suspend fun syncNotificationsToLocal(apiNotifications: List<ApiNotification>) {
        val localNotifications = apiNotifications.map { apiNotification ->
            NotificationEntity(
                id = apiNotification.id,
                title = apiNotification.title,
                message = apiNotification.message,
                type = apiNotification.type,
                timestamp = apiNotification.timestamp,
                isRead = apiNotification.isRead,
                relatedObjectId = apiNotification.relatedObjectId?.toString(),
                relatedObjectType = apiNotification.relatedObjectType,
                priority = apiNotification.priority ?: "medium"
            )
        }
        
        // Insérer ou mettre à jour les notifications
        notificationDao.insertNotifications(localNotifications)
    }

    // ==================== LOCAL DATABASE METHODS (FALLBACK) ====================
    
    /**
     * Récupère toutes les notifications depuis la base de données locale
     */
    fun getAllNotifications(): Flow<List<NotificationEntity>> {
        return notificationDao.getAllNotifications()
    }

    /**
     * Récupère les notifications non lues depuis la base de données locale
     */
    fun getUnreadNotifications(): Flow<List<NotificationEntity>> {
        return notificationDao.getUnreadNotifications()
    }

    /**
     * Récupère le nombre de notifications non lues depuis la base de données locale
     */
    fun getUnreadCount(): Flow<Int> {
        return notificationDao.getUnreadCount()
    }

    /**
     * Ajoute une notification à la base de données locale
     */
    suspend fun addNotification(notification: NotificationEntity) {
        notificationDao.insertNotification(notification)
    }

    /**
     * Marque une notification comme lue dans la base de données locale
     */
    suspend fun markAsRead(notificationId: String) {
        notificationDao.markAsRead(notificationId)
    }

    /**
     * Supprime une notification de la base de données locale
     */
    suspend fun deleteNotification(notificationId: String) {
        val notification = notificationDao.getNotificationById(notificationId)
        notification?.let { notificationDao.deleteNotification(it) }
    }

    /**
     * Nettoie les anciennes notifications de la base de données locale
     */
    suspend fun cleanOldNotifications(daysToKeep: Int = 30) {
        notificationDao.deleteOldNotifications(System.currentTimeMillis() - (daysToKeep * 24 * 60 * 60 * 1000))
    }
    
    suspend fun markAllAsReadLocal() {
        notificationDao.markAllAsRead()
    }
    
    suspend fun deleteAllNotificationsLocal() {
        notificationDao.deleteAllNotifications()
    }

    // ==================== HYBRID METHODS ====================
    
    /**
     * Récupère les notifications en essayant d'abord l'API, puis la base locale en cas d'échec
     */
    fun getNotificationsHybrid(): Flow<List<NotificationEntity>> = flow {
        try {
            // Essayer de récupérer depuis l'API
            val apiResult = getNotificationsFromApi()
            if (apiResult.isSuccess) {
                // Émettre les données locales mises à jour
                getAllNotifications().collect { emit(it) }
            } else {
                // En cas d'échec, utiliser les données locales
                getAllNotifications().collect { emit(it) }
            }
        } catch (e: Exception) {
            // En cas d'erreur, utiliser les données locales
            getAllNotifications().collect { emit(it) }
        }
    }
    
    /**
     * Récupère le nombre de notifications non lues en mode hybride
     */
    fun getUnreadCountHybrid(): Flow<Int> = flow {
        try {
            // Essayer de récupérer le résumé depuis l'API
            val summaryResult = getNotificationsSummaryFromApi()
            if (summaryResult.isSuccess) {
                emit(summaryResult.getOrNull()?.unreadCount ?: 0)
            } else {
                // En cas d'échec, utiliser les données locales
                getUnreadCount().collect { emit(it) }
            }
        } catch (e: Exception) {
            // En cas d'erreur, utiliser les données locales
            getUnreadCount().collect { emit(it) }
        }
    }

    // ==================== DEVELOPMENT METHODS ====================
    
    /**
     * Ajoute des notifications de test (pour le développement uniquement)
     */
    suspend fun addTestNotifications() {
        // Cette méthode est conservée pour les tests locaux si nécessaire
        val testNotifications = listOf(
            NotificationEntity(
                id = "test_1",
                title = "Test Local",
                message = "Notification de test locale",
                type = "info",
                timestamp = System.currentTimeMillis(),
                isRead = false
            )
        )
        
        testNotifications.forEach { notification ->
            notificationDao.insertNotification(notification)
        }
    }
}