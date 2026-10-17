from fastapi.testclient import TestClient


def test_get_supported_languages(client: TestClient):
    response = client.get("/api/v1/evaluation/languages")
    assert response.status_code == 200
    langs = response.json()
    codes = [lang["code"] for lang in langs]
    assert "all" in codes
    assert "en" in codes
    assert "hi" in codes
    assert "ta" in codes
    assert "te" in codes
    assert "kn" in codes
    assert "hinglish" in codes


def test_get_evaluation_metrics_aggregate_and_per_language(client: TestClient):
    # Aggregate test metrics
    resp_all = client.get("/api/v1/evaluation/metrics?model_name=linear_svm&split=test&language=all")
    assert resp_all.status_code == 200
    data_all = resp_all.json()
    assert "accuracy" in data_all
    assert "precision" in data_all
    assert "recall" in data_all
    assert "f1" in data_all
    assert "fpr" in data_all
    assert "fnr" in data_all
    assert data_all["accuracy"] >= 0.85

    # Hindi-specific metrics
    resp_hi = client.get("/api/v1/evaluation/metrics?model_name=linear_svm&split=test&language=hi")
    assert resp_hi.status_code == 200
    data_hi = resp_hi.json()
    assert data_hi["language"] == "hi"
    assert data_hi["samples"] == 6


def test_get_confusion_matrix(client: TestClient):
    resp = client.get("/api/v1/evaluation/confusion-matrix?model_name=linear_svm&split=test&language=all")
    assert resp.status_code == 200
    data = resp.json()
    assert "grid" in data
    assert len(data["grid"]) == 2
    assert len(data["grid"][0]) == 2
    assert "rates" in data
    assert "false_positive_rate" in data["rates"]


def test_get_model_comparison(client: TestClient):
    resp = client.get("/api/v1/evaluation/compare")
    assert resp.status_code == 200
    data = resp.json()
    assert "english_baseline" in data
    assert "multilingual_models" in data
    assert "logistic_regression" in data["multilingual_models"]
    assert "linear_svm" in data["multilingual_models"]


def test_get_dataset_provenance(client: TestClient):
    resp = client.get("/api/v1/evaluation/provenance")
    assert resp.status_code == 200
    data = resp.json()
    assert data["zero_group_leakage"] is True
    assert data["total_records"] == 144
    assert "splits" in data
    assert data["splits"]["train"]["template_groups"] == 24
    assert data["splits"]["validation"]["template_groups"] == 12
    assert data["splits"]["test"]["template_groups"] == 12


def test_get_demo_samples(client: TestClient):
    resp = client.get("/api/v1/evaluation/demo-samples")
    assert resp.status_code == 200
    samples = resp.json()
    assert len(samples) >= 12
    languages = {s["language"] for s in samples}
    assert {"en", "hi", "ta", "te", "kn", "hinglish"}.issubset(languages)


def test_predict_endpoint_returns_language_and_phishing_analysis(client: TestClient):
    # Hindi phishing email
    payload = {
        "subject": "अंतिम चेतावनी: खाता बंद",
        "body": "आपका स्टेट बैंक खाता 24 घंटे में बंद कर दिया जाएगा। तुरंत http://sbi-fake-kyc.com/login पर आधार सत्यापित करें।",
        "sender": "support@sbi-fake-kyc.com",
        "model_name": "multilingual_linear_svm",
    }
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_spam"] is True
    assert "language_analysis" in data
    assert data["language_analysis"]["detected_language"] == "hi"
    assert data["language_analysis"]["primary_script"] == "Devanagari"
    assert "phishing_analysis" in data
    assert data["phishing_analysis"]["risk_level"] in ("high", "critical")
    assert data["phishing_analysis"]["has_urgency_threat"] is True
