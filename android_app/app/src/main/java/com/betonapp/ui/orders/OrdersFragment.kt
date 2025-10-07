package com.betonapp.ui.orders

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.betonapp.R
import com.google.android.material.snackbar.Snackbar
import com.betonapp.databinding.FragmentOrdersBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class OrdersFragment : Fragment() {
    
    private var _binding: FragmentOrdersBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: OrdersViewModel by viewModels()
    private lateinit var ordersAdapter: OrdersAdapter
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentOrdersBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupObservers()
        setupRefreshListener()
        setupFab()
    }

    private fun setupRecyclerView() {
        ordersAdapter = OrdersAdapter { order ->
            onOrderClick(order)
        }
        binding.recyclerViewOrders.apply {
            adapter = ordersAdapter
            layoutManager = LinearLayoutManager(context)
        }
    }

    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect {
                updateUI(it)
            }
        }
    }

    private fun navigateToOrderDetail(orderId: Long) {
        val bundle = bundleOf("orderId" to orderId)
        findNavController().navigate(R.id.action_orders_to_order_detail, bundle)
    }

    private fun setupRefreshListener() {
        binding.swipeRefreshLayout.setOnRefreshListener {
            viewModel.loadOrders()
        }
    }
    
    private fun setupFab() {
        binding.fabNewOrder.setOnClickListener {
            try {
                android.util.Log.d("OrdersFragment", "FAB clicked - attempting navigation")
                findNavController().navigate(R.id.action_orders_to_create_order)
                android.util.Log.d("OrdersFragment", "Navigation successful")
            } catch (e: Exception) {
                android.util.Log.e("OrdersFragment", "Navigation failed", e)
                Snackbar.make(binding.root, "Erreur de navigation: ${e.message}", Snackbar.LENGTH_LONG).show()
            }
        }
    }
    
    private fun updateUI(state: OrdersUiState) {
        binding.swipeRefreshLayout.isRefreshing = state.isLoading
        
        if (state.errorMessage != null) {
            Snackbar.make(binding.root, state.errorMessage, Snackbar.LENGTH_LONG).show()
            viewModel.clearError()
            return
        }
        
        ordersAdapter.submitList(state.orders)
        
        // Afficher/masquer le message "pas de données"
        binding.textNoData.visibility = if (state.orders.isEmpty() && !state.isLoading) {
            View.VISIBLE
        } else {
            View.GONE
        }
    }

    private fun onOrderClick(order: com.betonapp.data.models.Commande) {
        navigateToOrderDetail(order.id.toLong())
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}