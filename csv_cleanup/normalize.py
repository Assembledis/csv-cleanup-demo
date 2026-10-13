"""Field-level normalizers. Rules are conservative and documented in the report."""

from __future__ import annotations

import re
from typing import Optional

EMAIL_RE = re.compile(r"^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$", re.IGNORECASE)
NON_DIGIT_RE = re.compile(r"\D+")
MULTI_SPACE_RE = re.compile(r"\s+")


def collapse_ws(value: str) -> str:
    return MULTI_SPACE_RE.sub(" ", value).strip()


def normalize_header(name: str) -> str:
    cleaned = collapse_ws(name).lower().replace(" ", "_")
    cleaned = re.sub(r"[^a-z0-9_]+", "", cleaned)
    return cleaned or "column"


def normalize_email(raw: str) -> tuple[str, bool]:
    value = collapse_ws(raw).replace(" @", "@").replace("@ ", "@").lower()
    if not value:
        return "", True
    return value, bool(EMAIL_RE.match(value))


def normalize_phone(raw: str) -> tuple[str, bool]:
    """Keep digits. 10-digit numbers become +1XXXXXXXXXX (NANP demo rule)."""
    value = collapse_ws(raw)
    if not value:
        return "", True
    digits = NON_DIGIT_RE.sub("", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"+1{digits}", True
    if 8 <= len(digits) <= 15:
        return f"+{digits}", True
    return value, False


def split_full_name(raw: str) -> tuple[str, str]:
    value = collapse_ws(raw)
    if not value:
        return "", ""
    if "," in value:
        last, _, first = value.partition(",")
        return collapse_ws(first).title(), collapse_ws(last).title()
    parts = value.split(" ")
    if len(parts) == 1:
        return parts[0].title(), ""
    return parts[0].title(), " ".join(parts[1:]).title()


def empty_to_none(value: Optional[str]) -> str:
    if value is None:
        return ""
    return collapse_ws(str(value))
