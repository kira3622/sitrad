package com.betonapp.di

import androidx.work.ListenableWorker
import com.betonapp.services.NotificationWorker
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import dagger.multibindings.IntoMap

@Module
@InstallIn(SingletonComponent::class)
abstract class WorkerModule {

    @Binds
    @IntoMap
    @WorkerKey(NotificationWorker::class)
    abstract fun bindNotificationWorker(factory: NotificationWorkerChildFactory): ChildWorkerFactory
}