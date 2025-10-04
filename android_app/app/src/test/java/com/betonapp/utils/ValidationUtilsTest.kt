package com.betonapp.utils

import org.junit.Test
import org.junit.Assert.*

/**
 * Tests unitaires pour ValidationUtils
 * Teste la validation des caractères spéciaux français
 */
class ValidationUtilsTest {

    @Test
    fun `validateFrenchName should accept valid French names`() {
        val validNames = listOf(
            "Jean-Pierre",
            "Marie-Claire",
            "François",
            "Céline",
            "José",
            "Anaïs",
            "Noël",
            "Chloé",
            "Jérôme",
            "Béatrice",
            "Société Générale",
            "L'Oréal",
            "Citroën",
            "Peugeot",
            "Renault"
        )

        validNames.forEach { name ->
            assertTrue("$name should be valid", ValidationUtils.isValidName(name))
        }
    }

    @Test
    fun `validateFrenchName should reject invalid names`() {
        val invalidNames = listOf(
            "",
            "   "
        )

        invalidNames.forEach { name ->
            assertFalse("Name should be invalid", ValidationUtils.isValidName(name))
        }
    }

    @Test
    fun `validateAddress should accept valid French addresses`() {
        val validAddresses = listOf(
            "123 Rue de la Paix",
            "45 Avenue des Champs-Élysées",
            "12 bis Boulevard Saint-Germain",
            "7 Place de la République",
            "156 Rue du Faubourg Saint-Honoré",
            "23 Allée des Tilleuls",
            "89 Impasse de la Liberté",
            "Château de Versailles",
            "1 Parvis Notre-Dame",
            "Zone Industrielle de Roissy"
        )

        validAddresses.forEach { address ->
            assertTrue("$address should be valid", ValidationUtils.isValidAddress(address))
        }
    }

    @Test
    fun `validateAddress should reject invalid addresses`() {
        val invalidAddresses = listOf(
            "",
            "   ",
            null
        )

        invalidAddresses.forEach { address ->
            assertFalse("Address should be invalid", ValidationUtils.isValidAddress(address))
        }
    }

    @Test
    fun `validateOrderNumber should accept valid order numbers`() {
        val validOrderNumbers = listOf(
            "CMD-2024-001",
            "ORD123456",
            "2024-CMD-001",
            "BET-001-2024",
            "COMMANDE_001",
            "CMD.2024.001",
            "ORDER-123-ABC"
        )

        validOrderNumbers.forEach { orderNumber ->
            assertTrue("$orderNumber should be valid", ValidationUtils.isValidOrderNumber(orderNumber))
        }
    }

    @Test
    fun `validateOrderNumber should reject invalid order numbers`() {
        val invalidOrderNumbers = listOf(
            "",
            "   ",
            "123",
            "CMD@2024",
            "ORDER#123",
            "CMD$2024",
            "ORDER%123",
            "CMD&2024"
        )

        invalidOrderNumbers.forEach { orderNumber ->
            assertFalse("$orderNumber should be invalid", ValidationUtils.isValidOrderNumber(orderNumber))
        }
    }

    @Test
    fun `validateWith should work correctly with TextInputLayout`() {
        // Ce test nécessiterait un contexte Android pour créer des TextInputLayout
        // Il sera implémenté dans les tests d'instrumentation
    }

    @Test
    fun `clearError should work correctly with TextInputLayout`() {
        // Ce test nécessiterait un contexte Android pour créer des TextInputLayout
        // Il sera implémenté dans les tests d'instrumentation
    }

    @Test
    fun `setupForFrenchNames should configure TextInputEditText correctly`() {
        // Ce test nécessiterait un contexte Android pour créer des TextInputEditText
        // Il sera implémenté dans les tests d'instrumentation
    }

    @Test
    fun `setupForAddresses should configure TextInputEditText correctly`() {
        // Ce test nécessiterait un contexte Android pour créer des TextInputEditText
        // Il sera implémenté dans les tests d'instrumentation
    }

    @Test
    fun `setupForOrderNumbers should configure TextInputEditText correctly`() {
        // Ce test nécessiterait un contexte Android pour créer des TextInputEditText
        // Il sera implémenté dans les tests d'instrumentation
    }
}