from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from csv_cleanup.normalize import (
    empty_to_none,
    normalize_email,
    normalize_header,
    normalize_phone,
    split_full_name,
)

OUTPUT_COLUMNS = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "company",
    "city",
    "source_row",
]


@dataclass
class CleanupResult:
    rows: list[dict[str, str]]
    report: dict[str, Any] = field(default_factory=dict)

    def to_csv(self) -> str:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(self.rows)
        return buf.getvalue()


def read_csv_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1251", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def parse_rows(text: str) -> list[dict[str, str]]:
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    rows: list[dict[str, str]] = []
    for raw in reader:
        mapped = {normalize_header(k or "column"): empty_to_none(v) for k, v in raw.items()}
        rows.append(mapped)
    return rows


def _pick(row: dict[str, str], *aliases: str) -> str:
    for key in aliases:
        if row.get(key):
            return row[key]
    return ""


def clean_table(rows: list[dict[str, str]]) -> CleanupResult:
    empty_dropped = 0
    invalid_emails: list[dict[str, Any]] = []
    invalid_phones: list[dict[str, Any]] = []
    cleaned: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=2):  # header is line 1
        first = _pick(row, "first_name", "firstname", "first")
        last = _pick(row, "last_name", "lastname", "last")
        full = _pick(row, "full_name", "name", "contact")
        if (not first and not last) and full:
            first, last = split_full_name(full)

        email, email_ok = normalize_email(_pick(row, "email", "e_mail", "mail"))
        phone, phone_ok = normalize_phone(_pick(row, "phone", "mobile", "tel"))
        company = _pick(row, "company", "organization", "org")
        city = _pick(row, "city", "town")

        if not any([first, last, email, phone, company, city]):
            empty_dropped += 1
            continue

        if email and not email_ok:
            invalid_emails.append({"source_row": index, "value": email})
        if phone and not phone_ok:
            invalid_phones.append({"source_row": index, "value": phone})

        cleaned.append(
            {
                "first_name": first,
                "last_name": last,
                "email": email,
                "phone": phone,
                "company": company,
                "city": city,
                "source_row": str(index),
            }
        )

    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, str]] = []
    duplicates_removed = 0
    for row in cleaned:
        key = (row["email"], row["phone"], f"{row['first_name']}|{row['last_name']}".lower())
        if key in seen:
            duplicates_removed += 1
            continue
        seen.add(key)
        unique.append(row)

    report = {
        "input_rows": len(rows),
        "output_rows": len(unique),
        "empty_rows_dropped": empty_dropped,
        "duplicates_removed": duplicates_removed,
        "invalid_email_count": len(invalid_emails),
        "invalid_phone_count": len(invalid_phones),
        "invalid_emails": invalid_emails,
        "invalid_phones": invalid_phones,
        "output_columns": OUTPUT_COLUMNS,
    }
    return CleanupResult(rows=unique, report=report)


def clean_file(path: Path) -> CleanupResult:
    return clean_table(parse_rows(read_csv_text(path)))
