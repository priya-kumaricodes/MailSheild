"""Tests for file upload handling, MIME parsing, size limits, and extension restrictions.
"""

import io


def test_upload_valid_eml_file(client):
    eml_content = b"""From: alerts@bank.com
To: user@example.com
Subject: Urgent Security Warning
Content-Type: text/plain

Suspicious unauthorized login detected from unknown location.
Verify your debit card pin immediately.
"""
    files = {"file": ("alert.eml", io.BytesIO(eml_content), "message/rfc822")}
    res = client.post("/api/v1/predict/file", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "Security Warning" in data["prediction"] or data["prediction"] in ("Spam", "Legitimate")
    assert "explanations" in data


def test_upload_valid_txt_file(client):
    txt_content = b"Subject: Team Lunch\n\nHey everyone, meeting at 12pm for lunch."
    files = {"file": ("email.txt", io.BytesIO(txt_content), "text/plain")}
    res = client.post("/api/v1/predict/file", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["prediction"] in ("Spam", "Legitimate")


def test_upload_unsupported_file_extension(client):
    malicious_content = b"MZ\x90\x00\x03\x00\x00\x00"
    files = {"file": ("malware.exe", io.BytesIO(malicious_content), "application/octet-stream")}
    res = client.post("/api/v1/predict/file", files=files)
    assert res.status_code == 400
    assert "Invalid file type" in res.json()["detail"]


def test_upload_oversized_file_rejected(client):
    # 6 MB file (limit is 5 MB)
    oversized = b"A" * (6 * 1024 * 1024)
    files = {"file": ("oversized.txt", io.BytesIO(oversized), "text/plain")}
    res = client.post("/api/v1/predict/file", files=files)
    assert res.status_code == 413
    assert "exceeds maximum allowed size" in res.json()["detail"]
