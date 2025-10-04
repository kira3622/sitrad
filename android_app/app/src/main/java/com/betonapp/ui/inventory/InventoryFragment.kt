package com.betonapp.ui.inventory

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
import com.betonapp.databinding.FragmentInventoryBinding
import com.betonapp.data.models.MatierePremiere
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class InventoryFragment : Fragment() {

    private var _binding: FragmentInventoryBinding? = null
    private val binding get() = _binding!!

    private val viewModel: InventoryViewModel by viewModels()
    private lateinit var inventoryAdapter: InventoryAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentInventoryBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupRecyclerView()
        setupSwipeRefresh()
        setupFab()
        observeUiState()
    }

    private fun setupRecyclerView() {
        inventoryAdapter = InventoryAdapter { item ->
            onInventoryItemClick(item)
        }
        
        binding.recyclerViewInventory.apply {
            adapter = inventoryAdapter
            layoutManager = LinearLayoutManager(requireContext())
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefreshLayout.setOnRefreshListener {
            viewModel.refreshInventory()
        }
    }

    private fun setupFab() {
        binding.fabAddInventory.setOnClickListener {
            try {
                findNavController().navigate(R.id.action_inventory_to_add_inventory)
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

    private fun updateUi(uiState: InventoryUiState) {
        binding.apply {
            // Update loading state
            swipeRefreshLayout.isRefreshing = uiState.isRefreshing
            
            // Update inventory list
            inventoryAdapter.submitList(uiState.materials)
            
            // Show/hide empty state
            if (uiState.materials.isEmpty() && !uiState.isLoading) {
                textEmptyState.visibility = View.VISIBLE
                recyclerViewInventory.visibility = View.GONE
            } else {
                textEmptyState.visibility = View.GONE
                recyclerViewInventory.visibility = View.VISIBLE
            }
            
            // Show error message
            uiState.errorMessage?.let { message ->
                Snackbar.make(root, message, Snackbar.LENGTH_LONG)
                    .setAction("Réessayer") {
                        viewModel.loadInventory()
                    }
                    .show()
                viewModel.clearError()
            }
        }
    }

    private fun onInventoryItemClick(item: MatierePremiere) {
        // Navigate to inventory item detail
        val action = InventoryFragmentDirections.actionInventoryFragmentToInventoryDetailFragment(item.id.toLong())
        findNavController().navigate(action)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}