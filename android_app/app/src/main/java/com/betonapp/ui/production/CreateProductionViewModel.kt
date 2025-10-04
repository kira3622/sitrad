package com.betonapp.ui.production

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.models.Commande
import com.betonapp.data.models.OrdreProduction
import com.betonapp.data.models.ProductionStatus
import com.betonapp.data.repository.OrdersRepository
import com.betonapp.data.repository.ProductionRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.Date
import javax.inject.Inject

data class CreateProductionUiState(
    val isLoading: Boolean = false,
    val isProductionCreated: Boolean = false,
    val commandes: List<Commande> = emptyList(),
    val selectedCommande: Commande? = null,
    val errorMessage: String? = null
)

@HiltViewModel
class CreateProductionViewModel @Inject constructor(
    private val productionRepository: ProductionRepository,
    private val ordersRepository: OrdersRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateProductionUiState())
    val uiState: StateFlow<CreateProductionUiState> = _uiState.asStateFlow()

    fun loadCommandes() {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                
                // Charger les commandes disponibles (non encore en production)
                val commandes = ordersRepository.getOrders()
                
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    commandes = commandes
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Erreur lors du chargement des commandes: ${e.message}"
                )
            }
        }
    }

    fun selectCommande(position: Int) {
        val commandes = _uiState.value.commandes
        if (position >= 0 && position < commandes.size) {
            _uiState.value = _uiState.value.copy(
                selectedCommande = commandes[position]
            )
        }
    }

    fun getSelectedCommande(): Commande? {
        return _uiState.value.selectedCommande
    }

    fun createProduction(
        numeroOrdre: String,
        dateProduction: Date,
        quantiteAProduite: Double,
        operateur: String,
        statut: ProductionStatus,
        notes: String
    ) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

                val selectedCommande = _uiState.value.selectedCommande
                if (selectedCommande == null) {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = "Aucune commande sélectionnée"
                    )
                    return@launch
                }

                // Formater la date pour correspondre au modèle
                val dateFormat = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.getDefault())
                val dateProductionStr = dateFormat.format(dateProduction)

                // Créer l'ordre de production
                val ordreProduction = OrdreProduction(
                    id = generateId().toInt(),
                    numeroOrdre = numeroOrdre,
                    commande = selectedCommande,
                    dateProduction = dateProductionStr,
                    quantiteProduite = quantiteAProduite,
                    statut = statut.value,
                    operateur = operateur,
                    notes = notes
                )

                // Sauvegarder via le repository
                productionRepository.createProductionOrder(ordreProduction)

                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    isProductionCreated = true
                )

            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Erreur lors de la création de l'ordre de production: ${e.message}"
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    private fun generateId(): String {
        return System.currentTimeMillis().toString()
    }
}