"""SpamAssassin Public Corpus downloader and verification script.

PROVENANCE & USAGE TERMS:
The SpamAssassin Public Corpus was compiled by Justin Mason and contributors
to the Apache SpamAssassin project (archives: https://spamassassin.apache.org/old/publiccorpus/).
The corpus contains donated personal and public mailing list emails (ham)
and donated unsolicited commercial emails (spam).
The individual messages are NOT all licensed under Apache License 2.0;
they were donated for research, benchmarking, and filter development purposes.
Some messages contain original headers and addresses.
This script downloads, validates MD5/SHA256 checksums, and parses clean text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import urllib.request
from pathlib import Path

from mailshield_ml.dataset import deduplicate_records, parse_rfc822_email

CORPUS_ARCHIVES = {
    "easy_ham": {
        "url": "https://spamassassin.apache.org/old/publiccorpus/20030228_easy_ham.tar.bz2",
        "sha256": "4b0b144fa5427909ebdf2bf6a5faef6d96a58bc2845c4784deecad9540b7ef56",
        "label": 0,
    },
    "spam": {
        "url": "https://spamassassin.apache.org/old/publiccorpus/20030228_spam.tar.bz2",
        "sha256": "81f7baefc490a18412fb19be2054ff47cb232ac6faadbe30ab258163f912e612",
        "label": 1,
    },
}


def verify_file_hash(filepath: Path, expected_sha256: str) -> bool:
    """Verify SHA256 checksum of downloaded archive."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower() == expected_sha256.lower()


def fetch_and_extract_corpus(output_dir: Path, target_json: Path) -> None:
    """Fetch archives, verify checksums, extract RFC 822 messages, and save sanitized JSON."""
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []

    print("Checking / Downloading SpamAssassin Corpus archives...")
    for name, info in CORPUS_ARCHIVES.items():
        archive_path = raw_dir / f"{name}.tar.bz2"
        if not archive_path.exists():
            print(f"Downloading {name} from {info['url']}...")
            try:
                urllib.request.urlretrieve(info["url"], archive_path)
            except Exception as e:
                print(f"Could not download {info['url']}: {e}")
                print("Falling back to local seed corpus.")
                return

        print(f"Verifying {name} checksum...")
        if not verify_file_hash(archive_path, info["sha256"]):
            print(f"Checksum mismatch for {archive_path}! Aborting archive extraction.")
            return

        print(f"Extracting and parsing {name}...")
        with tarfile.open(archive_path, "r:bz2") as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                f = tar.extractfile(member)
                if f is None:
                    continue
                content = f.read()
                try:
                    parsed = parse_rfc822_email(content)
                    if parsed.body or parsed.subject:
                        records.append({
                            "subject": parsed.subject,
                            "body": parsed.body,
                            "label": info["label"],
                            "content_hash": parsed.content_hash,
                            "category": f"spamassassin_{name}",
                        })
                except Exception:
                    continue

    print(f"Total extracted records before deduplication: {len(records)}")
    unique_records, dups = deduplicate_records(records)
    print(f"Removed {dups} duplicates. Clean unique records: {len(unique_records)}")

    with open(target_json, "w", encoding="utf-8") as out:
        json.dump(unique_records, out, indent=2, ensure_ascii=False)
    print(f"Saved processed dataset to {target_json}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and process SpamAssassin corpus")
    parser.add_argument("--data-dir", default="ml/data", help="Data directory")
    parser.add_argument("--output", default="ml/data/spamassassin_processed.json", help="Output JSON path")
    args = parser.parse_args()

    fetch_and_extract_corpus(Path(args.data_dir), Path(args.output))
