from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal


class IngestionUploadResponse(BaseModel):
    job_id: str
    status: str
    message: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    errors: List[str]


class DataQualitySummary(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    missing_values: dict
    validation_errors: List[str]


class IngestionJobResponse(BaseModel):
    job_id: str
    source_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    quality_summary: Optional[DataQualitySummary] = None
