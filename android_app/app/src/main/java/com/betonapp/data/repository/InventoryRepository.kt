package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.MatierePremiere
import com.betonapp.data.models.withUtf8Encoding
import com.betonapp.utils.EncodingUtils
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class InventoryRepository @Inject constructor(
    private val apiService: ApiService
) {

    suspend fun getAllMaterials(): List<MatierePremiere> {
        return try {
            val response = apiService.getMatieresPremières()
            if (response.isSuccessful) {
                response.body()?.results ?: emptyList()
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun getMaterialById(id: Int): MatierePremiere {
        return try {
            val response = apiService.getMatierePremiere(id)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Matière première non trouvée")
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun createMaterial(material: MatierePremiere): MatierePremiere {
        return try {
            val encodedMaterial = material.withUtf8Encoding()
            val response = apiService.createMatierePremiere(encodedMaterial)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Erreur lors de la création")
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun updateMaterial(id: Int, material: MatierePremiere): MatierePremiere {
        return try {
            val encodedMaterial = material.withUtf8Encoding()
            val response = apiService.updateMatierePremiere(id, encodedMaterial)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Erreur lors de la mise à jour")
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun deleteMaterial(id: Int) {
        try {
            val response = apiService.deleteMatierePremiere(id)
            if (!response.isSuccessful) {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun searchMaterials(query: String): List<MatierePremiere> {
        return try {
            val encodedQuery = EncodingUtils.encodeForApi(query)
            val response = apiService.getMatieresPremières(search = encodedQuery)
            if (response.isSuccessful) {
                response.body()?.results ?: emptyList()
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun filterByStatus(status: String): List<MatierePremiere> {
        return try {
            val response = apiService.getMatieresPremières(statutStock = status)
            if (response.isSuccessful) {
                response.body()?.results ?: emptyList()
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    /**
     * Récupère les matières premières avec stock faible pour les notifications
     */
    suspend fun getLowStockItems(): List<MatierePremiere> {
        return try {
            val response = apiService.getMatieresPremières()
            if (response.isSuccessful) {
                val materials = response.body()?.results ?: emptyList()
                // Filtrer les matières avec stock inférieur au seuil minimum
                materials.filter { material ->
                    val currentStock = material.stockActuel ?: 0.0
                    val minThreshold = material.stockMinimum ?: 0.0
                    currentStock <= minThreshold && minThreshold > 0
                }
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            emptyList()
        }
    }
}