from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import DashboardSummary, DashboardTrends, ReconciliationRunResponse, ReconciliationResultsResponse
from app.schemas.common import EntityListResponse, EntityResponse
from app.services.dashboard_service import DashboardService
from app.services.analytics_service import AnalyticsService
from app.repositories.entity import EntityRepository

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard KPI summary."""
    service = DashboardService(db)
    return service.get_summary()


@router.get("/dashboard/trends", response_model=DashboardTrends)
def get_dashboard_trends(
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """Get transaction trends over time."""
    service = DashboardService(db)
    return service.get_trends(months)


@router.get("/dashboard/vendor-distribution")
def get_vendor_distribution(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get transaction distribution by vendor."""
    service = DashboardService(db)
    return service.get_vendor_distribution(limit)


@router.get("/dashboard/entity-distribution")
def get_entity_distribution(db: Session = Depends(get_db)):
    """Get transaction distribution by entity."""
    service = DashboardService(db)
    return service.get_entity_distribution()


@router.get("/dashboard/exception-distribution")
def get_exception_distribution(db: Session = Depends(get_db)):
    """Get exception distribution by type."""
    service = DashboardService(db)
    return service.get_exception_distribution()


@router.get("/entities", response_model=EntityListResponse)
def get_entities(db: Session = Depends(get_db)):
    """Get all entities."""
    repo = EntityRepository(db)
    entities = repo.get_all()
    return EntityListResponse(
        items=[EntityResponse.model_validate(e) for e in entities],
        total=len(entities)
    )
