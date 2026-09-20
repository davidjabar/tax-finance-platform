from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.vendor import VendorListResponse, VendorResponse
from app.services.vendor_service import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("", response_model=VendorListResponse)
def get_vendors(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated list of vendors."""
    service = VendorService(db)
    return service.get_vendors(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
        country=country
    )


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    """Get a single vendor by ID."""
    service = VendorService(db)
    vendor = service.get_vendor(vendor_id)
    if not vendor:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor
