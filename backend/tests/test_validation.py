"""Tests for Data Validation in Ingestion Pipeline."""
import pytest
from app.ingestion.pipeline import DataValidator


class TestDataValidator:
    """Test suite for DataValidator."""

    def test_valid_row(self):
        """Test that a valid row passes validation."""
        row = {
            "document_number": "DOC-001",
            "transaction_date": "2024-01-15",
            "vendor_code": "V00001",
            "entity_code": "ENT-ID",
            "currency": "IDR",
            "amount": "1000000",
            "tax_code": "PPN11",
            "tax_amount": "110000"
        }
        
        result = DataValidator.validate_row(row, 1)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_missing_required_field(self):
        """Test that missing required fields are caught."""
        row = {
            "document_number": "DOC-002",
            "transaction_date": "2024-01-15",
            # Missing vendor_code
            "entity_code": "ENT-ID",
            "currency": "IDR",
            "amount": "1000000"
        }
        
        result = DataValidator.validate_row(row, 2)
        
        assert result["valid"] is False
        assert any("vendor_code" in err for err in result["errors"])

    def test_invalid_date_format(self):
        """Test that invalid date format is caught."""
        row = {
            "document_number": "DOC-003",
            "transaction_date": "15/01/2024",  # Wrong format
            "vendor_code": "V00001",
            "entity_code": "ENT-ID",
            "currency": "IDR",
            "amount": "1000000"
        }
        
        result = DataValidator.validate_row(row, 3)
        
        assert result["valid"] is False
        assert any("date" in err.lower() for err in result["errors"])

    def test_negative_amount(self):
        """Test that negative amounts are caught."""
        row = {
            "document_number": "DOC-004",
            "transaction_date": "2024-01-15",
            "vendor_code": "V00001",
            "entity_code": "ENT-ID",
            "currency": "IDR",
            "amount": "-1000"  # Negative
        }
        
        result = DataValidator.validate_row(row, 4)
        
        assert result["valid"] is False
        assert any("positive" in err.lower() for err in result["errors"])

    def test_unknown_currency_warning(self):
        """Test that unknown currencies generate warnings."""
        row = {
            "document_number": "DOC-005",
            "transaction_date": "2024-01-15",
            "vendor_code": "V00001",
            "entity_code": "ENT-ID",
            "currency": "XYZ",  # Unknown currency
            "amount": "1000000"
        }
        
        result = DataValidator.validate_row(row, 5)
        
        # Still valid, but with warning
        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert any("currency" in warn.lower() for warn in result["warnings"])

    def test_unknown_tax_code_warning(self):
        """Test that unknown tax codes generate warnings."""
        row = {
            "document_number": "DOC-006",
            "transaction_date": "2024-01-15",
            "vendor_code": "V00001",
            "entity_code": "ENT-ID",
            "currency": "IDR",
            "amount": "1000000",
            "tax_code": "UNKNOWN_CODE"
        }
        
        result = DataValidator.validate_row(row, 6)
        
        assert result["valid"] is True
        assert any("tax code" in warn.lower() for warn in result["warnings"])

    def test_invalid_amount_format(self):
        """Test that non-numeric amounts are caught."""
        row = {
            "document_number": "DOC-007",
            "transaction_date": "2024-01-15",
            "vendor_code": "V00001",
            "entity_code": "ENT-ID",
            "currency": "IDR",
            "amount": "not-a-number"
        }
        
        result = DataValidator.validate_row(row, 7)
        
        assert result["valid"] is False
        assert any("amount" in err.lower() for err in result["errors"])

    def test_multiple_errors(self):
        """Test that multiple errors are all reported."""
        row = {
            "document_number": "DOC-008",
            # Missing transaction_date
            "vendor_code": "V00001",
            # Missing entity_code
            "currency": "IDR",
            "amount": "-500"  # Negative
        }
        
        result = DataValidator.validate_row(row, 8)
        
        assert result["valid"] is False
        assert len(result["errors"]) >= 2
