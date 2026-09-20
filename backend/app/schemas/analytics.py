from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal


class TransactionAnalytics(BaseModel):
    total_volume: int
    total_value: Decimal
    average_value: Decimal
    monthly_trend: List[dict]
    vendor_concentration: List[dict]
    entity_distribution: List[dict]


class TaxAnalytics(BaseModel):
    tax_by_period: List[dict]
    tax_by_code: List[dict]
    tax_by_entity: List[dict]
    tax_by_vendor: List[dict]
    effective_tax_rate: Decimal


class ReconciliationAnalytics(BaseModel):
    reconciliation_rate: Decimal
    exception_rate: Decimal
    mismatch_rate: Decimal
    unresolved_exceptions: int
    reconciliation_trend: List[dict]


class AnalyticsFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    entity_id: Optional[int] = None
    vendor_id: Optional[int] = None
    tax_code: Optional[str] = None
    currency: Optional[str] = None
