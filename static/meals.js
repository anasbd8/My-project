(function () {
  // Ingredient row used on the edit meal page, where foods are typed by name.
  function buildEditMealIngredientRow() {
    return `
      <div class="col-7">
        <input type="text" class="form-control" name="food_name[]"
               list="food-options" placeholder="Search food..." required autocomplete="off">
      </div>
      <div class="col-4">
        <input type="number" class="form-control" name="amount[]"
               placeholder="Amount (g)" step="0.1" required>
      </div>
      <div class="col-1 d-flex align-items-center">
        <span class="remove-btn" data-remove-closest=".ingredient-row">✕</span>
      </div>
    `;
  }

  // Match the typed food name to the hidden select used for macro math.
  function syncSearchToSelect(row) {
    const searchInput = row.querySelector(".food-search-input");
    const hiddenSelect = row.querySelector(".food-select-hidden");
    if (!searchInput || !hiddenSelect) return;

    const typed = searchInput.value.trim().toLowerCase();
    let found = false;

    for (const option of hiddenSelect.options) {
      if (option.value.toLowerCase() === typed) {
        hiddenSelect.value = option.value;
        found = true;
        break;
      }
    }

    if (!found) hiddenSelect.value = "";
    updateMacroSummary();
  }

  // Recalculate the create-meal modal summary from the current ingredient rows.
  function updateMacroSummary() {
    let totalCalories = 0;
    let totalProtein = 0;
    let totalFat = 0;
    let totalCarbs = 0;
    let hasData = false;

    document
      .querySelectorAll("#ingredients-container .ingredient-row")
      .forEach(function (row) {
        const hiddenSelect = row.querySelector(".food-select-hidden");
        const amountInput = row.querySelector(".amount-input");
        if (!hiddenSelect || !amountInput) return;

        const option = hiddenSelect.options[hiddenSelect.selectedIndex];
        const amount = parseFloat(amountInput.value);

        if (option && option.value && amount > 0) {
          totalCalories += (parseFloat(option.dataset.calories || 0) * amount) / 100;
          totalProtein += (parseFloat(option.dataset.protein || 0) * amount) / 100;
          totalFat += (parseFloat(option.dataset.fat || 0) * amount) / 100;
          totalCarbs += (parseFloat(option.dataset.carbs || 0) * amount) / 100;
          hasData = true;
        }
      });

    const summary = document.getElementById("modal-macro-summary");
    if (!summary) return;

    summary.classList.toggle("ui-hidden", !hasData);
    document.getElementById("summary-calories").textContent =
      Math.round(totalCalories) + " kcal";
    document.getElementById("summary-protein").textContent =
      totalProtein.toFixed(1) + " g";
    document.getElementById("summary-fat").textContent = totalFat.toFixed(1) + " g";
    document.getElementById("summary-carbs").textContent =
      totalCarbs.toFixed(1) + " g";
  }

  // Keep the hidden select in sync as the user types ingredient names.
  function initIngredientSync() {
    const container = document.getElementById("ingredients-container");
    if (!container) return;

    container.addEventListener("input", function (event) {
      const row = event.target.closest(".ingredient-row");
      if (row) syncSearchToSelect(row);
    });
  }

  // Add a new ingredient row for either edit-meal or create-meal flows.
  function initAddIngredientButton() {
    const button = document.getElementById("add-ingredient-btn");
    const container = document.getElementById("ingredients-container");
    if (!button || !container) return;

    button.addEventListener("click", function () {
      const hiddenSelect = container.querySelector(".food-select-hidden");
      if (!hiddenSelect) {
        const row = document.createElement("div");
        row.className = "row g-2 mb-2 ingredient-row";
        row.innerHTML = buildEditMealIngredientRow();
        container.appendChild(row);
        return;
      }

      const firstRow = container.querySelector(".ingredient-row");
      if (!firstRow) return;

      const newRow = document.createElement("div");
      newRow.className = "row g-2 mb-2 ingredient-row";

      const cloned = firstRow.cloneNode(true);
      cloned.querySelector(".food-search-input").value = "";
      cloned.querySelector(".food-select-hidden").value = "";
      cloned.querySelector(".amount-input").value = "";
      newRow.innerHTML = cloned.innerHTML;

      const removeCol = document.createElement("div");
      removeCol.className = "col-1 d-flex align-items-center";
      removeCol.innerHTML = '<span class="remove-btn" data-remove-closest=".ingredient-row">✕</span>';
      newRow.appendChild(removeCol);

      container.appendChild(newRow);
    });
  }

  // Clear the create-meal modal back to its initial single-row state.
  function initModalReset() {
    const modal = document.getElementById("createMealModal");
    const container = document.getElementById("ingredients-container");
    const summary = document.getElementById("modal-macro-summary");
    if (!modal || !container || !summary) return;

    modal.addEventListener("hidden.bs.modal", function () {
      summary.classList.add("ui-hidden");
      const rows = container.querySelectorAll(".ingredient-row");
      rows.forEach(function (row, index) {
        if (index > 0) row.remove();
      });
      container.querySelectorAll("input, select").forEach(function (el) {
        el.value = "";
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initIngredientSync();
    initAddIngredientButton();
    initModalReset();
  });
})();
