"""OAuth state tracking model for server-side single-use CSRF and PKCE validation.
"""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class OAuthState(Base):
    __tablename__ = "oauth_states"

    state: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    client_type: Mapped[str] = mapped_column(String(16), default="web", nullable=False)  # "web" or "desktop"
    redirect_uri: Mapped[str] = mapped_column(String(255), nullable=False)
    code_verifier: Mapped[str | None] = mapped_column(String(128), nullable=True)  # RFC 7636 PKCE
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)  # "pending", "completed", "failed"
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
