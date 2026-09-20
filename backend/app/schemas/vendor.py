from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class VendorBase(BaseModel):
    vendor_code: str
    name: str
    tax_id: Optional[str] = None
    country: str
    vendor_type: Optional[str] = None
    is_active: bool = True


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    tax_id: Optional[str] = None
    vendor_type: Optional[str] = None
    is_active: Optional[bool] = None


class VendorResponse(VendorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VendorListResponse(BaseModel):
    items: List[VendorResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
