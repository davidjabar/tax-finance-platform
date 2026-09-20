"""Tests for Transaction API endpoints."""
from fastapi.testclient import TestClient
from app.models.entity import Entity
from app.models.vendor import Vendor
from app.models.transaction import Transaction, PaymentStatus, ReconciliationStatus, ExceptionStatus


def create_test_data(db):
    """Create test data for API tests."""
    entity = Entity(code="TEST-ENT", name="Test Entity", country="ID")
    vendor = Vendor(
        vendor_code="V00001",
        name="Test Vendor",
        tax_id="12.345.678.9-012.345",
        country="ID",
        vendor_type="SUPPLIER",
        is_active=True
    )
    db.add(entity)
    db.add(vendor)
    db.commit()
    db.refresh(entity)
    db.refresh(vendor)
    return entity, vendor


def test_get_transactions_empty(client):
    """Test getting transactions when none exist."""
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_transactions_with_data(client, db_session):
    """Test getting transactions with data."""
    entity, vendor = create_test_data(db_session)
    
    from datetime import date
    from decimal import Decimal
    
    tx = Transaction(
        document_number="DOC-001",
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
    
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["document_number"] == "DOC-001"


def test_get_transaction_by_id(client, db_session):
    """Test getting a single transaction."""
    entity, vendor = create_test_data(db_session)
    
    from datetime import date
    from decimal import Decimal
    
    tx = Transaction(
        document_number="DOC-002",
        transaction_date=date.today(),
        vendor_id=vendor.id,
        entity_id=entity.id,
        currency="IDR",
        amount=Decimal("500000"),
        payment_status=PaymentStatus.PENDING,
        reconciliation_status=ReconciliationStatus.UNRECONCILED,
        exception_status=ExceptionStatus.NONE
    )
    db_session.add(tx)
    db_session.commit()
    db_session.refresh(tx)
    
    response = client.get(f"/api/transactions/{tx.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["document_number"] == "DOC-002"
    assert data["amount"] == 500000


def test_update_transaction(client, db_session):
    """Test updating a transaction."""
    entity, vendor = create_test_data(db_session)
    
    from datetime import date
    from decimal import Decimal
    
    tx = Transaction(
        document_number="DOC-003",
        transaction_date=date.today(),
        vendor_id=vendor.id,
        entity_id=entity.id,
        currency="IDR",
        amount=Decimal("750000"),
        tax_code="PPN11",
        payment_status=PaymentStatus.PENDING,
        reconciliation_status=ReconciliationStatus.UNRECONCILED,
        exception_status=ExceptionStatus.NONE
    )
    db_session.add(tx)
    db_session.commit()
    db_session.refresh(tx)
    
    response = client.patch(
        f"/api/transactions/{tx.id}",
        json={"tax_code": "PPN12", "invoice_number": "INV-001"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tax_code"] == "PPN12"
    assert data["invoice_number"] == "INV-001"


def test_get_transactions_with_filters(client, db_session):
    """Test filtering transactions."""
    entity, vendor = create_test_data(db_session)
    
    from datetime import date, timedelta
    from decimal import Decimal
    
    tx1 = Transaction(
        document_number="DOC-004",
        transaction_date=date.today() - timedelta(days=10),
        vendor_id=vendor.id,
        entity_id=entity.id,
        currency="IDR",
        amount=Decimal("100000"),
        tax_code="PPN11",
        payment_status=PaymentStatus.PENDING,
        reconciliation_status=ReconciliationStatus.MATCHED,
        exception_status=ExceptionStatus.NONE
    )
    tx2 = Transaction(
        document_number="DOC-005",
        transaction_date=date.today(),
        vendor_id=vendor.id,
        entity_id=entity.id,
        currency="USD",
        amount=Decimal("500"),
        tax_code="PPN12",
        payment_status=PaymentStatus.PENDING,
        reconciliation_status=ReconciliationStatus.UNRECONCILED,
        exception_status=ExceptionStatus.NONE
    )
    db_session.add_all([tx1, tx2])
    db_session.commit()
    
    # Filter by currency
    response = client.get("/api/transactions?currency=USD")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["currency"] == "USD"
    
    # Filter by tax code
    response = client.get("/api/transactions?tax_code=PPN11")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["tax_code"] == "PPN11"
    
    # Search
    response = client.get("/api/transactions?search=DOC-005")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


def test_dashboard_summary(client, db_session):
    """Test dashboard summary endpoint."""
    entity, vendor = create_test_data(db_session)
    
    from datetime import date
    from decimal import Decimal
    
    for i in range(3):
        tx = Transaction(
            document_number=f"DOC-{i+10}",
            transaction_date=date.today(),
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency="IDR",
            amount=Decimal("1000000"),
            tax_amount=Decimal("110000"),
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.MATCHED if i < 2 else ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        db_session.add(tx)
    db_session.commit()
    
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] == 3
    assert data["reconciled_transactions"] == 2
    assert data["unreconciled_transactions"] == 1
