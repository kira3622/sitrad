package com.betonapp.ui.inventory

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.models.MatierePremiere
import com.betonapp.data.repository.InventoryRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class InventoryUiState(
    val materials: List<MatierePremiere> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val errorMessage: String? = null,
    val isEmpty: Boolean = false
)

@HiltViewModel
class InventoryViewModel @Inject constructor(
    private val inventoryRepository: InventoryRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(InventoryUiState())
    val uiState: StateFlow<InventoryUiState> = _uiState.asStateFlow()

    init {
        loadInventory()
    }

    fun loadInventory() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            
            try {
                val materials = inventoryRepository.getAllMaterials()
                _uiState.value = _uiState.value.copy(
                    materials = materials,
                    isLoading = false,
                    isEmpty = materials.isEmpty()
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Erreur lors du chargement de l'inventaire: ${e.message}"
                )
            }
        }
    }

    fun refreshInventory() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true, errorMessage = null)
            
            try {
                val materials = inventoryRepository.getAllMaterials()
                _uiState.value = _uiState.value.copy(
                    materials = materials,
                    isRefreshing = false,
                    isEmpty = materials.isEmpty()
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isRefreshing = false,
                    errorMessage = "Erreur lors du rafraîchissement: ${e.message}"
                )
            }
        }
    }

    fun searchMaterials(query: String) {
        if (query.isBlank()) {
            loadInventory()
            return
        }

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            
            try {
                val materials = inventoryRepository.searchMaterials(query)
                _uiState.value = _uiState.value.copy(
                    materials = materials,
                    isLoading = false,
                    isEmpty = materials.isEmpty()
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Erreur lors de la recherche: ${e.message}"
                )
            }
        }
    }

    fun filterByStatus(status: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            
            try {
                val materials = inventoryRepository.filterByStatus(status)
                _uiState.value = _uiState.value.copy(
                    materials = materials,
                    isLoading = false,
                    isEmpty = materials.isEmpty()
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = "Erreur lors du filtrage: ${e.message}"
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }
}