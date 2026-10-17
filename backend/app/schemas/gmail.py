"""Pydantic schemas for Gmail integration endpoints.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GmailAuthUrlRequest(BaseModel):
    client_type: Literal["web", "desktop"] = Field(default="web")
    redirect_uri: str | None = Field(default=None)


class GmailAuthUrlResponse(BaseModel):
    auth_url: str
    state: str
    client_type: str
    redirect_uri: str
    is_configured: bool


class GmailCallbackRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=512)
    state: str = Field(..., min_length=1, max_length=256)


class GmailStatusResponse(BaseModel):
    connected: bool
    email: str | None = None
    scopes: list[str] = Field(default_factory=list)
    connected_at: datetime | None = None
    is_configured: bool


class GmailDisconnectResponse(BaseModel):
    disconnected: bool
    remote_revocation_succeeded: bool
    message: str


class GmailMessageSummary(BaseModel):
    id: str
    thread_id: str
    snippet: str
    sender: str
    subject: str
    date: str


class GmailMessageListResponse(BaseModel):
    messages: list[GmailMessageSummary]
    next_page_token: str | None = None
    result_size_estimate: int = 0


class GmailScanBatchRequest(BaseModel):
    message_ids: list[str] = Field(..., min_length=1, max_length=50)
    store_content: bool = Field(default=False)


class GmailScanResultItem(BaseModel):
    message_id: str
    sender: str
    subject: str
    date: str
    prediction: str
    probability: float
    confidence: float
    language: str
    is_mixed: bool = False
    phishing_risk: dict
    top_tokens: list[dict]
    error: str | None = None


class GmailScanBatchResponse(BaseModel):
    results: list[GmailScanResultItem]
    total_scanned: int
    spam_count: int
    ham_count: int
    error_count: int
