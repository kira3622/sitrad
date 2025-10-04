package com.betonapp.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.betonapp.domain.usecase.GetAuthStateUseCase
import com.betonapp.domain.usecase.IsLoggedInUseCase
import com.betonapp.domain.usecase.LogoutUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel pour l'activité principale
 */
@HiltViewModel
class MainViewModel @Inject constructor(
    private val getAuthStateUseCase: GetAuthStateUseCase,
    private val isLoggedInUseCase: IsLoggedInUseCase,
    private val logoutUseCase: LogoutUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    init {
        observeAuthState()
    }

    fun checkAuthState() {
        viewModelScope.launch {
            val isLoggedIn = isLoggedInUseCase()
            _uiState.value = _uiState.value.copy(
                isAuthenticated = isLoggedIn,
                isLoading = false
            )
        }
    }

    private fun observeAuthState() {
        viewModelScope.launch {
            getAuthStateUseCase().collect { isAuthenticated ->
                _uiState.value = _uiState.value.copy(
                    isAuthenticated = isAuthenticated,
                    isLoading = false
                )
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            logoutUseCase()
            _uiState.value = _uiState.value.copy(
                isAuthenticated = false
            )
        }
    }
}

/**
 * État de l'interface utilisateur pour l'activité principale
 */
data class MainUiState(
    val isAuthenticated: Boolean = false,
    val isLoading: Boolean = true
)

