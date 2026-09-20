from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from app.models.tax_transaction import TaxStatus
from app.models.exception import ExceptionType, ExceptionSeverity, ExceptionStatus


class TaxTransactionBase(BaseModel):
    transaction_id: int
    tax_code: str
    tax_base: Decimal
    tax_amount: Decimal
    tax_period: str
    tax_status: Optional[TaxStatus] = TaxStatus.PENDING


class TaxTransactionCreate(TaxTransactionBase):
    pass


class TaxTransactionResponse(TaxTransactionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TaxTransactionListResponse(BaseModel):
    items: List[TaxTransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExceptionBase(BaseModel):
    transaction_id: int
    exception_type: ExceptionType
    severity: Optional[ExceptionSeverity] = ExceptionSeverity.MEDIUM
    description: str
    amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None


class ExceptionCreate(ExceptionBase):
    pass


class ExceptionUpdate(BaseModel):
    status: Optional[ExceptionStatus] = None
    assigned_user: Optional[str] = None
    notes: Optional[str] = None


class ExceptionResponse(ExceptionBase):
    id: int
    status: ExceptionStatus
    assigned_user: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExceptionListResponse(BaseModel):
    items: List[ExceptionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EntityBase(BaseModel):
    code: str
    name: str
    country: str


class EntityResponse(EntityBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EntityListResponse(BaseModel):
    items: List[EntityResponse]
    total: int


class AuditLogResponse(BaseModel):
    id: int
    user: str
    table_name: str
    record_id: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    action: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
