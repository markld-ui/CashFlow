async function initializeReferences() {
    try {
        toggleLoading(true);
        await Promise.all([
            loadReferences('statuses'),
            loadReferences('transaction-types'),
            loadReferences('categories'),
            loadReferences('subcategories')
        ]);
        await loadFilterOptions();
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить справочники');
    } finally {
        toggleLoading(false);
    }
}

async function loadReferences(endpoint, query = '') {
    try {
        const tableBody = document.getElementById(endpoint.replace('api/', '').replace('/', '') + '-table');
        if (!tableBody) return;

        // Загружаем справочные данные для transaction_type и category
        let apiEndpoint = endpoint;
        if (endpoint === 'statuses') apiEndpoint = 'statuses';
        if (endpoint === 'transaction-types') apiEndpoint = 'transaction-types';
        if (endpoint === 'categories') apiEndpoint = 'categories';
        if (endpoint === 'subcategories') apiEndpoint = 'subcategories';

        let apiQuery = query;
        if (query && query.startsWith('/')) {
            apiQuery = query.substring(1);
        }

        const referenceData = await apiRequest('reference-data/');
        const data = await apiRequest(`${endpoint}${apiQuery}`);

        tableBody.innerHTML = '';
        if (!data.results || data.results.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="${tableBody.getAttribute('data-fields').split(',').length + 1}" class="text-center py-4">
                        <div class="text-muted">
                            <i class="bi bi-database fs-1 d-block mb-2"></i>
                            Нет данных
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        const fields = tableBody.getAttribute('data-fields').split(',');
        const extraFields = tableBody.getAttribute('data-extra-fields')?.split(',') || [];
        const seenIds = new Set(); // Проверка дубликатов

        data.results.forEach(item => {
            if (seenIds.has(item.id)) {
                console.warn('Duplicate item skipped:', item);
                return;
            }
            seenIds.add(item.id);

            const row = document.createElement('tr');
            let rowHtml = '';

            fields.forEach(field => {
                let value = item[field] || '-';
                // Заменяем ID на имена для extra_fields
                if (extraFields.includes(field)) {
                    if (field === 'transaction_type' && referenceData.transaction_types) {
                        const type = referenceData.transaction_types.find(t => t.id === value);
                        value = type ? type.name : value;
                    } else if (field === 'category' && referenceData.categories) {
                        const category = referenceData.categories.find(c => c.id === value);
                        value = category ? category.name : value;
                    }
                }
                rowHtml += `<td>${value}</td>`;
            });

            rowHtml += `
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary me-1" 
                            onclick="showEditModal('${endpoint}', ${item.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="showDeleteModal('${endpoint}', ${item.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            row.innerHTML = rowHtml;
            tableBody.appendChild(row);
        });
    } catch (error) {
        showAlert('danger', `Не удалось загрузить ${endpoint}`);
    }
}

async function loadFilterOptions() {
    try {
        const data = await apiRequest('reference-data/');
        
        const categoryFilter = document.querySelector('#categories select');
        if (categoryFilter) {
            categoryFilter.innerHTML = '<option value="">Все типы операций</option>';
            data.transaction_types.forEach(type => {
                categoryFilter.innerHTML += `<option value="${type.id}">${type.name}</option>`;
            });
        }

        const subcategoryFilter = document.querySelector('#subcategories select');
        if (subcategoryFilter) {
            subcategoryFilter.innerHTML = '<option value="">Все категории</option>';
            data.categories.forEach(category => {
                subcategoryFilter.innerHTML += `<option value="${category.id}">${category.name}</option>`;
            });
        }
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить опции фильтров');
    }
}

function showAddModal(endpoint) {
    const modal = new bootstrap.Modal(document.getElementById('referenceModal'));
    document.getElementById('modalTitle').textContent = 'Добавить запись';
    document.getElementById('referenceId').value = '';
    document.getElementById('referenceApiUrl').value = endpoint;
    document.getElementById('referenceForm').reset();
    
    // Очищаем select'ы для categories и subcategories
    const typeSelect = document.getElementById('modalTransactionType');
    const categorySelect = document.getElementById('modalCategory');
    if (typeSelect) typeSelect.innerHTML = '<option value="">Выберите тип...</option>';
    if (categorySelect) categorySelect.innerHTML = '<option value="">Выберите категорию...</option>';
    
    modal.show();
}

async function showEditModal(endpoint, id) {
    try {
        let apiEndpoint = endpoint;
        if (endpoint === 'statuses') apiEndpoint = 'statuses';
        if (endpoint === 'transaction-types') apiEndpoint = 'transaction-types';
        if (endpoint === 'categories') apiEndpoint = 'categories';
        if (endpoint === 'subcategories') apiEndpoint = 'subcategories';

        const data = await apiRequest(`${endpoint}/${id}/`);
        const modal = new bootstrap.Modal(document.getElementById('referenceModal'));
        document.getElementById('modalTitle').textContent = 'Редактировать запись';
        document.getElementById('referenceId').value = id;
        document.getElementById('referenceApiUrl').value = endpoint;
        
        document.getElementById('modalName').value = data.name || '';
        document.getElementById('modalDescription').value = data.description || '';
        
        if (endpoint.includes('categories')) {
            const typeSelect = document.getElementById('modalTransactionType');
            typeSelect.innerHTML = '<option value="">Выберите тип...</option>';
            const types = await apiRequest('transaction-types/');
            types.results.forEach(type => {
                typeSelect.innerHTML += `<option value="${type.id}" ${type.id === data.transaction_type ? 'selected' : ''}>${type.name}</option>`;
            });
        }
        
        if (endpoint.includes('subcategories')) {
            const categorySelect = document.getElementById('modalCategory');
            categorySelect.innerHTML = '<option value="">Выберите категорию...</option>';
            const categories = await apiRequest('categories/');
            categories.results.forEach(category => {
                categorySelect.innerHTML += `<option value="${category.id}" ${category.id === data.category ? 'selected' : ''}>${category.name}</option>`;
            });
        }
        
        modal.show();
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить данные для редактирования');
    }
}

function showDeleteModal(endpoint, id) {
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    document.getElementById('deleteModal').dataset.endpoint = endpoint;
    document.getElementById('deleteModal').dataset.id = id;
    modal.show();
}

async function saveReference() {
    const endpoint = document.getElementById('referenceApiUrl').value;
    const id = document.getElementById('referenceId').value;

    let apiEndpoint = endpoint;
    if (endpoint === 'statuses') apiEndpoint = 'statuses';
    if (endpoint === 'transaction-types') apiEndpoint = 'transaction-types';
    if (endpoint === 'categories') apiEndpoint = 'categories';
    if (endpoint === 'subcategories') apiEndpoint = 'subcategories';

    const data = {
        name: document.getElementById('modalName').value,
        description: document.getElementById('modalDescription').value
    };

    if (endpoint.includes('categories')) {
        data.transaction_type = document.getElementById('modalTransactionType').value;
    }
    if (endpoint.includes('subcategories')) {
        data.category = document.getElementById('modalCategory').value;
    }

    try {
        if (id) 
        {
            await apiRequest(`${apiEndpoint}/${id}/`, 'PUT', data);
        }
        else
        {
            await apiRequest(`${apiEndpoint}/`, 'POST', data);
        }
        loadReferences(endpoint);
        bootstrap.Modal.getInstance(document.getElementById('referenceModal')).hide();
    } catch (error) {
        showAlert('danger', 'Не удалось сохранить запись');
    }
}

async function confirmDelete() {
    const modal = document.getElementById('deleteModal');
    const endpoint = modal.dataset.endpoint;
    const id = modal.dataset.id;

    let apiEndpoint = endpoint;
    if (endpoint === 'statuses') apiEndpoint = 'statuses';
    if (endpoint === 'transaction-types') apiEndpoint = 'transaction-types';
    if (endpoint === 'categories') apiEndpoint = 'categories';
    if (endpoint === 'subcategories') apiEndpoint = 'subcategories';

    try {
        await apiRequest(`${apiEndpoint}/${id}/`, 'DELETE');
        showAlert('success', 'Запись успешно удалена');
        loadReferences(endpoint);
        bootstrap.Modal.getInstance(modal).hide();
    } catch (error) {
        showAlert('danger', 'Не удалось удалить запись');
    }
}

async function filterReferences(endpoint, search) {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    await loadReferences(`${endpoint}${query}`);
}

async function filterByRelation(endpoint, value) {
    const query = value ? `?${endpoint.includes('categories') ? 'transaction_type' : 'category'}=${value}` : '';
    await loadReferences(`${endpoint}${query}`);
}

window.initializeReferences = initializeReferences;
window.showAddModal = showAddModal;
window.showEditModal = showEditModal;
window.showDeleteModal = showDeleteModal;
window.saveReference = saveReference;
window.confirmDelete = confirmDelete;
window.filterReferences = filterReferences;
window.filterByRelation = filterByRelation;