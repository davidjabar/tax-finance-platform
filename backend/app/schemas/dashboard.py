from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from app.models.reconciliation_run import RunStatus


class DashboardSummary(BaseModel):
    total_transactions: int
    total_transaction_value: Decimal
    total_tax_amount: Decimal
    reconciled_transactions: int
    unreconciled_transactions: int
    exceptions: int
    missing_data: int
    duplicate_transactions: int
    pending_review: int


class TrendData(BaseModel):
    date: date
    transaction_value: Decimal
    tax_amount: Decimal
    transaction_count: int


class DashboardTrends(BaseModel):
    trends: List[TrendData]


class ReconciliationRunCreate(BaseModel):
    period_start: date
    period_end: date


class ReconciliationRunResponse(BaseModel):
    id: int
    period_start: date
    period_end: date
    status: RunStatus
    total_records: int
    matched: int
    partial_match: int
    mismatch: int
    exceptions: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ReconciliationResultItem(BaseModel):
    transaction_id: int
    document_number: str
    vendor_name: str
    amount: Decimal
    tax_amount: Optional[Decimal]
    reconciliation_status: str
    exception_type: Optional[str] = None
    exception_description: Optional[str] = None


class ReconciliationResultsResponse(BaseModel):
    items: List[ReconciliationResultItem]
    total: int
    page: int
    page_size: int
