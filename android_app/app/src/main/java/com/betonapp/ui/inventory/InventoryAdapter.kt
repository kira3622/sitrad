package com.betonapp.ui.inventory

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.betonapp.R
import com.betonapp.data.models.MatierePremiere
import com.betonapp.databinding.ItemInventoryBinding
import java.text.NumberFormat
import java.util.*

class InventoryAdapter(
    private val onInventoryClick: (MatierePremiere) -> Unit
) : ListAdapter<MatierePremiere, InventoryAdapter.InventoryViewHolder>(InventoryDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): InventoryViewHolder {
        val binding = ItemInventoryBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return InventoryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: InventoryViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class InventoryViewHolder(
        private val binding: ItemInventoryBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: MatierePremiere) {
            binding.apply {
                textMaterial.text = item.nom
                textCategory.text = "Matière première" // Could be enhanced with actual category
                
                // Format quantities with unit
                val numberFormat = NumberFormat.getNumberInstance(Locale.FRANCE)
                textCurrentQuantity.text = "${numberFormat.format(item.stockActuel)} ${item.unite}"
                textMinThreshold.text = "${numberFormat.format(item.stockMinimum)} ${item.unite}"
                
                // Set status chip based on stock status
                chipStatus.text = when (item.statutStock) {
                    "normal" -> "En stock"
                    "faible" -> "Stock faible"
                    "critique" -> "Stock critique"
                    else -> "Inconnu"
                }
                
                // Set chip color based on status
                val chipColor = when (item.statutStock) {
                    "normal" -> ContextCompat.getColor(root.context, R.color.status_completed)
                    "faible" -> ContextCompat.getColor(root.context, R.color.status_in_progress)
                    "critique" -> ContextCompat.getColor(root.context, R.color.status_cancelled)
                    else -> ContextCompat.getColor(root.context, R.color.status_pending)
                }
                chipStatus.setChipBackgroundColorResource(android.R.color.transparent)
                chipStatus.chipBackgroundColor = android.content.res.ColorStateList.valueOf(chipColor)
                
                // For now, set placeholder values for missing fields
                textLastUpdate.text = "Non disponible"
                textLocation.text = "Entrepôt principal"
                
                root.setOnClickListener {
                    onInventoryClick(item)
                }
            }
        }
    }
}

class InventoryDiffCallback : DiffUtil.ItemCallback<MatierePremiere>() {
    override fun areItemsTheSame(oldItem: MatierePremiere, newItem: MatierePremiere): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: MatierePremiere, newItem: MatierePremiere): Boolean {
        return oldItem == newItem
    }
}