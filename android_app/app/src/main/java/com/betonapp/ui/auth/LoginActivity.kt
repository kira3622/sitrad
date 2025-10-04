package com.betonapp.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import androidx.lifecycle.lifecycleScope
import com.betonapp.databinding.ActivityLoginBinding
import com.betonapp.ui.MainActivity
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Activité de connexion
 */
@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private val viewModel: LoginViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        binding.apply {
            btnLogin.setOnClickListener {
                val username = etUsername.text.toString().trim()
                val password = etPassword.text.toString().trim()
                viewModel.login(username, password)
            }

            // Masquer l'erreur quand l'utilisateur commence à taper
            etUsername.setOnFocusChangeListener { _, hasFocus ->
                if (hasFocus) viewModel.clearError()
            }
            
            etPassword.setOnFocusChangeListener { _, hasFocus ->
                if (hasFocus) viewModel.clearError()
            }
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUI(state)
            }
        }
    }

    private fun updateUI(state: LoginUiState) {
        binding.apply {
            // Affichage du loading
            progressBar.isVisible = state.isLoading
            btnLogin.isEnabled = !state.isLoading
            btnLogin.text = if (state.isLoading) "Connexion..." else "Se connecter"

            // Affichage des erreurs
            state.error?.let { error ->
                Toast.makeText(this@LoginActivity, error, Toast.LENGTH_LONG).show()
            }

            // Redirection en cas de succès
            if (state.isLoginSuccessful) {
                navigateToMain()
            }
        }
    }

    private fun navigateToMain() {
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}