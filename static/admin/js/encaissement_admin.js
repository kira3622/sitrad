/*
 * encaissement_admin.js
 * Filtre la liste déroulante "Bon de livraison" (ordre_production)
 * selon le client sélectionné, triée par numéro de bon.
 */
(function () {
    'use strict';

    function getBonsEndpoint(clientId) {
        // Endpoint JSON fourni par EncaissementAdmin.get_urls
        return '/admin/encaissement/encaissement/bons-par-client/' + clientId + '/';
    }

    function updateBonsSelect(clientId) {
        var bonSelect = document.querySelector('select[name="ordre_production"]');
        if (!bonSelect) return;

        // Conserver la valeur actuellement sélectionnée
        var currentValue = bonSelect.value;

        // Vider la liste et ajouter l'option vide
        bonSelect.innerHTML = '';
        var emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '---------';
        bonSelect.appendChild(emptyOption);

        if (!clientId) {
            return;
        }

        fetch(getBonsEndpoint(clientId), {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (response) {
                if (!response.ok) throw new Error('Réponse réseau incorrecte');
                return response.json();
            })
            .then(function (data) {
                var bons = data.bons || [];
                bons.forEach(function (bon) {
                    var option = document.createElement('option');
                    option.value = bon.id;
                    option.textContent = bon.label;
                    if (String(bon.id) === String(currentValue)) {
                        option.selected = true;
                    }
                    bonSelect.appendChild(option);
                });
            })
            .catch(function (error) {
                console.error('Erreur lors du chargement des bons :', error);
            });
    }

    function init() {
        var clientSelect = document.querySelector('[name="client"]');
        if (!clientSelect) return;

        // Exposer la fonction pour débogage / usage externe
        window.encaissementUpdateBons = updateBonsSelect;

        // Mettre à jour au chargement (cas d'un formulaire de modification)
        updateBonsSelect(clientSelect.value);

        // Mettre à jour à chaque changement de client (événement natif)
        clientSelect.addEventListener('change', function () {
            updateBonsSelect(clientSelect.value);
        });

        // Avec select2 (autocomplete_fields), on capture aussi select2:select / select2:clear.
        // Django expose jQuery via django.jQuery (chargé après ce script), on attend qu'il soit prêt.
        function bindSelect2Events() {
            var $ = window.django && window.django.jQuery;
            if (!$) {
                setTimeout(bindSelect2Events, 100);
                return;
            }
            $(document).on('change select2:select select2:clear', '[name="client"]', function () {
                updateBonsSelect(clientSelect.value);
            });
        }
        bindSelect2Events();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
