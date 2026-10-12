"""Gmail Integration Service.

Handles Google OAuth 2.0 PKCE authorization, server-side single-use CSRF state validation,
encrypted token management, token refresh, grant revocation, Gmail API message listing,
MIME parsing with size limits, and batch scanning integration.
"""

import base64
import hashlib
import logging
import re
import secrets
import urllib.parse
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.crypto import get_token_encryption_service
from backend.app.models.gmail_account import GmailAccount
from backend.app.models.oauth_state import OAuthState
from backend.app.schemas.gmail import (
    GmailAuthUrlResponse,
    GmailDisconnectResponse,
    GmailMessageListResponse,
    GmailMessageSummary,
    GmailScanBatchResponse,
    GmailScanResultItem,
    GmailStatusResponse,
)
from backend.app.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)

# Constants
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

# Strictly minimal read-only scopes
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
]

# Security & processing limits
MAX_BATCH_SIZE = 50
MAX_MESSAGE_PAYLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
MESSAGE_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{5,64}$")
HTML_TAG_REGEX = re.compile(r"<[^>]+>")


class GmailServiceError(Exception):
    """Base exception for Gmail service errors."""
    pass


class OAuthStateError(GmailServiceError):
    """Raised when OAuth state validation fails."""
    pass


class ReauthenticationRequiredError(GmailServiceError):
    """Raised when refresh token is invalid or grant was revoked."""
    pass


class GmailService:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._http_client = http_client

    def is_configured(self) -> bool:
        """Check whether Google OAuth credentials are configured."""
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    def _validate_redirect_uri(self, client_type: str, custom_redirect_uri: str | None = None) -> str:
        """Validate and resolve redirect URI against the whitelist."""
        if client_type == "web":
            target = custom_redirect_uri or settings.GOOGLE_REDIRECT_URI_WEB
            if target != settings.GOOGLE_REDIRECT_URI_WEB:
                raise GmailServiceError("Invalid redirect URI for web client.")
            return target

        if client_type == "desktop":
            target = custom_redirect_uri or settings.GOOGLE_REDIRECT_URI_DESKTOP
            # Validate that it is a loopback URL
            parsed = urllib.parse.urlparse(target)
            if parsed.hostname not in ("127.0.0.1", "localhost") or parsed.scheme != "http":
                raise GmailServiceError("Desktop redirect URI must be a valid http loopback URL.")
            if not parsed.path.endswith("/callback/desktop"):
                raise GmailServiceError("Desktop redirect URI path must end with /callback/desktop.")
            return target

        raise GmailServiceError(f"Unsupported client type: {client_type}")

    def create_auth_url(
        self,
        db: Session,
        user_id: str,
        client_type: str = "web",
        custom_redirect_uri: str | None = None,
    ) -> GmailAuthUrlResponse:
        """Generate a Google OAuth authorization URL with single-use CSRF state and PKCE."""
        if not self.is_configured():
            logger.warning("Google OAuth credentials are not configured in settings.")
            return GmailAuthUrlResponse(
                auth_url="",
                state="",
                client_type=client_type,
                redirect_uri="",
                is_configured=False,
            )

        redirect_uri = self._validate_redirect_uri(client_type, custom_redirect_uri)

        # Generate single-use CSRF state
        state = secrets.token_urlsafe(32)
        code_verifier: str | None = None
        code_challenge: str | None = None

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(GMAIL_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        # Native desktop client enforces RFC 7636 PKCE with S256
        if client_type == "desktop":
            code_verifier = secrets.token_urlsafe(48)  # 64 characters
            hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
            code_challenge = base64.urlsafe_b64encode(hashed).decode("ascii").rstrip("=")
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        # Record state in database with 10-minute validity
        expires_at = datetime.now(UTC) + timedelta(minutes=10)
        oauth_state = OAuthState(
            state=state,
            user_id=user_id,
            client_type=client_type,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            status="pending",
            expires_at=expires_at,
            used=False,
        )
        db.add(oauth_state)
        db.commit()

        auth_url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
        return GmailAuthUrlResponse(
            auth_url=auth_url,
            state=state,
            client_type=client_type,
            redirect_uri=redirect_uri,
            is_configured=True,
        )

    def validate_and_consume_state(
        self,
        db: Session,
        state: str,
        expected_user_id: str | None = None,
    ) -> OAuthState:
        """Validate that state exists, is unexpired, unused, and belongs to expected user if specified.

        Atomically marks state as used.
        """
        if not state:
            raise OAuthStateError("Missing OAuth state parameter.")

        record = db.query(OAuthState).filter(OAuthState.state == state).first()
        if not record:
            raise OAuthStateError("Invalid or unknown OAuth state.")

        if record.used:
            raise OAuthStateError("OAuth state has already been used (replay rejected).")

        now = datetime.now(UTC)
        expiry = record.expires_at.replace(tzinfo=UTC) if record.expires_at.tzinfo is None else record.expires_at
        if expiry <= now:
            raise OAuthStateError("OAuth state has expired.")

        if expected_user_id is not None and record.user_id != expected_user_id:
            raise OAuthStateError("OAuth state does not match the initiating user session.")

        # Mark as consumed immediately
        record.used = True
        record.status = "processing"
        db.commit()
        return record

    async def exchange_code_for_tokens(
        self,
        db: Session,
        code: str,
        state_record: OAuthState,
    ) -> GmailAccount:
        """Exchange authorization code for access and refresh tokens using exact redirect URI."""
        if not self.is_configured():
            raise GmailServiceError("Google OAuth client is not configured.")

        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": state_record.redirect_uri,
            "grant_type": "authorization_code",
        }

        if state_record.code_verifier:
            data["code_verifier"] = state_record.code_verifier

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GOOGLE_TOKEN_URL, data=data)
            if resp.status_code != 200:
                logger.error("Failed to exchange OAuth code: HTTP %d", resp.status_code)
                state_record.status = "failed"
                db.commit()
                raise GmailServiceError(f"Google token exchange failed: {resp.text}")

            token_data = resp.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            granted_scopes = token_data.get("scope", "")

            if not access_token:
                state_record.status = "failed"
                db.commit()
                raise GmailServiceError("No access token returned from Google.")

            # Fetch connected Google user email
            userinfo_resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            email = "unknown@gmail.com"
            if userinfo_resp.status_code == 200:
                email = userinfo_resp.json().get("email", email)

        # Encrypt tokens bound to user_id as AAD
        crypto = get_token_encryption_service()
        enc_access = crypto.encrypt(access_token, user_id=state_record.user_id)
        enc_refresh = crypto.encrypt(refresh_token, user_id=state_record.user_id) if refresh_token else None

        token_expiry = datetime.now(UTC) + timedelta(seconds=expires_in)

        # Upsert GmailAccount
        account = db.query(GmailAccount).filter(GmailAccount.user_id == state_record.user_id).first()
        if not account:
            account = GmailAccount(
                user_id=state_record.user_id,
                email=email,
                encrypted_access_token=enc_access,
                encrypted_refresh_token=enc_refresh,
                token_expiry=token_expiry,
                scopes=granted_scopes,
            )
            db.add(account)
        else:
            account.email = email
            account.encrypted_access_token = enc_access
            if enc_refresh:
                account.encrypted_refresh_token = enc_refresh
            account.token_expiry = token_expiry
            account.scopes = granted_scopes

        state_record.status = "completed"
        db.commit()
        db.refresh(account)
        return account

    async def get_valid_access_token(self, db: Session, account: GmailAccount) -> str:
        """Return a valid decrypted access token, automatically refreshing if expired."""
        now = datetime.now(UTC)
        expiry = account.token_expiry.replace(tzinfo=UTC) if account.token_expiry.tzinfo is None else account.token_expiry
        crypto = get_token_encryption_service()

        # If token is still valid with 60-second buffer, return decrypted token
        if expiry > now + timedelta(seconds=60):
            return crypto.decrypt(account.encrypted_access_token, user_id=account.user_id)

        # Refresh expired token
        if not account.encrypted_refresh_token:
            raise ReauthenticationRequiredError("No refresh token available. Please reconnect Gmail.")

        refresh_token = crypto.decrypt(account.encrypted_refresh_token, user_id=account.user_id)
        refresh_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GOOGLE_TOKEN_URL, data=refresh_data)
            if resp.status_code == 400 and "invalid_grant" in resp.text:
                logger.warning("Google refresh token revoked or expired for user %s", account.user_id)
                raise ReauthenticationRequiredError("Google access revoked. Please reconnect Gmail.")

            if resp.status_code != 200:
                raise GmailServiceError(f"Failed to refresh Google access token: HTTP {resp.status_code}")

            data = resp.json()
            new_access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            if not new_access_token:
                raise GmailServiceError("Google refresh response missing access token.")

            # Update stored encrypted token and expiry
            account.encrypted_access_token = crypto.encrypt(new_access_token, user_id=account.user_id)
            account.token_expiry = datetime.now(UTC) + timedelta(seconds=expires_in)
            db.commit()
            return new_access_token

    def get_status(self, db: Session, user_id: str) -> GmailStatusResponse:
        """Return connection status for the user without exposing tokens."""
        account = db.query(GmailAccount).filter(GmailAccount.user_id == user_id).first()
        is_cfg = self.is_configured()
        if not account:
            return GmailStatusResponse(
                connected=False,
                email=None,
                scopes=[],
                connected_at=None,
                is_configured=is_cfg,
            )

        scopes = account.scopes.split() if account.scopes else []
        return GmailStatusResponse(
            connected=True,
            email=account.email,
            scopes=scopes,
            connected_at=account.created_at,
            is_configured=is_cfg,
        )

    async def disconnect(self, db: Session, user_id: str) -> GmailDisconnectResponse:
        """Attempt Google grant revocation, remove local credentials unconditionally, and report status."""
        account = db.query(GmailAccount).filter(GmailAccount.user_id == user_id).first()
        if not account:
            return GmailDisconnectResponse(
                disconnected=True,
                remote_revocation_succeeded=True,
                message="No connected Gmail account found.",
            )

        token_to_revoke: str | None = None
        crypto = get_token_encryption_service()
        try:
            if account.encrypted_refresh_token:
                token_to_revoke = crypto.decrypt(account.encrypted_refresh_token, user_id=user_id)
            elif account.encrypted_access_token:
                token_to_revoke = crypto.decrypt(account.encrypted_access_token, user_id=user_id)
        except Exception as e:
            logger.warning("Could not decrypt token for revocation: %s", str(e))

        remote_revoked = False
        if token_to_revoke:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(GOOGLE_REVOKE_URL, params={"token": token_to_revoke})
                    remote_revoked = resp.status_code == 200
            except Exception as e:
                logger.warning("Remote token revocation request failed: %s", str(e))
                remote_revoked = False

        # Unconditionally delete local credentials
        db.delete(account)
        # Also clean up any lingering oauth states for this user
        db.query(OAuthState).filter(OAuthState.user_id == user_id).delete()
        db.commit()

        msg = (
            "Gmail account disconnected and remote Google grant revoked successfully."
            if remote_revoked
            else "Gmail account disconnected and local credentials removed, but remote grant revocation could not be confirmed."
        )
        return GmailDisconnectResponse(
            disconnected=True,
            remote_revocation_succeeded=remote_revoked,
            message=msg,
        )

    async def list_messages(
        self,
        db: Session,
        user_id: str,
        limit: int = 10,
        page_token: str | None = None,
        query: str | None = None,
    ) -> GmailMessageListResponse:
        """List messages from the user's Gmail inbox with metadata."""
        limit = max(1, min(limit, MAX_BATCH_SIZE))
        account = db.query(GmailAccount).filter(GmailAccount.user_id == user_id).first()
        if not account:
            raise GmailServiceError("No connected Gmail account found. Please connect your account.")

        access_token = await self.get_valid_access_token(db, account)
        headers = {"Authorization": f"Bearer {access_token}"}

        params = {"maxResults": limit}
        if page_token:
            params["pageToken"] = page_token
        if query:
            params["q"] = query

        async with httpx.AsyncClient(timeout=15.0) as client:
            list_resp = await client.get(f"{GMAIL_API_BASE}/messages", headers=headers, params=params)
            if list_resp.status_code == 401:
                raise ReauthenticationRequiredError("Google access token expired or revoked.")
            if list_resp.status_code == 429:
                raise GmailServiceError("Google API rate limit exceeded. Please try again shortly.")
            if list_resp.status_code != 200:
                raise GmailServiceError(f"Gmail API list messages failed: HTTP {list_resp.status_code}")

            data = list_resp.json()
            message_stubs = data.get("messages", [])
            next_page = data.get("nextPageToken")
            result_estimate = data.get("resultSizeEstimate", len(message_stubs))

            summaries: list[GmailMessageSummary] = []
            for stub in message_stubs:
                msg_id = stub.get("id")
                if not msg_id or not MESSAGE_ID_REGEX.match(msg_id):
                    continue

                # Fetch metadata headers
                meta_url = f"{GMAIL_API_BASE}/messages/{msg_id}"
                meta_params = [
                    ("format", "metadata"),
                    ("metadataHeaders", "From"),
                    ("metadataHeaders", "Subject"),
                    ("metadataHeaders", "Date"),
                ]
                meta_resp = await client.get(meta_url, headers=headers, params=meta_params)
                if meta_resp.status_code == 200:
                    meta_json = meta_resp.json()
                    headers_list = meta_json.get("payload", {}).get("headers", [])
                    header_dict = {h.get("name", "").lower(): h.get("value", "") for h in headers_list}

                    summaries.append(
                        GmailMessageSummary(
                            id=msg_id,
                            thread_id=meta_json.get("threadId", ""),
                            snippet=meta_json.get("snippet", ""),
                            sender=header_dict.get("from", "Unknown"),
                            subject=header_dict.get("subject", "(No Subject)"),
                            date=header_dict.get("date", ""),
                        )
                    )

            return GmailMessageListResponse(
                messages=summaries,
                next_page_token=next_page,
                result_size_estimate=result_estimate,
            )

    @staticmethod
    def _extract_body_text(payload: dict) -> str:
        """Extract plain text from MIME payload parts, stripping HTML tags if necessary."""
        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data", "")

        if body_data and mime_type.startswith("text/plain"):
            try:
                decoded = base64.urlsafe_b64decode(body_data.encode("ascii")).decode("utf-8", errors="replace")
                return decoded
            except Exception:
                pass

        if body_data and mime_type.startswith("text/html"):
            try:
                decoded_html = base64.urlsafe_b64decode(body_data.encode("ascii")).decode("utf-8", errors="replace")
                return HTML_TAG_REGEX.sub(" ", decoded_html)
            except Exception:
                pass

        # Multipart recursion
        parts = payload.get("parts", [])
        for part in parts:
            text = GmailService._extract_body_text(part)
            if text:
                return text

        return ""

    async def fetch_and_scan_messages(
        self,
        db: Session,
        user_id: str,
        message_ids: list[str],
        store_content: bool = False,
    ) -> GmailScanBatchResponse:
        """Fetch selected messages, parse MIME bodies, and run inference through PredictionService.

        Strictly enforces store_content=False privacy default.
        """
        if not message_ids:
            raise GmailServiceError("No message IDs provided for scanning.")
        if len(message_ids) > MAX_BATCH_SIZE:
            raise GmailServiceError(f"Batch size exceeds maximum limit of {MAX_BATCH_SIZE} messages.")

        # Validate message IDs
        for mid in message_ids:
            if not MESSAGE_ID_REGEX.match(mid):
                raise GmailServiceError(f"Invalid message ID format: {mid}")

        account = db.query(GmailAccount).filter(GmailAccount.user_id == user_id).first()
        if not account:
            raise GmailServiceError("No connected Gmail account found.")

        access_token = await self.get_valid_access_token(db, account)
        headers = {"Authorization": f"Bearer {access_token}"}
        prediction_svc = PredictionService.get_instance()

        results: list[GmailScanResultItem] = []
        spam_count = 0
        ham_count = 0
        error_count = 0

        async with httpx.AsyncClient(timeout=20.0) as client:
            for mid in message_ids:
                try:
                    fetch_url = f"{GMAIL_API_BASE}/messages/{mid}?format=full"
                    resp = await client.get(fetch_url, headers=headers)
                    if resp.status_code != 200:
                        error_count += 1
                        results.append(
                            GmailScanResultItem(
                                message_id=mid,
                                sender="Unknown",
                                subject="(Failed to fetch)",
                                date="",
                                prediction="ham",
                                probability=0.0,
                                confidence=0.0,
                                language="unknown",
                                phishing_risk={"risk_level": "Low", "risk_score": 0.0, "indicators": []},
                                top_tokens=[],
                                error=f"HTTP {resp.status_code} while fetching message.",
                            )
                        )
                        continue

                    # Check payload byte size limit
                    if len(resp.content) > MAX_MESSAGE_PAYLOAD_BYTES:
                        error_count += 1
                        results.append(
                            GmailScanResultItem(
                                message_id=mid,
                                sender="Unknown",
                                subject="(Exceeded size limit)",
                                date="",
                                prediction="ham",
                                probability=0.0,
                                confidence=0.0,
                                language="unknown",
                                phishing_risk={"risk_level": "Low", "risk_score": 0.0, "indicators": []},
                                top_tokens=[],
                                error="Message size exceeds 5 MB limit.",
                            )
                        )
                        continue

                    msg_data = resp.json()
                    payload = msg_data.get("payload", {})
                    headers_list = payload.get("headers", [])
                    header_dict = {h.get("name", "").lower(): h.get("value", "") for h in headers_list}

                    sender = header_dict.get("from", "Unknown")
                    subject = header_dict.get("subject", "(No Subject)")
                    date_str = header_dict.get("date", "")

                    body_text = self._extract_body_text(payload)
                    body_to_scan = body_text if body_text.strip() else "(No content)"

                    # Run ML prediction with strict store_content flag
                    pred_resp = prediction_svc.predict(
                        subject=subject,
                        body=body_to_scan,
                        sender=sender,
                        user_id=user_id,
                        store_content=store_content,
                        db=db if store_content else None,
                    )

                    is_spam = pred_resp.prediction.lower() == "spam"
                    if is_spam:
                        spam_count += 1
                    else:
                        ham_count += 1

                    top_tokens = []
                    if pred_resp.explanations:
                        feat_list = (
                            pred_resp.explanations.top_spam_features
                            if is_spam
                            else pred_resp.explanations.top_legitimate_features
                        )
                        top_tokens = [f.model_dump() for f in feat_list[:5]]

                    lang = pred_resp.language_analysis.detected_language if pred_resp.language_analysis else "en"
                    is_mixed = pred_resp.language_analysis.is_mixed if pred_resp.language_analysis else False
                    phishing = (
                        pred_resp.phishing_analysis.model_dump()
                        if pred_resp.phishing_analysis
                        else {"risk_level": "Low", "risk_score": 0.0, "indicators_triggered": []}
                    )

                    results.append(
                        GmailScanResultItem(
                            message_id=mid,
                            sender=sender,
                            subject=subject,
                            date=date_str,
                            prediction=pred_resp.prediction.lower(),
                            probability=pred_resp.score,
                            confidence=0.9 if pred_resp.confidence_level == "High" else 0.5,
                            language=lang,
                            is_mixed=is_mixed,
                            phishing_risk=phishing,
                            top_tokens=top_tokens,
                            error=None,
                        )
                    )
                except Exception as e:
                    error_count += 1
                    logger.warning("Error processing message %s: %s", mid, str(e))
                    results.append(
                        GmailScanResultItem(
                            message_id=mid,
                            sender="Unknown",
                            subject="(Error)",
                            date="",
                            prediction="ham",
                            probability=0.0,
                            confidence=0.0,
                            language="unknown",
                            phishing_risk={"risk_level": "Low", "risk_score": 0.0, "indicators": []},
                            top_tokens=[],
                            error="An error occurred while analyzing this message.",
                        )
                    )

        return GmailScanBatchResponse(
            results=results,
            total_scanned=len(results),
            spam_count=spam_count,
            ham_count=ham_count,
            error_count=error_count,
        )


# Singleton instance
_gmail_service_instance: GmailService | None = None


def get_gmail_service() -> GmailService:
    global _gmail_service_instance
    if _gmail_service_instance is None:
        _gmail_service_instance = GmailService()
    return _gmail_service_instance
