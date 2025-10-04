package com.betonapp.di

import com.betonapp.data.api.ApiService
import com.betonapp.data.local.TokenManager
import com.betonapp.data.repository.AuthRepository
import com.betonapp.data.repository.DashboardRepository
import com.betonapp.data.repository.InventoryRepository
import com.betonapp.data.repository.OrdersRepository
import com.betonapp.data.repository.ProductionRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    
    @Provides
    @Singleton
    fun provideAuthRepository(
        apiService: ApiService,
        tokenManager: TokenManager
    ): AuthRepository {
        return AuthRepository(apiService, tokenManager)
    }
    
    @Provides
    @Singleton
    fun provideDashboardRepository(
        apiService: ApiService
    ): DashboardRepository {
        return DashboardRepository(apiService)
    }

    @Provides
    @Singleton
    fun provideOrdersRepository(
        apiService: ApiService
    ): OrdersRepository {
        return OrdersRepository(apiService)
    }

    @Provides
    @Singleton
    fun provideProductionRepository(
        apiService: ApiService
    ): ProductionRepository {
        return ProductionRepository(apiService)
    }

    @Provides
    @Singleton
    fun provideInventoryRepository(
        apiService: ApiService
    ): InventoryRepository {
        return InventoryRepository(apiService)
    }
}