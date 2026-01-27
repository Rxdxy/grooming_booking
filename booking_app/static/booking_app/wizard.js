(() => {
  const steps = Array.from(document.querySelectorAll(".wizard-step"));
  if (!steps.length) return; // not on booking page

  const stepLabel = document.getElementById("stepLabel");
  const bar = document.getElementById("stepProgress");
  const backBtn = document.getElementById("backBtn");
  const nextBtn = document.getElementById("nextBtn");
  const submitBtn = document.getElementById("submitBtn");

  let current = 1;
  const total = steps.length;

  function show(step) {
    current = step;
    steps.forEach(s => s.classList.toggle("d-none", Number(s.dataset.step) !== step));

    stepLabel.textContent = `Step ${step} of ${total}`;
    bar.style.width = `${Math.round((step / total) * 100)}%`;

    backBtn.disabled = step === 1;
    nextBtn.classList.toggle("d-none", step === total);
    submitBtn.classList.toggle("d-none", step !== total);
  }

  backBtn.addEventListener("click", () => show(Math.max(1, current - 1)));
  nextBtn.addEventListener("click", () => show(Math.min(total, current + 1)));

  show(1);
})();