package com.betonapp.ui.notifications

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.betonapp.databinding.FragmentNotificationsBinding
import com.betonapp.utils.BetonNotificationManager
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Fragment pour afficher et gérer les notifications
 */
@AndroidEntryPoint
class NotificationsFragment : Fragment() {

    private var _binding: FragmentNotificationsBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: NotificationsViewModel by viewModels()
    private lateinit var notificationsAdapter: NotificationsAdapter
    private lateinit var notificationManager: BetonNotificationManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentNotificationsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        notificationManager = BetonNotificationManager(requireContext())
        setupRecyclerView()
        setupSwipeRefresh()
        setupTestButton()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        notificationsAdapter = NotificationsAdapter { notification ->
            // Gérer le clic sur une notification
            viewModel.markAsRead(notification.id)
            
            // Naviguer vers l'écran approprié selon le type de notification
            when (notification.type) {
                NotificationType.NEW_ORDER -> {
                    // Naviguer vers les détails de la commande
                    // findNavController().navigate(...)
                }
                NotificationType.PRODUCTION_UPDATE -> {
                    // Naviguer vers les détails de production
                    // findNavController().navigate(...)
                }
                NotificationType.LOW_INVENTORY -> {
                    // Naviguer vers l'inventaire
                    // findNavController().navigate(...)
                }
                NotificationType.DELIVERY -> {
                    // Naviguer vers les détails de livraison
                    // findNavController().navigate(...)
                }
                else -> {
                    // Notification générale
                }
            }
        }
        
        binding.recyclerViewNotifications.apply {
            layoutManager = LinearLayoutManager(requireContext())
            adapter = notificationsAdapter
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefreshLayout.setOnRefreshListener {
            // Les notifications se rechargent automatiquement via le Flow
            // On peut ajouter des notifications de test pour le développement
            viewModel.addTestNotifications()
            binding.swipeRefreshLayout.isRefreshing = false
        }
    }

    private fun setupTestButton() {
        // Ajouter un bouton de test pour les notifications (pour le développement)
        binding.fabAddTestNotification?.setOnClickListener {
            viewModel.addTestNotifications()
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                binding.swipeRefreshLayout.isRefreshing = state.isLoading
                
                if (state.notifications.isNotEmpty()) {
                    binding.recyclerViewNotifications.visibility = View.VISIBLE
                    binding.textViewEmptyState.visibility = View.GONE
                    notificationsAdapter.submitList(state.notifications)
                } else {
                    binding.recyclerViewNotifications.visibility = View.GONE
                    binding.textViewEmptyState.visibility = View.VISIBLE
                }
                
                state.error?.let { error ->
                    // Afficher l'erreur
                    // Snackbar.make(binding.root, error, Snackbar.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}