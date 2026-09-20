from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/transactions")
def get_transaction_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    entity_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get transaction analytics."""
    service = AnalyticsService(db)
    return service.get_transaction_analytics(
        date_from=date_from,
        date_to=date_to,
        entity_id=entity_id,
        vendor_id=vendor_id
    )


@router.get("/tax")
def get_tax_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    entity_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get tax analytics."""
    service = AnalyticsService(db)
    return service.get_tax_analytics(
        date_from=date_from,
        date_to=date_to,
        entity_id=entity_id
    )


@router.get("/reconciliation")
def get_reconciliation_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get reconciliation analytics."""
    service = AnalyticsService(db)
    return service.get_reconciliation_analytics(
        date_from=date_from,
        date_to=date_to
    )
