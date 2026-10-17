"""Tests for database migration, schema compatibility, and backward compatibility.
"""

import uuid

from sqlalchemy import Column, String, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.db.migrations import ensure_db_schema


def test_schema_migration_preserves_existing_data(tmp_path):
    """Verify that migrating an existing v2.0 database safely creates new tables without affecting existing data."""
    db_file = tmp_path / "legacy_test.db"
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    # 1. Create a legacy database with only users and legacy analysis_records tables
    LegacyBase = declarative_base()

    class LegacyUser(LegacyBase):
        __tablename__ = "users"
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        username = Column(String(64), unique=True, nullable=False)
        email = Column(String(255), unique=True, nullable=False)
        hashed_password = Column(String(255), nullable=False)
        role = Column(String(32), default="user", nullable=False)

    LegacyBase.metadata.create_all(bind=engine)

    # Insert a legacy user
    Session = sessionmaker(bind=engine)
    session = Session()
    legacy_user_id = str(uuid.uuid4())
    user = LegacyUser(
        id=legacy_user_id,
        username="legacy_alice",
        email="alice@legacy.local",
        hashed_password="hashed_pw_secret",
        role="user",
    )
    session.add(user)
    session.commit()
    session.close()

    # Verify legacy state
    inspector = inspect(engine)
    tables_before = set(inspector.get_table_names())
    assert "users" in tables_before
    assert "gmail_accounts" not in tables_before
    assert "oauth_states" not in tables_before

    # 2. Run schema migration
    migration_result = ensure_db_schema(engine)
    assert "gmail_accounts" in migration_result["created_tables"]
    assert "oauth_states" in migration_result["created_tables"]

    # 3. Verify that legacy user data is still intact
    session = Session()
    alice = session.execute(text("SELECT id, username, email FROM users WHERE username = 'legacy_alice'")).fetchone()
    assert alice is not None
    assert alice[0] == legacy_user_id
    assert alice[1] == "legacy_alice"
    assert alice[2] == "alice@legacy.local"
    session.close()

    # 4. Verify new tables are usable
    session = Session()
    state_id = "test-state-token-12345"
    session.execute(
        text(
            "INSERT INTO oauth_states (state, user_id, client_type, redirect_uri, status, expires_at, used, created_at) "
            "VALUES (:state, :user_id, :client_type, :redirect_uri, :status, datetime('now', '+10 minutes'), 0, datetime('now'))"
        ),
        {
            "state": state_id,
            "user_id": legacy_user_id,
            "client_type": "web",
            "redirect_uri": "http://localhost:5173/gmail/callback",
            "status": "pending",
        },
    )
    session.commit()

    saved_state = session.execute(text("SELECT state, user_id, client_type FROM oauth_states WHERE state = :state"), {"state": state_id}).fetchone()
    assert saved_state is not None
    assert saved_state[0] == state_id
    assert saved_state[1] == legacy_user_id
    session.close()

    # 5. Idempotency: Running migration again causes no errors and creates zero new tables
    second_result = ensure_db_schema(engine)
    assert second_result["created_tables"] == []
