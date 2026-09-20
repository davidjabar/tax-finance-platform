from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import TaxTransactionListResponse
from app.services.tax_transaction_service import TaxTransactionService

router = APIRouter(prefix="/tax-transactions", tags=["Tax Transactions"])


@router.get("", response_model=TaxTransactionListResponse)
def get_tax_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    tax_code: Optional[str] = None,
    tax_period: Optional[str] = None,
    transaction_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get paginated list of tax transactions."""
    service = TaxTransactionService(db)
    return service.get_tax_transactions(
        page=page,
        page_size=page_size,
        tax_code=tax_code,
        tax_period=tax_period,
        transaction_id=transaction_id
    )
