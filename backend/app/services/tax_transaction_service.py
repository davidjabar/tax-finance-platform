from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.tax_transaction import TaxTransactionRepository
from app.schemas.common import TaxTransactionListResponse, TaxTransactionResponse


class TaxTransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.tax_repo = TaxTransactionRepository(db)

    def get_tax_transactions(
        self,
        page: int = 1,
        page_size: int = 50,
        tax_code: Optional[str] = None,
        tax_period: Optional[str] = None,
        transaction_id: Optional[int] = None
    ) -> TaxTransactionListResponse:
        tax_transactions, total = self.tax_repo.get_list(
            page=page,
            page_size=page_size,
            tax_code=tax_code,
            tax_period=tax_period,
            transaction_id=transaction_id
        )

        items = [TaxTransactionResponse.model_validate(t) for t in tax_transactions]
        total_pages = (total + page_size - 1) // page_size

        return TaxTransactionListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_tax_transaction(self, tax_id: int) -> Optional[TaxTransactionResponse]:
        tax = self.tax_repo.get_by_id(tax_id)
        if not tax:
            return None
        return TaxTransactionResponse.model_validate(tax)
