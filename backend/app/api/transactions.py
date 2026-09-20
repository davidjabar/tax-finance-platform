from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.transaction import TransactionListResponse, TransactionResponse, TransactionUpdate
from app.schemas.common import AuditLogResponse
from app.services.transaction_service import TransactionService
from app.repositories.audit_log import AuditLogRepository

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def get_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    vendor_id: Optional[int] = None,
    entity_id: Optional[int] = None,
    tax_code: Optional[str] = None,
    currency: Optional[str] = None,
    reconciliation_status: Optional[str] = None,
    exception_status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("transaction_date", regex="^(transaction_date|amount|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """Get paginated list of transactions with filtering and sorting."""
    service = TransactionService(db)
    return service.get_transactions(
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        vendor_id=vendor_id,
        entity_id=entity_id,
        tax_code=tax_code,
        currency=currency,
        reconciliation_status=reconciliation_status,
        exception_status=exception_status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a single transaction by ID."""
    service = TransactionService(db)
    transaction = service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update a transaction. Changes are audited."""
    service = TransactionService(db)
    transaction = service.update_transaction(transaction_id, update_data, user="api_user")
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/{transaction_id}/audit", response_model=list[AuditLogResponse])
def get_transaction_audit(
    transaction_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get audit history for a transaction."""
    audit_repo = AuditLogRepository(db)
    return audit_repo.get_by_record("transactions", transaction_id, limit)
