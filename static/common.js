(function () {
  // Auto-hide flash messages after a short delay.
  function initAlerts() {
    window.setTimeout(function () {
      document.querySelectorAll(".alert").forEach(function (el) {
        el.style.display = "none";
      });
    }, 3000);
  }

  // Centralize confirm dialogs via data-confirm on forms.
  function initConfirmations() {
    document.addEventListener(
      "submit",
      function (event) {
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) return;

        const message = form.dataset.confirm;
        if (!message) return;

        if (!window.confirm(message)) {
          event.preventDefault();
        }
      },
      true,
    );
  }

  // Let simple remove buttons delete their nearest matching wrapper.
  function initRemoveClosest() {
    document.addEventListener("click", function (event) {
      const trigger = event.target.closest("[data-remove-closest]");
      if (!trigger) return;

      const selector = trigger.dataset.removeClosest;
      if (!selector) return;

      const target = trigger.closest(selector);
      if (target) {
        target.remove();
      }
    });
  }

  // Enhance birthdate fields when flatpickr is loaded on the page.
  function initBirthdatePicker() {
    if (typeof flatpickr === "undefined") return;
    if (!document.querySelector("input[name='birthdate']")) return;

    flatpickr("input[name='birthdate']", {
      dateFormat: "Y-m-d",
      maxDate: "today",
      defaultDate: "2000-01-01",
      disableMobile: true,
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initAlerts();
    initConfirmations();
    initRemoveClosest();
    initBirthdatePicker();
  });
})();
