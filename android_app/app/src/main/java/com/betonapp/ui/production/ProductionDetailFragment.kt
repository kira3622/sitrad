package com.betonapp.ui.production

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.navArgs
import com.betonapp.R
import com.betonapp.data.models.OrdreProduction
import com.betonapp.databinding.FragmentProductionDetailBinding
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class ProductionDetailFragment : Fragment() {

    private var _binding: FragmentProductionDetailBinding? = null
    private val binding get() = _binding!!

    private val args: ProductionDetailFragmentArgs by navArgs()
    private val viewModel: ProductionDetailViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProductionDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        observeUiState()
        viewModel.loadProduction(args.productionId)
    }

    private fun observeUiState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { uiState ->
                updateUi(uiState)
            }
        }
    }

    private fun updateUi(uiState: ProductionDetailUiState) {
        binding.progressLoading.visibility = if (uiState.isLoading) View.VISIBLE else View.GONE
        
        uiState.production?.let { production ->
            bindProductionData(production)
        }
        
        uiState.errorMessage?.let { error ->
            showError(error)
            viewModel.clearError()
        }
    }

    private fun bindProductionData(production: OrdreProduction) {
        val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())

        binding.apply {
            textProductionNumber.text = production.numeroOrdre
            textOrderNumber.text = production.commande.numeroCommande
            textClientName.text = production.commande.client.nom
            textProductionDate.text = dateFormat.format(SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).parse(production.dateProduction) ?: Date())
            textQuantityProduced.text = getString(R.string.quantity_format, production.quantiteProduite)
            textOperator.text = production.operateur
            
            // Handle notes
            if (production.notes.isNullOrBlank()) {
                cardNotes.visibility = View.GONE
            } else {
                cardNotes.visibility = View.VISIBLE
                textNotes.text = production.notes
            }
            
            // Set status chip
            chipStatus.text = getStatusText(production.statut)
            chipStatus.setChipBackgroundColorResource(getStatusColor(production.statut))
        }
    }

    private fun getStatusText(status: String): String {
        return when (status.lowercase()) {
            "en_attente" -> getString(R.string.status_pending)
            "en_cours" -> getString(R.string.status_in_progress)
            "termine" -> getString(R.string.status_completed)
            "annule" -> getString(R.string.status_cancelled)
            else -> status
        }
    }

    private fun getStatusColor(status: String): Int {
        return when (status.lowercase()) {
            "en_attente" -> R.color.status_pending
            "en_cours" -> R.color.status_in_progress
            "termine" -> R.color.status_completed
            "annule" -> R.color.status_cancelled
            else -> R.color.status_pending
        }
    }

    private fun showError(message: String) {
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG)
            .setAction(getString(R.string.retry)) {
                viewModel.loadProduction(args.productionId)
            }
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}