"use strict";

const tokenInput = document.getElementById("form_token");
const topic = document.getElementById("topic");
const message = document.getElementById("message");
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

function syncTopicValidity() {
  topic.setCustomValidity(topic.value ? "" : "Velg hva innspillet gjelder.");
}

function syncMessageValidity() {
  const length = message.value.trim().length;
  if (length === 0) {
    message.setCustomValidity("Skriv inn et innspill.");
  } else if (length < 3) {
    message.setCustomValidity("Innspillet må inneholde minst tre tegn.");
  } else {
    message.setCustomValidity("");
  }
}

topic.addEventListener("change", syncTopicValidity);
message.addEventListener("input", syncMessageValidity);
consent.addEventListener("change", syncConsentRequirement);
personalFields.forEach((field) =>
  field.addEventListener("input", syncConsentRequirement),
);
syncTopicValidity();
syncMessageValidity();
syncConsentRequirement();
