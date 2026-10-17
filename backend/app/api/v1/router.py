"""API v1 master router aggregating all sub-routes.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    auth,
    evaluation,
    feedback,
    gmail,
    health,
    history,
    models,
    predict,
    reports,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(predict.router)
api_router.include_router(history.router)
api_router.include_router(models.router)
api_router.include_router(evaluation.router)
api_router.include_router(feedback.router)
api_router.include_router(reports.router)
api_router.include_router(gmail.router, prefix="/gmail", tags=["gmail"])
