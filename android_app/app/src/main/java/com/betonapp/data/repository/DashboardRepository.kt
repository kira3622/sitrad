package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.DashboardStats
import com.betonapp.data.models.ProductionStats
import com.betonapp.data.models.ProductionQuotidienne
import com.betonapp.data.models.ProductionParType
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DashboardRepository @Inject constructor(
    private val apiService: ApiService
) {
    
    suspend fun getDashboardStats(): DashboardStats {
        return apiService.getDashboardStats().body() ?: DashboardStats(
            commandesTotal = 0,
            commandesEnCours = 0,
            productionMensuelle = 0.0,
            chiffreAffairesMensuel = 0.0,
            stockCritique = 0,
            consommationCarburantMensuelle = 0.0
        )
    }
    
    suspend fun getProductionStats(): ProductionStats {
        return apiService.getProductionStats().body() ?: ProductionStats(
            productionQuotidienne = emptyList<ProductionQuotidienne>(),
            productionParType = emptyList<ProductionParType>()
        )
    }
}