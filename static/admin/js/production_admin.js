// JavaScript pour l'interface d'administration de production

function calculerSorties(ordreId) {
    if (confirm('Voulez-vous calculer les sorties de matières pour cet ordre de production ?')) {
        const url = `/production/ordre/${ordreId}/calculer-sorties/`;
        
        // Afficher un indicateur de chargement
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '⏳ Calcul en cours...';
        button.disabled = true;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Sorties de matières calculées avec succès !');
                location.reload(); // Recharger la page pour voir les changements
            } else {
                alert('❌ Erreur lors du calcul : ' + (data.error || 'Erreur inconnue'));
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('❌ Erreur de communication avec le serveur');
        })
        .finally(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        });
    }
}

function previewSorties(ordreId) {
    const url = `/production/ordre/${ordreId}/preview-sorties/`;
    
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showPreviewModal(data.preview);
        } else {
            alert('❌ Erreur lors de la prévisualisation : ' + (data.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('❌ Erreur de communication avec le serveur');
    });
}

function showPreviewModal(previewData) {
    // Créer la modal si elle n'existe pas
    let modal = document.getElementById('preview-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'preview-modal';
        modal.className = 'preview-modal';
        modal.innerHTML = `
            <div class="preview-content">
                <span class="close">&times;</span>
                <h2>Prévisualisation des sorties de matières</h2>
                <div id="preview-body"></div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Ajouter l'événement de fermeture
        modal.querySelector('.close').onclick = function() {
            modal.style.display = 'none';
        };
        
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        };
    }
    
    // Remplir le contenu
    const previewBody = document.getElementById('preview-body');
    let html = `
        <div class="calculation-summary">
            <h3>Ordre de Production #${previewData.ordre_id}</h3>
            <p><strong>Formule:</strong> ${previewData.formule}</p>
            <p><strong>Quantité à produire:</strong> ${previewData.quantite_produire}</p>
        </div>
        <h4>Matières premières nécessaires:</h4>
    `;
    
    previewData.matieres.forEach(matiere => {
        const stockClass = matiere.stock_suffisant ? '' : 'insufficient-stock';
        const stockWarning = matiere.stock_suffisant ? '' : '<span class="stock-warning">⚠️ Stock insuffisant</span>';
        
        html += `
            <div class="matiere-item ${stockClass}">
                <strong>${matiere.nom}</strong><br>
                Quantité nécessaire: ${matiere.quantite_necessaire} ${matiere.unite}<br>
                Stock actuel: ${matiere.stock_actuel} ${matiere.unite}<br>
                ${stockWarning}
            </div>
        `;
    });
    
    if (!previewData.stock_suffisant) {
        html += '<div class="stock-warning"><h4>⚠️ Attention: Stock insuffisant pour certaines matières</h4></div>';
    }
    
    previewBody.innerHTML = html;
    modal.style.display = 'block';
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Production admin interface loaded');
});