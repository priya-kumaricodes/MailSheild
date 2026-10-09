import json
import os
import signal
import socket
import subprocess
import time
import urllib.request
import zipfile

import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
APP_PATH = os.path.join(ROOT_DIR, "apps/desktop/dist/MailShield.app")
BIN_PATH = os.path.join(APP_PATH, "Contents/Resources/backend_bin/mailshield_server")
ZIP_PATH = os.path.join(ROOT_DIR, "apps/desktop/dist/MailShield-2.1.0-mac-arm64.zip")


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_standalone_bundle_and_archive_exist():
    """Verify that MailShield.app and the release zip archive exist with native executable."""
    assert os.path.exists(APP_PATH), f"MailShield.app bundle not found at {APP_PATH}"
    assert os.path.exists(BIN_PATH), f"Standalone backend executable not found at {BIN_PATH}"
    assert os.access(BIN_PATH, os.X_OK), f"Executable {BIN_PATH} does not have execute permissions"
    assert os.path.exists(ZIP_PATH), f"Distributable ZIP archive not found at {ZIP_PATH}"

    # Verify zip contains the standalone binary
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        names = zf.namelist()
        bin_in_zip = any("backend_bin/mailshield_server" in name for name in names)
        assert bin_in_zip, "ZIP archive does not contain Contents/Resources/backend_bin/mailshield_server"


@pytest.mark.standalone
def test_standalone_executable_clean_execution():
    """Test running the standalone binary in a clean environment without Python or repo dependencies."""
    port = get_free_port()
    test_dir = os.path.join(ROOT_DIR, "build/test_standalone_clean")
    os.makedirs(test_dir, exist_ok=True)
    db_file = os.path.join(test_dir, "desktop_clean.db")
    if os.path.exists(db_file):
        os.remove(db_file)

    # Scrub environment to simulate a machine with no python or developer tools
    clean_env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": test_dir,
        "HOME": test_dir,
        "MAILSHIELD_MODE": "desktop",
    }

    proc = subprocess.Popen(
        [
            BIN_PATH,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--database-url",
            f"sqlite:///{db_file}",
        ],
        cwd=test_dir,
        env=clean_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        # Wait for backend health
        health_url = f"http://127.0.0.1:{port}/api/v1/health"
        is_healthy = False
        health_data = {}
        for _ in range(40):
            time.sleep(0.5)
            try:
                req = urllib.request.Request(health_url)
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        health_data = json.loads(resp.read().decode())
                        is_healthy = True
                        break
            except Exception:
                pass

        if not is_healthy:
            proc.terminate()
            stdout, _ = proc.communicate(timeout=3)
            raise AssertionError(f"Standalone backend failed to respond to health checks within timeout.\nProcess output:\n{stdout}")

        assert health_data.get("status") == "healthy"
        assert health_data.get("model_loaded") is True
        assert "logistic_regression" in health_data.get("active_models", [])

        # Test live inference
        predict_url = f"http://127.0.0.1:{port}/api/v1/predict"
        payload = json.dumps(
            {
                "subject": "Urgent Security Verification Notice",
                "body": "Your bank account has been suspended due to suspicious login attempts. Verify immediately.",
                "model_name": "logistic_regression",
                "threshold": 0.5,
                "store_content": False,
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            predict_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            assert resp.status == 200
            pred = json.loads(resp.read().decode())
            assert pred["prediction"] == "Spam"
            assert pred["is_spam"] is True
            assert pred["score"] > 0.5
            assert "explanations" in pred
            assert len(pred["explanations"]["top_spam_features"]) > 0

        # Verify database creation
        assert os.path.exists(db_file), "SQLite database was not created in specified clean path"
        assert os.path.getsize(db_file) > 0

    finally:
        # Verify clean termination
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        assert proc.returncode is not None
