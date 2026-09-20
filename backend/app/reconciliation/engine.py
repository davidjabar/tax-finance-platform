"""
Reconciliation Engine

Matches transactions across different data sources and identifies exceptions.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
import logging

from sqlalchemy.orm import Session
from app.models.transaction import Transaction, ReconciliationStatus, ExceptionStatus
from app.models.tax_transaction import TaxTransaction
from app.models.exception import Exception as ExceptionModel, ExceptionType, ExceptionSeverity, ExceptionStatus as ExStatus
from app.models.vendor import Vendor
from app.repositories.transaction import TransactionRepository
from app.repositories.tax_transaction import TaxTransactionRepository
from app.repositories.exception import ExceptionRepository
from app.repositories.reconciliation_run import ReconciliationRunRepository

logger = logging.getLogger(__name__)


class MatchResult(str, Enum):
    MATCHED = "MATCHED"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    TAX_MISMATCH = "TAX_MISMATCH"
    MISSING_RECORD = "MISSING_RECORD"
    DUPLICATE = "DUPLICATE"
    EXCEPTION = "EXCEPTION"


@dataclass
class ReconciliationItem:
    transaction_id: int
    document_number: str
    vendor_id: int
    amount: Decimal
    tax_amount: Optional[Decimal]
    tax_code: Optional[str]
    match_result: MatchResult
    match_details: Dict[str, Any]
    exceptions: List[Dict[str, Any]]


class ReconciliationEngine:
    """
    Core reconciliation logic for matching transactions and detecting exceptions.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.tax_repo = TaxTransactionRepository(db)
        self.exception_repo = ExceptionRepository(db)
        self.run_repo = ReconciliationRunRepository(db)

    def run_reconciliation(
        self,
        period_start: date,
        period_end: date,
        user: str = "system"
    ) -> Dict[str, Any]:
        """
        Execute full reconciliation for a period.
        
        Steps:
        1. Load transactions for period
        2. Load tax transactions
        3. Match and validate
        4. Detect exceptions
        5. Create reconciliation run record
        """
        # Create run record
        run = self.run_repo.create({
            "period_start": period_start,
            "period_end": period_end,
            "status": "RUNNING"
        })

        try:
            # Get transactions for period
            transactions, _ = self.transaction_repo.get_list(
                date_from=period_start,
                date_to=period_end,
                page_size=10000  # Process all in period
            )

            total_records = len(transactions)
            matched = 0
            partial_match = 0
            mismatch = 0
            exceptions_created = 0

            for transaction in transactions:
                result = self.reconcile_transaction(transaction)
                
                # Update transaction status
                status_map = {
                    MatchResult.MATCHED: ReconciliationStatus.MATCHED,
                    MatchResult.PARTIAL_MATCH: ReconciliationStatus.PARTIAL_MATCH,
                    MatchResult.AMOUNT_MISMATCH: ReconciliationStatus.MISMATCH,
                    MatchResult.TAX_MISMATCH: ReconciliationStatus.MISMATCH,
                    MatchResult.MISSING_RECORD: ReconciliationStatus.EXCEPTION,
                    MatchResult.DUPLICATE: ReconciliationStatus.EXCEPTION,
                    MatchResult.EXCEPTION: ReconciliationStatus.EXCEPTION
                }
                
                update_data = {
                    "reconciliation_status": status_map.get(result.match_result, ReconciliationStatus.UNRECONCILED)
                }
                
                if result.exceptions:
                    update_data["exception_status"] = ExceptionStatus.OPEN
                    exceptions_created += len(result.exceptions)
                    
                    # Create exception records
                    for exc in result.exceptions:
                        self.exception_repo.create(exc)

                self.transaction_repo.update(transaction.id, update_data, user)

                # Count results
                if result.match_result == MatchResult.MATCHED:
                    matched += 1
                elif result.match_result == MatchResult.PARTIAL_MATCH:
                    partial_match += 1
                else:
                    mismatch += 1

            # Update run record
            from datetime import datetime
            self.run_repo.update(run.id, {
                "status": "COMPLETED",
                "total_records": total_records,
                "matched": matched,
                "partial_match": partial_match,
                "mismatch": mismatch,
                "exceptions": exceptions_created,
                "completed_at": datetime.utcnow()
            })

            return {
                "run_id": run.id,
                "status": "COMPLETED",
                "total_records": total_records,
                "matched": matched,
                "partial_match": partial_match,
                "mismatch": mismatch,
                "exceptions": exceptions_created
            }

        except Exception as e:
            logger.error(f"Reconciliation failed: {str(e)}")
            self.run_repo.update(run.id, {"status": "FAILED"})
            raise

    def reconcile_transaction(self, transaction: Transaction) -> ReconciliationItem:
        """
        Reconcile a single transaction.
        """
        exceptions = []
        match_details = {}

        # Check for duplicates
        duplicate_check = self._check_duplicate(transaction)
        if duplicate_check:
            exceptions.append({
                "transaction_id": transaction.id,
                "exception_type": ExceptionType.DUPLICATE,
                "severity": ExceptionSeverity.HIGH,
                "description": f"Duplicate document number: {transaction.document_number}",
                "amount": transaction.amount
            })
            return ReconciliationItem(
                transaction_id=transaction.id,
                document_number=transaction.document_number,
                vendor_id=transaction.vendor_id,
                amount=transaction.amount,
                tax_amount=transaction.tax_amount,
                tax_code=transaction.tax_code,
                match_result=MatchResult.DUPLICATE,
                match_details={"duplicate_of": duplicate_check},
                exceptions=exceptions
            )

        # Check vendor
        vendor_check = self._check_vendor(transaction)
        if not vendor_check["valid"]:
            exceptions.append({
                "transaction_id": transaction.id,
                "exception_type": ExceptionType.VENDOR_MISMATCH,
                "severity": ExceptionSeverity.MEDIUM,
                "description": vendor_check["message"],
                "amount": transaction.amount
            })

        # Check tax transaction exists and matches
        tax_check = self._check_tax_transaction(transaction)
        if tax_check["status"] == "missing":
            exceptions.append({
                "transaction_id": transaction.id,
                "exception_type": ExceptionType.MISSING_TAX_RECORD,
                "severity": ExceptionSeverity.HIGH,
                "description": "No tax transaction record found",
                "amount": transaction.amount,
                "tax_amount": transaction.tax_amount
            })
        elif tax_check["status"] == "mismatch":
            exceptions.append({
                "transaction_id": transaction.id,
                "exception_type": ExceptionType.TAX_MISMATCH,
                "severity": ExceptionSeverity.HIGH,
                "description": tax_check["message"],
                "amount": transaction.amount,
                "tax_amount": transaction.tax_amount
            })
        match_details["tax_check"] = tax_check

        # Check purchase order if exists
        if transaction.purchase_order:
            po_check = self._check_purchase_order(transaction)
            if po_check["status"] == "missing":
                exceptions.append({
                    "transaction_id": transaction.id,
                    "exception_type": ExceptionType.MISSING_PO,
                    "severity": ExceptionSeverity.MEDIUM,
                    "description": f"Purchase order {transaction.purchase_order} not found",
                    "amount": transaction.amount
                })

        # Check for missing invoice
        if not transaction.invoice_number:
            exceptions.append({
                "transaction_id": transaction.id,
                "exception_type": ExceptionType.MISSING_INVOICE,
                "severity": ExceptionSeverity.LOW,
                "description": "No invoice number associated",
                "amount": transaction.amount
            })

        # Determine match result
        if not exceptions:
            match_result = MatchResult.MATCHED
        elif any(e["exception_type"] in [ExceptionType.TAX_MISMATCH, ExceptionType.MISSING_TAX_RECORD] for e in exceptions):
            match_result = MatchResult.TAX_MISMATCH
        elif any(e["exception_type"] == ExceptionType.DUPLICATE for e in exceptions):
            match_result = MatchResult.DUPLICATE
        else:
            match_result = MatchResult.PARTIAL_MATCH

        return ReconciliationItem(
            transaction_id=transaction.id,
            document_number=transaction.document_number,
            vendor_id=transaction.vendor_id,
            amount=transaction.amount,
            tax_amount=transaction.tax_amount,
            tax_code=transaction.tax_code,
            match_result=match_result,
            match_details=match_details,
            exceptions=exceptions
        )

    def _check_duplicate(self, transaction: Transaction) -> Optional[int]:
        """Check for duplicate document numbers. Returns duplicate transaction ID if found."""
        existing = self.db.query(Transaction).filter(
            Transaction.document_number == transaction.document_number,
            Transaction.id != transaction.id
        ).first()
        
        return existing.id if existing else None

    def _check_vendor(self, transaction: Transaction) -> Dict[str, Any]:
        """Validate vendor exists and is active."""
        vendor = self.db.query(Vendor).filter(Vendor.id == transaction.vendor_id).first()
        
        if not vendor:
            return {"valid": False, "message": f"Vendor {transaction.vendor_id} not found"}
        
        if not vendor.is_active:
            return {"valid": False, "message": f"Vendor {vendor.name} is not active"}
        
        return {"valid": True, "vendor": vendor}

    def _check_tax_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """Check tax transaction exists and values match."""
        tax_record = self.tax_repo.get_by_transaction_id(transaction.id)
        
        if not tax_record:
            return {"status": "missing", "message": "No tax transaction record"}
        
        # Check tax amount
        expected_tax = transaction.tax_amount or Decimal(0)
        actual_tax = tax_record.tax_amount
        
        if abs(expected_tax - actual_tax) > Decimal("0.01"):
            return {
                "status": "mismatch",
                "message": f"Tax amount mismatch: expected {expected_tax}, got {actual_tax}",
                "expected": expected_tax,
                "actual": actual_tax
            }
        
        # Check tax code
        if transaction.tax_code and transaction.tax_code != tax_record.tax_code:
            return {
                "status": "mismatch",
                "message": f"Tax code mismatch: expected {transaction.tax_code}, got {tax_record.tax_code}",
                "expected_code": transaction.tax_code,
                "actual_code": tax_record.tax_code
            }
        
        return {"status": "matched", "tax_record": tax_record}

    def _check_purchase_order(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Check purchase order exists.
        
        ponytail: In production, this would check against PO table or ERP.
        For now, simulate with pattern check.
        """
        # Simulate PO validation - PO numbers should start with "PO"
        if not transaction.purchase_order.startswith("PO"):
            return {"status": "missing", "message": "Invalid PO format"}
        
        return {"status": "exists", "po_number": transaction.purchase_order}

    def get_reconciliation_results(
        self,
        run_id: int,
        page: int = 1,
        page_size: int = 50,
        match_result: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get results from a reconciliation run."""
        run = self.run_repo.get_by_id(run_id)
        if not run:
            return [], 0

        query = self.db.query(Transaction).join(Vendor).filter(
            Transaction.transaction_date >= run.period_start,
            Transaction.transaction_date <= run.period_end
        )

        if match_result:
            status_map = {
                "MATCHED": ReconciliationStatus.MATCHED,
                "PARTIAL_MATCH": ReconciliationStatus.PARTIAL_MATCH,
                "MISMATCH": ReconciliationStatus.MISMATCH,
                "EXCEPTION": ReconciliationStatus.EXCEPTION
            }
            if match_result in status_map:
                query = query.filter(Transaction.reconciliation_status == status_map[match_result])

        total = query.count()
        offset = (page - 1) * page_size
        transactions = query.offset(offset).limit(page_size).all()

        results = []
        for t in transactions:
            exception = self.db.query(ExceptionModel).filter(
                ExceptionModel.transaction_id == t.id
            ).first()

            results.append({
                "transaction_id": t.id,
                "document_number": t.document_number,
                "vendor_name": t.vendor.name if t.vendor else None,
                "amount": t.amount,
                "tax_amount": t.tax_amount,
                "reconciliation_status": t.reconciliation_status.value,
                "exception_type": exception.exception_type.value if exception else None,
                "exception_description": exception.description if exception else None
            })

        return results, total
