from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.repositories.transaction import TransactionRepository
from app.repositories.exception import ExceptionRepository
from app.schemas.dashboard import DashboardSummary, DashboardTrends, TrendData


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.exception_repo = ExceptionRepository(db)

    def get_summary(self) -> DashboardSummary:
        stats = self.transaction_repo.get_summary_stats()
        exception_stats = self.exception_repo.get_summary_stats()
        
        duplicates = len(self.transaction_repo.get_duplicates())

        return DashboardSummary(
            total_transactions=stats["total_transactions"],
            total_transaction_value=stats["total_transaction_value"],
            total_tax_amount=stats["total_tax_amount"],
            reconciled_transactions=stats["reconciled_transactions"],
            unreconciled_transactions=stats["unreconciled_transactions"],
            exceptions=stats["exceptions"],
            missing_data=0,  # ponytail: compute from data quality checks when implemented
            duplicate_transactions=duplicates,
            pending_review=stats["pending_review"]
        )

    def get_trends(self, months: int = 12) -> DashboardTrends:
        trends = self.transaction_repo.get_trends(months)
        
        trend_data = [
            TrendData(
                date=t["date"],
                transaction_value=t["transaction_value"],
                tax_amount=t["tax_amount"],
                transaction_count=t["transaction_count"]
            )
            for t in trends
        ]

        return DashboardTrends(trends=trend_data)

    def get_vendor_distribution(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.transaction_repo.get_vendor_distribution(limit)

    def get_entity_distribution(self) -> List[Dict[str, Any]]:
        return self.transaction_repo.get_entity_distribution()

    def get_exception_distribution(self) -> List[Dict[str, Any]]:
        return self.exception_repo.get_exception_distribution()
