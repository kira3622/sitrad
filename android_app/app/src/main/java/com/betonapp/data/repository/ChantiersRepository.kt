package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.Chantier
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ChantiersRepository @Inject constructor(
    private val apiService: ApiService
) {

    suspend fun getChantiersByClient(clientId: Int): List<Chantier> {
        return try {
            android.util.Log.d("ChantiersRepository", "Appel API getChantiers pour client: $clientId")
            val response = apiService.getChantiers(clientId = clientId)
            android.util.Log.d("ChantiersRepository", "Réponse API: code=${response.code()}, isSuccessful=${response.isSuccessful}")
            if (response.isSuccessful) {
                val results = response.body()?.results ?: emptyList()
                android.util.Log.d("ChantiersRepository", "Nombre de chantiers reçus: ${results.size}")
                results
            } else {
                android.util.Log.e("ChantiersRepository", "Erreur API: ${response.code()} - ${response.message()}")
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            android.util.Log.e("ChantiersRepository", "Exception lors de l'appel API: ${e.message}", e)
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun getAllChantiers(): List<Chantier> {
        return try {
            val response = apiService.getChantiers()
            if (response.isSuccessful) {
                response.body()?.results ?: emptyList()
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }

    suspend fun getChantierById(id: Int): Chantier {
        return try {
            val response = apiService.getChantier(id)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Chantier non trouvé")
            } else {
                throw Exception("Erreur ${response.code()}: ${response.message()}")
            }
        } catch (e: Exception) {
            throw Exception("Erreur de réseau: ${e.message}")
        }
    }
}