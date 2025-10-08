/**
 * Exemple d'intégration Android pour l'API des notifications
 * Sitrad - Système de gestion des notifications
 * 
 * Ce fichier contient des exemples de code Kotlin pour intégrer
 * l'API des notifications dans votre application Android.
 */

// ============================================================================
// 1. DÉPENDANCES GRADLE (app/build.gradle)
// ============================================================================
/*
dependencies {
    // Retrofit pour les appels API
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
    
    // Room pour le cache local
    implementation 'androidx.room:room-runtime:2.5.0'
    implementation 'androidx.room:room-ktx:2.5.0'
    kapt 'androidx.room:room-compiler:2.5.0'
    
    // WorkManager pour la synchronisation
    implementation 'androidx.work:work-runtime-ktx:2.8.1'
    
    // ViewModel et LiveData
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.7.0'
    
    // Jetpack Compose (optionnel)
    implementation 'androidx.compose.ui:ui:1.5.4'
    implementation 'androidx.compose.material3:material3:1.1.2'
}
*/

// ============================================================================
// 2. MODÈLES DE DONNÉES
// ============================================================================

import com.google.gson.annotations.SerializedName
import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "notifications")
data class Notification(
    @PrimaryKey
    val id: Int,
    val title: String,
    val message: String,
    val type: String, // "info", "warning", "error", "success"
    @SerializedName("is_read")
    val isRead: Boolean,
    @SerializedName("created_at")
    val createdAt: String, // Format ISO 8601
    @SerializedName("read_at")
    val readAt: String?, // Peut être null
    val user: Int
)

data class NotificationSummary(
    @SerializedName("total_count")
    val totalCount: Int,
    @SerializedName("unread_count")
    val unreadCount: Int,
    @SerializedName("read_count")
    val readCount: Int
)

data class MarkAsReadRequest(
    @SerializedName("notification_ids")
    val notificationIds: List<Int>
)

data class ApiResponse<T>(
    val count: Int,
    val next: String?,
    val previous: String?,
    val results: List<T>
)

data class AuthResponse(
    val access: String,
    val refresh: String
)

data class AuthRequest(
    val username: String,
    val password: String
)

// ============================================================================
// 3. INTERFACE API RETROFIT
// ============================================================================

import retrofit2.Response
import retrofit2.http.*

interface NotificationApiService {
    
    @POST("auth/token/")
    suspend fun login(@Body request: AuthRequest): Response<AuthResponse>
    
    @POST("auth/token/refresh/")
    suspend fun refreshToken(@Body refreshToken: Map<String, String>): Response<AuthResponse>
    
    @GET("notifications/")
    suspend fun getNotifications(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20,
        @Query("is_read") isRead: Boolean? = null,
        @Query("type") type: String? = null
    ): Response<ApiResponse<Notification>>
    
    @GET("notifications/{id}/")
    suspend fun getNotification(@Path("id") id: Int): Response<Notification>
    
    @GET("notifications/unread_count/")
    suspend fun getUnreadCount(): Response<Map<String, Int>>
    
    @GET("notifications/summary/")
    suspend fun getSummary(): Response<NotificationSummary>
    
    @POST("notifications/mark_as_read/")
    suspend fun markAsRead(@Body request: MarkAsReadRequest): Response<Map<String, String>>
    
    @POST("notifications/mark_all_as_read/")
    suspend fun markAllAsRead(): Response<Map<String, String>>
    
    @POST("notifications/{id}/mark_as_read/")
    suspend fun markSingleAsRead(@Path("id") id: Int): Response<Map<String, String>>
    
    @DELETE("notifications/{id}/")
    suspend fun deleteNotification(@Path("id") id: Int): Response<Unit>
}

// ============================================================================
// 4. INTERCEPTEUR D'AUTHENTIFICATION
// ============================================================================

import okhttp3.Interceptor
import okhttp3.Response
import android.content.SharedPreferences

class AuthInterceptor(private val sharedPreferences: SharedPreferences) : Interceptor {
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Récupérer le token d'accès
        val accessToken = sharedPreferences.getString("access_token", null)
        
        // Ajouter l'en-tête d'autorisation si le token existe
        val newRequest = if (accessToken != null) {
            originalRequest.newBuilder()
                .header("Authorization", "Bearer $accessToken")
                .build()
        } else {
            originalRequest
        }
        
        return chain.proceed(newRequest)
    }
}

// ============================================================================
// 5. CONFIGURATION RETROFIT
// ============================================================================

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor

object ApiClient {
    
    private const val BASE_URL = "https://sitrad-web.onrender.com/api/v1/"
    
    fun createApiService(sharedPreferences: SharedPreferences): NotificationApiService {
        
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        val authInterceptor = AuthInterceptor(sharedPreferences)
        
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .build()
        
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        
        return retrofit.create(NotificationApiService::class.java)
    }
}

// ============================================================================
// 6. BASE DE DONNÉES ROOM
// ============================================================================

import androidx.room.*

@Dao
interface NotificationDao {
    
    @Query("SELECT * FROM notifications ORDER BY created_at DESC")
    suspend fun getAllNotifications(): List<Notification>
    
    @Query("SELECT * FROM notifications WHERE isRead = 0 ORDER BY created_at DESC")
    suspend fun getUnreadNotifications(): List<Notification>
    
    @Query("SELECT COUNT(*) FROM notifications WHERE isRead = 0")
    suspend fun getUnreadCount(): Int
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertNotifications(notifications: List<Notification>)
    
    @Update
    suspend fun updateNotification(notification: Notification)
    
    @Query("UPDATE notifications SET isRead = 1 WHERE id = :id")
    suspend fun markAsRead(id: Int)
    
    @Query("UPDATE notifications SET isRead = 1")
    suspend fun markAllAsRead()
    
    @Query("DELETE FROM notifications WHERE id = :id")
    suspend fun deleteNotification(id: Int)
    
    @Query("DELETE FROM notifications")
    suspend fun clearAll()
}

@Database(
    entities = [Notification::class],
    version = 1,
    exportSchema = false
)
abstract class NotificationDatabase : RoomDatabase() {
    abstract fun notificationDao(): NotificationDao
    
    companion object {
        @Volatile
        private var INSTANCE: NotificationDatabase? = null
        
        fun getDatabase(context: Context): NotificationDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    NotificationDatabase::class.java,
                    "notification_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}

// ============================================================================
// 7. REPOSITORY PATTERN
// ============================================================================

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import android.content.Context

class NotificationRepository(
    private val apiService: NotificationApiService,
    private val notificationDao: NotificationDao,
    private val context: Context
) {
    
    fun getNotifications(forceRefresh: Boolean = false): Flow<List<Notification>> = flow {
        try {
            // Émettre d'abord les données en cache
            if (!forceRefresh) {
                val cachedNotifications = notificationDao.getAllNotifications()
                emit(cachedNotifications)
            }
            
            // Récupérer les données depuis l'API
            val response = apiService.getNotifications()
            if (response.isSuccessful) {
                response.body()?.results?.let { notifications ->
                    // Mettre à jour le cache
                    notificationDao.insertNotifications(notifications)
                    // Émettre les nouvelles données
                    emit(notifications)
                }
            }
        } catch (e: Exception) {
            // En cas d'erreur, émettre les données en cache
            val cachedNotifications = notificationDao.getAllNotifications()
            emit(cachedNotifications)
        }
    }
    
    suspend fun getUnreadCount(): Int {
        return try {
            val response = apiService.getUnreadCount()
            if (response.isSuccessful) {
                response.body()?.get("unread_count") ?: 0
            } else {
                notificationDao.getUnreadCount()
            }
        } catch (e: Exception) {
            notificationDao.getUnreadCount()
        }
    }
    
    suspend fun markAsRead(notificationId: Int): Boolean {
        return try {
            val response = apiService.markSingleAsRead(notificationId)
            if (response.isSuccessful) {
                notificationDao.markAsRead(notificationId)
                true
            } else {
                false
            }
        } catch (e: Exception) {
            false
        }
    }
    
    suspend fun markAllAsRead(): Boolean {
        return try {
            val response = apiService.markAllAsRead()
            if (response.isSuccessful) {
                notificationDao.markAllAsRead()
                true
            } else {
                false
            }
        } catch (e: Exception) {
            false
        }
    }
}

// ============================================================================
// 8. VIEWMODEL
// ============================================================================

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class NotificationViewModel(
    private val repository: NotificationRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(NotificationUiState())
    val uiState: StateFlow<NotificationUiState> = _uiState.asStateFlow()
    
    init {
        loadNotifications()
    }
    
    fun loadNotifications(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            repository.getNotifications(forceRefresh)
                .catch { exception ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = exception.message
                    )
                }
                .collect { notifications ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        notifications = notifications,
                        error = null
                    )
                }
        }
    }
    
    fun markAsRead(notificationId: Int) {
        viewModelScope.launch {
            val success = repository.markAsRead(notificationId)
            if (success) {
                loadNotifications()
            }
        }
    }
    
    fun markAllAsRead() {
        viewModelScope.launch {
            val success = repository.markAllAsRead()
            if (success) {
                loadNotifications()
            }
        }
    }
    
    fun refresh() {
        loadNotifications(forceRefresh = true)
    }
}

data class NotificationUiState(
    val isLoading: Boolean = false,
    val notifications: List<Notification> = emptyList(),
    val error: String? = null
)

// ============================================================================
// 9. INTERFACE UTILISATEUR JETPACK COMPOSE
// ============================================================================

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationScreen(
    viewModel: NotificationViewModel
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Barre d'actions
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Button(
                onClick = { viewModel.refresh() }
            ) {
                Text("Actualiser")
            }
            
            Button(
                onClick = { viewModel.markAllAsRead() }
            ) {
                Text("Tout marquer comme lu")
            }
        }
        
        // Contenu principal
        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            
            uiState.error != null -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "Erreur: ${uiState.error}",
                        color = MaterialTheme.colorScheme.error
                    )
                }
            }
            
            else -> {
                LazyColumn {
                    items(uiState.notifications) { notification ->
                        NotificationItem(
                            notification = notification,
                            onMarkAsRead = { viewModel.markAsRead(notification.id) }
                        )
                    }
                }
            }
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
            .padding(horizontal = 16.dp, vertical = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (notification.isRead) {
                MaterialTheme.colorScheme.surface
            } else {
                MaterialTheme.colorScheme.primaryContainer
            }
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = notification.title,
                style = MaterialTheme.typography.titleMedium
            )
            
            Text(
                text = notification.message,
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(vertical = 4.dp)
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = notification.type.uppercase(),
                    style = MaterialTheme.typography.labelSmall
                )
                
                if (!notification.isRead) {
                    TextButton(onClick = onMarkAsRead) {
                        Text("Marquer comme lu")
                    }
                }
            }
        }
    }
}

// ============================================================================
// 10. WORKMANAGER POUR LA SYNCHRONISATION
// ============================================================================

import androidx.work.*
import java.util.concurrent.TimeUnit

class NotificationSyncWorker(
    context: Context,
    params: WorkerParameters,
    private val repository: NotificationRepository
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            // Synchroniser les notifications
            repository.getNotifications(forceRefresh = true)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
    
    companion object {
        fun schedulePeriodicSync(context: Context) {
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
    }
}

// ============================================================================
// UTILISATION DANS L'APPLICATION
// ============================================================================

/*
class MainActivity : ComponentActivity() {
    
    private lateinit var viewModel: NotificationViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialiser les dépendances
        val sharedPreferences = getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        val apiService = ApiClient.createApiService(sharedPreferences)
        val database = NotificationDatabase.getDatabase(this)
        val repository = NotificationRepository(apiService, database.notificationDao(), this)
        
        viewModel = NotificationViewModel(repository)
        
        // Programmer la synchronisation périodique
        NotificationSyncWorker.schedulePeriodicSync(this)
        
        setContent {
            MaterialTheme {
                NotificationScreen(viewModel)
            }
        }
    }
}
*/