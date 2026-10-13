# csv-cleanup-demo

Freelance sample: take a **messy contacts CSV** the client already has and return a **clean CSV + JSON quality report**.

This is not a scraper. Input is always a file the client provides (CRM export, spreadsheet dump, form results).

## What it does

- Detects delimiter and common encodings (`utf-8`, `utf-8-sig`, `cp1251`, `latin-1`)
- Normalizes headers and whitespace
- Splits `Full Name` / `Last, First`
- Lowercases and repairs emails like `ana @example.com`
- Normalizes 10-digit NANP phones to `+1XXXXXXXXXX`
- Drops empty rows and exact duplicates (email + phone + name)
- Writes `output/clean.csv` and `output/report.json`

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python -m csv_cleanup samples/dirty_contacts.csv
pytest
```

Example:

```text
Wrote output/clean.csv (6 rows)
Wrote output/report.json
Dropped empty: 2; duplicates: 1; bad emails: 1; bad phones: 1
```

## $50 offer this repo supports

**CSV cleanup, one file:** dirty spreadsheet → clean CSV + short report (duplicates, invalid emails/phones). Typical turnaround: same day or 24 hours.

Out of scope: scraping websites, buying/selling contact lists, bypassing logins.

## Project layout

```text
csv_cleanup/     CLI + cleanup pipeline
samples/         synthetic dirty CSV (fake 555 numbers, example.com)
tests/           pytest
```
