from typing import Dict, Any, List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from app.repositories.transaction import TransactionRepository
from app.repositories.tax_transaction import TaxTransactionRepository
from app.repositories.exception import ExceptionRepository
from app.models.transaction import Transaction, ReconciliationStatus
from app.models.vendor import Vendor
from app.models.entity import Entity


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.tax_repo = TaxTransactionRepository(db)
        self.exception_repo = ExceptionRepository(db)

    def get_transaction_analytics(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        entity_id: Optional[int] = None,
        vendor_id: Optional[int] = None
    ) -> Dict[str, Any]:
        query = self.db.query(Transaction)

        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        if entity_id:
            query = query.filter(Transaction.entity_id == entity_id)
        if vendor_id:
            query = query.filter(Transaction.vendor_id == vendor_id)

        transactions = query.all()

        if not transactions:
            return {
                "total_volume": 0,
                "total_value": Decimal(0),
                "average_value": Decimal(0),
                "monthly_trend": [],
                "vendor_concentration": [],
                "entity_distribution": []
            }

        total_volume = len(transactions)
        total_value = sum(t.amount for t in transactions)
        average_value = total_value / total_volume

        # Monthly trend
        monthly_data = {}
        for t in transactions:
            month_key = t.transaction_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"volume": 0, "value": Decimal(0)}
            monthly_data[month_key]["volume"] += 1
            monthly_data[month_key]["value"] += t.amount

        monthly_trend = [
            {"month": k, "volume": v["volume"], "value": v["value"]}
            for k, v in sorted(monthly_data.items())
        ]

        # Vendor concentration
        vendor_totals = {}
        for t in transactions:
            if t.vendor_id not in vendor_totals:
                vendor_totals[t.vendor_id] = Decimal(0)
            vendor_totals[t.vendor_id] += t.amount

        vendor_concentration = []
        for vendor_id, total in sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)[:10]:
            vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
            vendor_concentration.append({
                "vendor": vendor.name if vendor else f"Vendor {vendor_id}",
                "value": total,
                "percentage": float(total / total_value * 100) if total_value > 0 else 0
            })

        # Entity distribution
        entity_totals = {}
        for t in transactions:
            if t.entity_id not in entity_totals:
                entity_totals[t.entity_id] = Decimal(0)
            entity_totals[t.entity_id] += t.amount

        entity_distribution = []
        for entity_id, total in entity_totals.items():
            entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            entity_distribution.append({
                "entity": entity.code if entity else f"Entity {entity_id}",
                "value": total
            })

        return {
            "total_volume": total_volume,
            "total_value": total_value,
            "average_value": average_value,
            "monthly_trend": monthly_trend,
            "vendor_concentration": vendor_concentration,
            "entity_distribution": entity_distribution
        }

    def get_tax_analytics(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        entity_id: Optional[int] = None
    ) -> Dict[str, Any]:
        query = self.db.query(Transaction)

        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        if entity_id:
            query = query.filter(Transaction.entity_id == entity_id)

        transactions = query.all()

        # Tax by code
        tax_by_code = {}
        for t in transactions:
            if t.tax_code:
                if t.tax_code not in tax_by_code:
                    tax_by_code[t.tax_code] = {"base": Decimal(0), "tax": Decimal(0), "count": 0}
                tax_by_code[t.tax_code]["base"] += t.amount
                tax_by_code[t.tax_code]["tax"] += t.tax_amount or Decimal(0)
                tax_by_code[t.tax_code]["count"] += 1

        tax_code_list = [
            {
                "tax_code": k,
                "tax_base": v["base"],
                "tax_amount": v["tax"],
                "transaction_count": v["count"]
            }
            for k, v in tax_by_code.items()
        ]

        # Tax by entity
        tax_by_entity = {}
        for t in transactions:
            if t.tax_amount:
                if t.entity_id not in tax_by_entity:
                    tax_by_entity[t.entity_id] = Decimal(0)
                tax_by_entity[t.entity_id] += t.tax_amount

        entity_list = []
        for entity_id, total in tax_by_entity.items():
            entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            entity_list.append({
                "entity": entity.code if entity else f"Entity {entity_id}",
                "tax_amount": total
            })

        # Effective tax rate
        total_tax = sum(t.tax_amount or Decimal(0) for t in transactions)
        total_base = sum(t.amount for t in transactions)
        effective_rate = (total_tax / total_base * 100) if total_base > 0 else Decimal(0)

        # Tax by period
        tax_by_period = {}
        for t in transactions:
            if t.tax_amount:
                period = t.transaction_date.strftime("%Y-%m")
                if period not in tax_by_period:
                    tax_by_period[period] = Decimal(0)
                tax_by_period[period] += t.tax_amount

        period_list = [
            {"period": k, "tax_amount": v}
            for k, v in sorted(tax_by_period.items())
        ]

        return {
            "tax_by_period": period_list,
            "tax_by_code": tax_code_list,
            "tax_by_entity": entity_list,
            "effective_tax_rate": effective_rate
        }

    def get_reconciliation_analytics(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        query = self.db.query(Transaction)

        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)

        transactions = query.all()
        total = len(transactions)

        if total == 0:
            return {
                "reconciliation_rate": Decimal(0),
                "exception_rate": Decimal(0),
                "mismatch_rate": Decimal(0),
                "unresolved_exceptions": 0,
                "reconciliation_trend": []
            }

        matched = sum(1 for t in transactions if t.reconciliation_status == ReconciliationStatus.MATCHED)
        mismatch = sum(1 for t in transactions if t.reconciliation_status == ReconciliationStatus.MISMATCH)
        exceptions = sum(1 for t in transactions if t.reconciliation_status == ReconciliationStatus.EXCEPTION)

        reconciliation_rate = Decimal(matched) / Decimal(total) * 100
        exception_rate = Decimal(exceptions) / Decimal(total) * 100
        mismatch_rate = Decimal(mismatch) / Decimal(total) * 100

        unresolved = self.exception_repo.get_summary_stats().get("by_status", {}).get("OPEN", 0)

        # Reconciliation trend by month
        monthly_stats = {}
        for t in transactions:
            month = t.transaction_date.strftime("%Y-%m")
            if month not in monthly_stats:
                monthly_stats[month] = {"total": 0, "matched": 0}
            monthly_stats[month]["total"] += 1
            if t.reconciliation_status == ReconciliationStatus.MATCHED:
                monthly_stats[month]["matched"] += 1

        trend = [
            {
                "month": k,
                "rate": Decimal(v["matched"]) / Decimal(v["total"]) * 100 if v["total"] > 0 else 0
            }
            for k, v in sorted(monthly_stats.items())
        ]

        return {
            "reconciliation_rate": reconciliation_rate,
            "exception_rate": exception_rate,
            "mismatch_rate": mismatch_rate,
            "unresolved_exceptions": unresolved,
            "reconciliation_trend": trend
        }
