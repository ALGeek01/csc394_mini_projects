const passwordInput = document.getElementById("password");
const meterFill = document.getElementById("meterFill");
const strengthText = document.getElementById("strengthText");
const requirementsList = document.getElementById("requirementsList");
const togglePasswordButton = document.getElementById("togglePassword");
const toggleIcon = document.getElementById("toggleIcon");

// Rule checks for the checklist and scoring.
const checks = {
  length: (value) => value.length >= 8,
  upper: (value) => /[A-Z]/.test(value),
  lower: (value) => /[a-z]/.test(value),
  number: (value) => /\d/.test(value),
  special: (value) => /[^A-Za-z0-9]/.test(value)
};

function evaluatePassword(value) {
  const results = {
    length: checks.length(value),
    upper: checks.upper(value),
    lower: checks.lower(value),
    number: checks.number(value),
    special: checks.special(value)
  };

  const score = Object.values(results).filter(Boolean).length;
  return { results, score };
}

function getStrengthMeta(score, hasAnyInput) {
  if (!hasAnyInput) {
    return { label: "Weak", width: 0, color: "var(--weak)" };
  }

  if (score <= 2) {
    return { label: "Weak", width: 33, color: "var(--weak)" };
  }

  if (score <= 4) {
    return { label: "Medium", width: 66, color: "var(--medium)" };
  }

  return { label: "Strong", width: 100, color: "var(--strong)" };
}

function updateChecklist(results) {
  for (const item of requirementsList.querySelectorAll("li")) {
    const rule = item.dataset.rule;
    const icon = item.querySelector(".icon");
    const passed = Boolean(results[rule]);

    item.classList.toggle("valid", passed);
    icon.textContent = passed ? "✓" : "•";
  }
}

function updateStrengthUI(meta) {
  meterFill.classList.remove("animate");
  // Force reflow so the pulse animation restarts each update.
  void meterFill.offsetWidth;
  meterFill.classList.add("animate");

  meterFill.style.width = `${meta.width}%`;
  meterFill.style.backgroundColor = meta.color;
  const glowByLabel = {
    Weak: "0 0 14px rgba(239, 68, 68, 0.26)",
    Medium: "0 0 14px rgba(245, 158, 11, 0.24)",
    Strong: "0 0 14px rgba(34, 197, 94, 0.26)"
  };
  meterFill.style.boxShadow = `0 0 0 1px rgba(255, 255, 255, 0.24) inset, ${glowByLabel[meta.label]}`;
  strengthText.textContent = meta.label;
  strengthText.style.color = meta.color;
}

function updatePasswordToggleUI(isVisible) {
  passwordInput.type = isVisible ? "text" : "password";
  togglePasswordButton.setAttribute("aria-pressed", String(isVisible));
  togglePasswordButton.setAttribute("aria-label", isVisible ? "Hide password" : "Show password");
  toggleIcon.textContent = isVisible ? "Hide" : "Show";
}

passwordInput.addEventListener("input", (event) => {
  const value = event.target.value;
  const { results, score } = evaluatePassword(value);
  const meta = getStrengthMeta(score, value.length > 0);

  updateChecklist(results);
  updateStrengthUI(meta);
});

togglePasswordButton.addEventListener("click", () => {
  const isVisible = passwordInput.type !== "password";
  updatePasswordToggleUI(!isVisible);
  passwordInput.focus();
});
