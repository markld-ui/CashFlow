// static/js/forms.js
import { apiRequest, showAlert, toggleLoading, formatDate } from './app.js';

async function initializeTransactionForm(transactionId = null) {
    toggleLoading(true);
    try {
        await loadFormOptions();
        if (transactionId) {
            await loadTransactionData(transactionId);
        }
        setupFormValidation();
        document.getElementById('transaction_type').addEventListener('change', updateCategories);
        document.getElementById('category').addEventListener('change', updateSubcategories);
    } catch (error) {
        showAlert('danger', 'Не удалось инициализировать форму');
    } finally {
        toggleLoading(false);
    }
}

async function loadFormOptions() {
    try {
        const data = await apiRequest('reference-data/');
        
        const statusSelect = document.getElementById('status');
        statusSelect.innerHTML = '<option value="">Выберите статус...</option>';
        data.statuses.forEach(status => {
            statusSelect.innerHTML += `<option value="${status.id}">${status.name}</option>`;
        });

        const typeSelect = document.getElementById('transaction_type');
        typeSelect.innerHTML = '<option value="">Выберите тип...</option>';
        data.transaction_types.forEach(type => {
            typeSelect.innerHTML += `<option value="${type.id}">${type.name}</option>`;
        });
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить данные для формы');
    }
}

async function loadTransactionData(id) {
    try {
        const transaction = await apiRequest(`transactions/${id}/`);
        document.getElementById('transaction-id').value = transaction.id;
        document.getElementById('transaction_date').value = transaction.transaction_date;
        document.getElementById('status').value = transaction.status;
        document.getElementById('transaction_type').value = transaction.transaction_type;
        document.getElementById('amount').value = transaction.amount;
        document.getElementById('comment').value = transaction.comment;

        await updateCategories();
        document.getElementById('category').value = transaction.category;
        await updateSubcategories();
        document.getElementById('subcategory').value = transaction.subcategory;
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить данные транзакции');
    }
}

async function updateCategories() {
    const typeId = document.getElementById('transaction_type').value;
    const categorySelect = document.getElementById('category');
    categorySelect.disabled = !typeId;
    categorySelect.innerHTML = '<option value="">Выберите категорию...</option>';

    if (typeId) {
        try {
            const categories = await apiRequest(`transaction-types/${typeId}/categories/`);
            categories.forEach(category => {
                categorySelect.innerHTML += `<option value="${category.id}">${category.name}</option>`;
            });
        } catch (error) {
            showAlert('danger', 'Не удалось загрузить категории');
        }
    }
    updateSubcategories();
}

async function updateSubcategories() {
    const categoryId = document.getElementById('category').value;
    const subcategorySelect = document.getElementById('subcategory');
    subcategorySelect.disabled = !categoryId;
    subcategorySelect.innerHTML = '<option value="">Выберите подкатегорию...</option>';

    if (categoryId) {
        try {
            const subcategories = await apiRequest(`categories/${categoryId}/subcategories/`);
            subcategories.forEach(subcategory => {
                subcategorySelect.innerHTML += `<option value="${subcategory.id}">${subcategory.name}</option>`;
            });
        } catch (error) {
            showAlert('danger', 'Не удалось загрузить подкатегории');
        }
    }
}

function setupFormValidation() {
    const form = document.getElementById('transaction-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const data = {
            transaction_date: document.getElementById('transaction_date').value,
            status: document.getElementById('status').value,
            transaction_type: document.getElementById('transaction_type').value,
            category: document.getElementById('category').value,
            subcategory: document.getElementById('subcategory').value,
            amount: parseFloat(document.getElementById('amount').value),
            comment: document.getElementById('comment').value
        };

        const id = document.getElementById('transaction-id').value;
        try {
            toggleLoading(true);
            if (id) {
                await apiRequest(`transactions/${id}/`, 'PUT', data);
                showAlert('success', 'Транзакция успешно обновлена');
            } else {
                await apiRequest('transactions/', 'POST', data);
                showAlert('success', 'Транзакция успешно создана');
            }
            window.location.href = '/';
        } catch (error) {
            showAlert('danger', 'Не удалось сохранить транзакцию');
        } finally {
            toggleLoading(false);
        }
    });
}

function formatAmount(input) {
    input.value = parseFloat(input.value).toFixed(2);
}

window.initializeTransactionForm = initializeTransactionForm;
window.updateCategories = updateCategories;
window.updateSubcategories = updateSubcategories;
window.formatAmount = formatAmount;