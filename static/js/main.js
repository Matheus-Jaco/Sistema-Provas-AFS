/**
 * Sistema de Geração de Provas Embaralhadas
 * JavaScript Principal - Gestão de Formulários e Alternativas Dinâmicas
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Fechamento de Alertas
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(button => {
        button.addEventListener('click', (e) => {
            const alertNode = e.target.closest('.alert');
            if (alertNode) {
                alertNode.style.opacity = '0';
                setTimeout(() => alertNode.remove(), 200);
            }
        });
    });

    // 2. Adição Dinâmica de Alternativas no Formulário de Questão
    const btnAddOption = document.getElementById('btn-add-option');
    const optionsContainer = document.getElementById('options-container');

    if (btnAddOption && optionsContainer) {
        const optionLetters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

        btnAddOption.addEventListener('click', () => {
            const currentCount = optionsContainer.children.length;
            if (currentCount >= 8) {
                alert('Limite máximo de 8 alternativas por questão atingido.');
                return;
            }

            const letter = optionLetters[currentCount] || `Opt ${currentCount + 1}`;

            const optionRow = document.createElement('div');
            optionRow.className = 'option-row style-option-row';
            optionRow.style.display = 'flex';
            optionRow.style.gap = '12px';
            optionRow.style.alignItems = 'center';
            optionRow.style.marginBottom = '12px';

            optionRow.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px;">
                    <input type="radio" name="item_correto" value="${currentCount}" id="radio_opt_${currentCount}">
                    <label for="radio_opt_${currentCount}" style="font-weight: 600; width: 20px;">${letter})</label>
                </div>
                <input type="text" name="item_texto[]" class="form-control" placeholder="Texto da alternativa ${letter}..." required>
                <button type="button" class="btn btn-sm btn-secondary btn-remove-option" style="color: #b91c1c;" title="Remover alternativa">
                    &times;
                </button>
            `;

            optionsContainer.appendChild(optionRow);
            reindexRadioValues();
        });

        // Event delegation para remover opção
        optionsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-remove-option')) {
                if (optionsContainer.children.length <= 2) {
                    alert('A questão deve possuir no mínimo 2 alternativas.');
                    return;
                }
                const row = e.target.closest('.option-row');
                if (row) {
                    row.remove();
                    reindexRadioValues();
                }
            }
        });

        function reindexRadioValues() {
            const rows = optionsContainer.querySelectorAll('.option-row');
            rows.forEach((row, idx) => {
                const radio = row.querySelector('input[type="radio"]');
                const label = row.querySelector('label');
                const letter = optionLetters[idx] || `Opt ${idx + 1}`;

                if (radio) {
                    radio.value = idx;
                    radio.id = `radio_opt_${idx}`;
                }
                if (label) {
                    label.setAttribute('for', `radio_opt_${idx}`);
                    label.textContent = `${letter})`;
                }
            });
        }
    }
});

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}
