from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.transaction import TransactionRepository
from app.repositories.vendor import VendorRepository
from app.repositories.entity import EntityRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionListResponse, TransactionResponse
from app.models.transaction import ReconciliationStatus, ExceptionStatus


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.vendor_repo = VendorRepository(db)
        self.entity_repo = EntityRepository(db)

    def get_transactions(
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
    ) -> TransactionListResponse:
        transactions, total = self.transaction_repo.get_list(
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to,
            vendor_id=vendor_id,
            entity_id=entity_id,
            tax_code=tax_code,
            currency=currency,
            reconciliation_status=reconciliation_status,
            exception_status=exception_status,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )

        items = []
        for t in transactions:
            vendor = self.vendor_repo.get_by_id(t.vendor_id)
            entity = self.entity_repo.get_by_id(t.entity_id)
            
            item = TransactionResponse(
                id=t.id,
                document_number=t.document_number,
                transaction_date=t.transaction_date,
                vendor_id=t.vendor_id,
                vendor_name=vendor.name if vendor else None,
                entity_id=t.entity_id,
                entity_code=entity.code if entity else None,
                currency=t.currency,
                amount=t.amount,
                tax_amount=t.tax_amount,
                tax_code=t.tax_code,
                purchase_order=t.purchase_order,
                purchase_order_line=t.purchase_order_line,
                invoice_number=t.invoice_number,
                payment_status=t.payment_status,
                reconciliation_status=t.reconciliation_status,
                exception_status=t.exception_status,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            items.append(item)

        total_pages = (total + page_size - 1) // page_size

        return TransactionListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_transaction(self, transaction_id: int) -> Optional[TransactionResponse]:
        t = self.transaction_repo.get_by_id(transaction_id)
        if not t:
            return None

        vendor = self.vendor_repo.get_by_id(t.vendor_id)
        entity = self.entity_repo.get_by_id(t.entity_id)

        return TransactionResponse(
            id=t.id,
            document_number=t.document_number,
            transaction_date=t.transaction_date,
            vendor_id=t.vendor_id,
            vendor_name=vendor.name if vendor else None,
            entity_id=t.entity_id,
            entity_code=entity.code if entity else None,
            currency=t.currency,
            amount=t.amount,
            tax_amount=t.tax_amount,
            tax_code=t.tax_code,
            purchase_order=t.purchase_order,
            purchase_order_line=t.purchase_order_line,
            invoice_number=t.invoice_number,
            payment_status=t.payment_status,
            reconciliation_status=t.reconciliation_status,
            exception_status=t.exception_status,
            created_at=t.created_at,
            updated_at=t.updated_at
        )

    def create_transaction(self, transaction_data: TransactionCreate) -> TransactionResponse:
        data = transaction_data.model_dump()
        transaction = self.transaction_repo.create(data)
        return self.get_transaction(transaction.id)

    def update_transaction(
        self,
        transaction_id: int,
        update_data: TransactionUpdate,
        user: str = "system"
    ) -> Optional[TransactionResponse]:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return self.get_transaction(transaction_id)

        transaction = self.transaction_repo.update(transaction_id, data, user)
        if not transaction:
            return None

        return self.get_transaction(transaction.id)

    def get_summary_stats(self) -> Dict[str, Any]:
        return self.transaction_repo.get_summary_stats()

    def get_duplicates(self) -> List[TransactionResponse]:
        duplicates = self.transaction_repo.get_duplicates()
        return [self.get_transaction(t.id) for t in duplicates]
