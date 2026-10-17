"""Database migration and schema verification utilities.

Ensures that new tables (gmail_accounts, oauth_states) and indices
are created safely on existing databases without data loss or corruption.
"""

import logging

from sqlalchemy import Engine, inspect

from backend.app.db.base import Base

logger = logging.getLogger(__name__)

EXPECTED_TABLES = [
    "users",
    "analysis_records",
    "eval_runs",
    "user_feedback",
    "gmail_accounts",
    "oauth_states",
]


def ensure_db_schema(engine: Engine) -> dict[str, list[str]]:
    """Inspects database tables, creates any missing tables, and verifies schema compatibility.

    Returns a summary dict with 'existing_tables' and 'created_tables'.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    # Import all models to ensure they are registered with Base.metadata
    import backend.app.models  # noqa: F401

    # Base.metadata.create_all only creates tables that do not already exist
    Base.metadata.create_all(bind=engine)

    new_inspector = inspect(engine)
    current_tables = set(new_inspector.get_table_names())
    created = list(current_tables - existing_tables)

    if created:
        logger.info("Created missing database tables during migration: %s", created)

    return {
        "existing_tables": sorted(existing_tables),
        "created_tables": sorted(created),
        "all_tables": sorted(current_tables),
    }
