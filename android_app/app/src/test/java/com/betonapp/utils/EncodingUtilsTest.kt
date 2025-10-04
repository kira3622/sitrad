package com.betonapp.utils

import org.junit.Test
import org.junit.Assert.*

/**
 * Tests unitaires pour EncodingUtils
 * Teste l'encodage et le décodage des caractères spéciaux français
 */
class EncodingUtilsTest {

    @Test
    fun `ensureUtf8 should handle French characters correctly`() {
        val testStrings = mapOf(
            "François" to "François",
            "Céline" to "Céline",
            "José" to "José",
            "Anaïs" to "Anaïs",
            "Noël" to "Noël",
            "Chloé" to "Chloé",
            "Jérôme" to "Jérôme",
            "Béatrice" to "Béatrice",
            "Société Générale" to "Société Générale",
            "L'Oréal" to "L'Oréal",
            "Citroën" to "Citroën"
        )

        testStrings.forEach { (input, expected) ->
            val result = EncodingUtils.ensureUtf8(input)
            assertEquals("Failed for: $input", expected, result)
        }
    }

    @Test
    fun `cleanForUtf8 should remove invalid characters`() {
        val testCases = mapOf(
            "François\u0000" to "François",
            "Test\u0001String" to "TestString",
            "Normal String" to "Normal String",
            "Céline\u0002Test" to "CélineTest"
        )

        testCases.forEach { (input, expected) ->
            val result = EncodingUtils.cleanForUtf8(input)
            assertEquals("Failed for: $input", expected, result)
        }
    }

    @Test
    fun `isValidUtf8 should validate UTF-8 strings correctly`() {
        val validStrings = listOf(
            "François",
            "Céline",
            "José",
            "Anaïs",
            "Noël",
            "Société Générale",
            "L'Oréal",
            "Citroën",
            "Regular English text",
            "123456789",
            "Special chars: !@#$%^&*()"
        )

        val invalidStrings = listOf(
            "Test\u0000String",
            "Invalid\u0001Char",
            "Bad\u0002String"
        )

        validStrings.forEach { str ->
            assertTrue("$str should be valid UTF-8", EncodingUtils.isValidUtf8(str))
        }

        invalidStrings.forEach { str ->
            assertFalse("$str should be invalid UTF-8", EncodingUtils.isValidUtf8(str))
        }
    }

    @Test
    fun `encodeForApi should prepare strings for API transmission`() {
        val testStrings = listOf(
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
            "Citroën"
        )

        testStrings.forEach { str ->
            val encoded = EncodingUtils.encodeForApi(str)
            assertNotNull("Encoded string should not be null", encoded)
            assertTrue("Encoded string should be valid UTF-8", EncodingUtils.isValidUtf8(encoded))
        }
    }

    @Test
    fun `decodeFromApi should handle API responses correctly`() {
        val testStrings = listOf(
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
            "Citroën"
        )

        testStrings.forEach { str ->
            val encoded = EncodingUtils.encodeForApi(str)
            val decoded = EncodingUtils.decodeFromApi(encoded)
            assertEquals("Round-trip encoding/decoding failed for: $str", str, decoded)
        }
    }

    @Test
    fun `containsFrenchCharacters should detect French characters correctly`() {
        val frenchStrings = listOf(
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
            "Citroën"
        )

        val nonFrenchStrings = listOf(
            "John",
            "Mary",
            "Company Ltd",
            "Test String",
            "123456789",
            "Regular text"
        )

        frenchStrings.forEach { str ->
            assertTrue("$str should contain French characters", EncodingUtils.containsFrenchCharacters(str))
        }

        nonFrenchStrings.forEach { str ->
            assertFalse("$str should not contain French characters", EncodingUtils.containsFrenchCharacters(str))
        }
    }

    @Test
    fun `normalizeFrenchForSearch should normalize accents for search`() {
        val testCases = mapOf(
            "François" to "francois",
            "Céline" to "celine",
            "José" to "jose",
            "Anaïs" to "anais",
            "Noël" to "noel",
            "Chloé" to "chloe",
            "Jérôme" to "jerome",
            "Béatrice" to "beatrice",
            "Société Générale" to "societe generale",
            "L'Oréal" to "l'oreal",
            "Citroën" to "citroen"
        )

        testCases.forEach { (input, expected) ->
            val result = EncodingUtils.normalizeFrenchForSearch(input)
            assertEquals("Failed for: $input", expected, result)
        }
    }

    @Test
    fun `normalizeFrenchForSearch should handle mixed case correctly`() {
        val testCases = mapOf(
            "FRANÇOIS" to "francois",
            "CéLiNe" to "celine",
            "JOSÉ" to "jose",
            "AnaÏs" to "anais",
            "NOËL" to "noel"
        )

        testCases.forEach { (input, expected) ->
            val result = EncodingUtils.normalizeFrenchForSearch(input)
            assertEquals("Failed for: $input", expected, result)
        }
    }

    @Test
    fun `encoding functions should handle null and empty strings`() {
        assertNull("Null input should return null", EncodingUtils.ensureUtf8(null))
        assertEquals("Empty string should remain empty", "", EncodingUtils.ensureUtf8(""))
        assertEquals("Whitespace should be preserved", "   ", EncodingUtils.ensureUtf8("   "))
        
        assertNull("Null input should return null", EncodingUtils.encodeForApi(null))
        assertEquals("Empty string should remain empty", "", EncodingUtils.encodeForApi(""))
        
        assertNull("Null input should return null", EncodingUtils.decodeFromApi(null))
        assertEquals("Empty string should remain empty", "", EncodingUtils.decodeFromApi(""))
        
        assertFalse("Null should not contain French characters", EncodingUtils.containsFrenchCharacters(null))
        assertFalse("Empty string should not contain French characters", EncodingUtils.containsFrenchCharacters(""))
        
        assertEquals("Null should normalize to empty", "", EncodingUtils.normalizeFrenchForSearch(null))
        assertEquals("Empty should normalize to empty", "", EncodingUtils.normalizeFrenchForSearch(""))
    }
}