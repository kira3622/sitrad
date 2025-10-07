package com.betonapp.receivers

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.betonapp.services.NotificationWorker

/**
 * Receiver pour redémarrer les services de notification au démarrage du système
 */
class BootReceiver : BroadcastReceiver() {
    
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Redémarrer le service de notifications périodiques
            NotificationWorker.schedulePeriodicWork(context)
        }
    }
}