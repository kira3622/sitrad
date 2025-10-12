package com.betonapp.data.models

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.parcelize.Parcelize

/**
 * Modèles de données métier pour l'application Béton
 */

@Parcelize
data class Client(
    val id: Int,
    val nom: String,
    val adresse: String,
    val telephone: String,
    val email: String,
    @SerializedName("date_creation")
    val dateCreation: String
) : Parcelable

@Parcelize
data class Chantier(
    val id: Int,
    val nom: String,
    val adresse: String,
    val client: Client,
    @SerializedName("date_debut")
    val dateDebut: String,
    @SerializedName("date_fin_prevue")
    val dateFinPrevue: String,
    val statut: String
) : Parcelable

@Parcelize
data class Commande(
    val id: Int,
    @SerializedName("client")
    val clientId: Int,
    @SerializedName("chantier")
    val chantierId: Int?,
    @SerializedName("date_commande")
    val dateCommande: String,
    @SerializedName("date_livraison_souhaitee")
    val dateLivraisonSouhaitee: String,
    val statut: String,
    @SerializedName("client_nom")
    val clientNom: String? = null,
    val numero: String? = null,
    @SerializedName("date_livraison_prevue")
    val dateLivraisonPrevue: String? = null,
    val deliveryNotified: Boolean = false,
    @SerializedName("lignes")
    val lignes: List<LigneCommande>? = null
) : Parcelable

@Parcelize
data class FormuleBeton(
    val id: Int,
    val nom: String,
    @SerializedName("description")
    val description: String? = null,
    @SerializedName("resistance_requise")
    val resistanceRequise: String? = null,
    @SerializedName("quantite_produite_reference")
    val quantiteProduiteReference: String? = null
) : Parcelable

@Parcelize
data class LigneCommande(
    val id: Int? = null,
    @SerializedName("formule")
    val formuleId: Int,
    val quantite: Double
) : Parcelable

@Parcelize
data class OrdreProduction(
    val id: Int,
    @SerializedName("numero_bon")
    val numeroBon: String?,
    @SerializedName("commande")
    val commandeId: Int,
    @SerializedName("formule")
    val formuleId: Int,
    @SerializedName("quantite_produire")
    val quantiteProduire: Double,
    @SerializedName("date_production")
    val dateProduction: String,
    @SerializedName("heure_production")
    val heureProduction: String?,
    val statut: String,
    @SerializedName("matieres_sorties_calculees")
    val matieresSortiesCalculees: Boolean = false
) : Parcelable

@Parcelize
data class MatierePremiere(
    val id: Int,
    val nom: String,
    val unite: String,
    @SerializedName("stock_actuel")
    val stockActuel: Double,
    @SerializedName("stock_minimum")
    val stockMinimum: Double,
    @SerializedName("statut_stock")
    val statutStock: String,
    @SerializedName("prix_unitaire")
    val prixUnitaire: Double
) : Parcelable

/**
 * Modèles pour les notifications depuis l'API
 */
@Parcelize
data class ApiNotification(
    val id: String,
    val title: String,
    val message: String,
    val type: String,
    val timestamp: Long,
    @SerializedName("is_read")
    val isRead: Boolean,
    @SerializedName("related_object_id")
    val relatedObjectId: Int? = null,
    @SerializedName("related_object_type")
    val relatedObjectType: String? = null,
    val priority: String? = "normal"
) : Parcelable

@Parcelize
data class NotificationSummary(
    @SerializedName("total_count")
    val totalCount: Int,
    @SerializedName("unread_count")
    val unreadCount: Int,
    @SerializedName("new_orders_count")
    val newOrdersCount: Int,
    @SerializedName("production_updates_count")
    val productionUpdatesCount: Int,
    @SerializedName("low_inventory_count")
    val lowInventoryCount: Int,
    @SerializedName("delivery_count")
    val deliveryCount: Int
) : Parcelable

@Parcelize
data class Approvisionnement(
    val id: Int,
    @SerializedName("matiere_premiere")
    val matierePremiere: MatierePremiere,
    val quantite: Double,
    val fournisseur: String,
    @SerializedName("prix_unitaire")
    val prixUnitaire: Double,
    @SerializedName("cout_total")
    val coutTotal: Double,
    val date: String
) : Parcelable

@Parcelize
data class ConsommationCarburant(
    val id: Int,
    val vehicule: String,
    val quantite: Double,
    @SerializedName("prix_unitaire")
    val prixUnitaire: Double,
    @SerializedName("cout_total")
    val coutTotal: Double,
    val date: String,
    val kilometrage: Int?
) : Parcelable

@Parcelize
data class Facture(
    val id: Int,
    @SerializedName("numero_facture")
    val numeroFacture: String,
    val commande: Commande,
    @SerializedName("date_emission")
    val dateEmission: String,
    @SerializedName("date_echeance")
    val dateEcheance: String,
    @SerializedName("montant_ht")
    val montantHT: Double,
    val tva: Double,
    @SerializedName("montant_ttc")
    val montantTTC: Double,
    val statut: String
) : Parcelable

// Modèles pour les statistiques du dashboard
data class DashboardStats(
    @SerializedName("commandes_total")
    val commandesTotal: Int,
    @SerializedName("commandes_en_cours")
    val commandesEnCours: Int,
    @SerializedName("production_mensuelle")
    val productionMensuelle: Double,
    @SerializedName("chiffre_affaires_mensuel")
    val chiffreAffairesMensuel: Double,
    @SerializedName("stock_critique")
    val stockCritique: Int,
    @SerializedName("consommation_carburant_mensuelle")
    val consommationCarburantMensuelle: Double
)

data class ProductionQuotidienne(
    val date: String,
    val quantite: Double
)

data class ProductionParType(
    @SerializedName("type_beton")
    val typeBeton: String,
    @SerializedName("quantite_totale")
    val quantiteTotale: Double
)

data class ProductionStats(
    @SerializedName("production_quotidienne")
    val productionQuotidienne: List<ProductionQuotidienne>,
    @SerializedName("production_par_type")
    val productionParType: List<ProductionParType>
)

// Modèles pour les réponses paginées
data class PaginatedResponse<T>(
    val count: Int,
    val next: String?,
    val previous: String?,
    val results: List<T>
)

// Modèles pour les erreurs API
data class ApiError(
    val detail: String?,
    @SerializedName("field_errors")
    val fieldErrors: Map<String, List<String>>?
)

// Énumérations pour les statuts
enum class CommandeStatus(val value: String, val displayName: String) {
    EN_ATTENTE("en_attente", "En attente"),
    EN_PRODUCTION("en_production", "En production"),
    TERMINEE("terminee", "Terminée"),
    ANNULEE("annulee", "Annulée");

    companion object {
        fun fromValue(value: String): CommandeStatus? {
            return values().find { it.value == value }
        }
    }
}

enum class StockStatus(val value: String, val displayName: String) {
    NORMAL("normal", "Normal"),
    FAIBLE("faible", "Faible"),
    CRITIQUE("critique", "Critique");

    companion object {
        fun fromValue(value: String): StockStatus? {
            return values().find { it.value == value }
        }
    }
}

enum class ProductionStatus(val value: String, val displayName: String) {
    EN_COURS("en_cours", "En cours"),
    TERMINE("termine", "Terminé"),
    ANNULE("annule", "Annulé");

    companion object {
        fun fromValue(value: String): ProductionStatus? {
            return values().find { it.value == value }
        }
    }
}