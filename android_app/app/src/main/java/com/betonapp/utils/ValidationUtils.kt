package com.betonapp.utils

import android.text.InputFilter
import android.text.Spanned
import java.text.Normalizer
import java.util.regex.Pattern

/**
 * Utilitaires de validation pour la gestion des caractères spéciaux français
 * et la validation de texte dans l'application
 */
object ValidationUtils {

    // Regex pour les caractères français autorisés (lettres, accents, espaces, tirets, apostrophes)
    private val FRENCH_TEXT_PATTERN = Pattern.compile("^[\\p{L}\\s\\-']+$")
    
    // Regex pour les noms de personnes/entreprises (plus permissif)
    private val NAME_PATTERN = Pattern.compile("^[\\p{L}\\s\\-'.&()0-9]+$")
    
    // Regex pour les adresses (très permissif)
    private val ADDRESS_PATTERN = Pattern.compile("^[\\p{L}\\s\\-'.,&()0-9]+$")
    
    // Regex pour les numéros de téléphone français
    private val PHONE_PATTERN = Pattern.compile("^(?:(?:\\+|00)33[\\s.-]?(?:\\(0\\)[\\s.-]?)?|0)[1-9](?:[\\s.-]?\\d{2}){4}$")
    
    // Regex pour les emails
    private val EMAIL_PATTERN = Pattern.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")

    /**
     * Valide un texte français (noms, prénoms, villes, etc.)
     */
    fun isValidFrenchText(text: String?): Boolean {
        return !text.isNullOrBlank() && FRENCH_TEXT_PATTERN.matcher(text.trim()).matches()
    }

    /**
     * Valide un nom (personne ou entreprise)
     */
    fun isValidName(name: String?): Boolean {
        return !name.isNullOrBlank() && NAME_PATTERN.matcher(name.trim()).matches()
    }

    /**
     * Valide une adresse
     */
    fun isValidAddress(address: String?): Boolean {
        return !address.isNullOrBlank() && ADDRESS_PATTERN.matcher(address.trim()).matches()
    }

    /**
     * Valide un numéro de téléphone français
     */
    fun isValidPhoneNumber(phone: String?): Boolean {
        return !phone.isNullOrBlank() && PHONE_PATTERN.matcher(phone.trim()).matches()
    }

    /**
     * Valide un numéro de commande
     */
    fun isValidOrderNumber(orderNumber: String): Boolean {
        val cleanOrderNumber = cleanText(orderNumber)
        // Validation préliminaire
        if (cleanOrderNumber.length !in 3..20) return false
        if (!cleanOrderNumber.any { it.isLetter() }) return false
        if (!cleanOrderNumber.all { it.isLetterOrDigit() || it == '-' || it == '_' || it == '.' }) return false
        // Toutes les vérifications sont satisfaites
        return true
    }

    /**
     * Valide une adresse email
     */
    fun isValidEmail(email: String?): Boolean {
        return !email.isNullOrBlank() && EMAIL_PATTERN.matcher(email.trim()).matches()
    }

    /**
     * Normalise un texte en supprimant les accents pour la recherche
     */
    fun normalizeForSearch(text: String): String {
        return Normalizer.normalize(text, Normalizer.Form.NFD)
            .replace("\\p{InCombiningDiacriticalMarks}+".toRegex(), "")
            .lowercase()
    }

    /**
     * Nettoie un texte en supprimant les espaces multiples et les caractères indésirables
     */
    fun cleanText(text: String): String {
        return text.trim()
            .replace("\\s+".toRegex(), " ") // Remplace les espaces multiples par un seul
            .replace("[\\u00A0\\u2007\\u202F]".toRegex(), " ") // Remplace les espaces insécables
    }

    /**
     * Vérifie si un texte contient uniquement des caractères autorisés
     */
    fun containsOnlyAllowedCharacters(text: String, pattern: Pattern): Boolean {
        return pattern.matcher(text).matches()
    }

    /**
     * Filtre d'entrée pour les noms français (personnes, entreprises)
     */
    class FrenchNameInputFilter : InputFilter {
        override fun filter(
            source: CharSequence?,
            start: Int,
            end: Int,
            dest: Spanned?,
            dstart: Int,
            dend: Int
        ): CharSequence? {
            if (source == null) return null
            
            val filtered = StringBuilder()
            for (i in start until end) {
                val char = source[i]
                if (isAllowedNameCharacter(char)) {
                    filtered.append(char)
                }
            }
            
            return if (filtered.length == end - start) {
                null // Pas de filtrage nécessaire
            } else {
                filtered.toString()
            }
        }
        
        private fun isAllowedNameCharacter(char: Char): Boolean {
            return char.isLetter() || 
                   char.isDigit() ||
                   char in "ÀÁÂÃÄÅàáâãäåÇçÈÉÊËèéêëÌÍÎÏìíîïÑñÒÓÔÕÖØòóôõöøÙÚÛÜùúûüÝýÿ" ||
                   char in " -'.&()"
        }
    }

    /**
     * Filtre d'entrée pour les adresses
     */
    class AddressInputFilter : InputFilter {
        override fun filter(
            source: CharSequence?,
            start: Int,
            end: Int,
            dest: Spanned?,
            dstart: Int,
            dend: Int
        ): CharSequence? {
            if (source == null) return null
            
            val filtered = StringBuilder()
            for (i in start until end) {
                val char = source[i]
                if (isAllowedAddressCharacter(char)) {
                    filtered.append(char)
                }
            }
            
            return if (filtered.length == end - start) {
                null // Pas de filtrage nécessaire
            } else {
                filtered.toString()
            }
        }
        
        private fun isAllowedAddressCharacter(char: Char): Boolean {
            return char.isLetter() || 
                   char.isDigit() ||
                   char in "ÀÁÂÃÄÅàáâãäåÇçÈÉÊËèéêëÌÍÎÏìíîïÑñÒÓÔÕÖØòóôõöøÙÚÛÜùúûüÝýÿ" ||
                   char in " -'.,&()/"
        }
    }

    /**
     * Filtre d'entrée pour le texte français général
     */
    class FrenchTextInputFilter : InputFilter {
        override fun filter(
            source: CharSequence?,
            start: Int,
            end: Int,
            dest: Spanned?,
            dstart: Int,
            dend: Int
        ): CharSequence? {
            if (source == null) return null
            
            val filtered = StringBuilder()
            for (i in start until end) {
                val char = source[i]
                if (isAllowedFrenchCharacter(char)) {
                    filtered.append(char)
                }
            }
            
            return if (filtered.length == end - start) {
                null // Pas de filtrage nécessaire
            } else {
                filtered.toString()
            }
        }
        
        private fun isAllowedFrenchCharacter(char: Char): Boolean {
            return char.isLetter() || 
                   char in "ÀÁÂÃÄÅàáâãäåÇçÈÉÊËèéêëÌÍÎÏìíîïÑñÒÓÔÕÖØòóôõöøÙÚÛÜùúûüÝýÿ" ||
                   char in " -'"
        }
    }

    /**
     * Messages d'erreur pour la validation
     */
    object ErrorMessages {
        const val FIELD_REQUIRED = "Ce champ est requis"
        const val INVALID_NAME = "Nom invalide. Utilisez uniquement des lettres, espaces, tirets et apostrophes"
        const val INVALID_ADDRESS = "Adresse invalide. Caractères non autorisés détectés"
        const val INVALID_PHONE = "Numéro de téléphone invalide. Format attendu: 01 23 45 67 89"
        const val INVALID_EMAIL = "Adresse email invalide"
        const val INVALID_FRENCH_TEXT = "Texte invalide. Utilisez uniquement des lettres françaises"
        const val TEXT_TOO_SHORT = "Le texte est trop court"
        const val TEXT_TOO_LONG = "Le texte est trop long"
    }

    /**
     * Valide un champ avec des règles personnalisées
     */
    fun validateField(
        value: String?,
        isRequired: Boolean = true,
        minLength: Int = 0,
        maxLength: Int = Int.MAX_VALUE,
        validator: ((String) -> Boolean)? = null,
        customErrorMessage: String? = null
    ): ValidationResult {
        
        // Vérification si requis
        if (isRequired && value.isNullOrBlank()) {
            return ValidationResult(false, ErrorMessages.FIELD_REQUIRED)
        }
        
        // Si pas requis et vide, c'est valide
        if (!isRequired && value.isNullOrBlank()) {
            return ValidationResult(true)
        }
        
        val cleanValue = value!!.trim()
        
        // Vérification de la longueur
        if (cleanValue.length < minLength) {
            return ValidationResult(false, ErrorMessages.TEXT_TOO_SHORT)
        }
        
        if (cleanValue.length > maxLength) {
            return ValidationResult(false, ErrorMessages.TEXT_TOO_LONG)
        }
        
        // Validation personnalisée
        if (validator != null && !validator(cleanValue)) {
            return ValidationResult(false, customErrorMessage ?: "Valeur invalide")
        }
        
        return ValidationResult(true)
    }

    /**
     * Résultat de validation
     */
    data class ValidationResult(
        val isValid: Boolean,
        val errorMessage: String? = null
    )
}

