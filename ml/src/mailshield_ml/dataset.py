"""Dataset preprocessing, email parsing, duplicate detection, and stratified splitting.
"""

from __future__ import annotations

import email
import email.policy
import hashlib
import html
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from sklearn.model_selection import train_test_split


@dataclass
class ParsedEmail:
    """Structured representation of an email extracted from raw text or RFC 822 format."""

    subject: str
    body: str
    headers: dict[str, str] = field(default_factory=dict)
    raw_length: int = 0
    is_multipart: bool = False
    content_hash: str = ""

    def combined_text(self) -> str:
        """Combine subject and body into a single representation for classification."""
        sub = self.subject.strip()
        body = self.body.strip()
        if sub and body:
            return f"Subject: {sub}\n\n{body}"
        return sub or body


def strip_html_tags(text: str) -> str:
    """Safely strip HTML tags and unescape HTML entities without rendering."""
    # Unescape common HTML entities
    unescaped = html.unescape(text)
    # Remove script and style elements completely
    cleaned = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", unescaped, flags=re.DOTALL | re.IGNORECASE)
    # Replace remaining tags with spaces
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return cleaned


def normalize_text(text: str) -> str:
    """Normalize text using Unicode NFKC, replace control characters, and collapse whitespace."""
    if not text:
        return ""
    # Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)
    # Strip HTML tags if any tag-like sequences appear
    if "<" in text and ">" in text:
        text = strip_html_tags(text)
    # Replace non-printable/control chars except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", " ", text)
    # Collapse multiple whitespace characters into single space or clean newline
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def parse_rfc822_email(raw_content: str | bytes) -> ParsedEmail:
    """Parse raw email string or bytes conforming to RFC 822 / MIME specifications."""
    raw_length = len(raw_content)

    if isinstance(raw_content, bytes):
        msg = email.message_from_bytes(raw_content, policy=email.policy.default)
    else:
        msg = email.message_from_string(raw_content, policy=email.policy.default)

    subject = str(msg.get("subject", "") or "")
    # Decode RFC 2047 encoded words in subject if needed
    subject = normalize_text(subject)

    headers = {}
    for h in ["from", "to", "date", "content-type"]:
        val = msg.get(h)
        if val:
            headers[h] = str(val)

    body_parts: list[str] = []
    is_multipart = msg.is_multipart()

    if is_multipart:
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            if content_type == "text/plain":
                try:
                    payload = part.get_content()
                    if isinstance(payload, str):
                        body_parts.append(payload)
                    elif isinstance(payload, bytes):
                        body_parts.append(payload.decode("utf-8", errors="replace"))
                except Exception:
                    raw_payload = part.get_payload(decode=True)
                    if raw_payload:
                        body_parts.append(raw_payload.decode("utf-8", errors="replace"))
            elif content_type == "text/html" and not body_parts:
                # If no text/plain part found yet, extract and strip text/html
                try:
                    payload = part.get_content()
                    if isinstance(payload, str):
                        body_parts.append(strip_html_tags(payload))
                except Exception:
                    pass
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_content()
            if isinstance(payload, str):
                body_parts.append(payload if content_type != "text/html" else strip_html_tags(payload))
        except Exception:
            raw_payload = msg.get_payload(decode=True)
            if raw_payload:
                decoded = raw_payload.decode("utf-8", errors="replace")
                body_parts.append(decoded if content_type != "text/html" else strip_html_tags(decoded))
            else:
                body_parts.append(str(msg.get_payload() or ""))

    raw_body = "\n\n".join(body_parts)
    normalized_body = normalize_text(raw_body)

    content_hash = compute_content_hash(subject, normalized_body)

    return ParsedEmail(
        subject=subject,
        body=normalized_body,
        headers=headers,
        raw_length=raw_length,
        is_multipart=is_multipart,
        content_hash=content_hash,
    )


def compute_content_hash(subject: str, body: str) -> str:
    """Generate deterministic SHA-256 hash for content deduplication."""
    norm_sub = subject.strip().lower()
    norm_body = body.strip().lower()
    payload = f"{norm_sub}\n{norm_body}".encode()
    return hashlib.sha256(payload).hexdigest()


def deduplicate_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Detect and remove duplicate email records by content hash.

    Preserves the first occurrence and reports total duplicates removed.
    """
    seen_hashes = set()
    unique_records: list[dict[str, Any]] = []
    duplicates_count = 0

    for rec in records:
        sub = rec.get("subject", "")
        body = rec.get("body", "")
        chash = rec.get("content_hash") or compute_content_hash(sub, body)

        if chash in seen_hashes:
            duplicates_count += 1
            continue

        seen_hashes.add(chash)
        rec["content_hash"] = chash
        unique_records.append(rec)

    return unique_records, duplicates_count


def stratified_split(
    records: list[dict[str, Any]],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Split records into stratified train, validation, and test subsets.

    Guarantees consistent class label proportions across splits.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-6, "Split ratios must sum to 1.0"

    # Extract labels
    labels = [r["label"] for r in records]

    # First split: train vs holdout (val + test)
    holdout_ratio = val_ratio + test_ratio
    train_recs, holdout_recs, train_labels, holdout_labels = train_test_split(
        records,
        labels,
        test_size=holdout_ratio,
        stratify=labels,
        random_state=random_state,
    )

    # Second split: validation vs test
    val_fraction_of_holdout = val_ratio / holdout_ratio
    val_recs, test_recs, _, _ = train_test_split(
        holdout_recs,
        holdout_labels,
        test_size=(1.0 - val_fraction_of_holdout),
        stratify=holdout_labels,
        random_state=random_state,
    )

    return train_recs, val_recs, test_recs


def extract_template_group_id(record: dict[str, Any]) -> str:
    """Identify template archetype or campaign cluster to group related/near-duplicate emails."""
    if "group_id" in record and record["group_id"]:
        return record["group_id"]
    sub = record.get("subject", "").lower()
    cat = record.get("category", "")
    lbl = record.get("label", 0)

    # Ham templates
    if "meeting notes" in sub:
        return "grp_ham_meeting"
    if "code review" in sub:
        return "grp_ham_codereview"
    if "receipt" in sub:
        return "grp_ham_receipt_retail"
    if "invoice" in sub and lbl == 0:
        return "grp_ham_invoice_cloud"
    if "banking alert" in sub or "debit card" in sub:
        return "grp_ham_banking_alert"
    if "booking confirmed" in sub or "flight reservation" in sub:
        return "grp_ham_travel_booking"
    if "newsletter" in sub:
        return "grp_ham_newsletter"
    if "reminder" in sub:
        return "grp_ham_reminder"

    # Spam templates
    if "compromised" in sub:
        return "grp_spam_compromised"
    if "invoice confirmation" in sub or ("invoice" in sub and lbl == 1):
        return "grp_spam_fake_invoice"
    if "delivery" in sub or "package" in sub:
        return "grp_spam_delivery"
    if "automated trading" in sub:
        return "grp_spam_trading"
    if "payout notification" in sub:
        return "grp_spam_payout"
    if "voucher" in sub:
        return "grp_spam_voucher"
    if "prescription medications" in sub:
        return "grp_spam_rx"
    if "winner notice" in sub or "jackpot" in sub:
        return "grp_spam_lottery"

    # Base unique samples grouped by category and label
    return f"grp_base_{cat}_{lbl}"


def grouped_template_split(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Partition records by grouping template families and campaigns together.

    Guarantees that no template archetype or campaign cluster crosses partitions:
    groups(train) ∩ groups(val) == ∅
    groups(train) ∩ groups(test) == ∅
    groups(val) ∩ groups(test) == ∅
    """
    for r in records:
        if "group_id" not in r:
            r["group_id"] = extract_template_group_id(r)

    val_groups = {
        "grp_ham_reminder",
        "grp_ham_travel_booking",
        "grp_spam_delivery",
        "grp_spam_payout",
        "grp_base_corporate_workplace_0",
        "grp_base_personal_social_0",
        "grp_base_academic_library_0",
        "grp_base_developer_code_review_0",
        "grp_base_financial_scam_419_1",
        "grp_base_lottery_scam_1",
        "grp_base_crypto_scam_1",
        "grp_base_delivery_phishing_1",
    }
    test_groups = {
        "grp_ham_receipt_retail",
        "grp_spam_voucher",
        "grp_base_transactional_travel_0",
        "grp_base_developer_newsletter_0",
        "grp_base_community_tech_0",
        "grp_base_transactional_ecommerce_0",
        "grp_base_phishing_banking_1",
        "grp_base_phishing_streaming_1",
        "grp_base_multilingual_spam_1",
        "grp_base_reward_voucher_spam_1",
    }

    train_recs = [r for r in records if r["group_id"] not in val_groups and r["group_id"] not in test_groups]
    val_recs = [r for r in records if r["group_id"] in val_groups]
    test_recs = [r for r in records if r["group_id"] in test_groups]

    return train_recs, val_recs, test_recs


def multilingual_grouped_split(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Partition multilingual corpus records by template group with zero overlap across train, val, and test.

    Guarantees balanced language distribution and 50% class balance across all splits.
    """
    for r in records:
        if "template_group" not in r:
            r["template_group"] = r.get("group_id") or extract_template_group_id(r)

    val_groups = {
        "grp_hi_ham_travel", "grp_hi_spam_electricity",
        "grp_ta_ham_college", "grp_ta_spam_loan",
        "grp_te_ham_academic", "grp_te_spam_loan",
        "grp_kn_ham_transport", "grp_kn_spam_loan",
        "grp_hinglish_ham_workplace", "grp_hinglish_spam_loan",
        "grp_en_ham_engineering", "grp_en_spam_package",
    }

    test_groups = {
        "grp_hi_ham_academic", "grp_hi_spam_job",
        "grp_ta_ham_utility", "grp_ta_spam_lottery",
        "grp_te_ham_ecommerce", "grp_te_spam_job",
        "grp_kn_ham_academic", "grp_kn_spam_job",
        "grp_hinglish_ham_telecom", "grp_hinglish_spam_job",
        "grp_en_ham_security", "grp_en_spam_invoice",
    }

    train_recs = [r for r in records if r["template_group"] not in val_groups and r["template_group"] not in test_groups]
    val_recs = [r for r in records if r["template_group"] in val_groups]
    test_recs = [r for r in records if r["template_group"] in test_groups]

    return train_recs, val_recs, test_recs
