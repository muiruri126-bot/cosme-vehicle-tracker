/**
 * Vehicle Request Tracker – Client-side form validation
 * Uses Bootstrap 5 validation classes (.is-invalid / .is-valid)
 */

(function () {
  "use strict";

  // ── CSRF token auto-inject ───────────────────────────────────────────────
  // Reads the token from the <meta name="csrf-token"> tag and injects a
  // hidden input into every POST form that doesn't already have one.
  var csrfMeta = document.querySelector('meta[name="csrf-token"]');
  if (csrfMeta) {
    var token = csrfMeta.getAttribute("content");
    document.querySelectorAll('form[method="POST"], form[method="post"]').forEach(function (form) {
      if (!form.querySelector('input[name="csrf_token"]')) {
        var input = document.createElement("input");
        input.type = "hidden";
        input.name = "csrf_token";
        input.value = token;
        form.appendChild(input);
      }
    });
  }

  // ── Bootstrap validated forms ────────────────────────────────────────────
  // Any form with class .needs-validation gets client-side checks.
  document.querySelectorAll("form.needs-validation").forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        // Run custom validators first
        runCustomValidators(form);

        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });

  // ── Custom validators ────────────────────────────────────────────────────

  function runCustomValidators(form) {
    // Password confirmation on register form
    var pw = form.querySelector("#password");
    var pw2 = form.querySelector("#password2");
    if (pw && pw2) {
      if (pw.value !== pw2.value) {
        pw2.setCustomValidity("Passwords do not match.");
      } else {
        pw2.setCustomValidity("");
      }
    }

    // Booking: end date must be after start date
    var startDt = form.querySelector("#start_datetime_planned");
    var endDt = form.querySelector("#end_datetime_planned");
    if (startDt && endDt && startDt.value && endDt.value) {
      if (new Date(endDt.value) <= new Date(startDt.value)) {
        endDt.setCustomValidity("End must be after start.");
      } else {
        endDt.setCustomValidity("");
      }
    }

    // Trip end: odometer_end >= odometer_start
    var odoEnd = form.querySelector("#odometer_end");
    if (odoEnd && odoEnd.min) {
      var minVal = parseInt(odoEnd.min, 10);
      var curVal = parseInt(odoEnd.value, 10);
      if (!isNaN(minVal) && !isNaN(curVal) && curVal < minVal) {
        odoEnd.setCustomValidity(
          "Must be ≥ " + minVal + " (start reading)."
        );
      } else {
        odoEnd.setCustomValidity("");
      }
    }
  }

  // ── Submit button loading spinner ───────────────────────────────────────────
  // Shows a spinner and disables the button on form submit to prevent
  // double-clicks and give users visual feedback that something is happening.
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      // If the form has needs-validation and is invalid, don't show spinner
      if (form.classList.contains('needs-validation') && !form.checkValidity()) {
        return;
      }

      var btn = form.querySelector('button[type="submit"]');
      if (!btn || btn.disabled) return;

      // Small delay so confirm() dialogs can cancel before we modify the button
      setTimeout(function () {
        btn.disabled = true;
        btn.classList.add('btn-loading');
        // Store original content to restore if navigation fails
        btn.dataset.originalHtml = btn.innerHTML;
        var btnText = btn.textContent.trim();
        btn.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' +
          'Processing\u2026';
      }, 0);
    });
  });

  // Restore buttons when user navigates back (bfcache)
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) {
      document.querySelectorAll('button.btn-loading').forEach(function (btn) {
        btn.disabled = false;
        btn.classList.remove('btn-loading');
        if (btn.dataset.originalHtml) {
          btn.innerHTML = btn.dataset.originalHtml;
          delete btn.dataset.originalHtml;
        }
      });
    }
  });

  // ── Live feedback on input ───────────────────────────────────────────────
  // Clear custom validity as user types so they can re-submit
  document.querySelectorAll("input, select, textarea").forEach(function (el) {
    el.addEventListener("input", function () {
      el.setCustomValidity("");
      // If form was already validated, re-run so green/red updates live
      var form = el.closest("form.was-validated");
      if (form) {
        runCustomValidators(form);
      }
    });
  });

  // ── Booking form: live date comparison hint ──────────────────────────────
  var startInput = document.getElementById("start_datetime_planned");
  var endInput = document.getElementById("end_datetime_planned");
  if (startInput && endInput) {
    startInput.addEventListener("change", function () {
      // Auto-set min on end input
      endInput.min = startInput.value;
    });
  }
})();
