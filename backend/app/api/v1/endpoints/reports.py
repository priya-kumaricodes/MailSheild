"""Report export endpoints supporting CSV and JSON formats with injection mitigation.
"""


from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.services.auth_service import get_optional_current_user
from backend.app.services.history_service import HistoryService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/export")
def export_reports(
    format: str = Query(default="csv", pattern="^(csv|json)$"),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Export analysis records in CSV or JSON format with CSV formula injection protection."""
    user_id = current_user.id if current_user else None

    if format == "csv":
        csv_data = HistoryService.export_csv(db, user_id=user_id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=mailshield_analyses.csv"},
        )
    else:
        json_data = HistoryService.export_json(db, user_id=user_id)
        return json_data
