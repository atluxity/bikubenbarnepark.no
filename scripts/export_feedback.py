#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from feedback_service.storage import DEFAULT_DB_PATH, export_csv, export_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Bikuben feedback submissions.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite database path. Defaults to BIKUBEN_FEEDBACK_DB.")
    parser.add_argument("--format", choices=("csv", "json"), default="csv")
    parser.add_argument("--output", type=Path, help="Output file. Defaults to stdout.")
    args = parser.parse_args()
    if args.db is None:
        parser.error("--db or BIKUBEN_FEEDBACK_DB is required")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as handle:
            if args.format == "csv":
                export_csv(handle, db_path=args.db)
            else:
                export_json(handle, db_path=args.db)
        return 0

    if args.format == "csv":
        export_csv(sys.stdout, db_path=args.db)
    else:
        export_json(sys.stdout, db_path=args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
