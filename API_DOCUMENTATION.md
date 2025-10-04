# 📚 Documentation API Béton - Version Complète

## 🚀 Vue d'ensemble

L'API Béton est une API REST complète développée avec Django REST Framework pour la gestion d'une entreprise de production de béton. Elle offre des fonctionnalités complètes pour la gestion des commandes, de la production, du stock, et des statistiques.

### 🔗 URLs de base
- **Développement**: `http://127.0.0.1:8000/api/v1/`
- **Production**: `https://beton-project.onrender.com/api/v1/`

### 🔐 Authentification
L'API utilise l'authentification JWT (JSON Web Tokens) pour sécuriser tous les endpoints.

---

## 🔑 Authentification

### Obtenir un token JWT
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "votre_mot_de_passe"
}
```

**Réponse:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Rafraîchir un token
```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Utilisation du token
Incluez le token dans l'en-tête Authorization de toutes vos requêtes :
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 👥 Gestion des Clients

### Lister tous les clients
```http
GET /api/v1/clients/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "count": 25,
    "next": "http://127.0.0.1:8000/api/v1/clients/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "nom": "Entreprise ABC",
            "adresse": "123 Rue de la Paix",
            "telephone": "0123456789",
            "email": "contact@abc.com",
            "date_creation": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Créer un nouveau client
```http
POST /api/v1/clients/
Authorization: Bearer <token>
Content-Type: application/json

{
    "nom": "Nouvelle Entreprise",
    "adresse": "456 Avenue des Champs",
    "telephone": "0987654321",
    "email": "contact@nouvelle.com"
}
```

### Obtenir un client spécifique
```http
GET /api/v1/clients/{id}/
Authorization: Bearer <token>
```

### Mettre à jour un client
```http
PUT /api/v1/clients/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
    "nom": "Entreprise ABC Modifiée",
    "adresse": "123 Rue de la Paix",
    "telephone": "0123456789",
    "email": "nouveau@abc.com"
}
```

### Supprimer un client
```http
DELETE /api/v1/clients/{id}/
Authorization: Bearer <token>
```

---

## 🏗️ Gestion des Chantiers

### Lister tous les chantiers
```http
GET /api/v1/chantiers/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "nom": "Construction Immeuble A",
            "adresse": "789 Boulevard Central",
            "client": {
                "id": 1,
                "nom": "Entreprise ABC"
            },
            "date_debut": "2024-02-01",
            "date_fin_prevue": "2024-08-01",
            "statut": "en_cours"
        }
    ]
}
```

### Créer un nouveau chantier
```http
POST /api/v1/chantiers/
Authorization: Bearer <token>
Content-Type: application/json

{
    "nom": "Nouveau Chantier",
    "adresse": "321 Rue du Projet",
    "client": 1,
    "date_debut": "2024-03-01",
    "date_fin_prevue": "2024-09-01",
    "statut": "planifie"
}
```

---

## 📦 Gestion des Commandes

### Lister toutes les commandes
```http
GET /api/v1/commandes/
Authorization: Bearer <token>
```

**Paramètres de filtrage disponibles:**
- `statut`: `en_attente`, `en_production`, `terminee`, `annulee`
- `client`: ID du client
- `date_commande`: Date de commande (format: YYYY-MM-DD)

**Exemple avec filtres:**
```http
GET /api/v1/commandes/?statut=en_production&client=1
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "numero_commande": "CMD-2024-001",
            "client": {
                "id": 1,
                "nom": "Entreprise ABC"
            },
            "chantier": {
                "id": 1,
                "nom": "Construction Immeuble A"
            },
            "type_beton": "C25/30",
            "quantite": 50.0,
            "date_commande": "2024-01-20T09:00:00Z",
            "date_livraison_prevue": "2024-01-25T14:00:00Z",
            "statut": "en_production",
            "prix_unitaire": 120.00,
            "prix_total": 6000.00
        }
    ]
}
```

### Créer une nouvelle commande
```http
POST /api/v1/commandes/
Authorization: Bearer <token>
Content-Type: application/json

{
    "client": 1,
    "chantier": 1,
    "type_beton": "C30/37",
    "quantite": 75.5,
    "date_livraison_prevue": "2024-02-15T10:00:00Z",
    "prix_unitaire": 125.00
}
```

### Mettre à jour le statut d'une commande
```http
PATCH /api/v1/commandes/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
    "statut": "terminee"
}
```

---

## 🏭 Gestion de la Production

### Lister tous les ordres de production
```http
GET /api/v1/ordres-production/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "numero_ordre": "OP-2024-001",
            "commande": {
                "id": 1,
                "numero_commande": "CMD-2024-001"
            },
            "date_production": "2024-01-24T08:00:00Z",
            "quantite_produite": 50.0,
            "statut": "en_cours",
            "operateur": "Jean Dupont",
            "notes": "Production normale"
        }
    ]
}
```

### Créer un ordre de production
```http
POST /api/v1/ordres-production/
Authorization: Bearer <token>
Content-Type: application/json

{
    "commande": 1,
    "date_production": "2024-02-01T08:00:00Z",
    "quantite_produite": 75.5,
    "operateur": "Marie Martin",
    "notes": "Production prioritaire"
}
```

---

## 📊 Gestion du Stock

### Lister les matières premières
```http
GET /api/v1/matieres-premieres/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "nom": "Ciment Portland",
            "unite": "tonne",
            "stock_actuel": 150.0,
            "stock_minimum": 50.0,
            "statut_stock": "normal",
            "prix_unitaire": 85.00
        },
        {
            "id": 2,
            "nom": "Sable",
            "unite": "m3",
            "stock_actuel": 25.0,
            "stock_minimum": 30.0,
            "statut_stock": "critique",
            "prix_unitaire": 25.00
        }
    ]
}
```

### Mettre à jour le stock
```http
PATCH /api/v1/matieres-premieres/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
    "stock_actuel": 200.0
}
```

### Lister les approvisionnements
```http
GET /api/v1/approvisionnements/
Authorization: Bearer <token>
```

### Créer un approvisionnement
```http
POST /api/v1/approvisionnements/
Authorization: Bearer <token>
Content-Type: application/json

{
    "matiere_premiere": 1,
    "quantite": 100.0,
    "fournisseur": "Fournisseur ABC",
    "prix_unitaire": 85.00,
    "date": "2024-02-01T10:00:00Z"
}
```

---

## ⛽ Gestion du Carburant

### Lister les consommations de carburant
```http
GET /api/v1/carburant/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "count": 20,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "vehicule": "Camion-Toupie 01",
            "quantite": 45.5,
            "prix_unitaire": 1.65,
            "cout_total": 75.08,
            "date": "2024-01-20T14:30:00Z",
            "kilometrage": 125000
        }
    ]
}
```

### Enregistrer une consommation
```http
POST /api/v1/carburant/
Authorization: Bearer <token>
Content-Type: application/json

{
    "vehicule": "Camion-Toupie 02",
    "quantite": 52.0,
    "prix_unitaire": 1.68,
    "kilometrage": 98500
}
```

---

## 💰 Gestion des Factures

### Lister toutes les factures
```http
GET /api/v1/factures/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "numero_facture": "FACT-2024-001",
            "commande": {
                "id": 1,
                "numero_commande": "CMD-2024-001",
                "client": {
                    "nom": "Entreprise ABC"
                }
            },
            "date_emission": "2024-01-25T16:00:00Z",
            "date_echeance": "2024-02-25T16:00:00Z",
            "montant_ht": 5000.00,
            "tva": 1000.00,
            "montant_ttc": 6000.00,
            "statut": "emise"
        }
    ]
}
```

### Créer une facture
```http
POST /api/v1/factures/
Authorization: Bearer <token>
Content-Type: application/json

{
    "commande": 1,
    "date_echeance": "2024-03-01T16:00:00Z",
    "taux_tva": 20.0
}
```

---

## 📈 Statistiques du Tableau de Bord

### Obtenir les statistiques générales
```http
GET /api/v1/dashboard/stats/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "commandes_total": 45,
    "commandes_en_cours": 12,
    "production_mensuelle": 1250.5,
    "chiffre_affaires_mensuel": 156750.00,
    "stock_critique": 3,
    "consommation_carburant_mensuelle": 2450.75
}
```

### Obtenir les statistiques de production
```http
GET /api/v1/dashboard/production/
Authorization: Bearer <token>
```

**Réponse:**
```json
{
    "production_quotidienne": [
        {
            "date": "2024-01-20",
            "quantite": 125.5
        },
        {
            "date": "2024-01-21",
            "quantite": 98.0
        }
    ],
    "production_par_type": [
        {
            "type_beton": "C25/30",
            "quantite_totale": 450.0
        },
        {
            "type_beton": "C30/37",
            "quantite_totale": 320.5
        }
    ]
}
```

---

## 🔍 Fonctionnalités Avancées

### Pagination
Tous les endpoints de liste supportent la pagination :
- `page`: Numéro de page (défaut: 1)
- `page_size`: Nombre d'éléments par page (défaut: 20, max: 100)

**Exemple:**
```http
GET /api/v1/commandes/?page=2&page_size=10
Authorization: Bearer <token>
```

### Filtrage et Recherche
La plupart des endpoints supportent le filtrage :
- Filtres par champs exacts
- Recherche textuelle sur certains champs
- Filtres par date (date, date__gte, date__lte)

**Exemples:**
```http
GET /api/v1/clients/?search=ABC
GET /api/v1/commandes/?date_commande__gte=2024-01-01&date_commande__lte=2024-01-31
GET /api/v1/ordres-production/?statut=termine
```

### Tri
Utilisez le paramètre `ordering` pour trier les résultats :
```http
GET /api/v1/commandes/?ordering=-date_commande
GET /api/v1/factures/?ordering=date_echeance,montant_ttc
```

---

## 🚨 Gestion des Erreurs

### Codes de statut HTTP
- `200 OK`: Succès
- `201 Created`: Ressource créée
- `400 Bad Request`: Données invalides
- `401 Unauthorized`: Token manquant ou invalide
- `403 Forbidden`: Permissions insuffisantes
- `404 Not Found`: Ressource non trouvée
- `500 Internal Server Error`: Erreur serveur

### Format des erreurs
```json
{
    "detail": "Description de l'erreur",
    "field_errors": {
        "nom": ["Ce champ est requis."],
        "email": ["Entrez une adresse email valide."]
    }
}
```

---

## 🔒 Sécurité

### Authentification JWT
- Tokens d'accès valides 60 minutes
- Tokens de rafraîchissement valides 7 jours
- Rotation automatique des tokens

### Permissions
- Authentification requise pour tous les endpoints
- Permissions basées sur les rôles utilisateur
- Validation des données côté serveur

### CORS
- Configuration CORS pour les applications web
- Headers de sécurité appropriés

---

## 📱 Intégration Android

### Configuration Retrofit
```kotlin
// Intercepteur pour l'authentification
class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${tokenManager.getAccessToken()}")
            .build()
        return chain.proceed(request)
    }
}

// Configuration Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl("https://beton-project.onrender.com/api/v1/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(
        OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(tokenManager))
            .build()
    )
    .build()
```

### Modèles de données Kotlin
```kotlin
data class Client(
    val id: Int,
    val nom: String,
    val adresse: String,
    val telephone: String,
    val email: String,
    val date_creation: String
)

data class Commande(
    val id: Int,
    val numero_commande: String,
    val client: Client,
    val type_beton: String,
    val quantite: Double,
    val statut: String,
    val prix_total: Double
)
```

---

## 🚀 Déploiement

### URL de Production
```
https://beton-project.onrender.com/api/v1/
```

### Variables d'Environnement
- `SECRET_KEY`: Clé secrète Django
- `DEBUG`: Mode debug (False en production)
- `DATABASE_URL`: URL de la base de données PostgreSQL
- `ALLOWED_HOSTS`: Domaines autorisés

---

## 📞 Support

Pour toute question ou problème avec l'API :
1. Vérifiez cette documentation
2. Consultez les logs d'erreur
3. Testez avec l'interface de navigation Django REST Framework
4. Contactez l'équipe de développement

---

**Version de l'API**: 1.0  
**Dernière mise à jour**: Janvier 2024  
**Framework**: Django REST Framework 3.15.2