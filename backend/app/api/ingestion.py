from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload CSV or Excel file for data ingestion.
    
    Supported formats: CSV, XLSX, XLS
    """
    # Determine file type
    filename = file.filename.lower()
    if filename.endswith(".csv"):
        source_type = "CSV"
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        source_type = "EXCEL"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use CSV or Excel (.xlsx, .xls)"
        )

    # Read file content
    content = await file.read()

    # Process
    pipeline = IngestionPipeline(db)
    result = pipeline.process_upload(content, file.filename, source_type, "api_user")

    return result


@router.post("/extract-erp")
def extract_from_erp(
    entity_code: str,
    date_from: str,
    date_to: str,
    db: Session = Depends(get_db)
):
    """
    Extract data from mock ERP.
    
    ponytail: Replace with actual ERP connector in production.
    """
    from datetime import datetime
    pipeline = IngestionPipeline(db)
    
    result = pipeline.extract_from_mock_erp(
        entity_code=entity_code,
        date_from=datetime.strptime(date_from, "%Y-%m-%d").date(),
        date_to=datetime.strptime(date_to, "%Y-%m-%d").date()
    )
    
    return result
