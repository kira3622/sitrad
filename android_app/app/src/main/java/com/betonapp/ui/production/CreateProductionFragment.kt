package com.betonapp.ui.production

import android.app.DatePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import androidx.core.widget.addTextChangedListener
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.betonapp.R
import com.betonapp.data.models.ProductionStatus
import com.betonapp.databinding.FragmentCreateProductionBinding
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale

@AndroidEntryPoint
class CreateProductionFragment : Fragment() {

    private var _binding: FragmentCreateProductionBinding? = null
    private val binding get() = _binding!!

    private val viewModel: CreateProductionViewModel by viewModels()
    private val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
    private var selectedDate: Date = Date()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCreateProductionBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupViews()
        observeUiState()
        setupListeners()
        loadCommandes()
    }

    private fun setupViews() {
        // Configuration du dropdown pour les statuts
        val statutOptions = ProductionStatus.values().map { it.displayName }.toTypedArray()
        val statutAdapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_dropdown_item_1line,
            statutOptions
        )
        binding.actvStatut.setAdapter(statutAdapter)
        
        // Statut par défaut
        binding.actvStatut.setText(ProductionStatus.EN_COURS.displayName, false)

        // Date par défaut (aujourd'hui)
        binding.etDateProduction.setText(dateFormat.format(selectedDate))
    }

    private fun setupListeners() {
        // Date picker
        binding.etDateProduction.setOnClickListener {
            showDatePicker()
        }

        // Sélection de commande
        binding.actvCommande.setOnItemClickListener { _, _, position, _ ->
            viewModel.selectCommande(position)
        }

        // Validation de la quantité
        binding.etQuantiteProduite.addTextChangedListener {
            validateQuantity()
        }

        // Boutons d'action
        binding.btnAnnuler.setOnClickListener {
            findNavController().navigateUp()
        }

        binding.btnCreer.setOnClickListener {
            createProduction()
        }
    }

    private fun showDatePicker() {
        val calendar = Calendar.getInstance()
        calendar.time = selectedDate

        DatePickerDialog(
            requireContext(),
            { _, year, month, dayOfMonth ->
                calendar.set(year, month, dayOfMonth)
                selectedDate = calendar.time
                binding.etDateProduction.setText(dateFormat.format(selectedDate))
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        ).show()
    }

    private fun validateQuantity() {
        val quantiteText = binding.etQuantiteProduite.text.toString()
        if (quantiteText.isNotEmpty()) {
            try {
                val quantite = quantiteText.toDouble()
                val selectedCommande = viewModel.getSelectedCommande()
                
                if (selectedCommande != null && quantite > selectedCommande.quantite) {
                    binding.etQuantiteProduite.error = 
                        "La quantité ne peut pas dépasser ${selectedCommande.quantite} m³"
                } else if (quantite <= 0) {
                    binding.etQuantiteProduite.error = "La quantité doit être positive"
                } else {
                    binding.etQuantiteProduite.error = null
                }
            } catch (e: NumberFormatException) {
                binding.etQuantiteProduite.error = "Quantité invalide"
            }
        }
    }

    private fun loadCommandes() {
        viewModel.loadCommandes()
    }

    private fun createProduction() {
        if (!validateInputs()) {
            return
        }

        val numeroOrdre = binding.etNumeroOrdre.text.toString()
        val quantite = binding.etQuantiteProduite.text.toString().toDouble()
        val operateur = binding.etOperateur.text.toString()
        val statutText = binding.actvStatut.text.toString()
        val statut = ProductionStatus.values().find { it.displayName == statutText } 
            ?: ProductionStatus.EN_COURS
        val notes = binding.etNotes.text.toString()

        viewModel.createProduction(
            numeroOrdre = numeroOrdre,
            dateProduction = selectedDate,
            quantiteAProduite = quantite,
            operateur = operateur,
            statut = statut,
            notes = notes
        )
    }

    private fun validateInputs(): Boolean {
        var isValid = true

        if (binding.etNumeroOrdre.text.isNullOrEmpty()) {
            binding.etNumeroOrdre.error = "Numéro d'ordre requis"
            isValid = false
        }

        if (binding.actvCommande.text.isNullOrEmpty()) {
            binding.actvCommande.error = "Commande requise"
            isValid = false
        }

        if (binding.etQuantiteProduite.text.isNullOrEmpty()) {
            binding.etQuantiteProduite.error = "Quantité requise"
            isValid = false
        } else {
            try {
                val quantite = binding.etQuantiteProduite.text.toString().toDouble()
                if (quantite <= 0) {
                    binding.etQuantiteProduite.error = "La quantité doit être positive"
                    isValid = false
                }
            } catch (e: NumberFormatException) {
                binding.etQuantiteProduite.error = "Quantité invalide"
                isValid = false
            }
        }

        if (binding.etOperateur.text.isNullOrEmpty()) {
            binding.etOperateur.error = "Opérateur requis"
            isValid = false
        }

        if (binding.actvStatut.text.isNullOrEmpty()) {
            binding.actvStatut.error = "Statut requis"
            isValid = false
        }

        return isValid
    }

    private fun observeUiState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { uiState ->
                updateUi(uiState)
            }
        }
    }

    private fun updateUi(uiState: CreateProductionUiState) {
        binding.progressBar.visibility = if (uiState.isLoading) View.VISIBLE else View.GONE
        binding.btnCreer.isEnabled = !uiState.isLoading
        binding.btnAnnuler.isEnabled = !uiState.isLoading

        // Mise à jour de la liste des commandes
        if (uiState.commandes.isNotEmpty()) {
            val commandeNames = uiState.commandes.map { 
                "${it.numeroCommande} - ${it.client.nom} (${it.quantite} m³)" 
            }
            val adapter = ArrayAdapter(
                requireContext(),
                android.R.layout.simple_dropdown_item_1line,
                commandeNames
            )
            binding.actvCommande.setAdapter(adapter)
        }

        // Mise à jour des informations de la commande sélectionnée
        uiState.selectedCommande?.let { commande ->
            val details = buildString {
                append("Client: ${commande.client.nom}\n")
                commande.chantier?.let { append("Chantier: ${it.nom}\n") }
                append("Type béton: ${commande.typeBeton}\n")
                append("Quantité: ${commande.quantite} m³\n")
                append("Date livraison: ${commande.dateLivraisonPrevue}")
            }
            binding.tvCommandeDetails.text = details
            binding.cardCommandeInfo.visibility = View.VISIBLE
        } ?: run {
            binding.cardCommandeInfo.visibility = View.GONE
        }

        uiState.errorMessage?.let { message ->
            Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
            viewModel.clearError()
        }

        if (uiState.isProductionCreated) {
            Snackbar.make(binding.root, "Ordre de production créé avec succès", Snackbar.LENGTH_SHORT).show()
            findNavController().navigateUp()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}