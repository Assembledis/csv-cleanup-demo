from __future__ import annotations

import argparse
import json
from pathlib import Path

from csv_cleanup.pipeline import clean_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean a messy contacts CSV and write a quality report."
    )
    parser.add_argument("input_csv", type=Path, help="Path to the source CSV")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output/clean.csv"),
        help="Clean CSV path (default: output/clean.csv)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("output/report.json"),
        help="JSON report path (default: output/report.json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.input_csv.exists():
        print(f"File not found: {args.input_csv}")
        return 1

    result = clean_file(args.input_csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result.to_csv(), encoding="utf-8")
    args.report.write_text(json.dumps(result.report, indent=2), encoding="utf-8")

    print(f"Wrote {args.output} ({result.report['output_rows']} rows)")
    print(f"Wrote {args.report}")
    print(
        "Dropped empty: {empty_rows_dropped}; duplicates: {duplicates_removed}; "
        "bad emails: {invalid_email_count}; bad phones: {invalid_phone_count}".format(
            **result.report
        )
    )
    return 0
