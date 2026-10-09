"""Tests verifying offline desktop inference and SQLite persistence without network connectivity.
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app


def test_desktop_offline_inference_and_persistence(tmp_path):
    # Setup temporary SQLite database representing desktop installation
    test_db_path = tmp_path / "mailshield_offline.db"
    desktop_db_url = f"sqlite:///{test_db_path}"

    engine = create_engine(desktop_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionTest()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Set desktop mode
    orig_mode = settings.MAILSHIELD_MODE
    settings.MAILSHIELD_MODE = "desktop"

    try:
        with TestClient(app) as client:
            # 1. Health check reports desktop mode
            h_res = client.get("/api/v1/health")
            assert h_res.status_code == 200
            assert h_res.json()["mode"] == "desktop"
            assert h_res.json()["model_loaded"] is True
            assert h_res.json()["database"] is True

            # 2. Run prediction offline on phishing sample
            pred_res = client.post("/api/v1/predict", json={
                "subject": "Offline Security Test",
                "body": "Congratulations, claim your lottery cash prize payout now!",
                "model_name": "logistic_regression",
            })
            assert pred_res.status_code == 200
            pred_data = pred_res.json()
            assert pred_data["prediction"] == "Spam"
            assert pred_data["score"] > 0.5
            analysis_id = pred_data["id"]

            # 3. Query history in desktop mode without bearer token (transparent local desktop user)
            hist_res = client.get("/api/v1/history")
            assert hist_res.status_code == 200
            hist_data = hist_res.json()
            assert hist_data["total"] >= 1
            assert any(item["id"] == analysis_id for item in hist_data["items"])

            # 4. Verify detail retrieval
            detail_res = client.get(f"/api/v1/history/{analysis_id}")
            assert detail_res.status_code == 200
            assert detail_res.json()["id"] == analysis_id
            assert "explanations" in detail_res.json()

    finally:
        settings.MAILSHIELD_MODE = orig_mode
        app.dependency_overrides.clear()
