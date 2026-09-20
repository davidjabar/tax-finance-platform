"""
Seed database with realistic mock data for Tax & Finance Platform.
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from faker import Faker

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.entity import Entity
from app.models.vendor import Vendor
from app.models.transaction import Transaction, PaymentStatus, ReconciliationStatus, ExceptionStatus
from app.models.tax_transaction import TaxTransaction, TaxStatus
from app.models.exception import Exception as ExceptionModel, ExceptionType, ExceptionSeverity, ExceptionStatus as ExStatus

fake = Faker()

TAX_CODES = ["PPN11", "PPN12", "PPN10", "PPN0", "PPNBM", "EXEMPT"]
CURRENCIES = ["IDR", "USD", "EUR", "SGD"]
COUNTRIES = ["ID", "SG", "MY", "TH", "VN", "US", "DE", "JP"]
VENDOR_TYPES = ["SUPPLIER", "CONTRACTOR", "SERVICE_PROVIDER"]


def create_entities(db: Session) -> list:
    """Create 5 entities (company codes)."""
    entities = [
        Entity(code="ENT-ID", name="PT Example Indonesia", country="ID"),
        Entity(code="ENT-SG", name="Example Singapore Pte Ltd", country="SG"),
        Entity(code="ENT-MY", name="Example Malaysia Sdn Bhd", country="MY"),
        Entity(code="ENT-TH", name="Example Thailand Co Ltd", country="TH"),
        Entity(code="ENT-VN", name="Example Vietnam LLC", country="VN"),
    ]
    
    created = []
    for e in entities:
        try:
            existing = db.query(Entity).filter(Entity.code == e.code).first()
            if not existing:
                db.add(e)
                db.commit()
                db.refresh(e)
                created.append(e)
            else:
                created.append(existing)
        except IntegrityError:
            db.rollback()
            existing = db.query(Entity).filter(Entity.code == e.code).first()
            if existing:
                created.append(existing)
    
    return created


def create_vendors(db: Session, count: int = 25) -> list:
    """Create vendor records."""
    vendors = []
    
    for i in range(count):
        vendor_code = f"V{str(i+1).zfill(5)}"
        
        # Check if exists
        existing = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
        if existing:
            vendors.append(existing)
            continue
        
        vendor = Vendor(
            vendor_code=vendor_code,
            name=fake.company(),
            tax_id=fake.bothify(text="##.###.###.#-###.###"),
            country=random.choice(COUNTRIES),
            vendor_type=random.choice(VENDOR_TYPES),
            is_active=random.random() > 0.1
        )
        try:
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
            vendors.append(vendor)
        except IntegrityError:
            db.rollback()
            existing = db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
            if existing:
                vendors.append(existing)
    
    return vendors


def create_transactions(
    db: Session,
    entities: list,
    vendors: list,
    count: int = 5000
) -> list:
    """Create transaction records with realistic exceptions."""
    transactions = []
    
    start_date = date.today() - timedelta(days=365)
    
    for i in range(count):
        vendor = random.choice(vendors)
        entity = random.choice(entities)
        transaction_date = fake.date_between(start_date=start_date, end_date="today")
        
        document_number = f"DOC-{str(i+1).zfill(8)}"
        
        # Check if exists
        existing = db.query(Transaction).filter(Transaction.document_number == document_number).first()
        if existing:
            transactions.append(existing)
            continue
        
        amount = Decimal(str(round(random.uniform(1000, 10000000), 2)))
        tax_code = random.choice(TAX_CODES)
        
        if tax_code in ["PPN11"]:
            tax_rate = Decimal("0.11")
        elif tax_code == "PPN12":
            tax_rate = Decimal("0.12")
        elif tax_code == "PPN10":
            tax_rate = Decimal("0.10")
        else:
            tax_rate = Decimal("0")
        
        if random.random() < 0.15:
            tax_amount = amount * tax_rate * Decimal(str(random.uniform(0.8, 1.2)))
        else:
            tax_amount = amount * tax_rate
        
        transaction = Transaction(
            document_number=document_number,
            transaction_date=transaction_date,
            vendor_id=vendor.id,
            entity_id=entity.id,
            currency=random.choice(CURRENCIES) if random.random() > 0.7 else "IDR",
            amount=amount,
            tax_amount=tax_amount,
            tax_code=tax_code,
            purchase_order=f"PO-{random.randint(10000, 99999)}" if random.random() > 0.2 else None,
            purchase_order_line=random.randint(1, 10) if random.random() > 0.5 else None,
            invoice_number=f"INV-{random.randint(100000, 999999)}" if random.random() > 0.15 else None,
            payment_status=random.choice(list(PaymentStatus)),
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        
        try:
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            transactions.append(transaction)
        except IntegrityError:
            db.rollback()
            existing = db.query(Transaction).filter(Transaction.document_number == document_number).first()
            if existing:
                transactions.append(existing)
        
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{count} transactions...")
    
    # Create intentional duplicates (~50) - these will be caught by reconciliation
    for i in range(50):
        if len(transactions) == 0:
            break
        original = random.choice(transactions)
        dup_doc_num = f"{original.document_number}-DUP"
        
        # Check if duplicate already exists
        existing = db.query(Transaction).filter(Transaction.document_number == dup_doc_num).first()
        if existing:
            continue
        
        duplicate = Transaction(
            document_number=dup_doc_num,
            transaction_date=original.transaction_date,
            vendor_id=original.vendor_id,
            entity_id=original.entity_id,
            currency=original.currency,
            amount=original.amount * Decimal("1.01"),
            tax_amount=original.tax_amount * Decimal("1.01") if original.tax_amount else None,
            tax_code=original.tax_code,
            purchase_order=original.purchase_order,
            invoice_number=original.invoice_number,
            payment_status=PaymentStatus.PENDING,
            reconciliation_status=ReconciliationStatus.UNRECONCILED,
            exception_status=ExceptionStatus.NONE
        )
        try:
            db.add(duplicate)
            db.commit()
        except IntegrityError:
            db.rollback()
    
    return transactions


def create_tax_transactions(db: Session, transactions: list) -> list:
    """Create tax transaction records (with some intentional mismatches)."""
    tax_transactions = []
    
    if len(transactions) == 0:
        return tax_transactions
    
    sampled = random.sample(transactions, min(int(len(transactions) * 0.9), len(transactions)))
    
    for t in sampled:
        # Check if tax transaction already exists
        existing = db.query(TaxTransaction).filter(TaxTransaction.transaction_id == t.id).first()
        if existing:
            continue
        
        period = t.transaction_date.strftime("%Y-%m")
        
        if random.random() < 0.10:
            tax_amount = (t.tax_amount or Decimal(0)) * Decimal(str(random.uniform(0.9, 1.1)))
            tax_code = random.choice(TAX_CODES)
        else:
            tax_amount = t.tax_amount or Decimal(0)
            tax_code = t.tax_code or "PPN11"
        
        tt = TaxTransaction(
            transaction_id=t.id,
            tax_code=tax_code,
            tax_base=t.amount,
            tax_amount=tax_amount,
            tax_period=period,
            tax_status=random.choice(list(TaxStatus))
        )
        tax_transactions.append(tt)
        db.add(tt)
        
        if len(tax_transactions) % 500 == 0:
            db.commit()
    
    db.commit()
    return tax_transactions


def create_exceptions_from_reconciliation(db: Session, transactions: list):
    """Run reconciliation and create exception records."""
    from app.reconciliation.engine import ReconciliationEngine
    
    engine = ReconciliationEngine(db)
    
    period_start = date.today() - timedelta(days=365)
    period_end = date.today()
    
    try:
        result = engine.run_reconciliation(period_start, period_end, "seed_user")
        print(f"Reconciliation completed: {result}")
        return result
    except Exception as e:
        print(f"Reconciliation error (non-fatal): {e}")
        return {"status": "SKIPPED", "message": str(e)}


def seed_database():
    """Main seeding function."""
    db = SessionLocal()
    
    try:
        print("Checking existing data...")
        existing_entities = db.query(Entity).count()
        existing_vendors = db.query(Vendor).count()
        existing_transactions = db.query(Transaction).count()
        
        if existing_transactions > 0:
            print(f"Database already seeded: {existing_entities} entities, {existing_vendors} vendors, {existing_transactions} transactions")
            print("Skipping seed to avoid duplicates.")
            return
        
        print("Seeding entities...")
        entities = create_entities(db)
        print(f"Created/found {len(entities)} entities")
        
        print("Seeding vendors...")
        vendors = create_vendors(db, 25)
        print(f"Created/found {len(vendors)} vendors")
        
        print("Seeding transactions...")
        transactions = create_transactions(db, entities, vendors, 5000)
        print(f"Created {len(transactions)} transactions")
        
        print("Seeding tax transactions...")
        tax_transactions = create_tax_transactions(db, transactions)
        print(f"Created {len(tax_transactions)} tax transactions")
        
        print("Running reconciliation and creating exceptions...")
        result = create_exceptions_from_reconciliation(db, transactions)
        print(f"Reconciliation result: {result}")
        
        print("\n=== Database seeding complete ===")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        # Don't raise - allow app to continue
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
