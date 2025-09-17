// static/js/references.js
import { apiRequest, showAlert, toggleLoading } from './app.js';

async function initializeReferences() {
    try {
        toggleLoading(true);
        await Promise.all([
            loadReferences('statuses'),
            loadReferences('transaction-types'),
            loadReferences('categories'),
            loadReferences('subcategories')
        ]);
        loadFilterOptions();
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить справочники');
    } finally {
        toggleLoading(false);
    }
}

async function loadReferences(endpoint) {
    try {
        const data = await apiRequest(`${endpoint}/`);
        const tableBody = document.getElementById(endpoint.replace('api/', '').replace('/', '') + '-table');
        if (!tableBody) return;

        tableBody.innerHTML = '';
        if (data.results.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-4">
                        <div class="text-muted">
                            <i class="bi bi-database fs-1 d-block mb-2"></i>
                            Нет данных
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        data.results.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                ${endpoint.includes('statuses') || endpoint.includes('transaction-types') ? 
                    `<td>${item.name}</td><td>${item.description || '-'}</td>` :
                    endpoint.includes('categories') ? 
                    `<td>${item.name}</td><td>${item.transaction_type_name}</td><td>${item.description || '-'}</td>` :
                    `<td>${item.name}</td><td>${item.category_name}</td><td>${item.description || '-'}</td>`}
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
            tableBody.appendChild(row);
        });
    } catch (error) {
        showAlert('danger', `Не удалось загрузить ${endpoint}`);
    }
}

async function loadFilterOptions() {
    try {
        const data = await apiRequest('reference-data/');
        
        // Заполнение фильтров для категорий
        const categoryFilter = document.querySelector('#categories select');
        if (categoryFilter) {
            categoryFilter.innerHTML = '<option value="">Все типы операций</option>';
            data.transaction_types.forEach(type => {
                categoryFilter.innerHTML += `<option value="${type.id}">${type.name}</option>`;
            });
        }

        // Заполнение фильтров для подкатегорий
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
    modal.show();
}

async function showEditModal(endpoint, id) {
    try {
        const data = await apiRequest(`${endpoint}/${id}/`);
        const modal = new bootstrap.Modal(document.getElementById('referenceModal'));
        document.getElementById('modalTitle').textContent = 'Редактировать запись';
        document.getElementById('referenceId').value = id;
        document.getElementById('referenceApiUrl').value = endpoint;
        
        document.getElementById('modalName').value = data.name || '';
        document.getElementById('modalDescription').value = data.description || '';
        
        if (endpoint.includes('categories')) {
            const typeSelect = document.getElementById('modalTransactionType');
            typeSelect.innerHTML = '';
            const types = await apiRequest('transaction-types/');
            types.results.forEach(type => {
                typeSelect.innerHTML += `<option value="${type.id}" ${type.id === data.transaction_type ? 'selected' : ''}>${type.name}</option>`;
            });
        }
        
        if (endpoint.includes('subcategories')) {
            const categorySelect = document.getElementById('modalCategory');
            categorySelect.innerHTML = '';
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
        if (id) {
            await apiRequest(`${endpoint}/${id}/`, 'PUT', data);
            showAlert('success', 'Запись успешно обновлена');
        } else {
            await apiRequest(`${endpoint}/`, 'POST', data);
            showAlert('success', 'Запись успешно создана');
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

    try {
        await apiRequest(`${endpoint}/${id}/`, 'DELETE');
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