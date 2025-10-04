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

data class ProductionDetailUiState(
    val production: OrdreProduction? = null,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class ProductionDetailViewModel @Inject constructor(
    private val productionRepository: ProductionRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProductionDetailUiState())
    val uiState: StateFlow<ProductionDetailUiState> = _uiState.asStateFlow()

    fun loadProduction(productionId: Long) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val production = productionRepository.getProductionById(productionId)
                _uiState.value = _uiState.value.copy(production = production, isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(errorMessage = e.message, isLoading = false)
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }
}