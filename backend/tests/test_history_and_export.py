"""Tests for history operations, bulk deletion, feedback, and formula-safe CSV/JSON export.
"""

def test_history_crud_and_bulk_deletion(client):
    # Create two analyses
    res1 = client.post("/api/v1/predict", json={"subject": "Email One", "body": "Meeting notes."})
    res2 = client.post("/api/v1/predict", json={"subject": "Email Two", "body": "Prize winner."})

    id1 = res1.json()["id"]
    id2 = res2.json()["id"]

    # Retrieve history
    hist = client.get("/api/v1/history").json()
    assert hist["total"] == 2

    # Bulk delete id1 and id2
    del_res = client.request("DELETE", "/api/v1/history", json={"ids": [id1, id2]})
    assert del_res.status_code == 200
    assert del_res.json()["deleted_count"] == 2

    # Confirm history is empty
    hist_after = client.get("/api/v1/history").json()
    assert hist_after["total"] == 0


def test_csv_formula_injection_defense(client):
    # Submit analysis with dangerous CSV formula prefixes (=, +, -, @)
    dangerous_subject = "=cmd|' /C calc'!A0"
    client.post("/api/v1/predict", json={
        "subject": dangerous_subject,
        "body": "Test body",
    })

    # Export CSV
    csv_res = client.get("/api/v1/reports/export?format=csv")
    assert csv_res.status_code == 200
    content = csv_res.text

    # Verify that the cell starts with apostrophe to neutralize execution in Excel/Calc
    assert "'=cmd|' /C calc'!A0" in content
    # Bare unescaped formula should NOT be at cell boundary
    assert "\n=cmd|" not in content


def test_feedback_submission(client):
    pred = client.post("/api/v1/predict", json={"subject": "Newsletter", "body": "Weekly tech tips."}).json()
    analysis_id = pred["id"]

    fb_res = client.post("/api/v1/feedback", json={
        "analysis_id": analysis_id,
        "suggested_label": "Legitimate",
        "comments": "This is our company internal newsletter.",
    })
    assert fb_res.status_code == 201
    assert fb_res.json()["suggested_label"] == "Legitimate"


def test_user_scoped_csv_and_json_export(client):
    # Register user1 and user2
    client.post("/api/v1/auth/register", json={"username": "exp_u1", "email": "exp_u1@example.com", "password": "Password123!"})
    t1 = client.post("/api/v1/auth/login", json={"username": "exp_u1", "password": "Password123!"}).json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}

    client.post("/api/v1/auth/register", json={"username": "exp_u2", "email": "exp_u2@example.com", "password": "Password123!"})
    t2 = client.post("/api/v1/auth/login", json={"username": "exp_u2", "password": "Password123!"}).json()["access_token"]
    h2 = {"Authorization": f"Bearer {t2}"}

    # User 1 submits analysis
    client.post("/api/v1/predict", headers=h1, json={"subject": "U1 Secret Invoice", "body": "Invoice #98234 for services"})

    # User 2 submits analysis
    client.post("/api/v1/predict", headers=h2, json={"subject": "U2 Bank Statement", "body": "Statement for account #1122"})

    # User 1 exports CSV
    csv_u1 = client.get("/api/v1/reports/export?format=csv", headers=h1).text
    assert "U1 Secret Invoice" in csv_u1
    assert "U2 Bank Statement" not in csv_u1

    # User 2 exports JSON
    json_u2 = client.get("/api/v1/reports/export?format=json", headers=h2).json()
    assert len(json_u2) == 1
    assert json_u2[0]["subject"] == "U2 Bank Statement"


def test_history_search_and_label_filters(client):
    # Submit 1 ham and 1 spam
    client.post("/api/v1/predict", json={"subject": "Architecture Design", "body": "Sprint meeting review"})
    client.post("/api/v1/predict", json={"subject": "Lottery Jackpot Winner", "body": "Claim your cash prize now"})

    # Search filter
    res_search = client.get("/api/v1/history?search=Architecture").json()
    assert res_search["total"] == 1
    assert "Architecture" in res_search["items"][0]["subject"]

    # Label filter for Spam
    res_spam = client.get("/api/v1/history?label=Spam").json()
    assert all(i["is_spam"] is True for i in res_spam["items"])

    # Label filter for Legitimate
    res_ham = client.get("/api/v1/history?label=Legitimate").json()
    assert all(i["is_spam"] is False for i in res_ham["items"])

