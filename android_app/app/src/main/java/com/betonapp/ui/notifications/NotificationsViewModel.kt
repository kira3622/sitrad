package com.betonapp.ui.notifications

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.repository.NotificationsRepository
import com.betonapp.data.local.entities.toNotificationItem
import com.betonapp.data.local.entities.toNotificationEntity
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch
import java.util.*
import javax.inject.Inject

/**
 * ViewModel pour gérer les notifications
 */
@HiltViewModel
class NotificationsViewModel @Inject constructor(
    private val notificationsRepository: NotificationsRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(NotificationsUiState())
    val uiState: StateFlow<NotificationsUiState> = _uiState.asStateFlow()

    init {
        loadNotifications()
    }

    private fun loadNotifications() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            // Utiliser le mode hybride: tente l'API puis bascule sur le local en cas d'échec
            notificationsRepository.getNotificationsHybrid()
                .catch { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "Erreur lors du chargement des notifications: ${e.message}"
                    )
                }
                .collect { notifications ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        notifications = notifications.map { it.toNotificationItem() },
                        error = null
                    )
                }
        }
    }

    fun markAsRead(notificationId: String) {
        viewModelScope.launch {
            try {
                notificationsRepository.markAsRead(notificationId)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Erreur lors de la mise à jour: ${e.message}"
                )
            }
        }
    }

    fun markAllAsRead() {
        viewModelScope.launch {
            try {
                // Utiliser l'API si disponible, sinon la base locale
                val result = notificationsRepository.markAllNotificationsAsReadApi()
                if (result.isFailure) {
                    // Fallback vers la base locale
                    notificationsRepository.markAllAsReadLocal()
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Erreur lors de la mise à jour: ${e.message}"
                )
            }
        }
    }

    fun clearAllNotifications() {
        viewModelScope.launch {
            try {
                notificationsRepository.deleteAllNotificationsLocal()
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Erreur lors de la suppression: ${e.message}"
                )
            }
        }
    }

    fun addNotification(notification: NotificationItem) {
        viewModelScope.launch {
            try {
                notificationsRepository.addNotification(notification.toNotificationEntity())
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Erreur lors de l'ajout: ${e.message}"
                )
            }
        }
    }

    fun addTestNotifications() {
        viewModelScope.launch {
            try {
                notificationsRepository.addTestNotifications()
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Erreur lors de l'ajout des notifications de test: ${e.message}"
                )
            }
        }
    }

    fun deleteNotification(notificationId: String) {
        viewModelScope.launch {
            try {
                notificationsRepository.deleteNotification(notificationId)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = "Erreur lors de la suppression: ${e.message}"
                )
            }
        }
    }
}

/**
 * État de l'interface utilisateur pour les notifications
 */
data class NotificationsUiState(
    val isLoading: Boolean = false,
    val notifications: List<NotificationItem> = emptyList(),
    val error: String? = null
)

/**
 * Modèle de données pour une notification
 */
data class NotificationItem(
    val id: String,
    val title: String,
    val message: String,
    val type: NotificationType,
    val timestamp: Long,
    val isRead: Boolean = false
)

/**
 * Types de notifications
 */
enum class NotificationType {
    NEW_ORDER,
    PRODUCTION_UPDATE,
    LOW_INVENTORY,
    DELIVERY,
    GENERAL
}