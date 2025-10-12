package com.betonapp.ui.orders

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.models.Chantier
import com.betonapp.data.models.Client
import com.betonapp.data.models.Commande
import com.betonapp.data.repository.OrdersRepository
import com.betonapp.data.models.FormuleBeton
import com.betonapp.data.repository.FormulasRepository
import com.betonapp.data.repository.ClientsRepository
import com.betonapp.data.repository.ChantiersRepository
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
    private val formulasRepository: FormulasRepository,
    private val clientsRepository: ClientsRepository,
    private val chantiersRepository: ChantiersRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateOrderUiState())
    val uiState: StateFlow<CreateOrderUiState> = _uiState.asStateFlow()

    private val _formulas = MutableStateFlow<List<FormuleBeton>>(emptyList())
    val formulas: StateFlow<List<FormuleBeton>> = _formulas.asStateFlow()

    private val _clients = MutableStateFlow<List<Client>>(emptyList())
    val clients: StateFlow<List<Client>> = _clients.asStateFlow()

    private val _chantiers = MutableStateFlow<List<Chantier>>(emptyList())
    val chantiers: StateFlow<List<Chantier>> = _chantiers.asStateFlow()

    init {
        loadFormulas()
        loadClients()
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

    fun loadClients() {
        viewModelScope.launch {
            try {
                val list = clientsRepository.getClients()
                _clients.value = list
            } catch (e: Exception) {
                _clients.value = emptyList()
                _uiState.value = _uiState.value.copy(errorMessage = "Impossible de charger les clients")
            }
        }
    }

    fun loadChantiersByClient(clientId: Int) {
        viewModelScope.launch {
            try {
                android.util.Log.d("CreateOrderViewModel", "Chargement des chantiers pour le client: $clientId")
                val list = chantiersRepository.getChantiersByClient(clientId)
                android.util.Log.d("CreateOrderViewModel", "Chantiers récupérés: ${list.size} chantiers")
                list.forEach { chantier ->
                    android.util.Log.d("CreateOrderViewModel", "Chantier: ${chantier.nom} - ${chantier.adresse}")
                }
                _chantiers.value = list
            } catch (e: Exception) {
                android.util.Log.e("CreateOrderViewModel", "Erreur lors du chargement des chantiers: ${e.message}", e)
                _chantiers.value = emptyList()
                _uiState.value = _uiState.value.copy(errorMessage = "Impossible de charger les chantiers: ${e.message}")
            }
        }
    }

    fun createOrder(
        numeroCommande: String,
        clientId: Int,
        clientNom: String,
        chantierId: Int?,
        typeBeton: String,
        quantite: Double,
        dateLivraisonPrevue: String,
        prixUnitaire: Double
    ) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

            try {
                // Trouver l'ID de la formule correspondant au type de béton sélectionné
                val selectedFormula = _formulas.value.firstOrNull { it.nom == typeBeton }
                    ?: throw Exception("Formule de béton introuvable : $typeBeton")

                // Nouveau modèle Commande: IDs et champs simplifiés
                val nouvelleCommande = Commande(
                    id = 0, // L'API assignera un ID
                    clientId = clientId,
                    chantierId = chantierId,
                    dateCommande = getCurrentDate(),
                    dateLivraisonSouhaitee = dateLivraisonPrevue,
                    statut = "en_attente",
                    clientNom = clientNom,
                    lignes = listOf(
                        LigneCommande(
                            formuleId = selectedFormula.id,
                            quantite = quantite
                        )
                    )
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