package com.betonapp.ui.orders

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.data.models.Chantier
import com.betonapp.data.models.Client
import com.betonapp.data.models.Commande
import com.betonapp.data.repository.OrdersRepository
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
    private val ordersRepository: OrdersRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateOrderUiState())
    val uiState: StateFlow<CreateOrderUiState> = _uiState.asStateFlow()

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
                // Création d'un client temporaire (dans une vraie app, on sélectionnerait depuis une liste)
                val clientObj = Client(
                    id = 0, // L'API assignera un ID
                    nom = client,
                    email = "",
                    telephone = "",
                    adresse = "",
                    dateCreation = getCurrentDate()
                )

                // Création d'un chantier temporaire si spécifié
                val chantierObj = chantier?.let {
                    Chantier(
                        id = 0,
                        nom = it,
                        adresse = "",
                        client = clientObj,
                        dateDebut = getCurrentDate(),
                        dateFinPrevue = dateLivraisonPrevue,
                        statut = "actif"
                    )
                }

                val prixTotal = quantite * prixUnitaire

                val nouvelleCommande = Commande(
                    id = 0, // L'API assignera un ID
                    numeroCommande = numeroCommande,
                    client = clientObj,
                    chantier = chantierObj,
                    typeBeton = typeBeton,
                    quantite = quantite,
                    dateCommande = getCurrentDate(),
                    dateLivraisonPrevue = dateLivraisonPrevue,
                    statut = "en_attente",
                    prixUnitaire = prixUnitaire,
                    prixTotal = prixTotal
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