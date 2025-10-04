package com.betonapp.utils

import android.text.InputFilter
import android.text.TextWatcher
import android.widget.EditText
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout

/**
 * Extensions pour faciliter la validation et la gestion des caractères spéciaux
 * dans les TextInputLayout et EditText
 */

/**
 * Configure un TextInputLayout pour la saisie de noms français
 */
fun TextInputLayout.setupForFrenchNames() {
    editText?.apply {
        filters = arrayOf(ValidationUtils.FrenchNameInputFilter(), InputFilter.LengthFilter(100))
        addTextChangedListener(createValidationWatcher { text ->
            ValidationUtils.validateField(
                value = text,
                validator = ValidationUtils::isValidName,
                customErrorMessage = ValidationUtils.ErrorMessages.INVALID_NAME
            )
        })
    }
}

/**
 * Configure un TextInputLayout pour la saisie d'adresses
 */
fun TextInputLayout.setupForAddresses() {
    editText?.apply {
        filters = arrayOf(ValidationUtils.AddressInputFilter(), InputFilter.LengthFilter(200))
        addTextChangedListener(createValidationWatcher { text ->
            ValidationUtils.validateField(
                value = text,
                validator = ValidationUtils::isValidAddress,
                customErrorMessage = ValidationUtils.ErrorMessages.INVALID_ADDRESS
            )
        })
    }
}

/**
 * Configure un TextInputLayout pour la saisie de texte français général
 */
fun TextInputLayout.setupForFrenchText() {
    editText?.apply {
        filters = arrayOf(ValidationUtils.FrenchTextInputFilter(), InputFilter.LengthFilter(100))
        addTextChangedListener(createValidationWatcher { text ->
            ValidationUtils.validateField(
                value = text,
                validator = ValidationUtils::isValidFrenchText,
                customErrorMessage = ValidationUtils.ErrorMessages.INVALID_FRENCH_TEXT
            )
        })
    }
}

/**
 * Configure un TextInputLayout pour la saisie d'emails
 */
fun TextInputLayout.setupForEmail() {
    editText?.apply {
        addTextChangedListener(createValidationWatcher { text ->
            ValidationUtils.validateField(
                value = text,
                validator = ValidationUtils::isValidEmail,
                customErrorMessage = ValidationUtils.ErrorMessages.INVALID_EMAIL
            )
        })
    }
}

/**
 * Configure un TextInputLayout pour la saisie de numéros de téléphone
 */
fun TextInputLayout.setupForPhoneNumber() {
    editText?.apply {
        addTextChangedListener(createValidationWatcher { text ->
            ValidationUtils.validateField(
                value = text,
                validator = ValidationUtils::isValidPhoneNumber,
                customErrorMessage = ValidationUtils.ErrorMessages.INVALID_PHONE
            )
        })
    }
}

/**
 * Valide un TextInputLayout avec des règles personnalisées
 */
fun TextInputLayout.validateWith(
    isRequired: Boolean = true,
    minLength: Int = 0,
    maxLength: Int = Int.MAX_VALUE,
    validator: ((String) -> Boolean)? = null,
    customErrorMessage: String? = null
): Boolean {
    val text = editText?.text?.toString()
    val result = ValidationUtils.validateField(
        value = text,
        isRequired = isRequired,
        minLength = minLength,
        maxLength = maxLength,
        validator = validator,
        customErrorMessage = customErrorMessage
    )
    
    error = if (result.isValid) null else result.errorMessage
    return result.isValid
}

/**
 * Efface l'erreur d'un TextInputLayout
 */
fun TextInputLayout.clearError() {
    error = null
}

/**
 * Définit une erreur sur un TextInputLayout
 */
fun TextInputLayout.setError(message: String) {
    error = message
}

/**
 * Vérifie si un TextInputLayout a une erreur
 */
fun TextInputLayout.hasError(): Boolean {
    return !error.isNullOrEmpty()
}

/**
 * Obtient le texte nettoyé d'un TextInputLayout
 */
fun TextInputLayout.getCleanText(): String {
    val text = editText?.text?.toString() ?: ""
    return ValidationUtils.cleanText(text)
}

/**
 * Définit le texte d'un TextInputLayout en le nettoyant
 */
fun TextInputLayout.setCleanText(text: String) {
    editText?.setText(ValidationUtils.cleanText(text))
}

/**
 * Configure la validation en temps réel pour un TextInputLayout
 */
fun TextInputLayout.setupRealTimeValidation(
    isRequired: Boolean = true,
    minLength: Int = 0,
    maxLength: Int = Int.MAX_VALUE,
    validator: ((String) -> Boolean)? = null,
    customErrorMessage: String? = null
) {
    editText?.addTextChangedListener(createValidationWatcher { text ->
        ValidationUtils.validateField(
            value = text,
            isRequired = isRequired,
            minLength = minLength,
            maxLength = maxLength,
            validator = validator,
            customErrorMessage = customErrorMessage
        )
    })
}

/**
 * Crée un TextWatcher pour la validation en temps réel
 */
private fun TextInputLayout.createValidationWatcher(
    validator: (String) -> ValidationUtils.ValidationResult
): TextWatcher {
    return object : TextWatcher {
        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
        
        override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        
        override fun afterTextChanged(s: android.text.Editable?) {
            val text = s?.toString() ?: ""
            val result = validator(text)
            error = if (result.isValid) null else result.errorMessage
        }
    }
}

/**
 * Extensions pour EditText
 */

/**
 * Applique un filtre de caractères français à un EditText
 */
fun EditText.applyFrenchNameFilter() {
    filters = arrayOf(ValidationUtils.FrenchNameInputFilter(), InputFilter.LengthFilter(100))
}

/**
 * Applique un filtre d'adresse à un EditText
 */
fun EditText.applyAddressFilter() {
    filters = arrayOf(ValidationUtils.AddressInputFilter(), InputFilter.LengthFilter(200))
}

/**
 * Applique un filtre de texte français général à un EditText
 */
fun EditText.applyFrenchTextFilter() {
    filters = arrayOf(ValidationUtils.FrenchTextInputFilter(), InputFilter.LengthFilter(100))
}

/**
 * Obtient le texte nettoyé d'un EditText
 */
fun EditText.getCleanText(): String {
    return ValidationUtils.cleanText(text.toString())
}

/**
 * Définit le texte d'un EditText en le nettoyant
 */
fun EditText.setCleanText(text: String) {
    setText(ValidationUtils.cleanText(text))
}