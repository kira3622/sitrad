package com.betonapp.data.api

import com.betonapp.data.local.TokenManager
import com.betonapp.data.models.RefreshTokenRequest
import dagger.Lazy
import kotlinx.coroutines.runBlocking
import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route
import javax.inject.Inject

class AuthAuthenticator @Inject constructor(
    private val tokenManager: TokenManager,
    private val apiService: Lazy<ApiService>
) : Authenticator {

    override fun authenticate(route: Route?, response: Response): Request? {
        // Éviter les boucles d'authentification (ex: plusieurs 401 consécutifs)
        var prior = response.priorResponse
        var count = 1
        while (prior != null) {
            count++
            prior = prior.priorResponse
        }
        if (count >= 2) {
            return null
        }

        // Ne pas tenter de rafraîchir sur les endpoints d'authentification
        val urlPath = response.request.url.encodedPath
        val isAuthEndpoint = urlPath.contains("/auth/token/") || urlPath.contains("/auth/token/refresh/")
        if (isAuthEndpoint) {
            return null
        }

        val refreshToken = runBlocking {
            tokenManager.getRefreshToken()
        } ?: return null

        val newTokens = runBlocking {
            try {
                val tokenResponse = apiService.get().refreshToken(RefreshTokenRequest(refreshToken))
                if (tokenResponse.isSuccessful) {
                    tokenResponse.body()
                } else {
                    null
                }
            } catch (e: Exception) {
                null
            }
        }

        if (newTokens == null) {
            runBlocking {
                tokenManager.clearTokens()
            }
            return null
        }

        runBlocking {
            tokenManager.updateAccessToken(newTokens.access)
        }

        return response.request.newBuilder()
            .header("Authorization", "Bearer ${newTokens.access}")
            .build()
    }
}