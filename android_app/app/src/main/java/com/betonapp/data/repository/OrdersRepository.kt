package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.Commande
import com.betonapp.data.models.withUtf8Encoding
import com.betonapp.utils.EncodingUtils
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OrdersRepository @Inject constructor(
    private val apiService: ApiService
) {

    suspend fun getOrders(): List<Commande> {
        val response = apiService.getCommandes()
        return if (response.isSuccessful) {
            response.body()?.results ?: emptyList()
        } else {
            throw Exception("Erreur lors du chargement des commandes")
        }
    }

    suspend fun getOrderById(orderId: Int): Commande {
        val response = apiService.getCommande(orderId)
        return if (response.isSuccessful) {
            response.body() ?: throw Exception("Commande non trouvée")
        } else {
            throw Exception("Erreur lors du chargement de la commande")
        }
    }

    suspend fun createOrder(order: Commande): Commande {
        val encodedOrder = order.withUtf8Encoding()
        val response = apiService.createCommande(encodedOrder)
        return if (response.isSuccessful) {
            response.body() ?: throw Exception("Erreur lors de la création")
        } else {
            val code = response.code()
            val errorBody = try {
                response.errorBody()?.string()
            } catch (e: Exception) {
                null
            }
            android.util.Log.e(
                "OrdersRepository",
                "Création de commande échouée (HTTP $code). Payload=${encodedOrder} Erreur=${errorBody}"
            )
            throw Exception("Création de commande échouée (HTTP $code): ${errorBody ?: "aucun détail"}")
        }
    }

    suspend fun updateOrder(orderId: Int, order: Commande): Commande {
        val encodedOrder = order.withUtf8Encoding()
        val response = apiService.updateCommande(orderId, encodedOrder)
        return if (response.isSuccessful) {
            response.body() ?: throw Exception("Erreur lors de la mise à jour")
        } else {
            throw Exception("Erreur lors de la mise à jour de la commande")
        }
    }

    suspend fun deleteOrder(orderId: Int) {
        val response = apiService.deleteCommande(orderId)
        if (!response.isSuccessful) {
            throw Exception("Erreur lors de la suppression de la commande")
        }
    }

    suspend fun searchOrders(query: String): List<Commande> {
        val encodedQuery = EncodingUtils.encodeForApi(query)
        val response = apiService.getCommandes(search = encodedQuery)
        return if (response.isSuccessful) {
            response.body()?.results ?: emptyList()
        } else {
            throw Exception("Erreur lors de la recherche")
        }
    }

    suspend fun getOrdersByStatus(status: String): List<Commande> {
        val response = apiService.getCommandes(status = status)
        return if (response.isSuccessful) {
            response.body()?.results ?: emptyList()
        } else {
            throw Exception("Erreur lors du filtrage par statut")
        }
    }

    suspend fun getOrdersByCustomer(customerId: Int): List<Commande> {
        val response = apiService.getCommandes(clientId = customerId)
        return if (response.isSuccessful) {
            response.body()?.results ?: emptyList()
        } else {
            throw Exception("Erreur lors du filtrage par client")
        }
    }

    suspend fun getOrdersByDateRange(startDate: String, endDate: String): List<Commande> {
        val response = apiService.getCommandes(dateAfter = startDate, dateBefore = endDate)
        return if (response.isSuccessful) {
            response.body()?.results ?: emptyList()
        } else {
            throw Exception("Erreur lors du filtrage par date")
        }
    }

    /**
     * Récupère les commandes récentes (dernières 24h) pour les notifications
     */
    suspend fun getRecentOrders(): List<Commande> {
        val calendar = Calendar.getInstance()
        calendar.add(Calendar.DAY_OF_YEAR, -1) // Dernières 24h
        val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        val yesterday = dateFormat.format(calendar.time)
        
        return getOrdersByDateRange(yesterday, dateFormat.format(Date()))
    }

    /**
     * Récupère les livraisons prévues pour aujourd'hui
     */
    suspend fun getTodayDeliveries(): List<Commande> {
        val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        val today = dateFormat.format(Date())
        
        val response = apiService.getCommandes()
        return if (response.isSuccessful) {
            response.body()?.results?.filter { 
                it.dateLivraisonPrevue?.startsWith(today) == true 
            } ?: emptyList()
        } else {
            emptyList()
        }
    }
}