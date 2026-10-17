"""Tests for prediction API, feature explanations, and model options.
"""

def test_predict_legitimate_email(client):
    res = client.post("/api/v1/predict", json={
        "subject": "Sprint planning notes and review meeting",
        "body": "Hi team,\nHere are the notes from our architecture review meeting. We finalized the database migration plans.",
        "model_name": "logistic_regression",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["prediction"] == "Legitimate"
    assert data["is_spam"] is False
    assert 0.0 <= data["score"] <= 1.0
    assert data["score_type"] == "probability"
    assert data["calibrated"] is True
    assert "explanations" in data
    assert len(data["explanations"]["top_legitimate_features"]) > 0


def test_predict_spam_email(client):
    res = client.post("/api/v1/predict", json={
        "subject": "URGENT: Claim your $1,000,000 cash lottery prize now!",
        "body": "Congratulations! You won the international global lottery. Wire $350 clearance fee to receive your check.",
        "model_name": "logistic_regression",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["prediction"] == "Spam"
    assert data["is_spam"] is True
    assert data["score"] > 0.5
    assert len(data["explanations"]["top_spam_features"]) > 0


def test_predict_empty_body_rejected(client):
    res = client.post("/api/v1/predict", json={
        "subject": "Test",
        "body": "   ",
    })
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_predict_with_naive_bayes_and_svm(client):
    # Test Naive Bayes
    res_nb = client.post("/api/v1/predict", json={
        "subject": "Cash prize winner",
        "body": "Congratulations you won cash payout wire transfer.",
        "model_name": "naive_bayes",
    })
    assert res_nb.status_code == 200
    assert res_nb.json()["model_name"] == "naive_bayes"
    assert res_nb.json()["score_type"] == "probability"
    assert res_nb.json()["calibrated"] is False  # Correctly labeled

    # Test Linear SVM
    res_svm = client.post("/api/v1/predict", json={
        "subject": "Meeting Friday",
        "body": "Sprint planning architecture review.",
        "model_name": "linear_svm",
    })
    assert res_svm.status_code == 200
    assert res_svm.json()["model_name"] == "linear_svm"
    assert res_svm.json()["score_type"] == "probability"
    assert res_svm.json()["calibrated"] is True
