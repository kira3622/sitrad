package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.OrdreProduction
import com.betonapp.data.models.withUtf8Encoding
import com.betonapp.utils.EncodingUtils
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProductionRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    suspend fun getProductionOrders(): List<OrdreProduction> {
        val response = apiService.getOrdresProduction()
        return response.body()?.results ?: emptyList()
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
                EncodingUtils.normalizeFrenchForSearch(production.numeroOrdre).contains(normalizedQuery, ignoreCase = true) ||
                EncodingUtils.normalizeFrenchForSearch(production.commande.numeroCommande).contains(normalizedQuery, ignoreCase = true) ||
                EncodingUtils.normalizeFrenchForSearch(production.operateur).contains(normalizedQuery, ignoreCase = true)
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
}