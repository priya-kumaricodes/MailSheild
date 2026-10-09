"""Database session configuration and lifecycle management.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    global engine, SessionLocal
    if str(engine.url) != settings.DATABASE_URL:
        connect_args = {}
        if settings.DATABASE_URL.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Import all models and run schema check/migration
    from backend.app.db.migrations import ensure_db_schema
    ensure_db_schema(engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields database session and ensures cleanup."""
    if str(engine.url) != settings.DATABASE_URL:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
