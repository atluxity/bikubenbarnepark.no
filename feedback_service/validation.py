from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

Topic = Literal["ide", "tilbakemelding", "mening", "bidra", "annet"]

TOPICS = {
    "ide": "Ide",
    "tilbakemelding": "Tilbakemelding",
    "mening": "Mening",
    "bidra": "Jeg kan bidra",
    "annet": "Annet",
}
MAX_MESSAGE_LENGTH = 3000
MAX_FIELD_LENGTH = 500


class FeedbackValidationError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class ProbableBotSubmission(ValueError):
    """Raised for spam-like submissions that should pretend to succeed."""


class FeedbackSubmission(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    topic: Topic
    message: str = Field(min_length=3, max_length=MAX_MESSAGE_LENGTH)
    name: str = Field(default="", max_length=MAX_FIELD_LENGTH)
    contact: str = Field(default="", max_length=MAX_FIELD_LENGTH)
    help_text: str = Field(default="", max_length=MAX_MESSAGE_LENGTH)
    consent: bool = False

    @field_validator("message", "help_text", mode="before")
    @classmethod
    def clean_long_text(cls, value: object) -> str:
        return _clean(value)

    @field_validator("name", "contact", "topic", mode="before")
    @classmethod
    def clean_short_text(cls, value: object) -> str:
        return _clean(value)

    @field_validator("consent", mode="before")
    @classmethod
    def parse_consent(cls, value: object) -> bool:
        if value is True:
            return True
        return str(value or "").lower() in {"1", "true", "yes", "on"}

    @model_validator(mode="after")
    def require_consent_for_personal_details(self) -> "FeedbackSubmission":
        if (self.name or self.contact or self.help_text) and not self.consent:
            raise ValueError("Samtykke kreves når du legger igjen kontaktopplysninger eller tilbud om hjelp.")
        return self


def _clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", "\n")
    # Remove non-whitespace control characters before collapsing whitespace.
    text = "".join(ch for ch in text if ch in "\n\t " or (ord(ch) >= 32 and ord(ch) != 127))
    return " ".join(text.split())


def validate_submission(
    *,
    topic: str | None,
    message: str | None,
    name: str | None = "",
    contact: str | None = "",
    help_text: str | None = "",
    consent: str | bool | None = False,
    honeypot: str | None = "",
) -> FeedbackSubmission:
    errors: list[str] = []

    if _clean(honeypot):
        raise ProbableBotSubmission()

    try:
        submission = FeedbackSubmission.model_validate(
            {
                "topic": topic,
                "message": message,
                "name": name,
                "contact": contact,
                "help_text": help_text,
                "consent": consent,
            }
        )
    except ValidationError as exc:
        for error in exc.errors():
            if error.get("type") == "literal_error":
                errors.append("Velg en gyldig kategori.")
            elif error.get("type") == "string_too_short":
                errors.append("Skriv inn et innspill.")
            elif error.get("type") in {"string_too_long", "too_long"}:
                errors.append("Innsendingen er for lang.")
            elif error.get("type") == "value_error":
                errors.append(str(error.get("ctx", {}).get("error", error.get("msg"))))
            else:
                errors.append("Kontroller feltene i skjemaet.")
        if errors:
            raise FeedbackValidationError(errors)
        raise

    return submission
