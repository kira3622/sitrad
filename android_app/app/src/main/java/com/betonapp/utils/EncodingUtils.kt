package com.betonapp.utils

import java.nio.charset.StandardCharsets

/**
 * Utilitaires pour la gestion de l'encodage UTF-8
 */
object EncodingUtils {

    /**
     * Convertit une chaîne en UTF-8 si nécessaire
     */
    fun ensureUtf8(input: String?): String? {
        if (input == null) return null
        
        return try {
            // Vérifier si la chaîne est déjà en UTF-8 valide
            val bytes = input.toByteArray(StandardCharsets.UTF_8)
            String(bytes, StandardCharsets.UTF_8)
        } catch (e: Exception) {
            // En cas d'erreur, retourner la chaîne originale
            input
        }
    }

    /**
     * Nettoie et normalise une chaîne pour l'UTF-8
     */
    fun cleanForUtf8(input: String?): String? {
        if (input == null) return null
        
        return input
            .trim()
            .replace("\u0000", "") // Supprimer les caractères null
            .replace("\u0001", "") // Supprimer les caractères de contrôle
            .replace("\u0002", "") // Supprimer les caractères de contrôle
            .replace("\\u0000", "") // Supprimer les séquences d'échappement null
    }

    /**
     * Valide qu'une chaîne est en UTF-8 valide
     */
    fun isValidUtf8(input: String?): Boolean {
        if (input == null) return true
        
        return try {
            // Vérifier qu'il n'y a pas de caractères de contrôle invalides
            if (input.contains('\u0000') || input.contains('\u0001') || input.contains('\u0002')) {
                return false
            }
            
            val bytes = input.toByteArray(StandardCharsets.UTF_8)
            val decoded = String(bytes, StandardCharsets.UTF_8)
            decoded == input
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Encode une chaîne pour l'envoi via API
     */
    fun encodeForApi(input: String?): String? {
        return input?.let { cleanForUtf8(ensureUtf8(it)) }
    }

    /**
     * Décode une chaîne reçue de l'API
     */
    fun decodeFromApi(input: String?): String? {
        return input?.let { ensureUtf8(it) }
    }

    /**
     * Vérifie si une chaîne contient des caractères spéciaux français
     */
    fun containsFrenchCharacters(input: String?): Boolean {
        if (input == null) return false
        
        val frenchChars = "àáâäèéêëìíîïòóôöùúûüÿçñÀÁÂÄÈÉÊËÌÍÎÏÒÓÔÖÙÚÛÜŸÇÑ"
        return input.any { it in frenchChars }
    }

    /**
     * Normalise les caractères français pour la recherche
     */
    fun normalizeFrenchForSearch(input: String?): String {
        if (input == null) return ""
        
        return input
            .lowercase()
            .replace("à|á|â|ä".toRegex(), "a")
            .replace("è|é|ê|ë".toRegex(), "e")
            .replace("ì|í|î|ï".toRegex(), "i")
            .replace("ò|ó|ô|ö".toRegex(), "o")
            .replace("ù|ú|û|ü".toRegex(), "u")
            .replace("ÿ".toRegex(), "y")
            .replace("ç".toRegex(), "c")
            .replace("ñ".toRegex(), "n")
    }
}