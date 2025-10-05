package com.betonapp.data.models

import com.betonapp.utils.EncodingUtils

/**
 * Extensions pour les modèles de données pour gérer l'encodage UTF-8
 */

/**
 * Extension pour Client avec encodage UTF-8
 */
fun Client.withUtf8Encoding(): Client {
    return this.copy(
        nom = EncodingUtils.encodeForApi(nom) ?: nom,
        adresse = EncodingUtils.encodeForApi(adresse) ?: adresse,
        telephone = EncodingUtils.encodeForApi(telephone) ?: telephone,
        email = EncodingUtils.encodeForApi(email) ?: email
    )
}

/**
 * Extension pour Chantier avec encodage UTF-8
 */
fun Chantier.withUtf8Encoding(): Chantier {
    return this.copy(
        nom = EncodingUtils.encodeForApi(nom) ?: nom,
        adresse = EncodingUtils.encodeForApi(adresse) ?: adresse,
        client = client.withUtf8Encoding()
    )
}

/**
 * Extension pour Commande avec encodage UTF-8
 */
fun Commande.withUtf8Encoding(): Commande {
    return this.copy(
        statut = EncodingUtils.encodeForApi(statut) ?: statut
    )
}

/**
 * Extension pour OrdreProduction avec encodage UTF-8
 */
fun OrdreProduction.withUtf8Encoding(): OrdreProduction {
    return this.copy(
        numeroBon = EncodingUtils.encodeForApi(numeroBon) ?: numeroBon
    )
}

/**
 * Extension pour MatierePremiere avec encodage UTF-8
 */
fun MatierePremiere.withUtf8Encoding(): MatierePremiere {
    return this.copy(
        nom = EncodingUtils.encodeForApi(nom) ?: nom,
        unite = EncodingUtils.encodeForApi(unite) ?: unite,
        statutStock = EncodingUtils.encodeForApi(statutStock) ?: statutStock
    )
}

/**
 * Extension pour Approvisionnement avec encodage UTF-8
 */
fun Approvisionnement.withUtf8Encoding(): Approvisionnement {
    return this.copy(
        matierePremiere = matierePremiere.withUtf8Encoding(),
        fournisseur = EncodingUtils.encodeForApi(fournisseur) ?: fournisseur
    )
}

/**
 * Extension pour ConsommationCarburant avec encodage UTF-8
 */
fun ConsommationCarburant.withUtf8Encoding(): ConsommationCarburant {
    return this.copy(
        vehicule = EncodingUtils.encodeForApi(vehicule) ?: vehicule
    )
}

/**
 * Extension pour Facture avec encodage UTF-8
 */
fun Facture.withUtf8Encoding(): Facture {
    return this.copy(
        numeroFacture = EncodingUtils.encodeForApi(numeroFacture) ?: numeroFacture,
        commande = commande.withUtf8Encoding(),
        statut = EncodingUtils.encodeForApi(statut) ?: statut
    )
}

/**
 * Extensions pour les listes - Supprimées pour éviter les conflits de signature JVM
 * Utiliser directement les fonctions d'extension individuelles avec map() si nécessaire
 */