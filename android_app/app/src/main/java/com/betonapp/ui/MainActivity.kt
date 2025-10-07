package com.betonapp.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import androidx.activity.viewModels
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.betonapp.R
import com.betonapp.databinding.ActivityMainBinding
import com.betonapp.ui.auth.LoginActivity
import com.betonapp.utils.BetonNotificationManager
import com.betonapp.services.NotificationWorker
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Activité principale de l'application
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()
    private val requestNotificationPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                // Notification pour confirmer que les notifications sont activées
                BetonNotificationManager(this).showGeneralNotification(
                    title = getString(R.string.app_name),
                    message = "Notifications activées"
                )
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupToolbar()
        setupNavigation()
        setupNotifications()
        checkAuthenticationState()
        // Éviter la redirection immédiate avant que l'état d'auth soit émis
        observeViewModel()
    }

    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
    }

    private fun setupNavigation() {
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController
        
        // Configuration des destinations de niveau supérieur
        val appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.dashboardFragment,
                R.id.ordersFragment,
                R.id.productionFragment,
                R.id.inventoryFragment
            )
        )
        
        setupActionBarWithNavController(navController, appBarConfiguration)
        binding.bottomNavigation.setupWithNavController(navController)
        
        // Configuration du FAB
        // Dans la méthode onCreate ou autre méthode où fab est référencé
        // Supprimer ou commenter la ligne qui fait référence à fab
        // fab.setOnClickListener { ... }
    }

    private fun setupNotifications() {
        // Initialiser le gestionnaire de notifications
        val notificationManager = BetonNotificationManager(this)
        
        // Demander la permission de notifications sur Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val granted = ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
            if (!granted) {
                requestNotificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        // Programmer les vérifications périodiques de notifications
        NotificationWorker.schedulePeriodicWork(this)
        // Déclenchement immédiat pour vérifier le bon fonctionnement
        NotificationWorker.runOnceNow(this)
    }

    private fun checkAuthenticationState() {
        viewModel.checkAuthState()
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                if (!state.isAuthenticated && !state.isLoading) {
                    navigateToLogin()
                }
            }
        }
    }

    private fun navigateToLogin() {
        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_search -> {
                // TODO: Implémenter la recherche
                true
            }
            R.id.action_notifications -> {
                val navHostFragment = supportFragmentManager
                    .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
                val navController = navHostFragment.navController
                navController.navigate(R.id.notificationsFragment)
                true
            }
            R.id.action_settings -> {
                // TODO: Ouvrir les paramètres
                true
            }
            R.id.action_logout -> {
                viewModel.logout()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
}
