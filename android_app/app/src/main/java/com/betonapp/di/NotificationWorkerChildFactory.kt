package com.betonapp.di

import android.content.Context
import androidx.work.ListenableWorker
import androidx.work.WorkerParameters
import com.betonapp.services.NotificationWorker
import javax.inject.Inject

/**
 * Adapte l'AssistedFactory du NotificationWorker vers l'interface ChildWorkerFactory utilisée par HiltWorkerFactory.
 */
class NotificationWorkerChildFactory @Inject constructor(
    private val assistedFactory: NotificationWorker.Factory
) : ChildWorkerFactory {
    override fun create(appContext: Context, params: WorkerParameters): ListenableWorker {
        return assistedFactory.create(appContext, params)
    }
}