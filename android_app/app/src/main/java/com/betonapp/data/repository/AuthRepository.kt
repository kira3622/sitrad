package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.local.TokenManager
import com.betonapp.data.models.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository pour la gestion de l'authentification
 */
@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) {

    /**
     * Connexion utilisateur
     */
    suspend fun login(username: String, password: String): Flow<Result<LoginResponse>> = flow {
        try {
            val response = apiService.login(LoginRequest(username, password))
            if (response.isSuccessful) {
                response.body()?.let { loginResponse ->
                    // Sauvegarder les tokens
                    tokenManager.saveTokens(loginResponse.access, loginResponse.refresh)
                    emit(Result.success(loginResponse))
                } ?: emit(Result.failure(Exception("Réponse vide du serveur")))
            } else {
                emit(Result.failure(Exception("Identifiants incorrects")))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    /**
     * Rafraîchissement du token
     */
    suspend fun refreshToken(): Flow<Result<String>> = flow {
        try {
            val refreshToken = tokenManager.getRefreshToken()
            if (refreshToken != null) {
                val response = apiService.refreshToken(RefreshTokenRequest(refreshToken))
                if (response.isSuccessful) {
                    response.body()?.let { refreshResponse ->
                        tokenManager.updateAccessToken(refreshResponse.access)
                        emit(Result.success(refreshResponse.access))
                    } ?: emit(Result.failure(Exception("Impossible de rafraîchir le token")))
                } else {
                    // Token de rafraîchissement expiré, déconnexion nécessaire
                    tokenManager.clearTokens()
                    emit(Result.failure(Exception("Session expirée")))
                }
            } else {
                emit(Result.failure(Exception("Aucun token de rafraîchissement")))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    /**
     * Récupération des informations utilisateur
     */
    suspend fun getCurrentUser(): Flow<Result<User>> = flow {
        try {
            val response = apiService.getCurrentUser()
            if (response.isSuccessful) {
                response.body()?.let { user ->
                    emit(Result.success(user))
                } ?: emit(Result.failure(Exception("Impossible de récupérer les informations utilisateur")))
            } else {
                emit(Result.failure(Exception("Erreur lors de la récupération des informations utilisateur")))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    /**
     * Déconnexion
     */
    suspend fun logout() {
        tokenManager.clearTokens()
    }

    /**
     * Vérification de l'état de connexion
     */
    suspend fun isLoggedIn(): Boolean {
        return tokenManager.isLoggedIn()
    }

    /**
     * Observer l'état de connexion
     */
    fun getAuthStateFlow(): Flow<Boolean> {
        return tokenManager.getAccessTokenFlow().let { tokenFlow ->
            flow {
                tokenFlow.collect { token ->
                    emit(token != null)
                }
            }
        }
    }
}