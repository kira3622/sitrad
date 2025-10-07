package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.Client
import com.betonapp.data.models.PaginatedResponse
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository pour gérer les opérations liées aux clients
 */
@Singleton
class ClientsRepository @Inject constructor(
    private val apiService: ApiService
) {

    /**
     * Récupère la liste de tous les clients
     * @param search Terme de recherche optionnel
     * @param ordering Critère de tri optionnel
     * @return Liste des clients
     */
    suspend fun getClients(
        search: String? = null,
        ordering: String? = "nom"
    ): List<Client> {
        val allClients = mutableListOf<Client>()
        var page = 1
        var hasNextPage = true

        while (hasNextPage) {
            val response = apiService.getClients(
                page = page,
                search = search,
                ordering = ordering
            )

            if (response.isSuccessful) {
                val paginatedResponse = response.body()
                if (paginatedResponse != null) {
                    allClients.addAll(paginatedResponse.results)
                    hasNextPage = paginatedResponse.next != null
                    page++
                } else {
                    hasNextPage = false
                }
            } else {
                throw Exception("Erreur lors de la récupération des clients: ${response.message()}")
            }
        }

        return allClients
    }

    /**
     * Récupère un client par son ID
     * @param id ID du client
     * @return Client trouvé
     */
    suspend fun getClient(id: Int): Client {
        val response = apiService.getClient(id)
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Client non trouvé")
        } else {
            throw Exception("Erreur lors de la récupération du client: ${response.message()}")
        }
    }

    /**
     * Crée un nouveau client
     * @param client Client à créer
     * @return Client créé avec son ID
     */
    suspend fun createClient(client: Client): Client {
        val response = apiService.createClient(client)
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Erreur lors de la création du client")
        } else {
            throw Exception("Erreur lors de la création du client: ${response.message()}")
        }
    }

    /**
     * Met à jour un client existant
     * @param id ID du client à mettre à jour
     * @param client Données du client mises à jour
     * @return Client mis à jour
     */
    suspend fun updateClient(id: Int, client: Client): Client {
        val response = apiService.updateClient(id, client)
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Erreur lors de la mise à jour du client")
        } else {
            throw Exception("Erreur lors de la mise à jour du client: ${response.message()}")
        }
    }

    /**
     * Supprime un client
     * @param id ID du client à supprimer
     */
    suspend fun deleteClient(id: Int) {
        val response = apiService.deleteClient(id)
        if (!response.isSuccessful) {
            throw Exception("Erreur lors de la suppression du client: ${response.message()}")
        }
    }
}