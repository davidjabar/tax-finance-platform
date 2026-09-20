from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from app.models.transaction import PaymentStatus, ReconciliationStatus, ExceptionStatus


class TransactionBase(BaseModel):
    document_number: str
    transaction_date: date
    vendor_id: int
    entity_id: int
    currency: str
    amount: Decimal
    tax_amount: Optional[Decimal] = None
    tax_code: Optional[str] = None
    purchase_order: Optional[str] = None
    purchase_order_line: Optional[int] = None
    invoice_number: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    vendor_id: Optional[int] = None
    tax_code: Optional[str] = None
    purchase_order: Optional[str] = None
    invoice_number: Optional[str] = None
    reconciliation_status: Optional[ReconciliationStatus] = None
    exception_status: Optional[ExceptionStatus] = None


class TransactionResponse(TransactionBase):
    id: int
    vendor_name: Optional[str] = None
    entity_code: Optional[str] = None
    payment_status: PaymentStatus
    reconciliation_status: ReconciliationStatus
    exception_status: ExceptionStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
