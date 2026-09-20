from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.models.transaction import Transaction, PaymentStatus, ReconciliationStatus, ExceptionStatus
from app.models.vendor import Vendor
from app.models.entity import Entity


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_list(
        self,
        page: int = 1,
        page_size: int = 50,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        vendor_id: Optional[int] = None,
        entity_id: Optional[int] = None,
        tax_code: Optional[str] = None,
        currency: Optional[str] = None,
        reconciliation_status: Optional[str] = None,
        exception_status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "transaction_date",
        sort_order: str = "desc"
    ) -> tuple[List[Transaction], int]:
        query = self.db.query(Transaction).join(Vendor).join(Entity)

        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        if vendor_id:
            query = query.filter(Transaction.vendor_id == vendor_id)
        if entity_id:
            query = query.filter(Transaction.entity_id == entity_id)
        if tax_code:
            query = query.filter(Transaction.tax_code == tax_code)
        if currency:
            query = query.filter(Transaction.currency == currency)
        if reconciliation_status:
            query = query.filter(Transaction.reconciliation_status == reconciliation_status)
        if exception_status:
            query = query.filter(Transaction.exception_status == exception_status)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.document_number.ilike(search_term),
                    Transaction.invoice_number.ilike(search_term),
                    Transaction.purchase_order.ilike(search_term),
                    Vendor.name.ilike(search_term)
                )
            )

        total = query.count()

        sort_column = getattr(Transaction, sort_by, Transaction.transaction_date)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_by_document_number(self, document_number: str) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.document_number == document_number).first()

    def create(self, transaction_data: dict) -> Transaction:
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction_id: int, update_data: dict, user: str = "system") -> Optional[Transaction]:
        transaction = self.get_by_id(transaction_id)
        if not transaction:
            return None

        # Track changes for audit
        from app.repositories.audit_log import AuditLogRepository
        audit_repo = AuditLogRepository(self.db)
        
        for field, new_value in update_data.items():
            old_value = getattr(transaction, field, None)
            if old_value != new_value:
                audit_repo.create({
                    "user": user,
                    "table_name": "transactions",
                    "record_id": transaction_id,
                    "field_name": field,
                    "old_value": str(old_value) if old_value else None,
                    "new_value": str(new_value) if new_value else None,
                    "action": "UPDATE"
                })
                setattr(transaction, field, new_value)

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, transaction_id: int) -> bool:
        transaction = self.get_by_id(transaction_id)
        if not transaction:
            return False
        self.db.delete(transaction)
        self.db.commit()
        return True

    def get_summary_stats(self) -> Dict[str, Any]:
        total_transactions = self.db.query(func.count(Transaction.id)).scalar() or 0
        total_value = self.db.query(func.sum(Transaction.amount)).scalar() or Decimal(0)
        total_tax = self.db.query(func.sum(Transaction.tax_amount)).scalar() or Decimal(0)
        
        reconciled = self.db.query(func.count(Transaction.id)).filter(
            Transaction.reconciliation_status == ReconciliationStatus.MATCHED
        ).scalar() or 0
        
        unreconciled = self.db.query(func.count(Transaction.id)).filter(
            Transaction.reconciliation_status == ReconciliationStatus.UNRECONCILED
        ).scalar() or 0
        
        exceptions = self.db.query(func.count(Transaction.id)).filter(
            Transaction.exception_status == ExceptionStatus.OPEN
        ).scalar() or 0
        
        pending_review = self.db.query(func.count(Transaction.id)).filter(
            Transaction.exception_status == ExceptionStatus.IN_REVIEW
        ).scalar() or 0

        return {
            "total_transactions": total_transactions,
            "total_transaction_value": total_value,
            "total_tax_amount": total_tax,
            "reconciled_transactions": reconciled,
            "unreconciled_transactions": unreconciled,
            "exceptions": exceptions,
            "pending_review": pending_review
        }

    def get_trends(self, months: int = 12) -> List[Dict[str, Any]]:
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        results = self.db.query(
            func.date_trunc('month', Transaction.transaction_date).label('month'),
            func.sum(Transaction.amount).label('total_value'),
            func.sum(Transaction.tax_amount).label('total_tax'),
            func.count(Transaction.id).label('count')
        ).filter(
            Transaction.transaction_date >= start_date
        ).group_by(
            func.date_trunc('month', Transaction.transaction_date)
        ).order_by('month').all()

        return [
            {
                "date": r.month,
                "transaction_value": r.total_value or Decimal(0),
                "tax_amount": r.total_tax or Decimal(0),
                "transaction_count": r.count
            }
            for r in results
        ]

    def get_vendor_distribution(self, limit: int = 10) -> List[Dict[str, Any]]:
        results = self.db.query(
            Vendor.name,
            func.sum(Transaction.amount).label('total_value'),
            func.count(Transaction.id).label('count')
        ).join(Vendor).group_by(Vendor.name).order_by(
            func.sum(Transaction.amount).desc()
        ).limit(limit).all()

        return [{"vendor": r.name, "value": r.total_value, "count": r.count} for r in results]

    def get_entity_distribution(self) -> List[Dict[str, Any]]:
        results = self.db.query(
            Entity.code,
            func.sum(Transaction.amount).label('total_value'),
            func.count(Transaction.id).label('count')
        ).join(Entity).group_by(Entity.code).all()

        return [{"entity": r.code, "value": r.total_value, "count": r.count} for r in results]

    def get_duplicates(self) -> List[Transaction]:
        duplicates = self.db.query(Transaction).filter(
            Transaction.document_number.in_(
                self.db.query(Transaction.document_number).group_by(
                    Transaction.document_number
                ).having(func.count(Transaction.id) > 1)
            )
        ).all()
        return duplicates
