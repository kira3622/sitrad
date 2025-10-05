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
                textProductionNumber.text = production.numeroBon ?: "—"
                textProductionStatus.text = production.statut
                textOrderReference.text = "Commande: #${production.commandeId}"
                textConcreteType.text = "" // Champ non disponible côté backend
                textQuantity.text = "${production.quantiteProduire} m³"

                // Format date: parse input (yyyy-MM-dd) then format (dd/MM/yyyy)
                val outputFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
                val inputFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                textProductionDate.text = try {
                    inputFormat.parse(production.dateProduction)?.let {
                        outputFormat.format(it)
                    } ?: production.dateProduction
                } catch (e: Exception) {
                    production.dateProduction
                }

                // Set status color
                val statusColorRes = when (production.statut.lowercase()) {
                    "planifie" -> android.R.color.darker_gray
                    "en_cours" -> android.R.color.holo_blue_light
                    "termine" -> android.R.color.holo_green_light
                    "annule" -> android.R.color.holo_red_light
                    else -> android.R.color.darker_gray
                }
                val statusColor = ContextCompat.getColor(root.context, statusColorRes)
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