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

  function chicagoInputValue(isoLike) {
    try {
      const d = new Date(isoLike);
      if (Number.isNaN(d.getTime())) return "";

      const parts = new Intl.DateTimeFormat("en-US", {
        timeZone: "America/Chicago",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      }).formatToParts(d);

      const y = parts.find(p => p.type === "year")?.value || "";
      const m = parts.find(p => p.type === "month")?.value || "";
      const da = parts.find(p => p.type === "day")?.value || "";
      const hh = parts.find(p => p.type === "hour")?.value || "";
      const mm = parts.find(p => p.type === "minute")?.value || "";

      if (!y || !m || !da || !hh || !mm) return "";

      return `${y}-${m}-${da}T${hh}:${mm}`;
    } catch (e) {
      return "";
    }
  }

  function prettyLocal(val) {
    if (!val) return "";
    return `${val.replace("T", " ")} CT`;
  }

  function refreshSlotSummaryFromInputs() {
    const startInput = document.getElementById("scheduledStartInput");
    const endInput = document.getElementById("scheduledEndInput");
    const summary = document.getElementById("selectedSlotSummary");
    const summaryWrap = document.getElementById("selectedSlotSummaryWrap");

    if (!summary || !summaryWrap || !startInput || !endInput) return;

    const s = (startInput.value || "").trim();
    const e = (endInput.value || "").trim();

    if (!s || !e) return;

    summaryWrap.classList.remove("d-none");
    summary.textContent = `${prettyLocal(s)} → ${prettyLocal(e)}`;
  }

  function addOneHourLocal(val) {
    try {
      if (!val) return "";
      const d = new Date(val);
      if (Number.isNaN(d.getTime())) return "";
      d.setHours(d.getHours() + 1);

      const pad = (n) => String(n).padStart(2, "0");
      const y = d.getFullYear();
      const m = pad(d.getMonth() + 1);
      const da = pad(d.getDate());
      const hh = pad(d.getHours());
      const mm = pad(d.getMinutes());

      return `${y}-${m}-${da}T${hh}:${mm}`;
    } catch (e) {
      return "";
    }
  }

  function syncScheduledFromManual() {
    const manualStart = document.getElementById("manualStart");
    const manualEnd = document.getElementById("manualEnd");
    const startInput = document.getElementById("scheduledStartInput");
    const endInput = document.getElementById("scheduledEndInput");

    if (!manualStart || !startInput || !endInput) return;

    const s = (manualStart.value || "").trim();
    const e = (manualEnd && manualEnd.value ? manualEnd.value : "").trim();

    if (!s) return;

    startInput.value = s;

    // If the user hasn't manually edited end, keep it synced to start + 1 hour
    if (!endWasManuallyEdited || !e) {
      endInput.value = addOneHourLocal(s);
    } else {
      endInput.value = e;
    }

    refreshSlotSummaryFromInputs();
  }

  function applySelectedSlotFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const start = params.get("slot_start");
    const end = params.get("slot_end");

    if (!start || !end) return false;

    const startInput = document.getElementById("scheduledStartInput");
    const endInput = document.getElementById("scheduledEndInput");

    if (!startInput || !endInput) return false;

    // Only apply URL slot if user hasn't chosen values yet.
    const hasStart = (startInput.value || "").trim().length > 0;
    const hasEnd = (endInput.value || "").trim().length > 0;

    if (!hasStart && !hasEnd) {
      const sVal = chicagoInputValue(start);
      const eVal = chicagoInputValue(end);

      if (sVal) startInput.value = sVal;
      if (eVal) endInput.value = eVal;
    }

    const manualStart = document.getElementById("manualStart");
    const manualEnd = document.getElementById("manualEnd");

    if (manualStart && !(manualStart.value || "").trim()) {
      manualStart.value = startInput.value;
    }

    if (manualEnd && !(manualEnd.value || "").trim()) {
      manualEnd.value = endInput.value;
    }

    syncScheduledFromManual();
    refreshSlotSummaryFromInputs();

    const availabilityWrap = document.getElementById("availabilityFieldWrap");
    if (availabilityWrap) availabilityWrap.classList.add("d-none");

    return true;
  }

  const scheduledStartInput = document.getElementById("scheduledStartInput");
  const scheduledEndInput = document.getElementById("scheduledEndInput");

  const manualStart = document.getElementById("manualStart");
  const manualEnd = document.getElementById("manualEnd");

  let endWasManuallyEdited = false;

  function autoFillEndFromStart() {
    const sVal = (
      manualStart && manualStart.value
        ? manualStart.value
        : scheduledStartInput && scheduledStartInput.value
          ? scheduledStartInput.value
          : ""
    ).trim();

    if (!sVal) return;

    const eVal = (
      manualEnd && manualEnd.value
        ? manualEnd.value
        : scheduledEndInput && scheduledEndInput.value
          ? scheduledEndInput.value
          : ""
    ).trim();

    if (!endWasManuallyEdited || !eVal) {
      const nextEnd = addOneHourLocal(sVal);

      if (manualEnd && manualEnd.value !== nextEnd) {
        manualEnd.value = nextEnd;
      }

      if (scheduledEndInput && scheduledEndInput.value !== nextEnd) {
        scheduledEndInput.value = nextEnd;
      }

      refreshSlotSummaryFromInputs();
    }
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
  autoFillEndFromStart();
  show(1);

  if (scheduledStartInput) {
    scheduledStartInput.addEventListener("change", () => {
      endWasManuallyEdited = false;
      refreshSlotSummaryFromInputs();
      autoFillEndFromStart();
    });

    scheduledStartInput.addEventListener("input", () => {
      endWasManuallyEdited = false;
      refreshSlotSummaryFromInputs();
      autoFillEndFromStart();
    });
  }

  if (scheduledEndInput) {
    scheduledEndInput.addEventListener("change", () => {
      endWasManuallyEdited = true;
      refreshSlotSummaryFromInputs();
    });

    scheduledEndInput.addEventListener("input", () => {
      endWasManuallyEdited = true;
      refreshSlotSummaryFromInputs();
    });
  }

  // If the page already has values (manual admin selection), show them.
  refreshSlotSummaryFromInputs();

  if (manualStart) {
    manualStart.addEventListener("change", () => {
      endWasManuallyEdited = false;
      syncScheduledFromManual();
      autoFillEndFromStart();
    });

    manualStart.addEventListener("input", () => {
      endWasManuallyEdited = false;
      syncScheduledFromManual();
      autoFillEndFromStart();
    });
  }

  if (manualEnd) {
    manualEnd.addEventListener("change", () => {
      endWasManuallyEdited = true;
      syncScheduledFromManual();
      refreshSlotSummaryFromInputs();
    });

    manualEnd.addEventListener("input", () => {
      endWasManuallyEdited = true;
      syncScheduledFromManual();
      refreshSlotSummaryFromInputs();
    });
  }

  // In admin mode, force hidden scheduled_* to match what was picked.
  syncScheduledFromManual();

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