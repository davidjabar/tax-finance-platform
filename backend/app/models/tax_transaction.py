from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TaxStatus(str, enum.Enum):
    PENDING = "PENDING"
    FILED = "FILED"
    PAID = "PAID"
    ADJUSTED = "ADJUSTED"


class TaxTransaction(Base):
    __tablename__ = "tax_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    tax_code = Column(String(20), nullable=False, index=True)
    tax_base = Column(Numeric(18, 2), nullable=False)
    tax_amount = Column(Numeric(18, 2), nullable=False)
    tax_period = Column(String(7), nullable=False, index=True)  # YYYY-MM format
    tax_status = Column(Enum(TaxStatus), default=TaxStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
