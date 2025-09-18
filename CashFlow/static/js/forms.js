// static/js/forms.js

async function initializeTransactionForm(transactionId = null) {
    console.log('initializeTransactionForm called with id:', transactionId);
    toggleLoading(true);
    try {
        await loadFormOptions();
        if (transactionId) {
            await loadTransactionData(transactionId);
        }
        setupFormValidation();
        const typeSelect = document.getElementById('transaction_type');
        const categorySelect = document.getElementById('category');
        if (typeSelect) {
            typeSelect.addEventListener('change', updateCategories);
            console.log('transaction_type select found');
        } else {
            console.error('Element with id "transaction_type" not found');
        }
        if (categorySelect) {
            categorySelect.addEventListener('change', updateSubcategories);
            console.log('category select found');
        } else {
            console.error('Element with id "category" not found');
        }
    } catch (error) {
        console.error('Error in initializeTransactionForm:', error);
        showAlert('danger', 'Не удалось инициализировать форму');
    } finally {
        toggleLoading(false);
    }
}

async function loadFormOptions() {
    try {
        console.log('Loading form options...');
        const data = await apiRequest('reference-data/');
        console.log('Reference data:', data);

        const statusSelect = document.getElementById('status');
        if (statusSelect) {
            // Полная очистка списка
            statusSelect.innerHTML = '';
            statusSelect.innerHTML = '<option value="">Выберите статус...</option>';
            if (data.statuses && data.statuses.length > 0) {
                data.statuses.forEach(status => {
                    statusSelect.innerHTML += `<option value="${status.id}">${status.name}</option>`;
                    console.log('Added status:', status.name);
                });
                console.log('Statuses loaded:', data.statuses.length);
            } else {
                console.warn('No statuses found in API response');
            }
        } else {
            console.error('Element with id "status" not found');
        }

        const typeSelect = document.getElementById('transaction_type');
        if (typeSelect) {
            // Полная очистка списка
            typeSelect.innerHTML = '';
            typeSelect.innerHTML = '<option value="">Выберите тип...</option>';
            if (data.transaction_types && data.transaction_types.length > 0) {
                data.transaction_types.forEach(type => {
                    typeSelect.innerHTML += `<option value="${type.id}">${type.name}</option>`;
                    console.log('Added transaction type:', type.name);
                });
                console.log('Transaction types loaded:', data.transaction_types.length);
            } else {
                console.warn('No transaction types found in API response');
            }
        } else {
            console.error('Element with id "transaction_type" not found');
        }
    } catch (error) {
        console.error('Error in loadFormOptions:', error);
        showAlert('danger', 'Не удалось загрузить данные для формы');
    }
}

async function loadTransactionData(id) {
    try {
        console.log('Loading transaction data for id:', id);
        const transaction = await apiRequest(`transactions/${id}/`);
        console.log('Transaction data:', transaction);
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
        console.error('Error in loadTransactionData:', error);
        showAlert('danger', 'Не удалось загрузить данные транзакции');
    }
}

async function updateCategories() {
    const typeSelect = document.getElementById('transaction_type');
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    if (!typeSelect || !categorySelect || !subcategorySelect) {
        console.error('Type, category, or subcategory select not found');
        return;
    }
    const typeId = typeSelect.value;
    console.log('updateCategories called with typeId:', typeId);
    // Полная очистка списка категорий
    categorySelect.innerHTML = '';
    categorySelect.innerHTML = '<option value="">Выберите категорию...</option>';
    subcategorySelect.innerHTML = '<option value="">Выберите подкатегорию...</option>';
    categorySelect.disabled = !typeId;
    subcategorySelect.disabled = true;
    if (typeId) {
        try {
            console.log('Loading categories for type:', typeId);
            const data = await apiRequest(`transaction-types/${typeId}/categories/`);
            console.log('Categories data:', data);
            if (data && data.length > 0) {
                // Проверяем на дубликаты перед добавлением
                const seenIds = new Set();
                data.forEach(category => {
                    if (!seenIds.has(category.id)) {
                        categorySelect.innerHTML += `<option value="${category.id}">${category.name}</option>`;
                        seenIds.add(category.id);
                        console.log('Added category:', category.name);
                    } else {
                        console.warn('Duplicate category skipped:', category.name);
                    }
                });
                console.log('Categories loaded:', seenIds.size);
                categorySelect.disabled = false;
            } else {
                console.warn('No categories found for type:', typeId);
            }
        } catch (error) {
            console.error('Error in updateCategories:', error);
            showAlert('danger', 'Не удалось загрузить категории');
        }
    }
}

async function updateSubcategories() {
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    if (!categorySelect || !subcategorySelect) {
        console.error('Category or subcategory select not found');
        return;
    }
    const categoryId = categorySelect.value;
    console.log('updateSubcategories called with categoryId:', categoryId);
    // Полная очистка списка подкатегорий
    subcategorySelect.innerHTML = '';
    subcategorySelect.innerHTML = '<option value="">Выберите подкатегорию...</option>';
    subcategorySelect.disabled = !categoryId;
    if (categoryId) {
        try {
            console.log('Loading subcategories for category:', categoryId);
            const data = await apiRequest(`categories/${categoryId}/subcategories/`);
            console.log('Subcategories data:', data);
            if (data && data.length > 0) {
                // Проверяем на дубликаты перед добавлением
                const seenIds = new Set();
                data.forEach(subcategory => {
                    if (!seenIds.has(subcategory.id)) {
                        subcategorySelect.innerHTML += `<option value="${subcategory.id}">${subcategory.name}</option>`;
                        seenIds.add(subcategory.id);
                        console.log('Added subcategory:', subcategory.name);
                    } else {
                        console.warn('Duplicate subcategory skipped:', subcategory.name);
                    }
                });
                console.log('Subcategories loaded:', seenIds.size);
                subcategorySelect.disabled = false;
            } else {
                console.warn('No subcategories found for category:', categoryId);
            }
        } catch (error) {
            console.error('Error in updateSubcategories:', error);
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