// JavaScript pour l'interface d'administration fuel_management
function formatMAD(valeur) {
    const n = Number(valeur);
    if (Number.isNaN(n)) return '0.00';
    return n.toFixed(2);
}

document.addEventListener('DOMContentLoaded', function () {
    // -------- Consommation : calcul en temps réel du montant total --------
    const quantiteInput = document.querySelector('.field-quantite input, #id_quantite');
    const prixInput = document.querySelector('.field-prix_unitaire input, #id_prix_unitaire');
    const totalInput = document.querySelector('.field-montant_total input, #id_montant_total');

    function recalculerTotal() {
        if (!quantiteInput || !prixInput || !totalInput) return;
        const qte = parseFloat(quantiteInput.value.replace(',', '.')) || 0;
        const prix = parseFloat(prixInput.value.replace(',', '.')) || 0;
        const total = qte * prix;
        totalInput.value = formatMAD(total);
    }

    if (quantiteInput && prixInput && totalInput) {
        totalInput.readOnly = true;
        totalInput.style.backgroundColor = '#f5f5f4';
        totalInput.style.fontWeight = '700';
        totalInput.style.color = '#7c2d12';
        quantiteInput.addEventListener('input', recalculerTotal);
        prixInput.addEventListener('input', recalculerTotal);
        recalculerTotal();
    }

    // -------- Approvisionnement : calcul en temps réel du montant total --------
    const approQte = document.querySelector('.approvisionnement .field-quantite input, #id_quantite');
    const approPrix = document.querySelector('.approvisionnement .field-prix_unitaire input, #id_prix_unitaire');
    const approTotal = document.querySelector('.approvisionnement .field-montant_total input, #id_montant_total');

    function recalculerApproTotal() {
        if (!approQte || !approPrix || !approTotal) return;
        const qte = parseFloat(approQte.value.replace(',', '.')) || 0;
        const prix = parseFloat(approPrix.value.replace(',', '.')) || 0;
        approTotal.value = formatMAD(qte * prix);
    }

    // Uniquement pour Approvisionnement si les inputs existent en dehors de Consommation
    const isApproPage = document.querySelector('body.model-approvisionnement');
    if (isApproPage && approQte && approPrix && approTotal && !quantiteInput) {
        approTotal.readOnly = true;
        approTotal.style.backgroundColor = '#f5f5f4';
        approTotal.style.fontWeight = '700';
        approTotal.style.color = '#7c2d12';
        approQte.addEventListener('input', recalculerApproTotal);
        approPrix.addEventListener('input', recalculerApproTotal);
        recalculerApproTotal();
    }
});
