package com.betonapp.data.api

import com.betonapp.data.local.TokenManager
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

/**
 * Intercepteur qui ajoute le header Authorization aux requêtes sortantes
 * en utilisant le token d'accès courant.
 */
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val urlPath = original.url.encodedPath

        // Ne pas ajouter de token pour les endpoints d'authentification
        val isAuthEndpoint = urlPath.contains("/auth/token/")
                || urlPath.contains("/auth/token/refresh/")

        if (isAuthEndpoint) {
            return chain.proceed(original)
        }

        val accessToken = tokenManager.getAccessTokenBlocking()
        val requestBuilder = original.newBuilder()

        if (!accessToken.isNullOrBlank()) {
            requestBuilder.header("Authorization", "Bearer $accessToken")
        }

        return chain.proceed(requestBuilder.build())
    }
}