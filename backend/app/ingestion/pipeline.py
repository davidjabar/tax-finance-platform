"""
Data Ingestion Module

Handles extraction, validation, transformation, and loading of financial data.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
import pandas as pd
import io
import uuid
import logging

from sqlalchemy.orm import Session
from app.models.transaction import Transaction, PaymentStatus, ReconciliationStatus, ExceptionStatus
from app.models.vendor import Vendor
from app.models.entity import Entity
from app.repositories.transaction import TransactionRepository
from app.repositories.vendor import VendorRepository
from app.repositories.entity import EntityRepository

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates transaction data before ingestion."""
    
    VALID_TAX_CODES = ["PPN11", "PPN12", "PPN10", "PPN0", "PPNBM", "EXEMPT", "NON_TAX"]
    VALID_CURRENCIES = ["IDR", "USD", "EUR", "SGD", "JPY"]
    
    @classmethod
    def validate_row(cls, row: Dict[str, Any], row_num: int) -> Dict[str, Any]:
        """Validate a single row. Returns validation result."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["document_number", "transaction_date", "vendor_code", "entity_code", "currency", "amount"]
        for field in required_fields:
            if not row.get(field):
                errors.append(f"Row {row_num}: Missing required field '{field}'")
        
        # Date validation
        if row.get("transaction_date"):
            try:
                if isinstance(row["transaction_date"], str):
                    datetime.strptime(row["transaction_date"], "%Y-%m-%d")
            except ValueError:
                errors.append(f"Row {row_num}: Invalid date format for 'transaction_date'. Use YYYY-MM-DD")
        
        # Amount validation
        if row.get("amount"):
            try:
                amount = Decimal(str(row["amount"]))
                if amount <= 0:
                    errors.append(f"Row {row_num}: Amount must be positive")
            except:
                errors.append(f"Row {row_num}: Invalid amount value")
        
        # Tax amount validation
        if row.get("tax_amount"):
            try:
                Decimal(str(row["tax_amount"]))
            except:
                errors.append(f"Row {row_num}: Invalid tax_amount value")
        
        # Currency validation
        if row.get("currency") and row["currency"] not in cls.VALID_CURRENCIES:
            warnings.append(f"Row {row_num}: Unknown currency '{row['currency']}'")
        
        # Tax code validation
        if row.get("tax_code") and row["tax_code"] not in cls.VALID_TAX_CODES:
            warnings.append(f"Row {row_num}: Unknown tax code '{row['tax_code']}'")
        
        return {
            "row_num": row_num,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class IngestionPipeline:
    """
    ETL pipeline for financial data ingestion.
    
    Steps: EXTRACT -> VALIDATE -> TRANSFORM -> LOAD
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.vendor_repo = VendorRepository(db)
        self.entity_repo = EntityRepository(db)

    def process_upload(
        self,
        file_content: bytes,
        filename: str,
        source_type: str = "CSV",
        user: str = "system"
    ) -> Dict[str, Any]:
        """
        Process uploaded file (CSV or Excel).
        """
        job_id = str(uuid.uuid4())[:8]
        
        try:
            # Extract
            df = self._extract(file_content, filename, source_type)
            
            # Validate
            validation_result = self._validate(df)
            
            # Transform
            transformed_data = self._transform(df, validation_result["valid_rows"])
            
            # Load
            load_result = self._load(transformed_data, user)
            
            return {
                "job_id": job_id,
                "status": "COMPLETED",
                "message": f"Processed {load_result['loaded']} of {len(df)} rows",
                "total_rows": len(df),
                "valid_rows": validation_result["valid_count"],
                "invalid_rows": validation_result["invalid_count"],
                "duplicate_rows": load_result["duplicates"],
                "errors": validation_result["all_errors"]
            }
            
        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            return {
                "job_id": job_id,
                "status": "FAILED",
                "message": str(e),
                "total_rows": 0,
                "valid_rows": 0,
                "invalid_rows": 0,
                "duplicate_rows": 0,
                "errors": [str(e)]
            }

    def _extract(self, file_content: bytes, filename: str, source_type: str) -> pd.DataFrame:
        """Extract data from file into DataFrame."""
        if source_type == "CSV":
            df = pd.read_csv(io.BytesIO(file_content))
        elif source_type in ["EXCEL", "XLSX", "XLS"]:
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        # Normalize column names
        df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]
        
        return df

    def _validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate all rows."""
        all_errors = []
        valid_rows = []
        invalid_rows = []
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            result = DataValidator.validate_row(row_dict, idx + 1)
            
            if result["valid"]:
                valid_rows.append(idx)
            else:
                invalid_rows.append(idx)
                all_errors.extend(result["errors"])
            
            if result["warnings"]:
                all_errors.extend(result["warnings"])
        
        return {
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "valid_count": len(valid_rows),
            "invalid_count": len(invalid_rows),
            "all_errors": all_errors
        }

    def _transform(self, df: pd.DataFrame, valid_row_indices: List[int]) -> List[Dict[str, Any]]:
        """Transform validated rows into transaction records."""
        transformed = []
        
        for idx in valid_row_indices:
            row = df.iloc[idx].to_dict()
            
            # Look up vendor
            vendor = self.vendor_repo.get_by_code(str(row.get("vendor_code", "")))
            if not vendor:
                continue  # Skip if vendor not found
            
            # Look up entity
            entity = self.entity_repo.get_by_code(str(row.get("entity_code", "")))
            if not entity:
                continue  # Skip if entity not found
            
            # Parse date
            date_val = row.get("transaction_date")
            if isinstance(date_val, str):
                date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
            elif isinstance(date_val, pd.Timestamp):
                date_val = date_val.date()
            
            transformed.append({
                "document_number": str(row.get("document_number")),
                "transaction_date": date_val,
                "vendor_id": vendor.id,
                "entity_id": entity.id,
                "currency": str(row.get("currency", "IDR")),
                "amount": Decimal(str(row.get("amount", 0))),
                "tax_amount": Decimal(str(row.get("tax_amount", 0))) if row.get("tax_amount") else None,
                "tax_code": row.get("tax_code"),
                "purchase_order": row.get("purchase_order"),
                "invoice_number": row.get("invoice_number"),
                "payment_status": PaymentStatus.PENDING,
                "reconciliation_status": ReconciliationStatus.UNRECONCILED,
                "exception_status": ExceptionStatus.NONE
            })
        
        return transformed

    def _load(self, data: List[Dict[str, Any]], user: str) -> Dict[str, Any]:
        """Load transformed data into database."""
        loaded = 0
        duplicates = 0
        
        for item in data:
            # Check for existing document number
            existing = self.transaction_repo.get_by_document_number(item["document_number"])
            if existing:
                duplicates += 1
                continue
            
            try:
                self.transaction_repo.create(item)
                loaded += 1
            except Exception as e:
                logger.error(f"Failed to load transaction {item['document_number']}: {str(e)}")
        
        self.db.commit()
        
        return {
            "loaded": loaded,
            "duplicates": duplicates,
            "failed": len(data) - loaded - duplicates
        }

    def extract_from_mock_erp(
        self,
        entity_code: str,
        date_from: date,
        date_to: date
    ) -> Dict[str, Any]:
        """
        Simulate ERP extraction.
        
        ponytail: Replace with actual ERP connector in production.
        """
        # This would connect to ERP and extract data
        # For now, return placeholder
        return {
            "status": "SUCCESS",
            "message": "Mock ERP extraction - no actual data extracted",
            "records": 0
        }
