"""Tests for Model Lab endpoints, validation threshold simulator, and admin-only evaluation execution.
"""

from backend.app.core.security import create_access_token


def test_models_overview_endpoint(client):
    res = client.get("/api/v1/models")
    assert res.status_code == 200
    data = res.json()
    assert len(data["models"]) >= 3
    names = [m["name"] for m in data["models"]]
    assert "logistic_regression" in names
    assert "naive_bayes" in names
    assert "linear_svm" in names
    assert data["vocab_size"] > 0


def test_validation_threshold_simulation_endpoint(client):
    # Simulate threshold at 0.35 on logistic_regression
    res = client.get("/api/v1/models/threshold-metrics?model=logistic_regression&threshold=0.35")
    assert res.status_code == 200
    data = res.json()
    assert data["model_name"] == "logistic_regression"
    assert "current_metrics" in data
    assert data["current_metrics"]["threshold"] == 0.35
    assert 0.0 <= data["current_metrics"]["accuracy"] <= 1.0
    assert 0.0 <= data["current_metrics"]["precision"] <= 1.0
    assert 0.0 <= data["current_metrics"]["recall"] <= 1.0
    assert 0.0 <= data["current_metrics"]["f1_score"] <= 1.0
    assert len(data["current_metrics"]["confusion_matrix"]) == 2
    assert len(data["sweep_curve"]) > 0


def test_evaluation_run_requires_admin_authorization(client, db_session):
    from backend.app.core.security import hash_password
    from backend.app.models.user import User

    # Create regular user
    user = User(
        username="standard_user",
        email="user@example.com",
        hashed_password=hash_password("password"),
        role="user",
    )
    # Create admin user
    admin = User(
        username="admin_user",
        email="admin@example.com",
        hashed_password=hash_password("password"),
        role="admin",
    )
    db_session.add_all([user, admin])
    db_session.commit()

    user_token = create_access_token(user.id, role="user")
    admin_token = create_access_token(admin.id, role="admin")

    # Regular user attempting evaluation run gets 403 Forbidden
    res_user = client.post("/api/v1/evaluation/run", headers={"Authorization": f"Bearer {user_token}"})
    assert res_user.status_code == 403
    assert "Administrative privileges required" in res_user.json()["detail"]

    # Admin user attempting evaluation run succeeds
    res_admin = client.post("/api/v1/evaluation/run", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert isinstance(res_admin.json(), list)
    assert len(res_admin.json()) >= 3


def test_invalid_model_name_rejected(client):
    res = client.post("/api/v1/predict", json={
        "subject": "Test",
        "body": "Some body content",
        "model_name": "non_existent_neural_net",
    })
    assert res.status_code == 400
    assert "Unknown model" in res.json()["detail"]


def test_validation_simulation_invalid_model(client):
    res = client.get("/api/v1/models/threshold-metrics?model=non_existent_model&threshold=0.5")
    assert res.status_code == 400
    assert "No validation scores found" in res.json()["detail"]

