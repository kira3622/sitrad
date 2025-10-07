package com.betonapp.ui.notifications

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.betonapp.R
import com.betonapp.databinding.ItemNotificationBinding
import java.text.SimpleDateFormat
import java.util.*

/**
 * Adaptateur pour afficher la liste des notifications
 */
class NotificationsAdapter(
    private val onNotificationClick: (NotificationItem) -> Unit
) : ListAdapter<NotificationItem, NotificationsAdapter.NotificationViewHolder>(NotificationDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): NotificationViewHolder {
        val binding = ItemNotificationBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return NotificationViewHolder(binding)
    }

    override fun onBindViewHolder(holder: NotificationViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class NotificationViewHolder(
        private val binding: ItemNotificationBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(notification: NotificationItem) {
            binding.apply {
                textViewTitle.text = notification.title
                textViewMessage.text = notification.message
                textViewTime.text = formatTime(notification.timestamp)
                
                // Icône selon le type de notification
                val iconRes = when (notification.type) {
                    NotificationType.NEW_ORDER -> R.drawable.ic_shopping_cart
                    NotificationType.PRODUCTION_UPDATE -> R.drawable.ic_build
                    NotificationType.LOW_INVENTORY -> R.drawable.ic_warning
                    NotificationType.DELIVERY -> R.drawable.ic_local_shipping
                    NotificationType.GENERAL -> R.drawable.ic_notifications
                }
                imageViewIcon.setImageResource(iconRes)
                
                // Couleur de l'icône selon le type
                val iconColor = when (notification.type) {
                    NotificationType.NEW_ORDER -> R.color.green_500
                    NotificationType.PRODUCTION_UPDATE -> R.color.blue_500
                    NotificationType.LOW_INVENTORY -> R.color.orange_500
                    NotificationType.DELIVERY -> R.color.purple_500
                    NotificationType.GENERAL -> R.color.gray_500
                }
                imageViewIcon.setColorFilter(
                    ContextCompat.getColor(itemView.context, iconColor)
                )
                
                // Style différent pour les notifications non lues
                if (!notification.isRead) {
                    cardView.setCardBackgroundColor(
                        ContextCompat.getColor(itemView.context, R.color.blue_50)
                    )
                    textViewTitle.setTextColor(
                        ContextCompat.getColor(itemView.context, R.color.blue_900)
                    )
                    viewUnreadIndicator.visibility = android.view.View.VISIBLE
                } else {
                    cardView.setCardBackgroundColor(
                        ContextCompat.getColor(itemView.context, android.R.color.white)
                    )
                    textViewTitle.setTextColor(
                        ContextCompat.getColor(itemView.context, R.color.gray_900)
                    )
                    viewUnreadIndicator.visibility = android.view.View.GONE
                }
                
                // Gestion du clic
                root.setOnClickListener {
                    onNotificationClick(notification)
                }
            }
        }

        private fun formatTime(timestamp: Long): String {
            val now = System.currentTimeMillis()
            val diff = now - timestamp
            
            return when {
                diff < 60000 -> "À l'instant" // Moins d'1 minute
                diff < 3600000 -> "${diff / 60000}m" // Moins d'1 heure
                diff < 86400000 -> "${diff / 3600000}h" // Moins d'1 jour
                diff < 604800000 -> "${diff / 86400000}j" // Moins d'1 semaine
                else -> {
                    val dateFormat = SimpleDateFormat("dd/MM", Locale.getDefault())
                    dateFormat.format(Date(timestamp))
                }
            }
        }
    }
}

/**
 * DiffCallback pour optimiser les mises à jour de la liste
 */
class NotificationDiffCallback : DiffUtil.ItemCallback<NotificationItem>() {
    override fun areItemsTheSame(oldItem: NotificationItem, newItem: NotificationItem): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: NotificationItem, newItem: NotificationItem): Boolean {
        return oldItem == newItem
    }
}