from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ExceptionListResponse, ExceptionResponse, ExceptionUpdate
from app.services.exception_service import ExceptionService

router = APIRouter(prefix="/exceptions", tags=["Exceptions"])


@router.get("", response_model=ExceptionListResponse)
def get_exceptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    exception_type: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_user: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated list of exceptions."""
    service = ExceptionService(db)
    return service.get_exceptions(
        page=page,
        page_size=page_size,
        exception_type=exception_type,
        status=status,
        severity=severity,
        assigned_user=assigned_user,
        search=search
    )


@router.get("/{exception_id}", response_model=ExceptionResponse)
def get_exception(
    exception_id: int,
    db: Session = Depends(get_db)
):
    """Get a single exception by ID."""
    service = ExceptionService(db)
    exception = service.get_exception(exception_id)
    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")
    return exception


@router.patch("/{exception_id}", response_model=ExceptionResponse)
def update_exception(
    exception_id: int,
    update_data: ExceptionUpdate,
    db: Session = Depends(get_db)
):
    """Update an exception (status, assignment, notes)."""
    service = ExceptionService(db)
    exception = service.update_exception(exception_id, update_data, user="api_user")
    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")
    return exception


@router.get("/summary/stats")
def get_exception_stats(db: Session = Depends(get_db)):
    """Get exception summary statistics."""
    service = ExceptionService(db)
    return service.get_summary_stats()
