"use strict";

const tokenInput = document.getElementById("form_token");
const consent = document.getElementById("consent");
const personalFields = ["name", "contact", "help_text"].map((id) =>
  document.getElementById(id),
);

fetch("/api/form-token", { credentials: "same-origin", cache: "no-store" })
  .then((response) => (response.ok ? response.json() : Promise.reject()))
  .then((data) => {
    tokenInput.value = data.token || "";
  })
  .catch(() => {
    tokenInput.value = "";
  });

function syncConsentRequirement() {
  const needsConsent = personalFields.some(
    (field) => field.value.trim().length > 0,
  );
  consent.required = needsConsent;
  consent.setCustomValidity(
    needsConsent && !consent.checked
      ? "Kryss av for samtykke når du legger igjen kontaktopplysninger eller tilbud om hjelp."
      : "",
  );
}

consent.addEventListener("change", syncConsentRequirement);
personalFields.forEach((field) =>
  field.addEventListener("input", syncConsentRequirement),
);
syncConsentRequirement();
