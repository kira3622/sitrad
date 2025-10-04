package com.betonapp.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import com.betonapp.data.models.ProductionParType
import com.betonapp.databinding.FragmentDashboardBinding
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.BarData
import com.github.mikephil.charting.data.BarDataSet
import com.github.mikephil.charting.data.BarEntry
import com.github.mikephil.charting.formatter.IndexAxisValueFormatter
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

// Nettoyage: pas d’extension inutile, on manipulera directement la liste

@AndroidEntryPoint
class DashboardFragment : Fragment() {
    
    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: DashboardViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupObservers()
        setupRefreshListener()
        
        // Charger les données initiales
        viewModel.loadDashboardData()
    }
    
    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUI(state)
            }
        }
    }
    
    private fun setupRefreshListener() {
        binding.swipeRefreshLayout.setOnRefreshListener {
            viewModel.loadDashboardData()
        }
    }
    
    private fun updateUI(state: DashboardUiState) {
        binding.swipeRefreshLayout.isRefreshing = state.isLoading

        if (state.error != null) {
            // TODO: Afficher l'erreur
            return
        }

        state.stats?.let { stats ->
            binding.textTotalOrders.text = stats.commandesEnCours.toString()
            binding.textMonthlyProduction.text = stats.productionMensuelle.toString()
            binding.textMonthlyRevenue.text = stats.chiffreAffairesMensuel.toString()
            binding.textCriticalStock.text = stats.stockCritique.toString()
            binding.textFuelConsumption.text = stats.consommationCarburantMensuelle.toString()
        }

        state.productionStats?.let { productionStats ->
            val productionQuotidienne = productionStats.productionQuotidienne.firstOrNull()?.quantite ?: 0.0
            binding.textDailyProduction.text = "$productionQuotidienne m³"

            // Construire les entrées et les labels correctement à partir de la liste
            val entries = productionStats.productionParType
                .mapIndexed { index, item ->
                    BarEntry(index.toFloat(), item.quantiteTotale.toFloat())
                }

            val labels = productionStats.productionParType
                .map { it.typeBeton }

            if (entries.isNotEmpty()) {
                val dataSet = BarDataSet(entries, "Production par Type")
                val barData = BarData(dataSet)
                binding.chartProductionByType.data = barData

                val xAxis = binding.chartProductionByType.xAxis
                xAxis.valueFormatter = IndexAxisValueFormatter(labels)
                xAxis.position = XAxis.XAxisPosition.BOTTOM
                xAxis.granularity = 1f
                xAxis.setDrawGridLines(false)
                xAxis.setLabelCount(labels.size, true)
                xAxis.axisMinimum = -0.5f
                xAxis.axisMaximum = labels.size - 0.5f

                binding.chartProductionByType.setFitBars(true)
                binding.chartProductionByType.invalidate()
            }
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

// Fin de fichier
