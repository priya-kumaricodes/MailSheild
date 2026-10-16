"""Standalone native entrypoint for MailShield backend server.
Designed to be compiled with PyInstaller into a standalone executable.
"""
import argparse
import os
import sys
from pathlib import Path

# When running frozen under PyInstaller
if getattr(sys, "frozen", False):
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    sys.path.insert(0, str(bundle_dir))
    sys.path.insert(0, str(bundle_dir / "_internal"))
    sys.path.insert(0, str(bundle_dir / "ml" / "src"))
    sys.path.insert(0, str(bundle_dir / "_internal" / "ml" / "src"))
else:
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(repo_root / "ml" / "src"))

import threading
import time


def _watch_parent_process():
    """Monitor parent process ID. If parent terminates (e.g. Electron quits), exit cleanly."""
    initial_ppid = os.getppid()
    while True:
        time.sleep(1.5)
        current_ppid = os.getppid()
        if current_ppid != initial_ppid:
            print("[MailShield Server] Parent process terminated. Shutting down cleanly...")
            os._exit(0)


def main():
    parser = argparse.ArgumentParser(description="MailShield Standalone Backend Service")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"), help="Host to bind")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")), help="Port to bind")
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"), help="Database URL")
    parser.add_argument("--artifacts-dir", default=os.environ.get("ARTIFACTS_DIR"), help="ML Artifacts directory")
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
    if args.artifacts_dir:
        os.environ["ARTIFACTS_DIR"] = args.artifacts_dir

    from backend.app.core.config import settings
    if args.database_url:
        settings.DATABASE_URL = args.database_url
    if args.artifacts_dir:
        settings.ARTIFACTS_DIR = args.artifacts_dir

    from backend.app.db.session import init_db
    init_db()

    import uvicorn

    from backend.app.main import app

    print(f"[MailShield Server] Starting on http://{args.host}:{args.port}")
    print(f"[MailShield Server] Database: {settings.DATABASE_URL}")
    print(f"[MailShield Server] Artifacts: {settings.ARTIFACTS_DIR}")

    # Start parent watchdog thread
    watchdog = threading.Thread(target=_watch_parent_process, daemon=True)
    watchdog.start()

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
