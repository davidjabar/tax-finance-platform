from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.vendor import Vendor


class VendorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_list(
        self,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        country: Optional[str] = None
    ) -> tuple[List[Vendor], int]:
        query = self.db.query(Vendor)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Vendor.name.ilike(search_term) |
                Vendor.vendor_code.ilike(search_term) |
                Vendor.tax_id.ilike(search_term)
            )

        if is_active is not None:
            query = query.filter(Vendor.is_active == is_active)

        if country:
            query = query.filter(Vendor.country == country)

        total = query.count()

        query = query.order_by(Vendor.name)
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total

    def get_by_id(self, vendor_id: int) -> Optional[Vendor]:
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first()

    def get_by_code(self, vendor_code: str) -> Optional[Vendor]:
        return self.db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()

    def create(self, vendor_data: dict) -> Vendor:
        vendor = Vendor(**vendor_data)
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def update(self, vendor_id: int, update_data: dict) -> Optional[Vendor]:
        vendor = self.get_by_id(vendor_id)
        if not vendor:
            return None

        for field, value in update_data.items():
            if value is not None:
                setattr(vendor, field, value)

        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def get_all_active(self) -> List[Vendor]:
        return self.db.query(Vendor).filter(Vendor.is_active == True).all()
