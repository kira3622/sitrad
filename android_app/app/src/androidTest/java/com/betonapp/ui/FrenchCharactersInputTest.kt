package com.betonapp.ui

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import com.betonapp.R
import com.betonapp.ui.MainActivity
import com.google.android.material.textfield.TextInputLayout
import org.hamcrest.Matchers.allOf
import org.junit.Ignore
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Tests d'instrumentation pour la saisie de caractères spéciaux français
 * dans les formulaires de l'application
 */
@RunWith(AndroidJUnit4::class)
@LargeTest
class FrenchCharactersInputTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testFrenchCharactersInCreateOrderForm() {
        // Naviguer vers le formulaire de création de commande
        onView(withId(R.id.ordersFragment)).perform(click())
        onView(withId(R.id.fabNewOrder)).perform(click())

        // Tester la saisie de caractères français dans le champ client
        val frenchClientName = "François Müller"
        onView(withId(R.id.etClient))
            .perform(clearText(), typeText(frenchClientName), closeSoftKeyboard())
        
        onView(withId(R.id.etClient))
            .check(matches(withText(frenchClientName)))

        // Tester la saisie de caractères français dans le champ chantier
        val frenchSiteName = "Chantier de la Société Générale"
        onView(withId(R.id.etChantier))
            .perform(clearText(), typeText(frenchSiteName), closeSoftKeyboard())
        
        onView(withId(R.id.etChantier))
            .check(matches(withText(frenchSiteName)))

        // Tester la saisie d'un numéro de commande avec caractères spéciaux
        val orderNumber = "CMD-2024-001-Société"
        onView(withId(R.id.etNumeroCommande))
            .perform(clearText(), typeText(orderNumber), closeSoftKeyboard())
        
        onView(withId(R.id.etNumeroCommande))
            .check(matches(withText(orderNumber)))

        // Vérifier qu'aucune erreur de validation n'est affichée
        onView(allOf(isAssignableFrom(TextInputLayout::class.java), hasDescendant(withId(R.id.etClient))))
            .check(matches(hasNoErrorText()))
        
        onView(allOf(isAssignableFrom(TextInputLayout::class.java), hasDescendant(withId(R.id.etChantier))))
            .check(matches(hasNoErrorText()))
        
        onView(allOf(isAssignableFrom(TextInputLayout::class.java), hasDescendant(withId(R.id.etNumeroCommande))))
            .check(matches(hasNoErrorText()))
    }

    @Test
    fun testFrenchCharactersInInventoryForm() {
        // Naviguer vers le formulaire d'ajout d'inventaire
        onView(withId(R.id.inventoryFragment)).perform(click())
        onView(withId(R.id.fabAddInventory)).perform(click())

        // Tester la saisie de caractères français dans le nom de la matière première
        val frenchMaterialName = "Béton préfabriqué spécialisé"
        onView(withId(R.id.etNomMatiere))
            .perform(clearText(), typeText(frenchMaterialName), closeSoftKeyboard())
        
        onView(withId(R.id.etNomMatiere))
            .check(matches(withText(frenchMaterialName)))

        // Tester la saisie de caractères français dans le nom du fournisseur
        val frenchSupplierName = "Société Française de Béton"
        onView(withId(R.id.etFournisseur))
            .perform(clearText(), typeText(frenchSupplierName), closeSoftKeyboard())
        
        onView(withId(R.id.etFournisseur))
            .check(matches(withText(frenchSupplierName)))

        // Vérifier qu'aucune erreur de validation n'est affichée
        onView(allOf(isAssignableFrom(TextInputLayout::class.java), hasDescendant(withId(R.id.etNomMatiere))))
            .check(matches(hasNoErrorText()))
        
        onView(allOf(isAssignableFrom(TextInputLayout::class.java), hasDescendant(withId(R.id.etFournisseur))))
            .check(matches(hasNoErrorText()))
    }

    @Test
    fun testSpecialCharactersValidation() {
        // Naviguer vers le formulaire de création de commande
        onView(withId(R.id.ordersFragment)).perform(click())
        onView(withId(R.id.fabNewOrder)).perform(click())

        // Tester des caractères spéciaux valides
        val validSpecialChars = listOf(
            "Jean-Pierre",
            "Marie-Claire",
            "L'Oréal",
            "Société Générale",
            "Citroën",
            "Peugeot & Fils"
        )

        validSpecialChars.forEach { name ->
            onView(withId(R.id.etClient))
                .perform(clearText(), typeText(name), closeSoftKeyboard())
            
            onView(withId(R.id.etClient))
                .check(matches(withText(name)))
            
            // Déclencher la validation en cliquant ailleurs
            onView(withId(R.id.etChantier)).perform(click())
            
            // Vérifier qu'aucune erreur n'est affichée
            onView(allOf(isAssignableFrom(TextInputLayout::class.java), hasDescendant(withId(R.id.etClient))))
                .check(matches(hasNoErrorText()))
        }
    }

    @Test
    fun testInvalidCharactersValidation() {
        // Naviguer vers le formulaire de création de commande
        onView(withId(R.id.ordersFragment)).perform(click())
        onView(withId(R.id.fabNewOrder)).perform(click())

        // Tester des caractères invalides
        val invalidChars = listOf(
            "Client@Invalid",
            "Client#Invalid",
            "Client$Invalid",
            "Client%Invalid"
        )

        invalidChars.forEach { name ->
            onView(withId(R.id.etClient))
                .perform(clearText(), typeText(name), closeSoftKeyboard())
            
            // Déclencher la validation en cliquant ailleurs
            onView(withId(R.id.etChantier)).perform(click())
            
            // Vérifier qu'une erreur est affichée
            onView(allOf(isAssignableFrom(TextInputLayout::class.java), hasDescendant(withId(R.id.etClient))))
                .check(matches(hasErrorText()))
        }
    }

    @Test
    @Ignore("Recherche non implémentée pour l'instant")
    fun testAccentedCharactersInSearch() {
        // Naviguer vers la liste des commandes
        onView(withId(R.id.ordersFragment)).perform(click())

        // Tester la recherche avec des caractères accentués
        val searchTerms = listOf(
            "François",
            "Société",
            "Générale",
            "Citroën"
        )

        searchTerms.forEach { term ->
            // TODO: Implémenter la recherche quand l'UI sera prête
            
            // Vérifier que la recherche fonctionne (pas d'erreur)
            onView(withId(R.id.recyclerViewOrders))
                .check(matches(isDisplayed()))
            
            // Effacer la recherche pour le prochain test
            // TODO: Effacer la recherche quand l'UI sera prête
        }
    }

    @Test
    fun testFormSubmissionWithFrenchCharacters() {
        // Naviguer vers le formulaire de création de commande
        onView(withId(R.id.ordersFragment)).perform(click())
        onView(withId(R.id.fabNewOrder)).perform(click())

        // Remplir le formulaire avec des caractères français
        onView(withId(R.id.etClient))
            .perform(typeText("François Müller"), closeSoftKeyboard())
        
        onView(withId(R.id.etChantier))
            .perform(typeText("Chantier de la Société Générale"), closeSoftKeyboard())
        
        onView(withId(R.id.etNumeroCommande))
            .perform(typeText("CMD-2024-001-Société"), closeSoftKeyboard())

        // Remplir les autres champs obligatoires
        onView(withId(R.id.actvTypeBeton)).perform(click())
        onView(withText("Béton C25/30")).perform(click())
        
        onView(withId(R.id.etQuantite))
            .perform(typeText("10.5"), closeSoftKeyboard())
        
        onView(withId(R.id.etPrixUnitaire))
            .perform(typeText("85.50"), closeSoftKeyboard())

        // Soumettre le formulaire
        onView(withId(R.id.btnCreer)).perform(click())

        // Vérifier que la soumission s'est bien passée
        // (cela dépendra de l'implémentation spécifique de votre application)
    }

    /**
     * Matcher personnalisé pour vérifier qu'un TextInputLayout n'a pas d'erreur
     */
    private fun hasNoErrorText() = object : org.hamcrest.TypeSafeMatcher<android.view.View>() {
        override fun describeTo(description: org.hamcrest.Description?) {
            description?.appendText("has no error text")
        }

        override fun matchesSafely(item: android.view.View?): Boolean {
            if (item !is com.google.android.material.textfield.TextInputLayout) {
                return false
            }
            return item.error == null
        }
    }

    /**
     * Matcher personnalisé pour vérifier qu'un TextInputLayout a une erreur
     */
    private fun hasErrorText() = object : org.hamcrest.TypeSafeMatcher<android.view.View>() {
        override fun describeTo(description: org.hamcrest.Description?) {
            description?.appendText("has error text")
        }

        override fun matchesSafely(item: android.view.View?): Boolean {
            if (item !is com.google.android.material.textfield.TextInputLayout) {
                return false
            }
            return item.error != null && item.error.toString().isNotEmpty()
        }
    }
}