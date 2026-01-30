(() => {
  const steps = Array.from(document.querySelectorAll(".wizard-step"));
  if (!steps.length) return;

  const stepLabel = document.getElementById("stepLabel");
  const bar = document.getElementById("stepProgress");
  const backBtn = document.getElementById("backBtn");
  const nextBtn = document.getElementById("nextBtn");
  const submitBtn = document.getElementById("submitBtn");

  const form = document.querySelector("form[data-wizard-form]");

  let current = 1;
  const total = steps.length;

  function show(step) {
    current = step;

    steps.forEach(s => {
      const n = Number(s.dataset.step);
      s.classList.toggle("d-none", n !== step);
    });

    if (stepLabel) stepLabel.textContent = `Step ${step} of ${total}`;
    if (bar) bar.style.width = `${Math.round((step / total) * 100)}%`;

    if (backBtn) backBtn.disabled = step === 1;
    if (nextBtn) nextBtn.classList.toggle("d-none", step === total);
    if (submitBtn) submitBtn.classList.toggle("d-none", step !== total);
  }

  function getStepForEl(el) {
    const stepEl = el.closest(".wizard-step");
    if (!stepEl) return 1;

    const n = Number(stepEl.dataset.step);
    return Number.isFinite(n) ? n : 1;
  }

  function jumpToFirstInvalid() {
    if (!form) return false;

    const invalid = form.querySelector(
      "input:invalid, select:invalid, textarea:invalid"
    );

    if (!invalid) return false;

    const step = getStepForEl(invalid);
    show(step);

    setTimeout(() => {
      if (typeof invalid.reportValidity === "function") {
        invalid.reportValidity();
      } else {
        invalid.focus();
      }
    }, 0);

    return true;
  }

  function fmtChicago(iso) {
    try {
      const d = new Date(iso);
      const fmt = new Intl.DateTimeFormat("en-US", {
        timeZone: "America/Chicago",
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
      return fmt.format(d);
    } catch (e) {
      return "";
    }
  }

  function applySelectedSlotFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const start = params.get("slot_start");
    const end = params.get("slot_end");

    if (!start || !end) return false;

    const startInput = document.getElementById("scheduledStartInput");
    const endInput = document.getElementById("scheduledEndInput");

    if (startInput) startInput.value = start;
    if (endInput) endInput.value = end;

    const summary = document.getElementById("selectedSlotSummary");
    const summaryWrap = document.getElementById("selectedSlotSummaryWrap");

    if (summary && summaryWrap) {
      summaryWrap.classList.remove("d-none");
      summary.textContent = `${fmtChicago(start)} → ${fmtChicago(end)}`;
    }

    const availabilityWrap = document.getElementById("availabilityFieldWrap");
    if (availabilityWrap) availabilityWrap.classList.add("d-none");

    return true;
  }

  if (backBtn) {
    backBtn.addEventListener("click", () => show(Math.max(1, current - 1)));
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => show(Math.min(total, current + 1)));
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", e => {
      if (!form) return;

      if (!form.checkValidity()) {
        e.preventDefault();
        jumpToFirstInvalid();
      }
    });
  }

  applySelectedSlotFromUrl();
  show(1);

  // --- Service description toggle ---
  function toggleServiceDescriptions() {
    const items = document.querySelectorAll("[data-service-desc]");

    items.forEach((wrap) => {
      const input = wrap.querySelector("input");
      const desc = wrap.querySelector(".service-desc");
      if (!input || !desc) return;

      if (input.checked) {
        desc.classList.remove("d-none");
      } else {
        desc.classList.add("d-none");
      }
    });
  }

  document.addEventListener("change", (e) => {
    if (e.target.matches("input[type='checkbox'], input[type='radio']")) {
      toggleServiceDescriptions();
    }
  });

  // Run once on load
  toggleServiceDescriptions();
})();