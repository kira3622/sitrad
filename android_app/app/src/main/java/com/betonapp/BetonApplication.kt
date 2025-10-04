package com.betonapp

import android.app.Application
import androidx.work.Configuration
import androidx.work.WorkManager
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject
import androidx.hilt.work.HiltWorkerFactory

/**
 * Application principale de l'app Béton
 * Configurée avec Hilt pour l'injection de dépendances
 */
@HiltAndroidApp
class BetonApplication : Application(), Configuration.Provider {

    @Inject
    lateinit var workerFactory: HiltWorkerFactory

    override fun onCreate() {
        super.onCreate()
        // WorkManager s'initialise automatiquement via AndroidX Startup.
        // Comme l'application implémente Configuration.Provider, sa configuration sera utilisée.
    }

    // Remplacer la méthode par une propriété pour être compatible avec les nouvelles versions
    override val workManagerConfiguration: Configuration
        get() = Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()
}