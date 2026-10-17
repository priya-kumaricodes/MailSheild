"""History management endpoints with pagination, search, detail view, and deletion.
"""


from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.history import (
    BulkDeleteRequest,
    DeleteResponse,
    HistoryDetail,
    HistoryResponse,
)
from backend.app.services.auth_service import get_optional_current_user
from backend.app.services.history_service import HistoryService

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=HistoryResponse)
def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    label: str | None = Query(default=None),
    sort_by: str = Query(default="timestamp"),
    sort_order: str = Query(default="desc"),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve paginated and filtered prediction history records."""
    user_id = current_user.id if current_user else None
    return HistoryService.get_history(
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        search=search,
        label_filter=label,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{analysis_id}", response_model=HistoryDetail)
def get_analysis_detail(
    analysis_id: str,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve complete prediction and explanation details for a single analysis record."""
    user_id = current_user.id if current_user else None
    return HistoryService.get_analysis_detail(db, analysis_id=analysis_id, user_id=user_id)


@router.delete("/{analysis_id}", response_model=DeleteResponse)
def delete_single_analysis(
    analysis_id: str,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Delete a single analysis record belonging to the authenticated user."""
    user_id = current_user.id if current_user else None
    HistoryService.delete_analysis(db, analysis_id=analysis_id, user_id=user_id)
    return DeleteResponse(deleted_count=1, message="Analysis record deleted successfully.")


@router.delete("", response_model=DeleteResponse)
def delete_analyses(
    request: BulkDeleteRequest | None = None,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Bulk delete selected analysis records belonging to the authenticated user."""
    user_id = current_user.id if current_user else None
    if request and request.ids:
        deleted = HistoryService.bulk_delete(db, ids=request.ids, user_id=user_id)
        return DeleteResponse(deleted_count=deleted, message=f"Deleted {deleted} records.")
    return DeleteResponse(deleted_count=0, message="No records deleted.")
