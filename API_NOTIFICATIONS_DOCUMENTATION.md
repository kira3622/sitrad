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

## 📱 Guide d'Intégration Android Complet

### 🚀 Statut : API Prête pour l'Intégration

L'API des notifications est **entièrement fonctionnelle** et déployée en production sur Render.

**URL de production :** `https://sitrad-web.onrender.com/api/v1/notifications/`

### 🔐 Configuration de l'Authentification

#### 1. Obtenir un Token JWT
```kotlin
// Service d'authentification
class AuthService {
    suspend fun login(username: String, password: String): AuthResponse {
        val response = apiService.login(LoginRequest(username, password))
        if (response.isSuccessful) {
            val authResponse = response.body()!!
            // Sauvegarder le token
            tokenManager.saveTokens(authResponse.access, authResponse.refresh)
            return authResponse
        } else {
            throw Exception("Erreur d'authentification")
        }
    }
}
```

#### 2. Intercepteur pour l'Authentification
```kotlin
class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val token = tokenManager.getAccessToken()
        
        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()
            
        return chain.proceed(authenticatedRequest)
    }
}
```

### 🏗️ Architecture Recommandée

#### 1. Repository Pattern
```kotlin
class NotificationRepository(
    private val apiService: NotificationApiService,
    private val notificationDao: NotificationDao
) {
    suspend fun getNotifications(refresh: Boolean = false): Flow<List<Notification>> {
        return if (refresh) {
            refreshNotifications()
            notificationDao.getAllNotifications()
        } else {
            notificationDao.getAllNotifications()
        }
    }
    
    private suspend fun refreshNotifications() {
        try {
            val response = apiService.getNotifications()
            if (response.isSuccessful) {
                val notifications = response.body()?.results ?: emptyList()
                notificationDao.insertAll(notifications.map { it.toEntity() })
            }
        } catch (e: Exception) {
            // Gérer l'erreur
        }
    }
    
    suspend fun markAsRead(notificationId: Int) {
        try {
            val response = apiService.markNotificationAsRead(notificationId)
            if (response.isSuccessful) {
                notificationDao.markAsRead(notificationId)
            }
        } catch (e: Exception) {
            // Gérer l'erreur
        }
    }
}
```

#### 2. ViewModel avec StateFlow
```kotlin
class NotificationsViewModel(
    private val repository: NotificationRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(NotificationsUiState())
    val uiState: StateFlow<NotificationsUiState> = _uiState.asStateFlow()
    
    init {
        loadNotifications()
    }
    
    fun loadNotifications(refresh: Boolean = false) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            repository.getNotifications(refresh).collect { notifications ->
                _uiState.value = _uiState.value.copy(
                    notifications = notifications,
                    isLoading = false,
                    unreadCount = notifications.count { !it.isRead }
                )
            }
        }
    }
    
    fun markAsRead(notificationId: Int) {
        viewModelScope.launch {
            repository.markAsRead(notificationId)
        }
    }
}

data class NotificationsUiState(
    val notifications: List<Notification> = emptyList(),
    val isLoading: Boolean = false,
    val unreadCount: Int = 0,
    val error: String? = null
)
```

### 🎨 Interface Utilisateur

#### 1. Composable Jetpack Compose
```kotlin
@Composable
fun NotificationsScreen(
    viewModel: NotificationsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LazyColumn {
        items(uiState.notifications) { notification ->
            NotificationItem(
                notification = notification,
                onMarkAsRead = { viewModel.markAsRead(notification.id) }
            )
        }
    }
}

@Composable
fun NotificationItem(
    notification: Notification,
    onMarkAsRead: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable { if (!notification.isRead) onMarkAsRead() },
        backgroundColor = if (notification.isRead) 
            MaterialTheme.colors.surface 
        else 
            MaterialTheme.colors.primary.copy(alpha = 0.1f)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = notification.title,
                    style = MaterialTheme.typography.h6,
                    fontWeight = if (notification.isRead) 
                        FontWeight.Normal 
                    else 
                        FontWeight.Bold
                )
                
                NotificationTypeIcon(type = notification.type)
            }
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = notification.message,
                style = MaterialTheme.typography.body2
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = formatTimestamp(notification.timestamp),
                style = MaterialTheme.typography.caption,
                color = MaterialTheme.colors.onSurface.copy(alpha = 0.6f)
            )
        }
    }
}
```

#### 2. Icônes par Type
```kotlin
@Composable
fun NotificationTypeIcon(type: String) {
    val (icon, color) = when (type) {
        "info" -> Icons.Default.Info to Color.Blue
        "warning" -> Icons.Default.Warning to Color.Orange
        "error" -> Icons.Default.Error to Color.Red
        "success" -> Icons.Default.CheckCircle to Color.Green
        else -> Icons.Default.Notifications to Color.Gray
    }
    
    Icon(
        imageVector = icon,
        contentDescription = type,
        tint = color
    )
}
```

### 🔄 Synchronisation en Temps Réel

#### 1. WorkManager pour la Synchronisation Périodique
```kotlin
class NotificationSyncWorker(
    context: Context,
    params: WorkerParameters,
    private val repository: NotificationRepository
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            repository.syncNotifications()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Planifier la synchronisation
fun scheduleNotificationSync(context: Context) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()
    
    val syncRequest = PeriodicWorkRequestBuilder<NotificationSyncWorker>(
        15, TimeUnit.MINUTES
    )
        .setConstraints(constraints)
        .build()
    
    WorkManager.getInstance(context)
        .enqueueUniquePeriodicWork(
            "notification_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            syncRequest
        )
}
```

### 🔔 Notifications Push (Optionnel)

#### 1. Configuration Firebase
```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)
        
        // Traiter la notification push
        val title = remoteMessage.notification?.title ?: ""
        val body = remoteMessage.notification?.body ?: ""
        
        showNotification(title, body)
        
        // Synchroniser les notifications depuis l'API
        syncNotifications()
    }
    
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // Envoyer le token au backend
        sendTokenToServer(token)
    }
}
```

### 🧪 Tests

#### 1. Tests Unitaires
```kotlin
@Test
fun `test notification repository returns cached data when offline`() = runTest {
    // Arrange
    val cachedNotifications = listOf(
        createTestNotification(id = 1, title = "Test 1"),
        createTestNotification(id = 2, title = "Test 2")
    )
    notificationDao.insertAll(cachedNotifications)
    
    // Act
    val result = repository.getNotifications(refresh = false).first()
    
    // Assert
    assertEquals(2, result.size)
    assertEquals("Test 1", result[0].title)
}
```

#### 2. Tests d'Intégration
```kotlin
@Test
fun `test mark notification as read updates local and remote`() = runTest {
    // Test de l'intégration complète
}
```

### 📊 Métriques et Analytics

```kotlin
class NotificationAnalytics {
    fun trackNotificationReceived(type: String) {
        // Firebase Analytics ou autre
    }
    
    fun trackNotificationRead(notificationId: Int) {
        // Tracker les lectures
    }
    
    fun trackNotificationAction(action: String) {
        // Tracker les actions utilisateur
    }
}
```

### ⚡ Optimisations de Performance

1. **Pagination** : Charger les notifications par pages
2. **Cache** : Utiliser Room pour le cache local
3. **Images** : Lazy loading pour les avatars/icônes
4. **Debouncing** : Pour les actions utilisateur répétées

### 🔧 Configuration Gradle

```kotlin
// app/build.gradle
dependencies {
    implementation "androidx.work:work-runtime-ktx:2.8.1"
    implementation "androidx.room:room-runtime:2.4.3"
    implementation "androidx.room:room-ktx:2.4.3"
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"
    implementation "androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2"
    implementation "androidx.compose.runtime:runtime-livedata:1.5.4"
}
```

## 🎯 Prêt pour l'Intégration

L'API est **entièrement fonctionnelle** et testée en production. Vous pouvez maintenant :

1. ✅ Utiliser tous les endpoints documentés
2. ✅ Implémenter l'authentification JWT
3. ✅ Créer l'interface utilisateur
4. ✅ Configurer la synchronisation
5. ✅ Ajouter les notifications push (optionnel)

**URL de production :** `https://sitrad-web.onrender.com/api/v1/notifications/`

## Support

Pour toute question ou problème avec l'API, contactez l'équipe backend.