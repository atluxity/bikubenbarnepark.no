from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from time import time

from fastapi.testclient import TestClient

from feedback_service.app import app
from feedback_service.form_token import InvalidFormToken, TooFreshFormToken, create_form_token, validate_form_token
from feedback_service.storage import export_csv, insert_submission, iter_submissions
from feedback_service.validation import FeedbackValidationError, ProbableBotSubmission, validate_submission


class FeedbackValidationTests(unittest.TestCase):
    def test_anonymous_feedback_does_not_require_consent(self) -> None:
        submission = validate_submission(topic="ide", message="Mer dugnad i parken")
        self.assertEqual(submission.topic, "ide")
        self.assertFalse(submission.consent)

    def test_contact_requires_consent(self) -> None:
        with self.assertRaises(FeedbackValidationError):
            validate_submission(topic="bidra", message="Jeg kan hjelpe", contact="test@example.com")

    def test_contact_with_consent_is_valid(self) -> None:
        submission = validate_submission(
            topic="bidra",
            message="Jeg kan hjelpe med snekring",
            contact="test@example.com",
            help_text="Snekring",
            consent="yes",
        )
        self.assertTrue(submission.consent)

    def test_honeypot_is_probable_bot(self) -> None:
        with self.assertRaises(ProbableBotSubmission):
            validate_submission(topic="ide", message="Hei", honeypot="https://spam.example")


class FormTokenTests(unittest.TestCase):
    def test_fresh_token_is_too_fresh(self) -> None:
        token = create_form_token(now=1000.0)
        with self.assertRaises(TooFreshFormToken):
            validate_form_token(token, now=1001.0)

    def test_token_after_more_than_three_seconds_is_valid(self) -> None:
        token = create_form_token(now=1000.0)
        validate_form_token(token, now=1003.1)

    def test_tampered_token_is_invalid(self) -> None:
        token = create_form_token(now=1000.0)
        with self.assertRaises(InvalidFormToken):
            validate_form_token(token + "x", now=1003.1)


class FeedbackStorageTests(unittest.TestCase):
    def test_insert_and_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "feedback.sqlite3"
            submission = validate_submission(topic="mening", message="Dette er bra")
            row_id = insert_submission(submission, remote_addr="127.0.0.1", user_agent="test", db_path=db_path)
            rows = list(iter_submissions(db_path))
            self.assertEqual(row_id, 1)
            self.assertEqual(rows[0]["message"], "Dette er bra")
            self.assertNotEqual(rows[0]["remote_addr_hash"], "127.0.0.1")

            output = io.StringIO()
            export_csv(output, db_path=db_path)
            self.assertIn("Dette er bra", output.getvalue())

    def test_csv_export_escapes_formula_like_cells(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "feedback.sqlite3"
            submission = validate_submission(topic="ide", message="=IMPORTXML(\"https://evil.example\")")
            insert_submission(submission, db_path=db_path)

            output = io.StringIO()
            export_csv(output, db_path=db_path)
            self.assertIn("'=IMPORTXML", output.getvalue())


class FeedbackApiTests(unittest.TestCase):
    def _patch_insert(self, db_path: Path):
        import feedback_service.app as app_module
        import feedback_service.storage as storage

        original_insert = app_module.insert_submission

        def insert_for_test(submission, *, remote_addr="", user_agent=""):
            return storage.insert_submission(submission, remote_addr=remote_addr, user_agent=user_agent, db_path=db_path)

        app_module.insert_submission = insert_for_test
        return app_module, original_insert

    def test_missing_token_redirects_without_storage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "feedback.sqlite3"
            app_module, original_insert = self._patch_insert(db_path)
            try:
                client = TestClient(app)
                response = client.post(
                    "/api/feedback",
                    data={"topic": "ide", "message": "Dette skal late som det virker"},
                    follow_redirects=False,
                )
                self.assertEqual(response.status_code, 303)
                self.assertEqual(response.headers["location"], "/innspill/takk/")
                self.assertEqual(list(iter_submissions(db_path)), [])
            finally:
                app_module.insert_submission = original_insert

    def test_fresh_token_redirects_without_storage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "feedback.sqlite3"
            app_module, original_insert = self._patch_insert(db_path)
            try:
                client = TestClient(app)
                token = create_form_token()
                response = client.post(
                    "/api/feedback",
                    data={"topic": "ide", "message": "Dette skal late som det virker", "form_token": token},
                    follow_redirects=False,
                )
                self.assertEqual(response.status_code, 303)
                self.assertEqual(list(iter_submissions(db_path)), [])
            finally:
                app_module.insert_submission = original_insert

    def test_old_enough_token_rejects_contact_without_consent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "feedback.sqlite3"
            app_module, original_insert = self._patch_insert(db_path)
            try:
                client = TestClient(app)
                token = create_form_token(now=time() - 3.5)
                response = client.post(
                    "/api/feedback",
                    data={
                        "topic": "bidra",
                        "message": "Jeg kan hjelpe",
                        "contact": "test@example.com",
                        "form_token": token,
                    },
                    follow_redirects=False,
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("Samtykke kreves", response.text)
                self.assertEqual(list(iter_submissions(db_path)), [])
            finally:
                app_module.insert_submission = original_insert

    def test_old_enough_token_stores_submission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "feedback.sqlite3"
            app_module, original_insert = self._patch_insert(db_path)
            try:
                client = TestClient(app)
                token = create_form_token(now=time() - 3.5)
                response = client.post(
                    "/api/feedback",
                    data={"topic": "ide", "message": "Dette skal lagres", "form_token": token},
                    follow_redirects=False,
                )
                self.assertEqual(response.status_code, 303)
                rows = list(iter_submissions(db_path))
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["message"], "Dette skal lagres")
            finally:
                app_module.insert_submission = original_insert


class FeedbackPageTests(unittest.TestCase):
    def test_form_uses_csp_compatible_external_script(self) -> None:
        form_html = Path("innspill/index.html").read_text()
        self.assertIn('<script src="/assets/feedback-form.js" defer></script>', form_html)
        self.assertNotIn("<script>", form_html)

        form_script = Path("assets/feedback-form.js").read_text()
        self.assertIn('fetch("/api/form-token"', form_script)
        self.assertIn("consent.required = needsConsent", form_script)
        self.assertIn("Velg hva innspillet gjelder.", form_script)
        self.assertIn("Skriv inn et innspill.", form_script)
        self.assertIn("Innspillet må inneholde minst tre tegn.", form_script)


if __name__ == "__main__":
    unittest.main()
