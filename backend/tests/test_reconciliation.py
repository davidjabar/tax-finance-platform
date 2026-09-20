"""Tests for Reconciliation Engine."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.entity import Entity
from app.models.vendor import Vendor
from app.models.transaction import Transaction, PaymentStatus, ReconciliationStatus, ExceptionStatus
from app.models.tax_transaction import TaxTransaction, TaxStatus
from app.reconciliation.engine import ReconciliationEngine, MatchResult


@pytest.fixture
def test_data(db_session):
    """Create comprehensive test data."""
    entity = Entity(code="TEST-ENT", name="Test Entity", country="ID")
    vendor = Vendor(
        vendor_code="V00001",
        name="Test Vendor",
        tax_id="12.345.678.9-012.345",
        country="ID",
        vendor_type="SUPPLIER",
        is_active=True
    )
    db_session.add(entity)
    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(entity)
    db_session.refresh(vendor)
    
    return entity, vendor


class TestReconciliationEngine:
    """Test suite for ReconciliationEngine."""

    def test_exact_match(self, db_session, test_data):
        """Test that matching transaction returns MATCHED."""
        entity, vendor = test_data
        
        tx = Transaction(
            document_number="DOC-MATCH-001",
            transaction_date=date.today(),
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency="IDR",
            amount=Decimal("1000000"),
            tax_amount=Decimal("110000"),
            tax_code="PPN11",
            invoice_number="INV-001",
            purchase_order="PO-12345",
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        db_session.add(tx)
        db_session.commit()
        db_session.refresh(tx)
        
        tax_tx = TaxTransaction(
            transaction_id=tx.id,
            tax_code="PPN11",
            tax_base=Decimal("1000000"),
            tax_amount=Decimal("110000"),
            tax_period=date.today().strftime("%Y-%m"),
            tax_status=TaxStatus.PENDING
        )
        db_session.add(tax_tx)
        db_session.commit()
        
        engine = ReconciliationEngine(db_session)
        result = engine.reconcile_transaction(tx)
        
        assert result.match_result == MatchResult.MATCHED
        assert len(result.exceptions) == 0

    def test_tax_mismatch(self, db_session, test_data):
        """Test that tax amount mismatch is detected."""
        entity, vendor = test_data
        
        tx = Transaction(
            document_number="DOC-TAX-MISMATCH",
            transaction_date=date.today(),
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency="IDR",
            amount=Decimal("1000000"),
            tax_amount=Decimal("110000"),
            tax_code="PPN11",
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        db_session.add(tx)
        db_session.commit()
        db_session.refresh(tx)
        
        # Tax record with different amount
        tax_tx = TaxTransaction(
            transaction_id=tx.id,
            tax_code="PPN11",
            tax_base=Decimal("1000000"),
            tax_amount=Decimal("120000"),  # Different from transaction
            tax_period=date.today().strftime("%Y-%m"),
            tax_status=TaxStatus.PENDING
        )
        db_session.add(tax_tx)
        db_session.commit()
        
        engine = ReconciliationEngine(db_session)
        result = engine.reconcile_transaction(tx)
        
        assert result.match_result == MatchResult.TAX_MISMATCH
        assert len(result.exceptions) > 0
        assert any(e["exception_type"].value == "TAX_MISMATCH" for e in result.exceptions)

    def test_missing_tax_record(self, db_session, test_data):
        """Test that missing tax record is detected."""
        entity, vendor = test_data
        
        tx = Transaction(
            document_number="DOC-NO-TAX",
            transaction_date=date.today(),
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency="IDR",
            amount=Decimal("1000000"),
            tax_amount=Decimal("110000"),
            tax_code="PPN11",
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        db_session.add(tx)
        db_session.commit()
        db_session.refresh(tx)
        
        # No tax transaction created
        
        engine = ReconciliationEngine(db_session)
        result = engine.reconcile_transaction(tx)
        
        assert result.match_result in [MatchResult.TAX_MISMATCH, MatchResult.EXCEPTION]
        assert any(e["exception_type"].value == "MISSING_TAX_RECORD" for e in result.exceptions)

    def test_duplicate_detection(self, db_session, test_data):
        """Test that duplicate document numbers are detected."""
        entity, vendor = test_data
        
        tx1 = Transaction(
            document_number="DOC-DUP-001",
            transaction_date=date.today(),
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency="IDR",
            amount=Decimal("1000000"),
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        tx2 = Transaction(
            document_number="DOC-DUP-001",  # Same document number
            transaction_date=date.today(),
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency="IDR",
            amount=Decimal("1010000"),
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        db_session.add_all([tx1, tx2])
        db_session.commit()
        db_session.refresh(tx2)
        
        engine = ReconciliationEngine(db_session)
        result = engine.reconcile_transaction(tx2)
        
        assert result.match_result == MatchResult.DUPLICATE
        assert any(e["exception_type"].value == "DUPLICATE" for e in result.exceptions)

    def test_missing_invoice_detection(self, db_session, test_data):
        """Test that missing invoice number is detected as partial match."""
        entity, vendor = test_data
        
        tx = Transaction(
            document_number="DOC-NO-INVOICE",
            transaction_date=date.today(),
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency="IDR",
            amount=Decimal("1000000"),
            tax_amount=Decimal("110000"),
            tax_code="PPN11",
            invoice_number=None,  # No invoice
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        db_session.add(tx)
        db_session.commit()
        db_session.refresh(tx)
        
        tax_tx = TaxTransaction(
            transaction_id=tx.id,
            tax_code="PPN11",
            tax_base=Decimal("1000000"),
            tax_amount=Decimal("110000"),
            tax_period=date.today().strftime("%Y-%m"),
            tax_status=TaxStatus.PENDING
        )
        db_session.add(tax_tx)
        db_session.commit()
        
        engine = ReconciliationEngine(db_session)
        result = engine.reconcile_transaction(tx)
        
        # Should be partial match due to missing invoice
        assert result.match_result in [MatchResult.PARTIAL_MATCH, MatchResult.MATCHED]
        assert any(e["exception_type"].value == "MISSING_INVOICE" for e in result.exceptions)

    def test_run_reconciliation(self, db_session, test_data):
        """Test running full reconciliation for a period."""
        entity, vendor = test_data
        
        # Create multiple transactions
        for i in range(5):
            tx = Transaction(
                document_number=f"DOC-RUN-{i:03d}",
                transaction_date=date.today(),
                vendor_id=vendor.id,
                entity_id=entity.id,
                currency="IDR",
                amount=Decimal("1000000"),
                tax_amount=Decimal("110000"),
                tax_code="PPN11",
                payment_status=PaymentStatus.PENDING,
                reconciliation_status=ReconciliationStatus.UNRECONCILED,
                exception_status=ExceptionStatus.NONE
            )
            db_session.add(tx)
        db_session.commit()
        
        engine = ReconciliationEngine(db_session)
        result = engine.run_reconciliation(
            period_start=date.today() - timedelta(days=30),
            period_end=date.today() + timedelta(days=1),
            user="test_user"
        )
        
        assert result["status"] == "COMPLETED"
        assert result["total_records"] == 5
