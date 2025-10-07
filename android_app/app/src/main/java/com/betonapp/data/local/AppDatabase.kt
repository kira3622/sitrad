package com.betonapp.data.local

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import android.content.Context
import com.betonapp.data.local.dao.NotificationDao
import com.betonapp.data.local.entities.NotificationEntity

/**
 * Base de données Room principale de l'application
 */
@Database(
    entities = [NotificationEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    
    abstract fun notificationDao(): NotificationDao
    
    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null
        
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "betonapp_database"
                )
                .fallbackToDestructiveMigration() // Pour le développement
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}