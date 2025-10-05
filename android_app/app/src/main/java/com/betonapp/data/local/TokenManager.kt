package com.betonapp.data.local

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Gestionnaire des tokens JWT avec DataStore
 */
@Singleton
class TokenManager @Inject constructor(
    private val dataStore: DataStore<Preferences>
) {
    companion object {
        private val ACCESS_TOKEN_KEY = stringPreferencesKey("access_token")
        private val REFRESH_TOKEN_KEY = stringPreferencesKey("refresh_token")
    }

    /**
     * Sauvegarde les tokens d'authentification
     */
    suspend fun saveTokens(accessToken: String, refreshToken: String) {
        dataStore.edit { preferences ->
            preferences[ACCESS_TOKEN_KEY] = accessToken
            preferences[REFRESH_TOKEN_KEY] = refreshToken
        }
    }

    /**
     * Récupère le token d'accès
     */
    suspend fun getAccessToken(): String? {
        return dataStore.data.first()[ACCESS_TOKEN_KEY]
    }

    /**
     * Récupère le token de rafraîchissement
     */
    suspend fun getRefreshToken(): String? {
        return dataStore.data.first()[REFRESH_TOKEN_KEY]
    }

    /**
     * Flow pour observer le token d'accès
     */
    fun getAccessTokenFlow(): Flow<String?> {
        return dataStore.data.map { preferences ->
            preferences[ACCESS_TOKEN_KEY]
        }
    }

    /**
     * Récupère le token d'accès de manière synchrone.
     * À n'utiliser que dans des contextes où la coroutine n'est pas disponible (ex: Interceptor).
     */
    fun getAccessTokenBlocking(): String? {
        return runBlocking {
            dataStore.data.first()[ACCESS_TOKEN_KEY]
        }
    }

    /**
     * Vérifie si l'utilisateur est connecté
     */
    suspend fun isLoggedIn(): Boolean {
        return getAccessToken() != null
    }

    /**
     * Supprime tous les tokens (déconnexion)
     */
    suspend fun clearTokens() {
        dataStore.edit { preferences ->
            preferences.remove(ACCESS_TOKEN_KEY)
            preferences.remove(REFRESH_TOKEN_KEY)
        }
    }

    /**
     * Met à jour uniquement le token d'accès (après rafraîchissement)
     */
    suspend fun updateAccessToken(accessToken: String) {
        dataStore.edit { preferences ->
            preferences[ACCESS_TOKEN_KEY] = accessToken
        }
    }
}