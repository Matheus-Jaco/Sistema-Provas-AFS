/**
 * Construtor Interativo de Prova-Base
 * Permite selecionar questões, filtrar por disciplina/dificuldade e visualizar o contador em tempo real.
 */

document.addEventListener('DOMContentLoaded', () => {
    const disciplinaSelect = document.getElementById('prova-disciplina-select');
    const selectedDisciplines = document.getElementById('selected-disciplines');
    const questionCards = document.querySelectorAll('.builder-question-card');
    const counterBadge = document.getElementById('selected-questions-counter');
    const selectAllBtn = document.getElementById('btn-select-all');
    const deselectAllBtn = document.getElementById('btn-deselect-all');
    const checkboxes = document.querySelectorAll('.question-checkbox');
    const selectedDiscIds = [];

    function renderSelectedDisciplines() {
        if (!selectedDisciplines) return;
        selectedDisciplines.innerHTML = '';
        selectedDiscIds.forEach((disciplinaId) => {
            const option = disciplinaSelect.querySelector(`option[value="${disciplinaId}"]`);
            if (!option) return;

            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'disciplinas_ids[]';
            input.value = disciplinaId;
            selectedDisciplines.appendChild(input);

            const tag = document.createElement('button');
            tag.type = 'button';
            tag.className = 'badge badge-code';
            tag.textContent = `${option.textContent} x`;
            tag.title = 'Remover disciplina';
            tag.addEventListener('click', () => {
                selectedDiscIds.splice(selectedDiscIds.indexOf(disciplinaId), 1);
                renderSelectedDisciplines();
                filterQuestions();
            });
            selectedDisciplines.appendChild(tag);
        });
    }

    function filterQuestions() {
        questionCards.forEach(card => {
            const cardDiscId = card.getAttribute('data-disciplina-id');
            if (selectedDiscIds.length === 0 || selectedDiscIds.includes(cardDiscId)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
                const cb = card.querySelector('.question-checkbox');
                if (cb) cb.checked = false;
            }
        });
        updateCounter();
    }

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
            if (e.target.value && !selectedDiscIds.includes(e.target.value)) {
                selectedDiscIds.push(e.target.value);
                renderSelectedDisciplines();
            }
            e.target.value = '';
            filterQuestions();
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
