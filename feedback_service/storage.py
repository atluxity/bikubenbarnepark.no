from __future__ import annotations

import csv
import hashlib
import hmac
import json
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, TextIO

from .validation import FeedbackSubmission

CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

DEFAULT_DB_PATH = Path(os.environ["BIKUBEN_FEEDBACK_DB"]) if os.environ.get("BIKUBEN_FEEDBACK_DB") else None
HASH_SALT = os.environ.get("BIKUBEN_FEEDBACK_HASH_SALT", "local-development-salt")

SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    topic TEXT NOT NULL,
    message TEXT NOT NULL,
    help_text TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    contact TEXT NOT NULL DEFAULT '',
    consent INTEGER NOT NULL DEFAULT 0,
    remote_addr_hash TEXT NOT NULL DEFAULT '',
    user_agent TEXT NOT NULL DEFAULT ''
);
"""


def _resolve_db_path(db_path: Path | None = DEFAULT_DB_PATH) -> Path:
    if db_path is None:
        raise RuntimeError("BIKUBEN_FEEDBACK_DB must be set to a database path outside the public web root.")
    return db_path


def connect(db_path: Path | None = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path = _resolve_db_path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(SCHEMA)
    return conn


def hash_remote_addr(remote_addr: str) -> str:
    if not remote_addr:
        return ""
    return hmac.new(HASH_SALT.encode(), remote_addr.encode(), hashlib.sha256).hexdigest()


def insert_submission(
    submission: FeedbackSubmission,
    *,
    remote_addr: str = "",
    user_agent: str = "",
    db_path: Path | None = DEFAULT_DB_PATH,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    user_agent = (user_agent or "")[:300]
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO feedback_submissions (
                created_at, topic, message, help_text, name, contact, consent,
                remote_addr_hash, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                submission.topic,
                submission.message,
                submission.help_text,
                submission.name,
                submission.contact,
                int(submission.consent),
                hash_remote_addr(remote_addr),
                user_agent,
            ),
        )
        return int(cur.lastrowid)


def iter_submissions(db_path: Path | None = DEFAULT_DB_PATH) -> Iterable[dict[str, object]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, topic, message, help_text, name, contact,
                   consent, remote_addr_hash, user_agent
            FROM feedback_submissions
            ORDER BY id ASC
            """
        )
        for row in rows:
            yield dict(row)


def _safe_csv_cell(value: object) -> object:
    if not isinstance(value, str) or not value:
        return value
    if value.startswith(CSV_FORMULA_PREFIXES):
        return "'" + value
    return value


def _safe_csv_row(row: dict[str, object]) -> dict[str, object]:
    return {key: _safe_csv_cell(value) for key, value in row.items()}


def export_csv(output: TextIO, *, db_path: Path | None = DEFAULT_DB_PATH) -> None:
    rows = [_safe_csv_row(row) for row in iter_submissions(db_path)]
    fieldnames = [
        "id",
        "created_at",
        "topic",
        "message",
        "help_text",
        "name",
        "contact",
        "consent",
        "remote_addr_hash",
        "user_agent",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def export_json(output: TextIO, *, db_path: Path | None = DEFAULT_DB_PATH) -> None:
    json.dump(list(iter_submissions(db_path)), output, ensure_ascii=False, indent=2)
    output.write("\n")
