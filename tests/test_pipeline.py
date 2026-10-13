from pathlib import Path

from csv_cleanup.normalize import normalize_email, normalize_phone, split_full_name
from csv_cleanup.pipeline import clean_file, clean_table


def test_split_last_comma_first():
    assert split_full_name("DOE, Jane") == ("Jane", "Doe")


def test_email_strips_spaces_and_lowercases():
    value, ok = normalize_email("Ana @Example.com")
    assert value == "ana@example.com"
    assert ok


def test_phone_nanp_to_e164():
    value, ok = normalize_phone("(555) 010-1001")
    assert value == "+15550101001"
    assert ok


def test_empty_and_duplicate_rows(tmp_path: Path):
    src = Path("samples/dirty_contacts.csv")
    result = clean_file(src)
    emails = [row["email"] for row in result.rows]
    assert result.report["empty_rows_dropped"] >= 1
    assert result.report["duplicates_removed"] >= 1
    assert emails.count("jane.doe@example.com") == 1
    assert "john.smith@example.com" in emails


def test_invalid_fields_are_reported():
    result = clean_table(
        [
            {
                "full_name": "Alex Nguyen",
                "email": "not-an-email",
                "phone": "12345",
                "company": "Fabrikam",
                "city": "Seattle",
            }
        ]
    )
    assert result.report["invalid_email_count"] == 1
    assert result.report["invalid_phone_count"] == 1
