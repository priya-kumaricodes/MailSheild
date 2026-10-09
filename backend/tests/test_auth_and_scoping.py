"""Tests verifying authentication, JWT issuance, and cross-user isolation of history records.
"""

def test_auth_registration_and_login(client):
    # Register user 1
    reg_res = client.post("/api/v1/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password123!",
    })
    assert reg_res.status_code == 201
    user1_data = reg_res.json()
    assert user1_data["username"] == "alice"
    assert "hashed_password" not in user1_data

    # Login user 1
    login_res = client.post("/api/v1/auth/login", json={
        "username": "alice",
        "password": "Password123!",
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Access /auth/me with token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "alice"


def test_user_scoping_prevents_cross_user_history_access(client):
    # Register user1 (Alice)
    client.post("/api/v1/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password123!",
    })
    token1 = client.post("/api/v1/auth/login", json={"username": "alice", "password": "Password123!"}).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Register user2 (Bob)
    client.post("/api/v1/auth/register", json={
        "username": "bob",
        "email": "bob@example.com",
        "password": "Password123!",
    })
    token2 = client.post("/api/v1/auth/login", json={"username": "bob", "password": "Password123!"}).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Alice submits a prediction
    pred_res = client.post("/api/v1/predict", headers=headers1, json={
        "subject": "Alice Private Email",
        "body": "Hi Alice, this is your secret code review.",
    })
    assert pred_res.status_code == 200
    alice_record_id = pred_res.json()["id"]

    # Alice checks her history: sees the record
    alice_hist = client.get("/api/v1/history", headers=headers1).json()
    assert alice_hist["total"] == 1
    assert alice_hist["items"][0]["id"] == alice_record_id

    # Bob checks his history: total is 0 (cannot see Alice's records!)
    bob_hist = client.get("/api/v1/history", headers=headers2).json()
    assert bob_hist["total"] == 0

    # Bob tries to directly fetch Alice's record by ID: returns 404
    bob_detail = client.get(f"/api/v1/history/{alice_record_id}", headers=headers2)
    assert bob_detail.status_code == 404

    # Bob tries to delete Alice's record by ID: returns 404
    bob_del = client.delete(f"/api/v1/history/{alice_record_id}", headers=headers2)
    assert bob_del.status_code == 404

    # Alice's record is still intact
    alice_detail = client.get(f"/api/v1/history/{alice_record_id}", headers=headers1)
    assert alice_detail.status_code == 200
    assert alice_detail.json()["id"] == alice_record_id

    # Anonymous user (no Authorization header) cannot view Alice's record
    anon_detail = client.get(f"/api/v1/history/{alice_record_id}")
    assert anon_detail.status_code == 404

    # Anonymous user cannot delete Alice's record
    anon_del = client.delete(f"/api/v1/history/{alice_record_id}")
    assert anon_del.status_code == 404


def test_cross_user_bulk_delete_prevention(client):
    # Register Alice and Bob
    client.post("/api/v1/auth/register", json={"username": "alice_bd", "email": "alice_bd@example.com", "password": "Password123!"})
    token_a = client.post("/api/v1/auth/login", json={"username": "alice_bd", "password": "Password123!"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    client.post("/api/v1/auth/register", json={"username": "bob_bd", "email": "bob_bd@example.com", "password": "Password123!"})
    token_b = client.post("/api/v1/auth/login", json={"username": "bob_bd", "password": "Password123!"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Alice creates a record
    res_a = client.post("/api/v1/predict", headers=headers_a, json={"subject": "Alice Memo", "body": "Confidential meeting"})
    alice_id = res_a.json()["id"]

    # Bob attempts to bulk delete Alice's record ID
    res_del = client.request("DELETE", "/api/v1/history", headers=headers_b, json={"ids": [alice_id]})
    assert res_del.status_code == 200
    assert res_del.json()["deleted_count"] == 0  # 0 deleted because Bob doesn't own it

    # Alice's record is still present
    check_res = client.get(f"/api/v1/history/{alice_id}", headers=headers_a)
    assert check_res.status_code == 200


def test_invalid_or_expired_token_rejected(client):
    # Invalid token
    res_invalid = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
    assert res_invalid.status_code == 401

    # Malformed header
    res_malformed = client.get("/api/v1/auth/me", headers={"Authorization": "Basic 12345"})
    assert res_malformed.status_code == 401

