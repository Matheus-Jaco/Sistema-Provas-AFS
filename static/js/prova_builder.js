/**
 * Construtor Interativo de Prova-Base
 * Permite selecionar questões, filtrar por disciplina/dificuldade e visualizar o contador em tempo real.
 */

document.addEventListener('DOMContentLoaded', () => {
    const disciplinaSelect = document.getElementById('prova-disciplina-select');
    const questionCards = document.querySelectorAll('.builder-question-card');
    const counterBadge = document.getElementById('selected-questions-counter');
    const selectAllBtn = document.getElementById('btn-select-all');
    const deselectAllBtn = document.getElementById('btn-deselect-all');
    const checkboxes = document.querySelectorAll('.question-checkbox');

    function updateCounter() {
        let count = 0;
        checkboxes.forEach(cb => {
            if (cb.checked) count++;
        });
        if (counterBadge) {
            counterBadge.textContent = `${count} selecionada(s)`;
        }
    }

    if (checkboxes.length > 0) {
        checkboxes.forEach(cb => {
            cb.addEventListener('change', updateCounter);
        });
        updateCounter();
    }

    if (disciplinaSelect) {
        disciplinaSelect.addEventListener('change', (e) => {
            const selectedDiscId = e.target.value;
            questionCards.forEach(card => {
                const cardDiscId = card.getAttribute('data-disciplina-id');
                if (!selectedDiscId || cardDiscId === selectedDiscId) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                    // Desmarcar se ocultado
                    const cb = card.querySelector('.question-checkbox');
                    if (cb) cb.checked = false;
                }
            });
            updateCounter();
        });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            questionCards.forEach(card => {
                if (card.style.display !== 'none') {
                    const cb = card.querySelector('.question-checkbox');
                    if (cb) cb.checked = true;
                }
            });
            updateCounter();
        });
    }

    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => {
            checkboxes.forEach(cb => cb.checked = false);
            updateCounter();
        });
    }
});
