package com.betonapp.data.api

import android.util.Log
import com.betonapp.data.local.TokenManager
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Intercepteur pour ajouter automatiquement le token JWT aux requêtes
 */
@Singleton
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Ne pas ajouter de token pour les endpoints d'authentification JWT
        if (originalRequest.url.encodedPath.contains("/auth/token/") ||
            originalRequest.url.encodedPath.contains("/auth/token/refresh/")) {
            Log.d("AuthInterceptor", "Requête auth sans en-tête: ${originalRequest.url}")
            return chain.proceed(originalRequest)
        }

        val accessToken = runBlocking { tokenManager.getAccessToken() }
        
        return if (accessToken != null) {
            Log.d("AuthInterceptor", "Token présent, ajout de l'en-tête Authorization")
            val authenticatedRequest = originalRequest.newBuilder()
                .header("Authorization", "Bearer $accessToken")
                .build()
            chain.proceed(authenticatedRequest)
        } else {
            Log.w("AuthInterceptor", "Aucun token d'accès, requête sans Authorization: ${originalRequest.url}")
            chain.proceed(originalRequest)
        }
    }
}