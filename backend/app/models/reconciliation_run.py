from sqlalchemy import Column, Integer, String, DateTime, Date, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"

    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING, index=True)
    total_records = Column(Integer, default=0)
    matched = Column(Integer, default=0)
    partial_match = Column(Integer, default=0)
    mismatch = Column(Integer, default=0)
    exceptions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
