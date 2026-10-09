"""Comprehensive tests for Gmail OAuth 2.0 PKCE, CSRF protection,
token encryption, grant revocation, input limits, and privacy defaults.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.crypto import get_token_encryption_service
from backend.app.core.security import create_access_token
from backend.app.models.analysis import AnalysisRecord
from backend.app.models.gmail_account import GmailAccount
from backend.app.models.oauth_state import OAuthState
from backend.app.models.user import User


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.username == "test_alice").first()
    if not user:
        user = User(
            username="test_alice",
            email="alice@test.local",
            hashed_password="hashed_pw_secret",
            role="user",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def test_user_b(db_session: Session) -> User:
    user = db_session.query(User).filter(User.username == "test_bob").first()
    if not user:
        user = User(
            username="test_bob",
            email="bob@test.local",
            hashed_password="hashed_pw_secret",
            role="user",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    token = create_access_token(test_user.id, role=test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b(test_user_b: User) -> dict[str, str]:
    token = create_access_token(test_user_b.id, role=test_user_b.role)
    return {"Authorization": f"Bearer {token}"}


def test_unconfigured_credentials_returns_safe_response(client: TestClient, auth_headers: dict[str, str]):
    """When Google credentials are not set, return is_configured=False without throwing 500."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", ""), patch.object(settings, "GOOGLE_CLIENT_SECRET", ""):
        resp = client.get("/api/v1/gmail/auth-url", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_configured"] is False
        assert data["auth_url"] == ""

        status_resp = client.get("/api/v1/gmail/status", headers=auth_headers)
        assert status_resp.status_code == 200
        assert status_resp.json()["is_configured"] is False
        assert status_resp.json()["connected"] is False


def test_auth_url_generation_web_and_desktop_pkce(client: TestClient, auth_headers: dict[str, str], db_session: Session):
    """Verify web and desktop auth URL generation with minimal scopes and PKCE."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id-123.apps.googleusercontent.com"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret-xyz"):

        # 1. Web flow
        resp = client.get("/api/v1/gmail/auth-url?client_type=web", headers=auth_headers)
        assert resp.status_code == 200
        web_data = resp.json()
        assert web_data["is_configured"] is True
        assert "accounts.google.com/o/oauth2/v2/auth" in web_data["auth_url"]
        assert "scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email" in web_data["auth_url"]
        assert "gmail.modify" not in web_data["auth_url"]  # Strictly read-only
        assert "code_challenge" not in web_data["auth_url"]

        state_rec = db_session.query(OAuthState).filter(OAuthState.state == web_data["state"]).first()
        assert state_rec is not None
        assert state_rec.client_type == "web"
        assert state_rec.code_verifier is None

        # 2. Desktop PKCE flow
        resp_desktop = client.get("/api/v1/gmail/auth-url?client_type=desktop", headers=auth_headers)
        assert resp_desktop.status_code == 200
        desk_data = resp_desktop.json()
        assert "code_challenge=" in desk_data["auth_url"]
        assert "code_challenge_method=S256" in desk_data["auth_url"]

        desk_state = db_session.query(OAuthState).filter(OAuthState.state == desk_data["state"]).first()
        assert desk_state is not None
        assert desk_state.client_type == "desktop"
        assert desk_state.code_verifier is not None
        assert len(desk_state.code_verifier) >= 43


def test_arbitrary_redirect_uri_rejection(client: TestClient, auth_headers: dict[str, str]):
    """Arbitrary or malicious redirect URIs must be rejected."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret"):
        resp = client.get(
            "/api/v1/gmail/auth-url?client_type=web&redirect_uri=https://attacker.com/evil-callback",
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "Invalid redirect URI" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_web_callback_success_and_token_encryption(
    client: TestClient, auth_headers: dict[str, str], db_session: Session, test_user: User
):
    """Test full web OAuth code exchange, AES-256-GCM token encryption, and status response."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret"):

        # Create state
        url_resp = client.get("/api/v1/gmail/auth-url?client_type=web", headers=auth_headers)
        state = url_resp.json()["state"]

        # Mock Google token and userinfo responses
        def mock_post(url, **kwargs):
            if "oauth2.googleapis.com/token" in str(url):
                return httpx.Response(
                    200,
                    json={
                        "access_token": "mock-access-token-987",
                        "refresh_token": "mock-refresh-token-456",
                        "expires_in": 3600,
                        "scope": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email",
                    },
                    request=httpx.Request("POST", str(url)),
                )
            return httpx.Response(404, request=httpx.Request("POST", str(url)))

        def mock_get(url, **kwargs):
            if "oauth2/v2/userinfo" in str(url):
                return httpx.Response(
                    200,
                    json={"email": "alice@gmail.com"},
                    request=httpx.Request("GET", str(url)),
                )
            return httpx.Response(404, request=httpx.Request("GET", str(url)))

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("httpx.AsyncClient.get", side_effect=mock_get):

            cb_resp = client.post(
                "/api/v1/gmail/callback",
                json={"code": "valid-google-code-123", "state": state},
                headers=auth_headers,
            )
            assert cb_resp.status_code == 200
            data = cb_resp.json()
            assert data["connected"] is True
            assert data["email"] == "alice@gmail.com"
            assert "access_token" not in data  # Never expose tokens!
            assert "refresh_token" not in data

            # Verify in DB that tokens are encrypted and not plain
            account = db_session.query(GmailAccount).filter(GmailAccount.user_id == test_user.id).first()
            assert account is not None
            assert account.encrypted_access_token != "mock-access-token-987"
            assert account.encrypted_refresh_token != "mock-refresh-token-456"

            # Decrypt verify
            crypto = get_token_encryption_service()
            dec_access = crypto.decrypt(account.encrypted_access_token, user_id=test_user.id)
            dec_refresh = crypto.decrypt(account.encrypted_refresh_token, user_id=test_user.id)
            assert dec_access == "mock-access-token-987"
            assert dec_refresh == "mock-refresh-token-456"


def test_oauth_state_replay_rejected(client: TestClient, auth_headers: dict[str, str]):
    """Replaying an OAuth state token must be rejected with HTTP 400."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret"):

        url_resp = client.get("/api/v1/gmail/auth-url?client_type=web", headers=auth_headers)
        state = url_resp.json()["state"]

        with patch("httpx.AsyncClient.post") as mock_post, \
             patch("httpx.AsyncClient.get") as mock_get:
            mock_post.return_value = httpx.Response(200, json={"access_token": "tok", "expires_in": 3600}, request=httpx.Request("POST", "url"))
            mock_get.return_value = httpx.Response(200, json={"email": "alice@gmail.com"}, request=httpx.Request("GET", "url"))

            # First callback succeeds
            resp1 = client.post("/api/v1/gmail/callback", json={"code": "code1", "state": state}, headers=auth_headers)
            assert resp1.status_code == 200

            # Second callback with same state must fail
            resp2 = client.post("/api/v1/gmail/callback", json={"code": "code2", "state": state}, headers=auth_headers)
            assert resp2.status_code == 400
            assert "replay rejected" in resp2.json()["detail"]


def test_cross_user_state_rejection(client: TestClient, auth_headers: dict[str, str], auth_headers_b: dict[str, str]):
    """User B cannot complete callback using state generated for User A."""
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret"):

        # User A generates state
        url_resp = client.get("/api/v1/gmail/auth-url?client_type=web", headers=auth_headers)
        state_alice = url_resp.json()["state"]

        # User B attempts to consume Alice's state
        resp = client.post(
            "/api/v1/gmail/callback",
            json={"code": "code-xyz", "state": state_alice},
            headers=auth_headers_b,
        )
        assert resp.status_code == 400
        assert "initiating user session" in resp.json()["detail"]


def test_electron_desktop_callback_identity_binding(
    client: TestClient, auth_headers: dict[str, str], db_session: Session, test_user: User
):
    """Electron desktop browser-to-loopback callback flow:
    - Browser visits loopback endpoint without Bearer token.
    - Resolves initiating user from state record.
    - Exchanging code uses PKCE code_verifier.
    - Renders clean HTML completion page.
    """
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret"):

        # Desktop client initiates flow
        url_resp = client.get("/api/v1/gmail/auth-url?client_type=desktop", headers=auth_headers)
        state = url_resp.json()["state"]

        captured_verifier = []

        def mock_token_exchange(url, data=None, **kwargs):
            if data and "code_verifier" in data:
                captured_verifier.append(data["code_verifier"])
            return httpx.Response(
                200,
                json={"access_token": "desk-access-tok", "refresh_token": "desk-ref-tok", "expires_in": 3600},
                request=httpx.Request("POST", str(url)),
            )

        def mock_userinfo(url, **kwargs):
            return httpx.Response(200, json={"email": "desktop_user@gmail.com"}, request=httpx.Request("GET", str(url)))

        with patch("httpx.AsyncClient.post", side_effect=mock_token_exchange), \
             patch("httpx.AsyncClient.get", side_effect=mock_userinfo):

            # Browser GET request to loopback without Auth headers
            loopback_resp = client.get(f"/api/v1/gmail/callback/desktop?code=desk-code&state={state}")
            assert loopback_resp.status_code == 200
            assert "text/html" in loopback_resp.headers["content-type"]
            assert "Gmail Connected!" in loopback_resp.text
            assert "desktop_user@gmail.com" in loopback_resp.text

            # Verify PKCE code_verifier was submitted
            assert len(captured_verifier) == 1
            assert len(captured_verifier[0]) >= 43

            # Verify desktop user's account is now connected
            status_resp = client.get("/api/v1/gmail/status", headers=auth_headers)
            assert status_resp.status_code == 200
            assert status_resp.json()["connected"] is True
            assert status_resp.json()["email"] == "desktop_user@gmail.com"


def test_disconnect_and_revocation_handling(
    client: TestClient, auth_headers: dict[str, str], db_session: Session, test_user: User
):
    """Test disconnecting account attempts revocation and unconditionally deletes local credentials."""
    # 1. Setup connected account
    crypto = get_token_encryption_service()
    enc_access = crypto.encrypt("sample-access", user_id=test_user.id)
    enc_refresh = crypto.encrypt("sample-refresh", user_id=test_user.id)
    account = GmailAccount(
        user_id=test_user.id,
        email="alice@gmail.com",
        encrypted_access_token=enc_access,
        encrypted_refresh_token=enc_refresh,
        token_expiry=datetime.now(UTC) + timedelta(hours=1),
        scopes="https://www.googleapis.com/auth/gmail.readonly",
    )
    db_session.merge(account)
    db_session.commit()

    # Case A: Google revocation succeeds
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = httpx.Response(200, request=httpx.Request("POST", "revoke"))
        resp = client.post("/api/v1/gmail/disconnect", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["disconnected"] is True
        assert resp.json()["remote_revocation_succeeded"] is True

        # Verify DB row deleted
        assert db_session.query(GmailAccount).filter(GmailAccount.user_id == test_user.id).first() is None

    # Case B: Google revocation fails (e.g. 500 error or network failure)
    # Local credentials MUST STILL BE DELETED!
    db_session.add(
        GmailAccount(
            user_id=test_user.id,
            email="alice@gmail.com",
            encrypted_access_token=enc_access,
            token_expiry=datetime.now(UTC) + timedelta(hours=1),
        )
    )
    db_session.commit()

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = httpx.Response(500, request=httpx.Request("POST", "revoke"))
        resp = client.post("/api/v1/gmail/disconnect", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["disconnected"] is True
        assert resp.json()["remote_revocation_succeeded"] is False
        assert "could not be confirmed" in resp.json()["message"]

        # Local row must be gone
        assert db_session.query(GmailAccount).filter(GmailAccount.user_id == test_user.id).first() is None


def test_privacy_default_in_batch_scan(
    client: TestClient, auth_headers: dict[str, str], db_session: Session, test_user: User
):
    """Verify that store_content=False (default) processes emails in memory without saving body to database."""
    # Setup account
    crypto = get_token_encryption_service()
    enc_access = crypto.encrypt("mock-token", user_id=test_user.id)
    db_session.merge(
        GmailAccount(
            user_id=test_user.id,
            email="alice@gmail.com",
            encrypted_access_token=enc_access,
            token_expiry=datetime.now(UTC) + timedelta(hours=1),
        )
    )
    db_session.commit()

    mock_msg_payload = {
        "id": "msg_001",
        "threadId": "th_001",
        "snippet": "Urgent account update required",
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": "support@bank-security.com"},
                {"name": "Subject", "value": "Immediate Action Required: Verify Account"},
                {"name": "Date", "value": "Thu, 15 Oct 2026 12:00:00 GMT"},
            ],
            "body": {
                # Base64url encoded: "Dear customer, your account will be suspended. Click here to verify."
                "data": "RGVhciBjdXN0b21lciwgeW91ciBhY2NvdW50IHdpbGwgYmUgc3VzcGVuZGVkLiBDbGljayBoZXJlIHRvIHZlcmlmeS4="
            },
        },
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(200, json=mock_msg_payload, request=httpx.Request("GET", "url"))

        initial_records_count = db_session.query(AnalysisRecord).filter(AnalysisRecord.user_id == test_user.id).count()

        # 1. Scan with store_content omitted (default False)
        resp = client.post(
            "/api/v1/gmail/scan",
            json={"message_ids": ["msg_001"]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_scanned"] == 1
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["message_id"] == "msg_001"
        assert result["prediction"] in ("spam", "ham")
        assert "phishing_risk" in result
        assert "language" in result

        # Verify ZERO new database records saved
        records_after = db_session.query(AnalysisRecord).filter(AnalysisRecord.user_id == test_user.id).count()
        assert records_after == initial_records_count

        # 2. Scan with store_content=True (opt-in)
        resp_opt_in = client.post(
            "/api/v1/gmail/scan",
            json={"message_ids": ["msg_001"], "store_content": True},
            headers=auth_headers,
        )
        assert resp_opt_in.status_code == 200

        # Now exactly 1 record must be saved
        records_final = db_session.query(AnalysisRecord).filter(AnalysisRecord.user_id == test_user.id).count()
        assert records_final == initial_records_count + 1


def test_batch_scan_input_validation(client: TestClient, auth_headers: dict[str, str]):
    """Test validation of message_ids, batch limits, and malicious IDs."""
    # Empty list
    resp = client.post("/api/v1/gmail/scan", json={"message_ids": []}, headers=auth_headers)
    assert resp.status_code == 422

    # Exceeding batch limit (>50)
    oversized = [f"msg_{i:04d}" for i in range(51)]
    resp_over = client.post("/api/v1/gmail/scan", json={"message_ids": oversized}, headers=auth_headers)
    assert resp_over.status_code == 422

    # Malicious / invalid format message ID
    resp_invalid = client.post("/api/v1/gmail/scan", json={"message_ids": ["../../etc/passwd"]}, headers=auth_headers)
    assert resp_invalid.status_code == 400
    assert "Invalid message ID format" in resp_invalid.json()["detail"]


def test_state_expired_rejection(client: TestClient, auth_headers: dict[str, str], db_session: Session, test_user: User):
    """Expired OAuth states must be rejected with HTTP 400."""
    expired_state = "expired-state-token-12345"
    db_session.add(
        OAuthState(
            state=expired_state,
            user_id=test_user.id,
            client_type="web",
            redirect_uri=settings.GOOGLE_REDIRECT_URI_WEB,
            expires_at=datetime.now(UTC) - timedelta(minutes=5),  # Already expired
            used=False,
        )
    )
    db_session.commit()

    resp = client.post("/api/v1/gmail/callback", json={"code": "dummy-code", "state": expired_state}, headers=auth_headers)
    assert resp.status_code == 400
    assert "expired" in resp.json()["detail"]


def test_token_refresh_automatic_when_expired(
    client: TestClient, auth_headers: dict[str, str], db_session: Session, test_user: User
):
    """When access token is expired, list_messages automatically refreshes it via refresh token."""
    crypto = get_token_encryption_service()
    enc_access = crypto.encrypt("stale-access-token", user_id=test_user.id)
    enc_refresh = crypto.encrypt("valid-refresh-token", user_id=test_user.id)

    db_session.merge(
        GmailAccount(
            user_id=test_user.id,
            email="alice@gmail.com",
            encrypted_access_token=enc_access,
            encrypted_refresh_token=enc_refresh,
            token_expiry=datetime.now(UTC) - timedelta(minutes=10),  # Expired
            scopes="https://www.googleapis.com/auth/gmail.readonly",
        )
    )
    db_session.commit()

    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret"):

        def mock_post(url, **kwargs):
            if "oauth2.googleapis.com/token" in str(url):
                return httpx.Response(
                    200,
                    json={"access_token": "fresh-access-token-999", "expires_in": 3600},
                    request=httpx.Request("POST", str(url)),
                )
            return httpx.Response(404, request=httpx.Request("POST", str(url)))

        def mock_get(url, **kwargs):
            if "messages" in str(url):
                return httpx.Response(200, json={"messages": [], "resultSizeEstimate": 0}, request=httpx.Request("GET", str(url)))
            return httpx.Response(404, request=httpx.Request("GET", str(url)))

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("httpx.AsyncClient.get", side_effect=mock_get):

            resp = client.get("/api/v1/gmail/messages?limit=5", headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["messages"] == []

            # Verify token in DB was updated to fresh token
            updated_account = db_session.query(GmailAccount).filter(GmailAccount.user_id == test_user.id).first()
            assert updated_account is not None
            decrypted_new_access = crypto.decrypt(updated_account.encrypted_access_token, user_id=test_user.id)
            assert decrypted_new_access == "fresh-access-token-999"


def test_token_refresh_invalid_grant_handling(
    client: TestClient, auth_headers: dict[str, str], db_session: Session, test_user: User
):
    """When refresh returns invalid_grant (revoked by user in Google Account), return clean 401."""
    crypto = get_token_encryption_service()
    enc_access = crypto.encrypt("stale-access", user_id=test_user.id)
    enc_refresh = crypto.encrypt("revoked-refresh", user_id=test_user.id)

    db_session.merge(
        GmailAccount(
            user_id=test_user.id,
            email="alice@gmail.com",
            encrypted_access_token=enc_access,
            encrypted_refresh_token=enc_refresh,
            token_expiry=datetime.now(UTC) - timedelta(minutes=10),
            scopes="https://www.googleapis.com/auth/gmail.readonly",
        )
    )
    db_session.commit()

    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-client-secret"):

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = httpx.Response(
                400,
                text='{"error": "invalid_grant", "error_description": "Token has been expired or revoked."}',
                request=httpx.Request("POST", "token"),
            )

            resp = client.get("/api/v1/gmail/messages", headers=auth_headers)
            assert resp.status_code == 401
            assert "reconnect Gmail" in resp.json()["detail"]
