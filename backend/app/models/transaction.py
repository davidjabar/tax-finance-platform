from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"


class ReconciliationStatus(str, enum.Enum):
    UNRECONCILED = "UNRECONCILED"
    MATCHED = "MATCHED"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISMATCH = "MISMATCH"
    EXCEPTION = "EXCEPTION"


class ExceptionStatus(str, enum.Enum):
    NONE = "NONE"
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String(100), unique=True, nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    currency = Column(String(3), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    tax_amount = Column(Numeric(18, 2), nullable=True)
    tax_code = Column(String(20), index=True)
    purchase_order = Column(String(100), index=True)
    purchase_order_line = Column(Integer)
    invoice_number = Column(String(100), index=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    reconciliation_status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.UNRECONCILED)
    exception_status = Column(Enum(ExceptionStatus), default=ExceptionStatus.NONE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
