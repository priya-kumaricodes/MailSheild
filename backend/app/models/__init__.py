"""SQLAlchemy models registration.
"""

from backend.app.models.analysis import AnalysisRecord
from backend.app.models.evaluation import EvaluationRun
from backend.app.models.feedback import UserFeedback
from backend.app.models.gmail_account import GmailAccount
from backend.app.models.oauth_state import OAuthState
from backend.app.models.user import User

__all__ = [
    "AnalysisRecord",
    "EvaluationRun",
    "GmailAccount",
    "OAuthState",
    "User",
    "UserFeedback",
]
