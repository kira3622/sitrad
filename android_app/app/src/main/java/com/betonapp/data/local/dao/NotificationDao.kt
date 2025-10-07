package com.betonapp.data.local.dao

import androidx.room.*
import com.betonapp.data.local.entities.NotificationEntity
import kotlinx.coroutines.flow.Flow

/**
 * DAO pour les opérations sur les notifications
 */
@Dao
interface NotificationDao {
    
    /**
     * Récupérer toutes les notifications triées par timestamp décroissant
     */
    @Query("SELECT * FROM notifications ORDER BY timestamp DESC")
    fun getAllNotifications(): Flow<List<NotificationEntity>>
    
    /**
     * Récupérer les notifications non lues
     */
    @Query("SELECT * FROM notifications WHERE isRead = 0 ORDER BY timestamp DESC")
    fun getUnreadNotifications(): Flow<List<NotificationEntity>>
    
    /**
     * Récupérer une notification par ID
     */
    @Query("SELECT * FROM notifications WHERE id = :id")
    suspend fun getNotificationById(id: String): NotificationEntity?
    
    /**
     * Insérer une nouvelle notification
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertNotification(notification: NotificationEntity)
    
    /**
     * Insérer plusieurs notifications
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertNotifications(notifications: List<NotificationEntity>)
    
    /**
     * Mettre à jour une notification
     */
    @Update
    suspend fun updateNotification(notification: NotificationEntity)
    
    /**
     * Marquer une notification comme lue
     */
    @Query("UPDATE notifications SET isRead = 1 WHERE id = :id")
    suspend fun markAsRead(id: String)
    
    /**
     * Marquer toutes les notifications comme lues
     */
    @Query("UPDATE notifications SET isRead = 1")
    suspend fun markAllAsRead()
    
    /**
     * Supprimer une notification
     */
    @Delete
    suspend fun deleteNotification(notification: NotificationEntity)
    
    /**
     * Supprimer toutes les notifications
     */
    @Query("DELETE FROM notifications")
    suspend fun deleteAllNotifications()
    
    /**
     * Supprimer les notifications anciennes (plus de 30 jours)
     */
    @Query("DELETE FROM notifications WHERE timestamp < :cutoffTime")
    suspend fun deleteOldNotifications(cutoffTime: Long)
    
    /**
     * Compter les notifications non lues
     */
    @Query("SELECT COUNT(*) FROM notifications WHERE isRead = 0")
    fun getUnreadCount(): Flow<Int>
}