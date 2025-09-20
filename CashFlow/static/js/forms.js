async function initializeTransactionForm(transactionId = null) {
  console.log("initializeTransactionForm called with id:", transactionId);
  toggleLoading(true);
  try {
    await loadFormOptions();

    const typeSelect = document.getElementById("transaction_type");
    const categorySelect = document.getElementById("category");

    // Навешиваем обработчики один раз
    if (typeSelect && !typeSelect.dataset.listener) {
      typeSelect.addEventListener("change", updateCategories);
      typeSelect.dataset.listener = "true";
      console.log("transaction_type listener added");
    }

    if (categorySelect && !categorySelect.dataset.listener) {
      categorySelect.addEventListener("change", updateSubcategories);
      categorySelect.dataset.listener = "true";
      console.log("category listener added");
    }

    setupFormValidation();

    // Очищаем форму для новой транзакции
    if (!transactionId) {
      const form = document.getElementById("transaction-form");
      if (form) form.reset();
      document.getElementById("transaction-id").value = "";
      const categorySelect = document.getElementById("category");
      const subcategorySelect = document.getElementById("subcategory");
      if (categorySelect) {
        categorySelect.innerHTML = '<option value="">Выберите категорию...</option>';
        categorySelect.disabled = true;
      }
      if (subcategorySelect) {
        subcategorySelect.innerHTML = '<option value="">Выберите подкатегорию...</option>';
        subcategorySelect.disabled = true;
      }
    }

    // Загружаем данные только для редактирования (если transactionId - число)
    if (transactionId && !isNaN(parseInt(transactionId))) {
      await loadTransactionData(transactionId);
    }
  } catch (error) {
    console.error("Error in initializeTransactionForm:", error);
    showAlert("danger", "Не удалось инициализировать форму");
  } finally {
    toggleLoading(false);
  }
}

async function loadFormOptions() {
  try {
    console.log("Loading form options...");
    const data = await apiRequest("reference-data/");
    console.log("Reference data:", data);

    fillSelect("status", data.statuses, "Выберите статус...");
    fillSelect("transaction_type", data.transaction_types, "Выберите тип...");
  } catch (error) {
    console.error("Error in loadFormOptions:", error);
    showAlert("danger", "Не удалось загрузить данные для формы");
  }
}

// Универсальная функция для заполнения select
function fillSelect(elementId, items, placeholder) {
  const select = document.getElementById(elementId);
  if (!select) {
    console.error(`Element with id "${elementId}" not found`);
    return;
  }

  select.innerHTML = `<option value="">${placeholder}</option>`;
  if (items && items.length > 0) {
    const seen = new Set();
    items.forEach((item) => {
      if (!seen.has(item.id)) {
        select.innerHTML += `<option value="${item.id}">${item.name}</option>`;
        seen.add(item.id);
      }
    });
  }
}

async function loadTransactionData(id) {
  try {
    console.log("Loading transaction data for id:", id);
    const transaction = await apiRequest(`transactions/${id}/`);
    console.log("Transaction data:", transaction);

    const setValue = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.value = value ?? "";
    };

    setValue("transaction-id", transaction.id);
    setValue("transaction_date", transaction.transaction_date);
    setValue("status", transaction.status);
    setValue("transaction_type", transaction.transaction_type);
    setValue("amount", transaction.amount);
    setValue("comment", transaction.comment);

    await updateCategories(transaction.category, transaction.subcategory);
  } catch (error) {
    console.error("Error in loadTransactionData:", error);
    showAlert("danger", "Не удалось загрузить данные транзакции");
  }
}

// Поддержка установки выбранных значений при инициализации
async function updateCategories(
  selectedCategoryId = null,
  selectedSubcategoryId = null
) {
  const typeSelect = document.getElementById("transaction_type");
  const categorySelect = document.getElementById("category");
  const subcategorySelect = document.getElementById("subcategory");

  if (!typeSelect || !categorySelect || !subcategorySelect) return;

  const typeId = typeSelect.value;
  categorySelect.disabled = !typeId;
  subcategorySelect.disabled = true;
  categorySelect.innerHTML = '<option value="">Выберите категорию...</option>';
  subcategorySelect.innerHTML =
    '<option value="">Выберите подкатегорию...</option>';

  if (!typeId) return;

  try {
    const data = await apiRequest(`transaction-types/${typeId}/categories/`);
    fillSelect("category", data || [], "Выберите категорию...");
    categorySelect.disabled = false;


    if (selectedCategoryId) categorySelect.value = selectedCategoryId;

    if (selectedCategoryId) {
      await updateSubcategories(selectedSubcategoryId);
    }
  } catch (error) {
    console.error("Error in updateCategories:", error);
    showAlert("danger", "Не удалось загрузить категории");
  }
}

async function updateSubcategories(selectedSubcategoryId = null) {
  const categorySelect = document.getElementById("category");
  const subcategorySelect = document.getElementById("subcategory");

  if (!categorySelect || !subcategorySelect) return;

  const categoryId = categorySelect.value;
  subcategorySelect.disabled = !categoryId;
  subcategorySelect.innerHTML =
    '<option value="">Выберите подкатегорию...</option>';

  if (!categoryId) return;

  try {
    const data = await apiRequest(`categories/${categoryId}/subcategories/`);
    fillSelect("subcategory", data || [], "Выберите подкатегорию...");
    subcategorySelect.disabled = false;

    if (selectedSubcategoryId) subcategorySelect.value = selectedSubcategoryId;
  } catch (error) {
    console.error("Error in updateSubcategories:", error);
    showAlert("danger", "Не удалось загрузить подкатегории");
  }
}

function setupFormValidation() {
  const form = document.getElementById("transaction-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      return;
    }

    const amountValue = parseFloat(document.getElementById("amount").value);
    const data = {
      transaction_date: document.getElementById("transaction_date").value,
      status: document.getElementById("status").value,
      transaction_type: document.getElementById("transaction_type").value,
      category: document.getElementById("category").value,
      subcategory: document.getElementById("subcategory").value,
      amount: isNaN(amountValue) ? 0 : amountValue,
      comment: document.getElementById("comment").value,
    };

    const id = document.getElementById("transaction-id").value;

    try {
      toggleLoading(true);
      if (id) 
      {
        await apiRequest(`transactions/${id}/`, "PUT", data);
      } 
      else 
      {
        await apiRequest("transactions/", "POST", data);
      }
      window.location.href = "/";
    } catch (error) {
      console.error("Error saving transaction:", error);
      showAlert("danger", "Не удалось сохранить транзакцию");
    } finally {
      toggleLoading(false);
    }
  });
}

function formatAmount(input) {
  const value = parseFloat(input.value);
  if (!isNaN(value)) {
    input.value = value.toFixed(2);
  }
}

window.initializeTransactionForm = initializeTransactionForm;
window.updateCategories = updateCategories;
window.updateSubcategories = updateSubcategories;
window.formatAmount = formatAmount;
