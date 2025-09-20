let currentPage = 1;

async function loadTransactions(page = 1) {
    currentPage = page;
    toggleLoading(true);
    try {
        const filters = getFilters();
        const queryString = new URLSearchParams({ ...filters, page, page_size: 10 }).toString();
        const data = await apiRequest(`transactions/?${queryString}`);
        
        console.log('Полный ответ API:', data);
        console.log('Результаты:', data.results);
        console.log('Пагинация:', data.pagination);
        console.log('Счетчик:', data.count);
        
        renderTransactions(data.results || data);
        renderPagination(data);
        updateStatistics();
    } catch (error) {
        console.error('Error loading transactions:', error);
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
            let paramName = input.id.replace('filter-', '');
            const paramMap = {
                'type': 'transaction_type',
                'status': 'status',
                'category': 'category',
                'subcategory': 'subcategory',
                'date-from': 'date_from',
                'date-to': 'date_to',
                'amount-min': 'amount_min',
                'amount-max': 'amount_max',
                'search': 'search'
            };
            paramName = paramMap[paramName] || paramName;
            let value = input.value;
            
            if (paramName === 'date_from' || paramName === 'date_to') {
                if (value.includes('.')) {
                    const [day, month, year] = value.split('.');
                    value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                }
            }
            filters[paramName] = value;
        }
    });
    return filters;
}

function renderTransactions(transactions) {
    const tbody = document.getElementById('transactions-body');
    if (!tbody) return;

    if (!transactions || transactions.length === 0) {
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

    tbody.innerHTML = transactions.map(transaction => `
        <tr>
            <td class="text-center">${formatDate(transaction.transaction_date)}</td>
            <td><span class="badge bg-secondary">${transaction.status_name}</span></td>
            <td>${transaction.transaction_type_name}</td>
            <td>${transaction.category_name}</td>
            <td>${transaction.subcategory_name}</td>
            <td class="text-end fw-bold ${transaction.transaction_type_name === 'Пополнение' ? 'text-success' : 'text-danger'}">
                ${formatAmount(transaction.amount)}
            </td>
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
        </tr>
    `).join('');
}

function renderPagination(data) {
    const pagination = document.getElementById('pagination');
    const paginationInfo = document.getElementById('pagination-info');
    if (!pagination || !paginationInfo) return;

    const total_count = data.count || 0;
    const next_url = data.next;
    const previous_url = data.previous;
    
    // Определяем текущую страницу по URL
    let current_page = 1;
    
    if (next_url) {
        try {
            const urlObj = new URL(next_url);
            const pageParam = urlObj.searchParams.get('page');
            if (pageParam) {
                current_page = parseInt(pageParam) - 1;
            }
        } catch (e) {
            console.error('Error parsing next URL:', e);
        }
    } else if (previous_url) {
        try {
            const urlObj = new URL(previous_url);
            const pageParam = urlObj.searchParams.get('page');
            if (pageParam) {
                current_page = parseInt(pageParam) + 1;
            }
        } catch (e) {
            console.error('Error parsing previous URL:', e);
        }
    }
    
    // Обеспечиваем корректные границы
    current_page = Math.max(1, current_page);
    const total_pages = Math.ceil(total_count / 10);
    current_page = Math.min(current_page, total_pages);
    
    const start_index = (current_page - 1) * 10 + 1;
    const end_index = Math.min(current_page * 10, total_count);

    paginationInfo.textContent = `Показано ${start_index}–${end_index} из ${total_count} записей`;
    pagination.innerHTML = '';

    if (total_pages <= 1) return;

    const prevDisabled = current_page <= 1;
    const nextDisabled = current_page >= total_pages;

    // Создаем кнопки с проверкой на disabled
    const prevButton = prevDisabled ? 
        '<li class="page-item disabled"><span class="page-link"><i class="bi bi-chevron-left"></i></span></li>' :
        `<li class="page-item"><a class="page-link" href="#" onclick="loadTransactions(${current_page - 1}); return false;"><i class="bi bi-chevron-left"></i></a></li>`;
    
    const nextButton = nextDisabled ? 
        '<li class="page-item disabled"><span class="page-link"><i class="bi bi-chevron-right"></i></span></li>' :
        `<li class="page-item"><a class="page-link" href="#" onclick="loadTransactions(${current_page + 1}); return false;"><i class="bi bi-chevron-right"></i></a></li>`;
    
    pagination.innerHTML = `
        ${prevButton}
        <li class="page-item disabled">
            <span class="page-link">${current_page} / ${total_pages}</span>
        </li>
        ${nextButton}
    `;
}

async function updateStatistics() {
    try {
        const filters = getFilters();
        const queryString = new URLSearchParams(filters).toString();
        const data = await apiRequest(`transactions/summary/?${queryString}`);

        document.getElementById('total-count').textContent = data.summary?.total_count || 0;
        document.getElementById('total-income').textContent = formatAmount(data.summary?.income || 0);
        document.getElementById('total-expense').textContent = formatAmount(data.summary?.expense || 0);
        document.getElementById('total-balance').textContent = formatAmount(data.summary?.balance || 0);
    } catch (error) {
        console.error('Error updating statistics:', error);
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
        loadTransactions(currentPage);
    } catch (error) {
        showAlert('danger', 'Не удалось удалить транзакцию');
    }
}

function loadTransactionForm(id = null) {
    if (id) {
        window.location.href = `/transaction/${id}/`;
    } else {
        window.location.href = '/transaction/';
    }
}

// Утилиты форматирования
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

function formatAmount(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2
    }).format(amount);
}

function toggleLoading(show) {
    const loading = document.getElementById('loading');
    const content = document.getElementById('content');
    if (loading && content) {
        loading.style.display = show ? 'flex' : 'none';
        content.style.opacity = show ? '0.5' : '1';
    }
}

function showAlert(type, message) {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

window.loadTransactions = loadTransactions;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.loadTransactionForm = loadTransactionForm;
window.deleteTransaction = deleteTransaction;
window.loadFilterOptions = loadFilterOptions;
window.updateStatistics = updateStatistics;