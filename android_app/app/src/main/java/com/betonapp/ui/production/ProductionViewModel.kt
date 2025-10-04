package com.betonapp.ui.production

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.models.OrdreProduction
import com.betonapp.data.repository.ProductionRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ProductionUiState(
    val productions: List<OrdreProduction> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val errorMessage: String? = null,
    val isEmpty: Boolean = false
)

@HiltViewModel
class ProductionViewModel @Inject constructor(
    private val productionRepository: ProductionRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProductionUiState())
    val uiState: StateFlow<ProductionUiState> = _uiState.asStateFlow()

    init {
        loadProductions()
    }

    fun loadProductions() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val productions = productionRepository.getAllProductions()
                _uiState.value = _uiState.value.copy(productions = productions, isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(errorMessage = e.message, isLoading = false)
            }
        }
    }

    fun refreshProductions() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true)
            try {
                val productions = productionRepository.getAllProductions()
                _uiState.value = _uiState.value.copy(productions = productions, isRefreshing = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(errorMessage = e.message, isRefreshing = false)
            }
        }
    }

    fun searchProductions(query: String) {
        if (query.isBlank()) {
            loadProductions()
            return
        }

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            
            try {
                val productions = productionRepository.searchProductions(query)
                _uiState.value = _uiState.value.copy(
                    productions = productions,
                    isLoading = false,
                    isEmpty = productions.isEmpty()
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
                val productions = productionRepository.getProductionsByStatus(status)
                _uiState.value = _uiState.value.copy(
                    productions = productions,
                    isLoading = false,
                    isEmpty = productions.isEmpty()
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