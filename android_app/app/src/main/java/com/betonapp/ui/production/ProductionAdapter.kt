package com.betonapp.ui.production

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.betonapp.R
import com.betonapp.data.models.OrdreProduction
import com.betonapp.databinding.ItemProductionBinding
import java.text.SimpleDateFormat
import java.util.*

class ProductionAdapter(
    private val onProductionClick: (OrdreProduction) -> Unit
) : ListAdapter<OrdreProduction, ProductionAdapter.ProductionViewHolder>(ProductionDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductionViewHolder {
        val binding = ItemProductionBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ProductionViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ProductionViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ProductionViewHolder(
        private val binding: ItemProductionBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        init {
            binding.root.setOnClickListener {
                val position = adapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onProductionClick(getItem(position))
                }
            }
        }

        fun bind(production: OrdreProduction) {
            binding.apply {
                textProductionNumber.text = production.numeroOrdre
                textProductionStatus.text = production.statut
                textOrderReference.text = "Commande: ${production.commande.numeroCommande}"
                textConcreteType.text = production.operateur
                textQuantity.text = "${production.quantiteProduite} m³"
                
                // Format date
                val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
                textProductionDate.text = try {
                    dateFormat.parse(production.dateProduction)?.let { 
                        dateFormat.format(it) 
                    } ?: production.dateProduction
                } catch (e: Exception) {
                    production.dateProduction
                }

                // Set status color
                // Remplacer la référence à status_default par une couleur standard
                val statusColor = when (production.statut.lowercase()) {
                    "en_attente" -> android.R.color.holo_orange_light
                    "en_cours" -> android.R.color.holo_blue_light
                    "termine" -> android.R.color.holo_green_light
                    "annule" -> android.R.color.holo_red_light
                    else -> android.R.color.darker_gray
                }
                textProductionStatus.setTextColor(statusColor)
            }
        }
    }

    private class ProductionDiffCallback : DiffUtil.ItemCallback<OrdreProduction>() {
        override fun areItemsTheSame(oldItem: OrdreProduction, newItem: OrdreProduction): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: OrdreProduction, newItem: OrdreProduction): Boolean {
            return oldItem == newItem
        }
    }
}