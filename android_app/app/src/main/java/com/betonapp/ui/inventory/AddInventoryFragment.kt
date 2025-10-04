package com.betonapp.ui.inventory

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import androidx.core.content.ContextCompat
import androidx.core.widget.addTextChangedListener
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.betonapp.R
import com.betonapp.data.models.StockStatus
import com.betonapp.databinding.FragmentAddInventoryBinding
import com.betonapp.utils.ValidationUtils
import com.betonapp.utils.setupForFrenchNames
import com.betonapp.utils.validateWith
import com.betonapp.utils.clearError
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class AddInventoryFragment : Fragment() {

    private var _binding: FragmentAddInventoryBinding? = null
    private val binding get() = _binding!!

    private val viewModel: AddInventoryViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAddInventoryBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupViews()
        observeUiState()
        setupListeners()
    }

    private fun setupViews() {
        // Configuration du dropdown pour les unités
        val uniteOptions = arrayOf(
            "kg", "tonnes", "m³", "litres", "sacs", "palettes", "unités"
        )
        val uniteAdapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_dropdown_item_1line,
            uniteOptions
        )
        binding.actvUnite.setAdapter(uniteAdapter)
        
        // Unité par défaut
        binding.actvUnite.setText("kg", false)
        
        // Configuration de la validation pour les caractères spéciaux français
        setupValidation()
    }

    private fun setupValidation() {
        // Configuration de la validation pour le nom de la matière première (caractères français)
        val nomMatiereLayout = binding.etNomMatiere.parent.parent as? com.google.android.material.textfield.TextInputLayout
        nomMatiereLayout?.setupForFrenchNames()
        
        // Configuration de la validation pour le fournisseur (caractères français)
        val fournisseurLayout = binding.etFournisseur.parent.parent as? com.google.android.material.textfield.TextInputLayout
        fournisseurLayout?.setupForFrenchNames()
    }

    private fun setupListeners() {
        // Calcul automatique du statut du stock
        binding.etStockActuel.addTextChangedListener {
            updateStockStatus()
        }
        binding.etStockMinimum.addTextChangedListener {
            updateStockStatus()
        }

        // Boutons d'action
        binding.btnAnnuler.setOnClickListener {
            findNavController().navigateUp()
        }

        binding.btnAjouter.setOnClickListener {
            addInventoryItem()
        }
    }

    private fun updateStockStatus() {
        val stockActuelText = binding.etStockActuel.text.toString()
        val stockMinimumText = binding.etStockMinimum.text.toString()

        if (stockActuelText.isNotEmpty() && stockMinimumText.isNotEmpty()) {
            try {
                val stockActuel = stockActuelText.toDouble()
                val stockMinimum = stockMinimumText.toDouble()

                val status = when {
                    stockActuel <= 0 -> StockStatus.CRITIQUE
                    stockActuel <= stockMinimum -> StockStatus.FAIBLE
                    stockActuel <= stockMinimum * 1.5 -> StockStatus.FAIBLE
                    else -> StockStatus.NORMAL
                }

                binding.tvStatutStock.text = status.displayName
                binding.tvStatutStock.setTextColor(
                    ContextCompat.getColor(
                        requireContext(),
                        when (status) {
                            StockStatus.NORMAL -> android.R.color.holo_green_dark
                            StockStatus.FAIBLE -> android.R.color.holo_orange_dark
                            StockStatus.CRITIQUE -> android.R.color.holo_red_dark
                        }
                    )
                )
            } catch (e: NumberFormatException) {
                binding.tvStatutStock.text = "À calculer"
                binding.tvStatutStock.setTextColor(
                    ContextCompat.getColor(requireContext(), android.R.color.darker_gray)
                )
            }
        } else {
            binding.tvStatutStock.text = "À calculer"
            binding.tvStatutStock.setTextColor(
                ContextCompat.getColor(requireContext(), android.R.color.darker_gray)
            )
        }
    }

    private fun addInventoryItem() {
        if (!validateInputs()) {
            return
        }

        val nom = binding.etNomMatiere.text.toString()
        val unite = binding.actvUnite.text.toString()
        val stockActuel = binding.etStockActuel.text.toString().toDouble()
        val stockMinimum = binding.etStockMinimum.text.toString().toDouble()
        val prixUnitaire = binding.etPrixUnitaire.text.toString().toDouble()
        val fournisseur = binding.etFournisseur.text.toString()

        viewModel.addInventoryItem(
            nom = nom,
            unite = unite,
            stockActuel = stockActuel,
            stockMinimum = stockMinimum,
            prixUnitaire = prixUnitaire,
            fournisseur = fournisseur
        )
    }

    private fun validateInputs(): Boolean {
        var isValid = true

        // Validation du nom de la matière première avec support des caractères français
        val nomMatiereLayout = binding.etNomMatiere.parent.parent as? com.google.android.material.textfield.TextInputLayout
        if (!nomMatiereLayout?.validateWith(
            isRequired = true,
            minLength = 2,
            maxLength = 100,
            validator = ValidationUtils::isValidName,
            customErrorMessage = "Nom de matière première invalide (caractères français acceptés)"
        )!!) {
            isValid = false
        }

        // Validation de l'unité de mesure
        if (binding.actvUnite.text.isNullOrEmpty()) {
            val uniteLayout = binding.actvUnite.parent.parent as? com.google.android.material.textfield.TextInputLayout
            uniteLayout?.error = "Unité de mesure requise"
            isValid = false
        }

        // Validation du stock actuel
        if (binding.etStockActuel.text.isNullOrEmpty()) {
            val stockActuelLayout = binding.etStockActuel.parent.parent as? com.google.android.material.textfield.TextInputLayout
            stockActuelLayout?.error = "Stock actuel requis"
            isValid = false
        } else {
            try {
                val stock = binding.etStockActuel.text.toString().toDouble()
                if (stock < 0) {
                    val stockActuelLayout = binding.etStockActuel.parent.parent as? com.google.android.material.textfield.TextInputLayout
                    stockActuelLayout?.error = "Le stock ne peut pas être négatif"
                    isValid = false
                }
            } catch (e: NumberFormatException) {
                val stockActuelLayout = binding.etStockActuel.parent.parent as? com.google.android.material.textfield.TextInputLayout
                stockActuelLayout?.error = "Stock invalide"
                isValid = false
            }
        }

        // Validation du stock minimum
        if (binding.etStockMinimum.text.isNullOrEmpty()) {
            val stockMinimumLayout = binding.etStockMinimum.parent.parent as? com.google.android.material.textfield.TextInputLayout
            stockMinimumLayout?.error = "Stock minimum requis"
            isValid = false
        } else {
            try {
                val stockMin = binding.etStockMinimum.text.toString().toDouble()
                if (stockMin < 0) {
                    val stockMinimumLayout = binding.etStockMinimum.parent.parent as? com.google.android.material.textfield.TextInputLayout
                    stockMinimumLayout?.error = "Le stock minimum ne peut pas être négatif"
                    isValid = false
                }
            } catch (e: NumberFormatException) {
                val stockMinimumLayout = binding.etStockMinimum.parent.parent as? com.google.android.material.textfield.TextInputLayout
                stockMinimumLayout?.error = "Stock minimum invalide"
                isValid = false
            }
        }

        // Validation du prix unitaire
        if (binding.etPrixUnitaire.text.isNullOrEmpty()) {
            val prixUnitaireLayout = binding.etPrixUnitaire.parent.parent as? com.google.android.material.textfield.TextInputLayout
            prixUnitaireLayout?.error = "Prix unitaire requis"
            isValid = false
        } else {
            try {
                val prix = binding.etPrixUnitaire.text.toString().toDouble()
                if (prix <= 0) {
                    val prixUnitaireLayout = binding.etPrixUnitaire.parent.parent as? com.google.android.material.textfield.TextInputLayout
                    prixUnitaireLayout?.error = "Le prix doit être positif"
                    isValid = false
                }
            } catch (e: NumberFormatException) {
                val prixUnitaireLayout = binding.etPrixUnitaire.parent.parent as? com.google.android.material.textfield.TextInputLayout
                prixUnitaireLayout?.error = "Prix invalide"
                isValid = false
            }
        }

        // Validation du fournisseur avec support des caractères français
        val fournisseurLayout = binding.etFournisseur.parent.parent as? com.google.android.material.textfield.TextInputLayout
        if (!fournisseurLayout?.validateWith(
            isRequired = true,
            minLength = 2,
            maxLength = 100,
            validator = ValidationUtils::isValidName,
            customErrorMessage = "Nom de fournisseur invalide (caractères français acceptés)"
        )!!) {
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

    private fun updateUi(uiState: AddInventoryUiState) {
        binding.progressBar.visibility = if (uiState.isLoading) View.VISIBLE else View.GONE
        binding.btnAjouter.isEnabled = !uiState.isLoading
        binding.btnAnnuler.isEnabled = !uiState.isLoading

        uiState.errorMessage?.let { message ->
            Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
            viewModel.clearError()
        }

        if (uiState.isItemAdded) {
            Snackbar.make(binding.root, "Matière première ajoutée avec succès", Snackbar.LENGTH_SHORT).show()
            findNavController().navigateUp()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}