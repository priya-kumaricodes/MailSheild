"""Gmail Integration REST API Endpoints.
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.gmail import (
    GmailAuthUrlResponse,
    GmailCallbackRequest,
    GmailDisconnectResponse,
    GmailMessageListResponse,
    GmailScanBatchRequest,
    GmailScanBatchResponse,
    GmailStatusResponse,
)
from backend.app.services.auth_service import get_current_user
from backend.app.services.gmail_service import (
    GmailServiceError,
    OAuthStateError,
    ReauthenticationRequiredError,
    get_gmail_service,
)

router = APIRouter()


@router.get("/auth-url", response_model=GmailAuthUrlResponse)
def get_auth_url(
    client_type: Literal["web", "desktop"] = Query(default="web"),
    redirect_uri: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a single-use Google OAuth authorization URL for the authenticated user."""
    svc = get_gmail_service()
    try:
        return svc.create_auth_url(
            db,
            user_id=current_user.id,
            client_type=client_type,
            custom_redirect_uri=redirect_uri,
        )
    except GmailServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/callback", response_model=GmailStatusResponse)
async def oauth_callback(
    payload: GmailCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle web OAuth callback by validating single-use state and exchanging code for encrypted tokens."""
    svc = get_gmail_service()
    try:
        state_record = svc.validate_and_consume_state(db, payload.state, expected_user_id=current_user.id)
        account = await svc.exchange_code_for_tokens(db, payload.code, state_record)
        return svc.get_status(db, user_id=account.user_id)
    except OAuthStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CSRF validation failed: {e}")
    except GmailServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/callback/desktop", response_class=HTMLResponse)
async def desktop_oauth_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Handle native desktop browser-to-loopback callback.

    Recovers the initiating user through the single-use OAuth state record.
    Never issues general session authentication or exposes tokens to the browser.
    """
    if error:
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>MailShield - Connection Cancelled</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #0f172a; color: #f8fafc;">
                <div style="background-color: #1e293b; padding: 2.5rem; border-radius: 1rem; border: 1px solid #334155; text-align: center; max-width: 420px;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                    <h2 style="margin: 0 0 0.5rem 0; color: #f87171;">Authorization Failed</h2>
                    <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">Google returned an error: <strong>{error}</strong>. You can close this tab and return to MailShield.</p>
                </div>
            </body>
            </html>
            """,
            status_code=400,
        )

    if not code or not state:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>MailShield - Invalid Request</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #0f172a; color: #f8fafc;">
                <div style="background-color: #1e293b; padding: 2.5rem; border-radius: 1rem; border: 1px solid #334155; text-align: center; max-width: 420px;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
                    <h2 style="margin: 0 0 0.5rem 0; color: #f87171;">Missing Parameters</h2>
                    <p style="color: #94a3b8; font-size: 0.95rem;">Missing OAuth authorization code or state token.</p>
                </div>
            </body>
            </html>
            """,
            status_code=400,
        )

    svc = get_gmail_service()
    try:
        # Recover initiating user strictly from validated state record
        state_record = svc.validate_and_consume_state(db, state, expected_user_id=None)
        account = await svc.exchange_code_for_tokens(db, code, state_record)

        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>MailShield - Gmail Connected</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #0f172a; color: #f8fafc;">
                <div style="background-color: #1e293b; padding: 2.5rem; border-radius: 1rem; border: 1px solid #334155; text-align: center; max-width: 440px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);">
                    <div style="font-size: 3.5rem; margin-bottom: 1rem;">✅</div>
                    <h2 style="margin: 0 0 0.5rem 0; color: #34d399; font-size: 1.5rem;">Gmail Connected!</h2>
                    <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem;">
                        Successfully connected <strong>{account.email}</strong> to MailShield.
                    </p>
                    <p style="color: #64748b; font-size: 0.85rem;">You may safely close this browser window and return to the MailShield Desktop application.</p>
                </div>
            </body>
            </html>
            """,
            status_code=200,
        )
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head><title>MailShield - Connection Error</title></head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #0f172a; color: #f8fafc;">
                <div style="background-color: #1e293b; padding: 2.5rem; border-radius: 1rem; border: 1px solid #334155; text-align: center; max-width: 440px;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
                    <h2 style="margin: 0 0 0.5rem 0; color: #f87171;">Connection Failed</h2>
                    <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">{str(e)}</p>
                    <p style="color: #64748b; font-size: 0.85rem; margin-top: 1rem;">Please return to MailShield and try connecting again.</p>
                </div>
            </body>
            </html>
            """,
            status_code=400,
        )


@router.get("/status", response_model=GmailStatusResponse)
def get_connection_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check current Gmail connection status for the authenticated user."""
    svc = get_gmail_service()
    return svc.get_status(db, user_id=current_user.id)


@router.post("/disconnect", response_model=GmailDisconnectResponse)
async def disconnect_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disconnect Gmail account, revoke Google grant, and purge all local encrypted credentials."""
    svc = get_gmail_service()
    return await svc.disconnect(db, user_id=current_user.id)


@router.get("/messages", response_model=GmailMessageListResponse)
async def list_recent_messages(
    limit: int = Query(default=10, ge=1, le=50),
    page_token: str | None = Query(default=None),
    q: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List recent messages from the user's connected mailbox."""
    svc = get_gmail_service()
    try:
        return await svc.list_messages(
            db,
            user_id=current_user.id,
            limit=limit,
            page_token=page_token,
            query=q,
        )
    except ReauthenticationRequiredError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except GmailServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/scan", response_model=GmailScanBatchResponse)
async def scan_messages(
    payload: GmailScanBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Scan a limited batch of user-selected Gmail messages through the ML pipeline.

    store_content defaults to False (privacy-preserving in-memory analysis).
    """
    svc = get_gmail_service()
    try:
        return await svc.fetch_and_scan_messages(
            db,
            user_id=current_user.id,
            message_ids=payload.message_ids,
            store_content=payload.store_content,
        )
    except ReauthenticationRequiredError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except GmailServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
