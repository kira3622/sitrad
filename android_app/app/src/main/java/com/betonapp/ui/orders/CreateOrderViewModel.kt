package com.betonapp.ui.orders

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.models.Chantier
import com.betonapp.data.models.Client
import com.betonapp.data.models.Commande
import com.betonapp.data.repository.OrdersRepository
import com.betonapp.data.models.FormuleBeton
import com.betonapp.data.repository.FormulasRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

data class CreateOrderUiState(
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val isOrderCreated: Boolean = false
)

@HiltViewModel
class CreateOrderViewModel @Inject constructor(
    private val ordersRepository: OrdersRepository,
    private val formulasRepository: FormulasRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateOrderUiState())
    val uiState: StateFlow<CreateOrderUiState> = _uiState.asStateFlow()

    private val _formulas = MutableStateFlow<List<FormuleBeton>>(emptyList())
    val formulas: StateFlow<List<FormuleBeton>> = _formulas.asStateFlow()

    init {
        loadFormulas()
    }

    fun loadFormulas() {
        viewModelScope.launch {
            try {
                val list = formulasRepository.getFormulas()
                _formulas.value = list
            } catch (e: Exception) {
                _formulas.value = emptyList()
                _uiState.value = _uiState.value.copy(errorMessage = "Impossible de charger les formules")
            }
        }
    }

    fun createOrder(
        numeroCommande: String,
        client: String,
        chantier: String?,
        typeBeton: String,
        quantite: Double,
        dateLivraisonPrevue: String,
        prixUnitaire: Double
    ) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

            try {
                // Nouveau modèle Commande: IDs et champs simplifiés
                val nouvelleCommande = Commande(
                    id = 0, // L'API assignera un ID
                    clientId = 0, // À remplacer par une sélection réelle
                    chantierId = null,
                    dateCommande = getCurrentDate(),
                    dateLivraisonSouhaitee = dateLivraisonPrevue,
                    statut = "en_attente",
                    clientNom = client
                )

                ordersRepository.createOrder(nouvelleCommande)

                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    isOrderCreated = true
                )

            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = e.message ?: "Erreur lors de la création de la commande"
                )
            }
        }
    }

    private fun getCurrentDate(): String {
        val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        return dateFormat.format(Date())
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }
}