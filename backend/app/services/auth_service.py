"""Authentication service and FastAPI dependency providers.
"""


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import (
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import UserCreate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


class AuthService:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_in: UserCreate, role: str = "user") -> User:
        if AuthService.get_user_by_username(db, user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists.",
            )
        if AuthService.get_user_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )

        hashed = hash_password(user_in.password)
        user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed,
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        user = AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency that strictly requires an authenticated user."""
    if not token:
        # In desktop mode with no users registered yet, support seamless local single-user profile
        if settings.MAILSHIELD_MODE == "desktop":
            local_user = db.query(User).filter(User.username == "desktop_user").first()
            if not local_user:
                local_user = User(
                    username="desktop_user",
                    email="desktop@mailshield.local",
                    hashed_password=hash_password("desktop_offline_secret"),
                    role="admin",
                )
                db.add(local_user)
                db.commit()
                db.refresh(local_user)
            return local_user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User | None:
    """Dependency returning the current user if token is provided, or None."""
    if not token:
        if settings.MAILSHIELD_MODE == "desktop":
            return get_current_user(token=None, db=db)
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        return AuthService.get_user_by_id(db, user_id) if user_id else None
    except Exception:
        return None


def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency restricting endpoint access to admin users only."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to access this resource.",
        )
    return current_user
