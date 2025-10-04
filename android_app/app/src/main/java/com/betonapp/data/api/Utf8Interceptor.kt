package com.betonapp.data.api

import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Intercepteur pour configurer l'encodage UTF-8 pour toutes les requêtes
 */
@Singleton
class Utf8Interceptor @Inject constructor() : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Ajouter les headers UTF-8 pour toutes les requêtes
        val requestBuilder = originalRequest.newBuilder()
            .addHeader("Accept-Charset", "UTF-8")
            .addHeader("Content-Type", "application/json; charset=UTF-8")
        
        // Si la requête a un body, s'assurer qu'il utilise UTF-8
        originalRequest.body?.let { body ->
            val contentType = body.contentType()
            if (contentType != null && contentType.type == "application" && contentType.subtype == "json") {
                // Forcer l'encodage UTF-8 pour les requêtes JSON
                val utf8ContentType = "application/json; charset=UTF-8".toMediaType()
                requestBuilder.method(originalRequest.method, body)
                requestBuilder.header("Content-Type", utf8ContentType.toString())
            }
        }
        
        val request = requestBuilder.build()
        return chain.proceed(request)
    }
}