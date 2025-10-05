package com.betonapp.data.repository

import com.betonapp.data.api.ApiService
import com.betonapp.data.models.FormuleBeton
import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class FormulasRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getFormulas(): List<FormuleBeton> {
        val response = apiService.getFormules()
        return if (response.isSuccessful) {
            val count = response.body()?.results?.size ?: 0
            Log.d("FormulasRepository", "GET /formules => code=${response.code()} count=${count}")
            response.body()?.results ?: emptyList()
        } else {
            Log.e("FormulasRepository", "GET /formules failed => code=${response.code()} message=${response.message()}")
            throw Exception("Erreur ${response.code()}: ${response.message()}")
        }
    }

    suspend fun getFormulaById(id: Int): FormuleBeton? {
        val response = apiService.getFormule(id)
        return if (response.isSuccessful) response.body() else null
    }
}