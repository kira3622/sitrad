package com.betonapp.ui.orders

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
import com.betonapp.databinding.FragmentCreateOrderBinding
import com.betonapp.utils.ValidationUtils
import com.betonapp.utils.setupForFrenchNames
import com.betonapp.utils.setupForAddresses
import com.betonapp.utils.validateWith
import com.betonapp.utils.clearError
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class CreateOrderFragment : Fragment() {

    private var _binding: FragmentCreateOrderBinding? = null
    private val binding get() = _binding!!

    private val viewModel: CreateOrderViewModel by viewModels()
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private val displayDateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())
    private val numberFormat = NumberFormat.getCurrencyInstance(Locale.FRANCE)

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCreateOrderBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupViews()
        observeUiState()
        setupListeners()
    }

    private fun setupViews() {
        // Configuration du dropdown pour le type de béton
        val typeBetonOptions = arrayOf(
            "C20/25", "C25/30", "C30/37", "C35/45", "C40/50",
            "Béton armé", "Béton précontraint", "Béton léger",
            "Béton haute performance", "Béton autoplaçant"
        )
        val typeBetonAdapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_dropdown_item_1line,
            typeBetonOptions
        )
        binding.actvTypeBeton.setAdapter(typeBetonAdapter)

        // Configuration de la validation pour les caractères spéciaux français
        setupValidation()

        // Génération automatique du numéro de commande
        val numeroCommande = "CMD-${System.currentTimeMillis().toString().takeLast(6)}"
        binding.etNumeroCommande.setText(numeroCommande)

        // Date par défaut (aujourd'hui + 7 jours)
        val calendar = Calendar.getInstance()
        calendar.add(Calendar.DAY_OF_MONTH, 7)
        val defaultDate = dateFormat.format(calendar.time)
        binding.etDateLivraison.setText(displayDateFormat.format(calendar.time))
        binding.etDateLivraison.tag = defaultDate
    }

    private fun setupValidation() {
        // Configuration de la validation pour le nom du client (caractères français)
        // Nous devons accéder au TextInputLayout parent de etClient
        val clientLayout = binding.etClient.parent.parent as? com.google.android.material.textfield.TextInputLayout
        clientLayout?.setupForFrenchNames()
        
        // Configuration de la validation pour le chantier (adresse)
        val chantierLayout = binding.etChantier.parent.parent as? com.google.android.material.textfield.TextInputLayout
        chantierLayout?.setupForAddresses()
        
        // Configuration de la validation pour le numéro de commande
        // La validation sera effectuée lors de la soumission du formulaire
    }

    private fun setupListeners() {
        // Date picker pour la date de livraison
        binding.etDateLivraison.setOnClickListener {
            showDatePicker()
        }

        // Calcul automatique du prix total
        binding.etQuantite.addTextChangedListener {
            calculateTotal()
        }
        binding.etPrixUnitaire.addTextChangedListener {
            calculateTotal()
        }

        // Boutons d'action
        binding.btnAnnuler.setOnClickListener {
            findNavController().navigateUp()
        }

        binding.btnCreer.setOnClickListener {
            createOrder()
        }
    }

    private fun showDatePicker() {
        val calendar = Calendar.getInstance()
        val currentDate = binding.etDateLivraison.tag as? String
        if (currentDate != null) {
            try {
                calendar.time = dateFormat.parse(currentDate) ?: Date()
            } catch (e: Exception) {
                // Utiliser la date actuelle en cas d'erreur
            }
        }

        DatePickerDialog(
            requireContext(),
            { _, year, month, dayOfMonth ->
                calendar.set(year, month, dayOfMonth)
                val selectedDate = dateFormat.format(calendar.time)
                binding.etDateLivraison.setText(displayDateFormat.format(calendar.time))
                binding.etDateLivraison.tag = selectedDate
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        ).apply {
            datePicker.minDate = System.currentTimeMillis()
        }.show()
    }

    private fun calculateTotal() {
        val quantiteText = binding.etQuantite.text.toString()
        val prixUnitaireText = binding.etPrixUnitaire.text.toString()

        if (quantiteText.isNotEmpty() && prixUnitaireText.isNotEmpty()) {
            try {
                val quantite = quantiteText.toDouble()
                val prixUnitaire = prixUnitaireText.toDouble()
                val total = quantite * prixUnitaire
                binding.etPrixTotal.setText(numberFormat.format(total))
            } catch (e: NumberFormatException) {
                binding.etPrixTotal.setText("")
            }
        } else {
            binding.etPrixTotal.setText("")
        }
    }

    private fun createOrder() {
        if (!validateInputs()) {
            return
        }

        val numeroCommande = binding.etNumeroCommande.text.toString()
        val client = binding.etClient.text.toString()
        val chantier = binding.etChantier.text.toString().ifEmpty { null }
        val typeBeton = binding.actvTypeBeton.text.toString()
        val quantite = binding.etQuantite.text.toString().toDouble()
        val dateLivraison = binding.etDateLivraison.tag as String
        val prixUnitaire = binding.etPrixUnitaire.text.toString().toDouble()

        viewModel.createOrder(
            numeroCommande = numeroCommande,
            client = client,
            chantier = chantier,
            typeBeton = typeBeton,
            quantite = quantite,
            dateLivraisonPrevue = dateLivraison,
            prixUnitaire = prixUnitaire
        )
    }

    private fun validateInputs(): Boolean {
        var isValid = true

        // Validation du numéro de commande avec support des caractères spéciaux
        val numeroCommandeLayout = binding.etNumeroCommande.parent.parent as? com.google.android.material.textfield.TextInputLayout
        if (!numeroCommandeLayout?.validateWith(
            isRequired = true,
            minLength = 3,
            maxLength = 20,
            validator = ValidationUtils::isValidOrderNumber,
            customErrorMessage = "Format de numéro de commande invalide"
        )!!) {
            isValid = false
        }

        // Validation du nom du client avec support des caractères français
        val clientLayout = binding.etClient.parent.parent as? com.google.android.material.textfield.TextInputLayout
        if (!clientLayout?.validateWith(
            isRequired = true,
            minLength = 2,
            maxLength = 100,
            validator = ValidationUtils::isValidName,
            customErrorMessage = "Nom de client invalide (caractères français acceptés)"
        )!!) {
            isValid = false
        }

        // Validation du chantier (optionnel) avec support des adresses françaises
        val chantierLayout = binding.etChantier.parent.parent as? com.google.android.material.textfield.TextInputLayout
        val chantierText = binding.etChantier.text?.toString()
        if (!chantierText.isNullOrEmpty()) {
            if (!chantierLayout?.validateWith(
                isRequired = false,
                minLength = 2,
                maxLength = 200,
                validator = ValidationUtils::isValidAddress,
                customErrorMessage = "Adresse de chantier invalide"
            )!!) {
                isValid = false
            }
        } else {
            chantierLayout?.clearError()
        }

        // Validation du type de béton
        if (binding.actvTypeBeton.text.isNullOrEmpty()) {
            val typeBetonLayout = binding.actvTypeBeton.parent.parent as? com.google.android.material.textfield.TextInputLayout
            typeBetonLayout?.error = "Type de béton requis"
            isValid = false
        }

        // Validation de la quantité
        if (binding.etQuantite.text.isNullOrEmpty()) {
            val quantiteLayout = binding.etQuantite.parent.parent as? com.google.android.material.textfield.TextInputLayout
            quantiteLayout?.error = "Quantité requise"
            isValid = false
        } else {
            try {
                val quantite = binding.etQuantite.text.toString().toDouble()
                if (quantite <= 0) {
                    val quantiteLayout = binding.etQuantite.parent.parent as? com.google.android.material.textfield.TextInputLayout
                    quantiteLayout?.error = "La quantité doit être positive"
                    isValid = false
                }
            } catch (e: NumberFormatException) {
                val quantiteLayout = binding.etQuantite.parent.parent as? com.google.android.material.textfield.TextInputLayout
                quantiteLayout?.error = "Quantité invalide"
                isValid = false
            }
        }

        // Validation du prix unitaire
        if (binding.etPrixUnitaire.text.isNullOrEmpty()) {
            val prixLayout = binding.etPrixUnitaire.parent.parent as? com.google.android.material.textfield.TextInputLayout
            prixLayout?.error = "Prix unitaire requis"
            isValid = false
        } else {
            try {
                val prix = binding.etPrixUnitaire.text.toString().toDouble()
                if (prix <= 0) {
                    val prixLayout = binding.etPrixUnitaire.parent.parent as? com.google.android.material.textfield.TextInputLayout
                    prixLayout?.error = "Le prix doit être positif"
                    isValid = false
                }
            } catch (e: NumberFormatException) {
                val prixLayout = binding.etPrixUnitaire.parent.parent as? com.google.android.material.textfield.TextInputLayout
                prixLayout?.error = "Prix invalide"
                isValid = false
            }
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

    private fun updateUi(uiState: CreateOrderUiState) {
        binding.progressBar.visibility = if (uiState.isLoading) View.VISIBLE else View.GONE
        binding.btnCreer.isEnabled = !uiState.isLoading
        binding.btnAnnuler.isEnabled = !uiState.isLoading

        uiState.errorMessage?.let { message ->
            Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
            viewModel.clearError()
        }

        if (uiState.isOrderCreated) {
            Snackbar.make(binding.root, "Commande créée avec succès", Snackbar.LENGTH_SHORT).show()
            findNavController().navigateUp()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}