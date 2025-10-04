package com.betonapp.ui.inventory

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.models.MatierePremiere
import com.betonapp.data.models.StockStatus
import com.betonapp.data.repository.InventoryRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.Date
import javax.inject.Inject

data class AddInventoryUiState(
    val isLoading: Boolean = false,
    val isItemAdded: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class AddInventoryViewModel @Inject constructor(
    private val inventoryRepository: InventoryRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AddInventoryUiState())
    val uiState: StateFlow<AddInventoryUiState> = _uiState.asStateFlow()

    fun addInventoryItem(
        nom: String,
        unite: String,
        stockActuel: Double,
        stockMinimum: Double,
        prixUnitaire: Double,
        fournisseur: String
    ) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

                // Calculer le statut du stock
                val status = when {
                    stockActuel <= 0 -> StockStatus.CRITIQUE
                    stockActuel <= stockMinimum -> StockStatus.FAIBLE
                    stockActuel <= stockMinimum * 1.5 -> StockStatus.FAIBLE
                    else -> StockStatus.NORMAL
                }

                // Créer l'objet MatierePremiere
                val matierePremiere = MatierePremiere(
                    id = generateId().toInt(),
                    nom = nom,
                    unite = unite,
                    stockActuel = stockActuel,
                    stockMinimum = stockMinimum,
                    statutStock = status.value,
                    prixUnitaire = prixUnitaire
                )

                // Ajouter via le repository
                inventoryRepository.createMaterial(matierePremiere)

                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    isItemAdded = true
                )

            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Erreur lors de l'ajout de la matière première: ${e.message}"
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