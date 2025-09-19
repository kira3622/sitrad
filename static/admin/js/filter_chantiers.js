// Attendre que Django et jQuery soient chargés
(function() {
    'use strict';
    
    function initFilterChantiers() {
        // Vérifier que django.jQuery est disponible
        if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
            setTimeout(initFilterChantiers, 100);
            return;
        }
        
        var $ = django.jQuery;
        
        $(document).ready(function() {
            // Fonction pour filtrer les chantiers
            function filterChantiers() {
                var clientSelect = $('#id_client');
                var chantierSelect = $('#id_chantier');
                
                if (clientSelect.length && chantierSelect.length) {
                    clientSelect.change(function() {
                        var clientId = $(this).val();
                        
                        // Vider la liste des chantiers
                        chantierSelect.empty();
                        chantierSelect.append('<option value="">---------</option>');
                        
                        if (clientId) {
                            // Faire une requête AJAX pour récupérer les chantiers du client
                            $.ajax({
                                url: '../ajax/filter-chantiers/',
                                data: {
                                    'client_id': clientId
                                },
                                dataType: 'json',
                                success: function(data) {
                                    $.each(data.chantiers, function(index, chantier) {
                                        chantierSelect.append(
                                            '<option value="' + chantier.id + '">' + 
                                            chantier.nom + '</option>'
                                        );
                                    });
                                },
                                error: function(xhr, status, error) {
                                    console.error('Erreur lors du filtrage des chantiers:', error);
                                }
                            });
                        }
                    });
                    
                    // Déclencher le changement si un client est déjà sélectionné
                    if (clientSelect.val()) {
                        clientSelect.trigger('change');
                    }
                }
            }
            
            // Initialiser le filtrage
            filterChantiers();
            
            // Réinitialiser le filtrage si la page est rechargée dynamiquement (pour les inlines)
            $(document).on('formset:added', function() {
                filterChantiers();
            });
        });
    }
    
    // Démarrer l'initialisation
    initFilterChantiers();
})();