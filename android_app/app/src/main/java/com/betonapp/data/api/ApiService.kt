package com.betonapp.data.api

import com.betonapp.data.models.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Interface pour les appels API REST
 */
interface ApiService {

    // ==================== AUTHENTIFICATION ====================
    
    @POST("auth/token/")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
    
    @POST("auth/token/refresh/")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<RefreshTokenResponse>
    
    @GET("auth/user/")
    suspend fun getCurrentUser(): Response<User>

    // ==================== CLIENTS ====================
    
    @GET("clients/")
    suspend fun getClients(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<Client>>
    
    @GET("clients/{id}/")
    suspend fun getClient(@Path("id") id: Int): Response<Client>
    
    @POST("clients/")
    suspend fun createClient(@Body client: Client): Response<Client>
    
    @PUT("clients/{id}/")
    suspend fun updateClient(@Path("id") id: Int, @Body client: Client): Response<Client>
    
    @DELETE("clients/{id}/")
    suspend fun deleteClient(@Path("id") id: Int): Response<Unit>

    // ==================== CHANTIERS ====================
    
    @GET("chantiers/")
    suspend fun getChantiers(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("client") clientId: Int? = null,
        @Query("statut") statut: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<Chantier>>
    
    @GET("chantiers/{id}/")
    suspend fun getChantier(@Path("id") id: Int): Response<Chantier>
    
    @POST("chantiers/")
    suspend fun createChantier(@Body chantier: Chantier): Response<Chantier>
    
    @PUT("chantiers/{id}/")
    suspend fun updateChantier(@Path("id") id: Int, @Body chantier: Chantier): Response<Chantier>
    
    @DELETE("chantiers/{id}/")
    suspend fun deleteChantier(@Path("id") id: Int): Response<Unit>

    // ==================== COMMANDES ====================
    
    @GET("commandes/")
    suspend fun getCommandes(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("client") clientId: Int? = null,
        @Query("chantier") chantierId: Int? = null,
        @Query("status") status: String? = null,
        @Query("date_commande_after") dateAfter: String? = null,
        @Query("date_commande_before") dateBefore: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<Commande>>
    
    @GET("commandes/{id}/")
    suspend fun getCommande(@Path("id") id: Int): Response<Commande>
    
    @POST("commandes/")
    suspend fun createCommande(@Body commande: Commande): Response<Commande>
    
    @PUT("commandes/{id}/")
    suspend fun updateCommande(@Path("id") id: Int, @Body commande: Commande): Response<Commande>
    
    @DELETE("commandes/{id}/")
    suspend fun deleteCommande(@Path("id") id: Int): Response<Unit>

    // ==================== FORMULES BÉTON ====================
    @GET("formules/")
    suspend fun getFormules(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<FormuleBeton>>

    @GET("formules/{id}/")
    suspend fun getFormule(@Path("id") id: Int): Response<FormuleBeton>

    // ==================== PRODUCTION ====================
    
    @GET("production/")
    suspend fun getOrdresProduction(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("commande") commandeId: Int? = null,
        @Query("statut") statut: String? = null,
        @Query("date_production_after") dateAfter: String? = null,
        @Query("date_production_before") dateBefore: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<OrdreProduction>>
    
    @GET("production/{id}/")
    suspend fun getOrdreProduction(@Path("id") id: Int): Response<OrdreProduction>
    
    @POST("production/")
    suspend fun createOrdreProduction(@Body ordre: OrdreProduction): Response<OrdreProduction>
    
    @PUT("production/{id}/")
    suspend fun updateOrdreProduction(@Path("id") id: Int, @Body ordre: OrdreProduction): Response<OrdreProduction>
    
    @DELETE("production/{id}/")
    suspend fun deleteOrdreProduction(@Path("id") id: Int): Response<Unit>

    // ==================== STOCK ====================
    
    @GET("stock/")
    suspend fun getMatieresPremières(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("statut_stock") statutStock: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<MatierePremiere>>
    
    @GET("stock/{id}/")
    suspend fun getMatierePremiere(@Path("id") id: Int): Response<MatierePremiere>
    
    @POST("stock/")
    suspend fun createMatierePremiere(@Body matiere: MatierePremiere): Response<MatierePremiere>
    
    @PUT("stock/{id}/")
    suspend fun updateMatierePremiere(@Path("id") id: Int, @Body matiere: MatierePremiere): Response<MatierePremiere>
    
    @DELETE("stock/{id}/")
    suspend fun deleteMatierePremiere(@Path("id") id: Int): Response<Unit>

    // ==================== APPROVISIONNEMENTS ====================
    
    @GET("approvisionnements/")
    suspend fun getApprovisionnements(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("matiere_premiere") matiereId: Int? = null,
        @Query("date_after") dateAfter: String? = null,
        @Query("date_before") dateBefore: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<Approvisionnement>>
    
    @GET("approvisionnements/{id}/")
    suspend fun getApprovisionnement(@Path("id") id: Int): Response<Approvisionnement>
    
    @POST("approvisionnements/")
    suspend fun createApprovisionnement(@Body approvisionnement: Approvisionnement): Response<Approvisionnement>
    
    @PUT("approvisionnements/{id}/")
    suspend fun updateApprovisionnement(@Path("id") id: Int, @Body approvisionnement: Approvisionnement): Response<Approvisionnement>
    
    @DELETE("approvisionnements/{id}/")
    suspend fun deleteApprovisionnement(@Path("id") id: Int): Response<Unit>

    // ==================== CARBURANT ====================
    
    @GET("carburant/")
    suspend fun getConsommationsCarburant(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("vehicule") vehicule: String? = null,
        @Query("date_after") dateAfter: String? = null,
        @Query("date_before") dateBefore: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<ConsommationCarburant>>
    
    @GET("carburant/{id}/")
    suspend fun getConsommationCarburant(@Path("id") id: Int): Response<ConsommationCarburant>
    
    @POST("carburant/")
    suspend fun createConsommationCarburant(@Body consommation: ConsommationCarburant): Response<ConsommationCarburant>
    
    @PUT("carburant/{id}/")
    suspend fun updateConsommationCarburant(@Path("id") id: Int, @Body consommation: ConsommationCarburant): Response<ConsommationCarburant>
    
    @DELETE("carburant/{id}/")
    suspend fun deleteConsommationCarburant(@Path("id") id: Int): Response<Unit>

    // ==================== FACTURES ====================
    
    @GET("factures/")
    suspend fun getFactures(
        @Query("page") page: Int? = null,
        @Query("search") search: String? = null,
        @Query("commande") commandeId: Int? = null,
        @Query("statut") statut: String? = null,
        @Query("date_emission_after") dateAfter: String? = null,
        @Query("date_emission_before") dateBefore: String? = null,
        @Query("ordering") ordering: String? = null
    ): Response<PaginatedResponse<Facture>>
    
    @GET("factures/{id}/")
    suspend fun getFacture(@Path("id") id: Int): Response<Facture>
    
    @POST("factures/")
    suspend fun createFacture(@Body facture: Facture): Response<Facture>
    
    @PUT("factures/{id}/")
    suspend fun updateFacture(@Path("id") id: Int, @Body facture: Facture): Response<Facture>
    
    @DELETE("factures/{id}/")
    suspend fun deleteFacture(@Path("id") id: Int): Response<Unit>

    // ==================== DASHBOARD & STATISTIQUES ====================
    
    @GET("dashboard/stats/")
    suspend fun getDashboardStats(): Response<DashboardStats>
    
    @GET("dashboard/production-stats/")
    suspend fun getProductionStats(
        @Query("date_debut") dateDebut: String? = null,
        @Query("date_fin") dateFin: String? = null
    ): Response<ProductionStats>
}