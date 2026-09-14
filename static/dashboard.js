(function () {
  const TOTAL_GLASSES = 8;
  const MEAL_CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snack"];

  // Render the half-doughnut calorie gauge on the dashboard hero card.
  function initGauge() {
    const gaugeCanvas = document.getElementById("calorieGaugeChart");
    if (!gaugeCanvas || typeof Chart === "undefined") return;

    const calories = Number(gaugeCanvas.dataset.calories || 0);
    const calorieGoal = Number(gaugeCanvas.dataset.calorieGoal || 0);
    const consumed = Math.max(0, Math.min(calories, calorieGoal || calories));
    const remaining = Math.max((calorieGoal || 0) - consumed, 0);

    new Chart(gaugeCanvas, {
      type: "doughnut",
      data: {
        datasets: [
          {
            data: calorieGoal > 0 ? [consumed, remaining] : [1],
            backgroundColor:
              calorieGoal > 0
                ? ["#00a4d1", "rgba(255, 255, 255, 0.92)"]
                : ["rgba(255, 255, 255, 0.92)"],
            borderWidth: 0,
            cutout: "78%",
            circumference: 180,
            rotation: 270,
            borderRadius: 10,
          },
        ],
      },
      options: {
        responsive: false,
        animation: {
          duration: 700,
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            enabled: false,
          },
        },
        events: [],
      },
    });
  }

  // Build and persist the clickable water glasses tracker.
  function initWaterTracker() {
    const wrap = document.getElementById("waterGlasses");
    const count = document.getElementById("waterCount");
    if (!wrap || !count) return;
    
    let filled = Number(document.body.dataset.waterToday || 0);
    const updateUrl = wrap.dataset.updateUrl;

    function saveWater() {
      if (!updateUrl) return;

      const formData = new FormData();
      formData.append("glasses", filled);
      fetch(updateUrl, {
        method: "POST",
        body: formData,
      });
    }

    function renderGlasses() {
      wrap.innerHTML = "";

      for (let i = 0; i < TOTAL_GLASSES; i += 1) {
        const glass = document.createElement("button");
        glass.className = "glass" + (i < filled ? " filled" : "");
        glass.innerHTML = `<i class="bi ${i < filled ? "bi-cup-straw" : "bi-cup"}"></i>`;
        glass.title = i < filled ? "Click to remove" : "Click to add";
        glass.addEventListener("click", function () {
          filled = i < filled ? i : i + 1;
          renderGlasses();
          saveWater();
        });
        wrap.appendChild(glass);
      }

      count.innerHTML = `${filled} / ${TOTAL_GLASSES} <small style="font-size:.75em; opacity:.7;">250ml/glass</small>`;
    }

    renderGlasses();
  }

  // Reset modal forms so repeated openings start from a clean state.
  function initModalResets() {
    document.querySelectorAll(".modal").forEach(function (modal) {
      modal.addEventListener("hidden.bs.modal", function () {
        modal.querySelectorAll("form").forEach(function (form) {
          form.reset();
        });
      });
    });
  }

  // Recalculate the live macro preview for one meal category modal.
  function updateCaloriePreview(category) {
    const container = document.getElementById(`ingredients-container-${category}`);
    const preview = document.getElementById(`calorie-preview-${category}`);
    if (!container || !preview) return;

    let totalCal = 0;
    let totalProt = 0;
    let totalFat = 0;
    let totalCarbs = 0;
    let hasData = false;

    container.querySelectorAll(".ingredient-row").forEach(function (row) {
      const select = row.querySelector(".food-select-live");
      const amount = parseFloat(row.querySelector('input[name="amount[]"]')?.value) || 0;
      if (!select) return;

      const opt = select.options[select.selectedIndex];
      if (opt && opt.value && amount > 0) {
        totalCal += (parseFloat(opt.dataset.calories || 0) * amount) / 100;
        totalProt += (parseFloat(opt.dataset.protein || 0) * amount) / 100;
        totalFat += (parseFloat(opt.dataset.fat || 0) * amount) / 100;
        totalCarbs += (parseFloat(opt.dataset.carbs || 0) * amount) / 100;
        hasData = true;
      }
    });

    if (hasData) {
      preview.querySelector(".calorie-preview-value").textContent = Math.round(totalCal);
      preview.querySelector(".protein-preview-value").textContent = totalProt.toFixed(1);
      preview.querySelector(".fat-preview-value").textContent = totalFat.toFixed(1);
      preview.querySelector(".carbs-preview-value").textContent = totalCarbs.toFixed(1);
      preview.classList.remove("ui-hidden");
    } else {
      preview.classList.add("ui-hidden");
    }
  }

  // Watch each meal modal for ingredient and amount changes.
  function initMealPreviewHandlers() {
    MEAL_CATEGORIES.forEach(function (category) {
      const container = document.getElementById(`ingredients-container-${category}`);
      if (!container) return;

      container.addEventListener("change", function (event) {
        if (event.target.tagName === "SELECT") {
          updateCaloriePreview(category);
        }
      });

      container.addEventListener("input", function (event) {
        if (event.target.tagName === "INPUT") {
          updateCaloriePreview(category);
        }
      });
    });
  }

  // Toggle the inline amount edit form for one logged ingredient.
  function toggleEdit(id) {
    const form = document.getElementById(id);
    if (!form) return;
    form.classList.toggle("ui-hidden");
  }

  // Clone one ingredient row inside a meal modal.
  function addIngredientRow(category) {
    const container = document.getElementById(`ingredients-container-${category}`);
    if (!container) return;

    const firstRow = container.querySelector(".ingredient-row");
    if (!firstRow) return;

    const newRow = document.createElement("div");
    newRow.classList.add("row", "g-2", "mb-2", "ingredient-row");

    const cloned = firstRow.cloneNode(true);
    cloned.querySelector("select").selectedIndex = 0;
    cloned.querySelector("input").value = "";
    newRow.innerHTML = cloned.innerHTML;

    const removeCol = document.createElement("div");
    removeCol.className = "col-1 d-flex align-items-center";
    removeCol.innerHTML = '<span class="remove-btn">✕</span>';
    removeCol.querySelector("span").addEventListener("click", function () {
      newRow.remove();
      updateCaloriePreview(category);
    });
    newRow.appendChild(removeCol);

    container.appendChild(newRow);
  }

  // Route data-attribute driven buttons to their dashboard helpers.
  function initMealActions() {
    document.addEventListener("click", function (event) {
      const editTrigger = event.target.closest("[data-toggle-edit-id]");
      if (editTrigger) {
        toggleEdit(editTrigger.dataset.toggleEditId);
        return;
      }

      const addTrigger = event.target.closest("[data-add-ingredient-row]");
      if (addTrigger) {
        addIngredientRow(addTrigger.dataset.addIngredientRow);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initGauge();
    initWaterTracker();
    initModalResets();
    initMealPreviewHandlers();
    initMealActions();
  });
})();
