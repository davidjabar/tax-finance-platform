from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.vendor import VendorRepository
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorListResponse, VendorResponse


class VendorService:
    def __init__(self, db: Session):
        self.db = db
        self.vendor_repo = VendorRepository(db)

    def get_vendors(
        self,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        country: Optional[str] = None
    ) -> VendorListResponse:
        vendors, total = self.vendor_repo.get_list(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active,
            country=country
        )

        items = [VendorResponse.model_validate(v) for v in vendors]
        total_pages = (total + page_size - 1) // page_size

        return VendorListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_vendor(self, vendor_id: int) -> Optional[VendorResponse]:
        vendor = self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            return None
        return VendorResponse.model_validate(vendor)

    def create_vendor(self, vendor_data: VendorCreate) -> VendorResponse:
        data = vendor_data.model_dump()
        vendor = self.vendor_repo.create(data)
        return VendorResponse.model_validate(vendor)

    def update_vendor(self, vendor_id: int, update_data: VendorUpdate) -> Optional[VendorResponse]:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return self.get_vendor(vendor_id)

        vendor = self.vendor_repo.update(vendor_id, data)
        if not vendor:
            return None
        return VendorResponse.model_validate(vendor)
