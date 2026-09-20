from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from decimal import Decimal
from app.models.tax_transaction import TaxTransaction, TaxStatus
from app.models.transaction import Transaction


class TaxTransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_list(
        self,
        page: int = 1,
        page_size: int = 50,
        tax_code: Optional[str] = None,
        tax_period: Optional[str] = None,
        tax_status: Optional[TaxStatus] = None,
        transaction_id: Optional[int] = None
    ) -> tuple[List[TaxTransaction], int]:
        query = self.db.query(TaxTransaction)

        if tax_code:
            query = query.filter(TaxTransaction.tax_code == tax_code)
        if tax_period:
            query = query.filter(TaxTransaction.tax_period == tax_period)
        if tax_status:
            query = query.filter(TaxTransaction.tax_status == tax_status)
        if transaction_id:
            query = query.filter(TaxTransaction.transaction_id == transaction_id)

        total = query.count()
        query = query.order_by(TaxTransaction.created_at.desc())
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total

    def get_by_id(self, tax_id: int) -> Optional[TaxTransaction]:
        return self.db.query(TaxTransaction).filter(TaxTransaction.id == tax_id).first()

    def get_by_transaction_id(self, transaction_id: int) -> Optional[TaxTransaction]:
        return self.db.query(TaxTransaction).filter(
            TaxTransaction.transaction_id == transaction_id
        ).first()

    def create(self, tax_data: dict) -> TaxTransaction:
        tax_transaction = TaxTransaction(**tax_data)
        self.db.add(tax_transaction)
        self.db.commit()
        self.db.refresh(tax_transaction)
        return tax_transaction

    def get_tax_by_code(self) -> List[Dict[str, Any]]:
        results = self.db.query(
            TaxTransaction.tax_code,
            func.sum(TaxTransaction.tax_amount).label('total_tax'),
            func.count(TaxTransaction.id).label('count')
        ).group_by(TaxTransaction.tax_code).all()

        return [{"tax_code": r.tax_code, "total_tax": r.total_tax, "count": r.count} for r in results]

    def get_tax_by_period(self, months: int = 12) -> List[Dict[str, Any]]:
        results = self.db.query(
            TaxTransaction.tax_period,
            func.sum(TaxTransaction.tax_amount).label('total_tax')
        ).group_by(TaxTransaction.tax_period).order_by(
            TaxTransaction.tax_period.desc()
        ).limit(months).all()

        return [{"period": r.tax_period, "total_tax": r.total_tax} for r in results]
