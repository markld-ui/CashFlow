// static/js/transactions.js

async function loadTransactions(page = 1) {
    toggleLoading(true);
    try {
        const filters = getFilters();
        const queryString = new URLSearchParams({ ...filters, page }).toString();
        const data = await apiRequest(`transactions/?${queryString}`);
        
        renderTransactions(data.results);
        renderPagination(data);
        updateStatistics();
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить транзакции');
    } finally {
        toggleLoading(false);
    }
}

function getFilters() {
    const filters = {};
    const inputs = document.querySelectorAll('.filter-input');
    inputs.forEach(input => {
        if (input.value) {
            filters[input.id.replace('filter-', '')] = input.value;
        }
    });
    return filters;
}

function renderTransactions(transactions) {
    const tbody = document.getElementById('transactions-body');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (transactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-5">
                    <div class="text-muted">
                        <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                        Нет транзакций для отображения
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-center">${formatDate(transaction.transaction_date)}</td>
            <td>${transaction.status_name}</td>
            <td>${transaction.transaction_type_name}</td>
            <td>${transaction.category_name}</td>
            <td>${transaction.subcategory_name}</td>
            <td class="text-end">${formatAmount(transaction.amount)}</td>
            <td>${transaction.comment || '-'}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-primary me-1" 
                        onclick="loadTransactionForm(${transaction.id})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" 
                        onclick="deleteTransaction(${transaction.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderPagination(data) {
    const pagination = document.getElementById('pagination');
    const paginationInfo = document.getElementById('pagination-info');
    if (!pagination || !paginationInfo) return;

    const currentPage = data.current_page || 1;
    const totalPages = data.total_pages || 1;
    const totalCount = data.count || 0;
    const startIndex = data.start_index || 0;
    const endIndex = data.end_index || 0;

    paginationInfo.textContent = `Показано ${startIndex}–${endIndex} из ${totalCount} записей`;

    pagination.innerHTML = '';
    const prevDisabled = !data.previous ? 'disabled' : '';
    const nextDisabled = !data.next ? 'disabled' : '';

    pagination.innerHTML = `
        <li class="page-item ${prevDisabled}">
            <a class="page-link" href="#" onclick="loadTransactions(${currentPage - 1}); return false;">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;

    const pageRange = Array.from({ length: totalPages }, (_, i) => i + 1);
    pageRange.forEach(page => {
        pagination.innerHTML += `
            <li class="page-item ${page === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadTransactions(${page}); return false;">${page}</a>
            </li>
        `;
    });

    pagination.innerHTML += `
        <li class="page-item ${nextDisabled}">
            <a class="page-link" href="#" onclick="loadTransactions(${currentPage + 1}); return false;">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;
}

async function updateStatistics() {
    try {
        const filters = getFilters();
        const data = await apiRequest(`transactions/summary/?${new URLSearchParams(filters)}`);
        document.getElementById('total-count').textContent = data.summary.total_count || 0;
        document.getElementById('total-income').textContent = formatAmount(
            data.by_type.find(t => t.transaction_type_name.includes('Пополнение'))?.total || 0
        );
        document.getElementById('total-expense').textContent = formatAmount(
            data.by_type.find(t => t.transaction_type_name.includes('Списание'))?.total || 0
        );
        document.getElementById('total-balance').textContent = formatAmount(
            (data.by_type.find(t => t.transaction_type_name.includes('Пополнение'))?.total || 0) -
            (data.by_type.find(t => t.transaction_type_name.includes('Списание'))?.total || 0)
        );
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить статистику');
    }
}

async function loadFilterOptions() {
    try {
        const data = await apiRequest('reference-data/');
        
        const statusSelect = document.getElementById('filter-status');
        const typeSelect = document.getElementById('filter-type');
        const categorySelect = document.getElementById('filter-category');
        const subcategorySelect = document.getElementById('filter-subcategory');

        if (statusSelect) {
            statusSelect.innerHTML = '<option value="">Все статусы</option>';
            data.statuses.forEach(status => {
                statusSelect.innerHTML += `<option value="${status.id}">${status.name}</option>`;
            });
        }

        if (typeSelect) {
            typeSelect.innerHTML = '<option value="">Все типы</option>';
            data.transaction_types.forEach(type => {
                typeSelect.innerHTML += `<option value="${type.id}">${type.name}</option>`;
            });
        }

        if (categorySelect) {
            categorySelect.innerHTML = '<option value="">Все категории</option>';
            data.categories.forEach(category => {
                categorySelect.innerHTML += `<option value="${category.id}">${category.name}</option>`;
            });
        }

        if (subcategorySelect) {
            subcategorySelect.innerHTML = '<option value="">Все подкатегории</option>';
            data.subcategories.forEach(subcategory => {
                subcategorySelect.innerHTML += `<option value="${subcategory.id}">${subcategory.name}</option>`;
            });
        }
    } catch (error) {
        showAlert('danger', 'Не удалось загрузить опции фильтров');
    }
}

function applyFilters() {
    loadTransactions(1);
}

function resetFilters() {
    document.querySelectorAll('.filter-input').forEach(input => {
        input.value = '';
    });
    loadTransactions(1);
}

async function deleteTransaction(id) {
    if (!confirm('Вы уверены, что хотите удалить эту транзакцию?')) return;
    
    try {
        await apiRequest(`transactions/${id}/`, 'DELETE');
        showAlert('success', 'Транзакция успешно удалена');
        loadTransactions();
    } catch (error) {
        showAlert('danger', 'Не удалось удалить транзакцию');
    }
}

function loadTransactionForm(id = null) {
    console.log('loadTransactionForm called with id:', id); // Для отладки
    window.location.href = id ? `/transaction/${id}/` : '/transaction/';
}

window.loadTransactions = loadTransactions;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.loadTransactionForm = loadTransactionForm;
window.deleteTransaction = deleteTransaction;
window.loadFilterOptions = loadFilterOptions;
window.updateStatistics = updateStatistics;