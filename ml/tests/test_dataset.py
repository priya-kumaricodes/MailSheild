"""Unit tests for dataset preprocessing, RFC 822 parsing, duplicate detection, and splitting.
"""

from mailshield_ml.dataset import (
    compute_content_hash,
    deduplicate_records,
    normalize_text,
    parse_rfc822_email,
    stratified_split,
    strip_html_tags,
)


def test_strip_html_tags():
    raw_html = "<html><body><h1>Urgent Notice</h1><p>Click <a href='http://bad.com'>here</a>.</p></body></html>"
    stripped = strip_html_tags(raw_html)
    assert "Urgent Notice" in stripped
    assert "Click" in stripped
    assert "<" not in stripped
    assert ">" not in stripped


def test_normalize_text_unicode_and_whitespace():
    # Test with Hindi text, messy whitespace, and control chars
    hindi_text = "  नमस्ते   अनुराग\t\n\nकल सुबह 10 बजे   "
    normalized = normalize_text(hindi_text)
    assert "नमस्ते अनुराग" in normalized
    assert "कल सुबह 10 बजे" in normalized
    assert "\t" not in normalized


def test_compute_content_hash_deterministic():
    h1 = compute_content_hash("Meeting Tomorrow", "Hi team, see you tomorrow.")
    h2 = compute_content_hash("meeting tomorrow ", "Hi team, see you tomorrow.\n")
    # Should be case-insensitive and whitespace-stripped
    assert h1 == h2


def test_deduplicate_records():
    records = [
        {"subject": "Meeting", "body": "See you at 10.", "label": 0},
        {"subject": "Meeting", "body": "See you at 10.", "label": 0},  # Duplicate
        {"subject": "Lottery", "body": "You won $1M!", "label": 1},
        {"subject": "Lottery", "body": "You won $1M!", "label": 1},  # Duplicate
        {"subject": "Sprint Review", "body": "Demo at 3pm.", "label": 0},
    ]
    unique, dup_count = deduplicate_records(records)
    assert dup_count == 2
    assert len(unique) == 3
    assert len({r["content_hash"] for r in unique}) == 3


def test_stratified_split_proportions():
    # 100 records: 60 ham (0), 40 spam (1)
    records = [{"subject": f"Sub {i}", "body": f"Body {i}", "label": 0 if i < 60 else 1} for i in range(100)]
    train, val, test = stratified_split(records, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42)

    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15

    # Check class ratios are preserved (~60% ham, ~40% spam)
    train_ham = sum(1 for r in train if r["label"] == 0)
    val_ham = sum(1 for r in val if r["label"] == 0)
    test_ham = sum(1 for r in test if r["label"] == 0)

    assert train_ham == 42  # 60% of 70
    assert val_ham == 9    # 60% of 15
    assert test_ham == 9   # 60% of 15


def test_parse_rfc822_email_multipart():
    raw_eml = """From: security@bank.com
To: victim@domain.com
Subject: Unauthorized Login Detected
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary-123"

--boundary-123
Content-Type: text/plain; charset="utf-8"

Your account was accessed from an unrecognized device.
Please verify your identity immediately.

--boundary-123
Content-Type: text/html; charset="utf-8"

<html><body><p>Your account was accessed.</p></body></html>
--boundary-123--
"""
    parsed = parse_rfc822_email(raw_eml)
    assert parsed.subject == "Unauthorized Login Detected"
    assert "Your account was accessed from an unrecognized device" in parsed.body
    assert parsed.is_multipart is True
    assert parsed.content_hash != ""
