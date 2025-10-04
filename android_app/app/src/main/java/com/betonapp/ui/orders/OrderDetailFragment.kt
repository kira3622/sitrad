package com.betonapp.ui.orders

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.navArgs
import com.betonapp.R
import com.betonapp.data.models.Commande
import com.betonapp.databinding.FragmentOrderDetailBinding
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class OrderDetailFragment : Fragment() {

    private var _binding: FragmentOrderDetailBinding? = null
    private val binding get() = _binding!!

    private val args: OrderDetailFragmentArgs by navArgs()
    private val viewModel: OrderDetailViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentOrderDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        observeUiState()
        viewModel.loadOrder(args.orderId)
    }

    private fun observeUiState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { uiState ->
                updateUi(uiState)
            }
        }
    }

    private fun updateUi(uiState: OrderDetailUiState) {
        binding.progressLoading.visibility = if (uiState.isLoading) View.VISIBLE else View.GONE
        
        uiState.order?.let { order ->
            bindOrderData(order)
        }
        
        uiState.errorMessage?.let { error ->
            showError(error)
            viewModel.clearError()
        }
    }

    private fun bindOrderData(order: Commande) {
        val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
        val currencyFormat = NumberFormat.getCurrencyInstance(Locale.FRANCE)

        binding.apply {
            textOrderNumber.text = order.numeroCommande
            textClientName.text = order.client.nom
            textChantierName.text = order.chantier?.nom ?: getString(R.string.no_chantier)
            textConcreteType.text = order.typeBeton
            textQuantity.text = getString(R.string.quantity_format, order.quantite)
            textOrderDate.text = dateFormat.format(SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).parse(order.dateCommande) ?: Date())
            textDeliveryDate.text = dateFormat.format(SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).parse(order.dateLivraisonPrevue) ?: Date())
            textUnitPrice.text = getString(R.string.unit_price_format, currencyFormat.format(order.prixUnitaire))
            textTotalPrice.text = currencyFormat.format(order.prixTotal)
            
            // Set status chip
            chipStatus.text = getStatusText(order.statut)
            chipStatus.setChipBackgroundColorResource(getStatusColor(order.statut))
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
                viewModel.loadOrder(args.orderId)
            }
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}