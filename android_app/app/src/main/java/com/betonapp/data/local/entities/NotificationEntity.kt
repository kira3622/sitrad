package com.betonapp.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.betonapp.ui.notifications.NotificationItem
import com.betonapp.ui.notifications.NotificationType

/**
 * Entité Room pour stocker les notifications localement
 */
@Entity(tableName = "notifications")
data class NotificationEntity(
    @PrimaryKey
    val id: String,
    val title: String,
    val message: String,
    val type: String, // Stocké comme String pour Room
    val timestamp: Long,
    val isRead: Boolean = false,
    val relatedObjectId: String? = null,
    val relatedObjectType: String? = null,
    val priority: String = "medium"
)

/**
 * Extensions pour convertir entre NotificationEntity et NotificationItem
 */
fun NotificationEntity.toNotificationItem(): NotificationItem {
    return NotificationItem(
        id = id,
        title = title,
        message = message,
        type = NotificationType.valueOf(type),
        timestamp = timestamp,
        isRead = isRead
    )
}

fun NotificationItem.toNotificationEntity(): NotificationEntity {
    return NotificationEntity(
        id = id,
        title = title,
        message = message,
        type = type.name,
        timestamp = timestamp,
        isRead = isRead
    )
}