package com.betonapp.ui.production

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.betonapp.R
import com.google.android.material.snackbar.Snackbar
import com.betonapp.databinding.FragmentProductionBinding
import dagger.hilt.android.AndroidEntryPoint
import android.util.Log
import kotlinx.coroutines.launch

@AndroidEntryPoint
class ProductionFragment : Fragment() {

    private var _binding: FragmentProductionBinding? = null
    private val binding get() = _binding!!

    private val viewModel: ProductionViewModel by viewModels()
    private lateinit var productionAdapter: ProductionAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        Log.d("ProductionFragment", "onCreateView")
        _binding = FragmentProductionBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d("ProductionFragment", "onViewCreated")
        
        setupRecyclerView()
        setupSwipeRefresh()
        setupFab()
        observeUiState()
    }

    private fun setupRecyclerView() {
        productionAdapter = ProductionAdapter { production ->
            onProductionClick(production)
        }
        
        binding.recyclerViewProduction.apply {
            adapter = productionAdapter
            layoutManager = LinearLayoutManager(requireContext())
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefreshLayout.setOnRefreshListener {
            viewModel.refreshProductions()
        }
    }

    private fun setupFab() {
        binding.fabAddProduction.setOnClickListener {
            try {
                findNavController().navigate(R.id.action_production_to_create_production)
            } catch (e: Exception) {
                Snackbar.make(binding.root, "Erreur de navigation: ${e.message}", Snackbar.LENGTH_LONG).show()
            }
        }
    }

    private fun observeUiState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { uiState ->
                    updateUi(uiState)
                }
            }
        }
    }

    private fun updateUi(uiState: ProductionUiState) {
        binding.apply {
            // Update loading state
            swipeRefreshLayout.isRefreshing = uiState.isRefreshing
            
            // Update production list
            productionAdapter.submitList(uiState.productions)
            
            // Show/hide empty state
            if (uiState.productions.isEmpty() && !uiState.isLoading) {
                textEmptyState.visibility = View.VISIBLE
                recyclerViewProduction.visibility = View.GONE
            } else {
                textEmptyState.visibility = View.GONE
                recyclerViewProduction.visibility = View.VISIBLE
            }
            
            // Show error message
            uiState.errorMessage?.let { message ->
                Snackbar.make(root, message, Snackbar.LENGTH_LONG)
                    .setAction("Réessayer") {
                        viewModel.loadProductions()
                    }
                    .show()
                viewModel.clearError()
            }
        }
    }

    private fun onProductionClick(production: com.betonapp.data.models.OrdreProduction) {
        // Navigate to production detail
        val action = ProductionFragmentDirections.actionProductionToProductionDetail(production.id.toLong())
        findNavController().navigate(action)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}