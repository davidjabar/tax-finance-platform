from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ExceptionType(str, enum.Enum):
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    TAX_MISMATCH = "TAX_MISMATCH"
    MISSING_INVOICE = "MISSING_INVOICE"
    MISSING_PO = "MISSING_PO"
    DUPLICATE = "DUPLICATE"
    VENDOR_MISMATCH = "VENDOR_MISMATCH"
    TAX_CODE_MISMATCH = "TAX_CODE_MISMATCH"
    MISSING_TAX_RECORD = "MISSING_TAX_RECORD"
    INVALID_DATA = "INVALID_DATA"


class ExceptionSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExceptionStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class Exception(Base):
    __tablename__ = "exceptions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    exception_type = Column(Enum(ExceptionType), nullable=False, index=True)
    severity = Column(Enum(ExceptionSeverity), default=ExceptionSeverity.MEDIUM)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(18, 2))
    tax_amount = Column(Numeric(18, 2))
    status = Column(Enum(ExceptionStatus), default=ExceptionStatus.OPEN, index=True)
    assigned_user = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
