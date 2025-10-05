package com.betonapp.ui.orders

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.betonapp.data.models.Commande
import com.betonapp.databinding.ItemOrderBinding
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.*

class OrdersAdapter(
    private val onOrderClick: (Commande) -> Unit
) : ListAdapter<Commande, OrdersAdapter.OrderViewHolder>(OrderDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrderViewHolder {
        val binding = ItemOrderBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return OrderViewHolder(binding)
    }

    override fun onBindViewHolder(holder: OrderViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class OrderViewHolder(
        val binding: ItemOrderBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        init {
            binding.root.setOnClickListener {
                val position = adapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onOrderClick(getItem(position))
                }
            }
        }

        // Dans la méthode bind, utiliser binding pour accéder aux vues
        fun bind(order: Commande) {
            binding.apply {
                textOrderNumber.text = "Commande #${order.id}"
                chipStatus.text = order.statut
                textClientName.text = order.clientNom ?: "Client #${order.clientId}"
                textConcreteType.text = "" // Champ non disponible côté backend
                textQuantity.text = "" // Quantité par lignes de commande (non inclus ici)

                // Format delivery date: yyyy-MM-dd -> dd/MM/yyyy
                val outputFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
                val inputFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                textDeliveryDate.text = try {
                    inputFormat.parse(order.dateLivraisonSouhaitee)?.let {
                        outputFormat.format(it)
                    } ?: "Date inconnue"
                } catch (e: Exception) {
                    "Date inconnue"
                }

                // Prix non disponibles sur Commande côté backend; masquer
                textTotalPrice.text = ""

                val statusColor = when (order.statut.lowercase()) {
                    "en_attente" -> android.R.color.holo_orange_light
                    "en_production" -> android.R.color.holo_blue_light
                    "livree" -> android.R.color.holo_green_light
                    "annulee" -> android.R.color.holo_red_light
                    else -> android.R.color.darker_gray
                }
                chipStatus.setTextColor(root.context.getColor(statusColor))
            }
        }
    }

    private class OrderDiffCallback : DiffUtil.ItemCallback<Commande>() {
        override fun areItemsTheSame(oldItem: Commande, newItem: Commande): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Commande, newItem: Commande): Boolean {
            return oldItem == newItem
        }
    }
}