package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.OrdreProduction
import com.betonapp.data.models.withUtf8Encoding
import com.betonapp.utils.EncodingUtils
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProductionRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    suspend fun getProductionOrders(): List<OrdreProduction> {
        val response = apiService.getOrdresProduction()
        if (response.isSuccessful) {
            return response.body()?.results ?: emptyList()
        } else {
            throw Exception("Erreur ${response.code()}: ${response.message()}")
        }
    }
    
    suspend fun getProductionOrderById(id: Int): OrdreProduction {
        val response = apiService.getOrdreProduction(id)
        return response.body() ?: throw Exception("Ordre de production non trouvé")
    }
    
    suspend fun createProductionOrder(order: OrdreProduction): OrdreProduction {
        val encodedOrder = order.withUtf8Encoding()
        val response = apiService.createOrdreProduction(encodedOrder)
        return response.body() ?: throw Exception("Erreur lors de la création")
    }
    
    suspend fun updateProductionOrder(id: Int, order: OrdreProduction): OrdreProduction {
        val encodedOrder = order.withUtf8Encoding()
        val response = apiService.updateOrdreProduction(id, encodedOrder)
        return response.body() ?: throw Exception("Erreur lors de la mise à jour")
    }
    
    suspend fun deleteProductionOrder(id: Int) {
        apiService.deleteOrdreProduction(id)
    }
    
    suspend fun searchProductions(query: String): List<OrdreProduction> {
        return try {
            val response = apiService.getOrdresProduction()
            val productions = response.body()?.results ?: emptyList()
            val normalizedQuery = EncodingUtils.normalizeFrenchForSearch(query)
            productions.filter { production ->
                EncodingUtils.normalizeFrenchForSearch(production.numeroBon ?: "").contains(normalizedQuery, ignoreCase = true) ||
                production.commandeId.toString().contains(normalizedQuery, ignoreCase = true) ||
                EncodingUtils.normalizeFrenchForSearch(production.statut).contains(normalizedQuery, ignoreCase = true)
            }
        } catch (e: Exception) {
            throw Exception("Erreur lors de la recherche de productions: ${e.message}")
        }
    }
    
    suspend fun getProductionsByStatus(status: String): List<OrdreProduction> {
        return try {
            val response = apiService.getOrdresProduction()
            val productions = response.body()?.results ?: emptyList()
            productions.filter { production -> production.statut == status }
        } catch (e: Exception) {
            throw Exception("Erreur lors du filtrage par statut: ${e.message}")
        }
    }
    
    suspend fun getProductionsByDateRange(startDate: String, endDate: String): List<OrdreProduction> {
        return try {
            val response = apiService.getOrdresProduction()
            val productions = response.body()?.results ?: emptyList()
            productions.filter { production ->
                production.dateProduction >= startDate && production.dateProduction <= endDate
            }
        } catch (e: Exception) {
            throw Exception("Erreur lors du filtrage par date: ${e.message}")
        }
    }
    
    // Ajout des méthodes manquantes
    suspend fun getAllProductions(): List<OrdreProduction> {
        return getProductionOrders()
    }
    
    suspend fun getProductionById(id: Long): OrdreProduction {
        return getProductionOrderById(id.toInt())
    }

    /**
     * Récupère les productions avec des mises à jour récentes pour les notifications
     */
    suspend fun getRecentProductionUpdates(): List<OrdreProduction> {
        return try {
            val calendar = Calendar.getInstance()
            calendar.add(Calendar.HOUR_OF_DAY, -2) // Dernières 2 heures
            val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
            val recentTime = dateFormat.format(calendar.time)
            
            val response = apiService.getOrdresProduction()
            val productions = response.body()?.results ?: emptyList()
            
            // Filtrer les productions modifiées récemment
            // Note: Vous devrez peut-être ajuster cette logique selon votre API
            productions.filter { production ->
                // Supposons qu'il y a un champ dateModification ou similaire
                production.dateProduction >= recentTime.substring(0, 10) // Date seulement
            }
        } catch (e: Exception) {
            emptyList()
        }
    }
}