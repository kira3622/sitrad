# API des Notifications - Documentation

## Vue d'ensemble

L'API des notifications permet de gérer les notifications dans l'application de gestion de béton. Elle fournit des endpoints pour créer, lire, marquer comme lues et supprimer les notifications.

**Base URL:** `http://localhost:8000/api/v1/notifications/`

## Authentification

Tous les endpoints nécessitent une authentification JWT. Incluez le token dans l'en-tête de la requête :

```
Authorization: Bearer <votre_token_jwt>
```

## Modèle de données

### Notification

```json
{
    "id": 1,
    "title": "Titre de la notification",
    "message": "Message détaillé de la notification",
    "type": "NEW_ORDER",
    "priority": "high",
    "timestamp": 1759830664101,
    "is_read": false,
    "user": 7,
    "related_object_id": null,
    "related_object_type": null
}
```

### Champs

- **id** (integer): Identifiant unique de la notification
- **title** (string): Titre de la notification (max 255 caractères)
- **message** (string): Message détaillé
- **type** (string): Type de notification
  - `NEW_ORDER`: Nouvelle commande
  - `PRODUCTION_UPDATE`: Mise à jour de production
  - `LOW_INVENTORY`: Stock faible
  - `DELIVERY`: Livraison
  - `GENERAL`: Général
- **priority** (string): Priorité de la notification
  - `low`: Faible
  - `normal`: Normal
  - `high`: Élevé
  - `urgent`: Urgent
- **timestamp** (integer): Timestamp Unix en millisecondes
- **is_read** (boolean): Statut de lecture
- **user** (integer): ID de l'utilisateur destinataire
- **related_object_id** (integer, nullable): ID de l'objet lié
- **related_object_type** (string, nullable): Type de l'objet lié

## Endpoints

### 1. Lister les notifications

**GET** `/api/v1/notifications/`

Récupère la liste paginée des notifications de l'utilisateur connecté.

#### Paramètres de requête (optionnels)

- `type`: Filtrer par type de notification
- `is_read`: Filtrer par statut de lecture (`true`/`false`)
- `page`: Numéro de page pour la pagination
- `page_size`: Nombre d'éléments par page

#### Exemple de requête

```bash
GET /api/v1/notifications/?type=NEW_ORDER&is_read=false&page=1&page_size=10
```

#### Réponse

```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Nouvelle commande",
            "message": "Une nouvelle commande de béton a été reçue",
            "type": "NEW_ORDER",
            "priority": "high",
            "timestamp": 1759830664101,
            "is_read": false,
            "user": 7,
            "related_object_id": null,
            "related_object_type": null
        }
    ]
}
```

### 2. Créer une notification

**POST** `/api/v1/notifications/`

Crée une nouvelle notification.

#### Corps de la requête

```json
{
    "title": "Titre de la notification",
    "message": "Message de la notification",
    "type": "NEW_ORDER",
    "priority": "high",
    "user": 7,
    "related_object_id": 123,
    "related_object_type": "Order"
}
```

#### Réponse

```json
{
    "id": 5,
    "title": "Titre de la notification",
    "message": "Message de la notification",
    "type": "NEW_ORDER",
    "priority": "high",
    "timestamp": 1759830664200,
    "is_read": false,
    "user": 7,
    "related_object_id": 123,
    "related_object_type": "Order"
}
```

### 3. Récupérer une notification spécifique

**GET** `/api/v1/notifications/{id}/`

Récupère les détails d'une notification spécifique.

#### Réponse

```json
{
    "id": 1,
    "title": "Nouvelle commande",
    "message": "Une nouvelle commande de béton a été reçue",
    "type": "NEW_ORDER",
    "priority": "high",
    "timestamp": 1759830664101,
    "is_read": false,
    "user": 7,
    "related_object_id": null,
    "related_object_type": null
}
```

### 4. Supprimer une notification

**DELETE** `/api/v1/notifications/{id}/`

Supprime une notification spécifique.

#### Réponse

```
Status: 204 No Content
```

### 5. Résumé des notifications

**GET** `/api/v1/notifications/summary/`

Récupère un résumé des notifications de l'utilisateur.

#### Réponse

```json
{
    "total_count": 4,
    "unread_count": 3,
    "new_orders_count": 1,
    "production_updates_count": 1,
    "low_inventory_count": 1,
    "delivery_count": 1
}
```

### 6. Marquer une notification comme lue

**POST** `/api/v1/notifications/{id}/mark_as_read/`

Marque une notification spécifique comme lue.

#### Réponse

```json
{
    "id": 1,
    "title": "Nouvelle commande",
    "message": "Une nouvelle commande de béton a été reçue",
    "type": "NEW_ORDER",
    "priority": "high",
    "timestamp": 1759830664101,
    "is_read": true,
    "user": 7,
    "related_object_id": null,
    "related_object_type": null
}
```

### 7. Marquer plusieurs notifications comme lues

**POST** `/api/v1/notifications/mark_all_as_read/`

Marque plusieurs notifications comme lues.

#### Corps de la requête

Option 1 - Marquer toutes les notifications comme lues :
```json
{
    "mark_all": true
}
```

Option 2 - Marquer des notifications spécifiques comme lues :
```json
{
    "notification_ids": [1, 2, 3]
}
```

#### Réponse

```json
{
    "message": "3 notifications marquées comme lues",
    "updated_count": 3
}
```

### 8. Supprimer les notifications lues

**DELETE** `/api/v1/notifications/delete_read/`

Supprime toutes les notifications marquées comme lues.

#### Réponse

```json
{
    "message": "2 notifications supprimées",
    "deleted_count": 2
}
```

## Codes d'erreur

- **200**: Succès
- **201**: Créé avec succès
- **204**: Supprimé avec succès
- **400**: Requête invalide
- **401**: Non authentifié
- **403**: Accès interdit
- **404**: Ressource non trouvée
- **500**: Erreur serveur

## Exemples d'intégration Android

### Configuration du client HTTP (Retrofit)

```kotlin
interface NotificationApiService {
    @GET("notifications/")
    suspend fun getNotifications(
        @Query("type") type: String? = null,
        @Query("is_read") isRead: Boolean? = null,
        @Query("page") page: Int? = null
    ): Response<NotificationListResponse>
    
    @GET("notifications/summary/")
    suspend fun getNotificationsSummary(): Response<NotificationSummary>
    
    @POST("notifications/{id}/mark_as_read/")
    suspend fun markNotificationAsRead(@Path("id") id: Int): Response<Notification>
    
    @POST("notifications/mark_all_as_read/")
    suspend fun markAllNotificationsAsRead(@Body request: MarkAsReadRequest): Response<MarkAsReadResponse>
    
    @DELETE("notifications/{id}/")
    suspend fun deleteNotification(@Path("id") id: Int): Response<Unit>
}
```

### Modèles de données Kotlin

```kotlin
data class Notification(
    val id: Int,
    val title: String,
    val message: String,
    val type: String,
    val priority: String,
    val timestamp: Long,
    val isRead: Boolean,
    val user: Int,
    val relatedObjectId: Int?,
    val relatedObjectType: String?
)

data class NotificationSummary(
    val totalCount: Int,
    val unreadCount: Int,
    val newOrdersCount: Int,
    val productionUpdatesCount: Int,
    val lowInventoryCount: Int,
    val deliveryCount: Int
)

data class MarkAsReadRequest(
    val markAll: Boolean? = null,
    val notificationIds: List<Int>? = null
)
```

## Notes importantes

1. **Timestamp**: Le timestamp est fourni en millisecondes Unix pour faciliter la conversion en Android
2. **Pagination**: L'API utilise la pagination par défaut de Django REST Framework
3. **Filtrage**: Les notifications sont automatiquement filtrées par utilisateur connecté
4. **Permissions**: Seul l'utilisateur propriétaire peut accéder à ses notifications
5. **Tri**: Les notifications sont triées par date de création (plus récentes en premier)

## Support

Pour toute question ou problème avec l'API, contactez l'équipe backend.