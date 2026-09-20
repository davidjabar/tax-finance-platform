from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models.exception import Exception as ExceptionModel, ExceptionType, ExceptionStatus, ExceptionSeverity
from app.models.transaction import Transaction


class ExceptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_list(
        self,
        page: int = 1,
        page_size: int = 50,
        exception_type: Optional[ExceptionType] = None,
        status: Optional[ExceptionStatus] = None,
        severity: Optional[ExceptionSeverity] = None,
        assigned_user: Optional[str] = None,
        transaction_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> tuple[List[ExceptionModel], int]:
        query = self.db.query(ExceptionModel)

        if exception_type:
            query = query.filter(ExceptionModel.exception_type == exception_type)
        if status:
            query = query.filter(ExceptionModel.status == status)
        if severity:
            query = query.filter(ExceptionModel.severity == severity)
        if assigned_user:
            query = query.filter(ExceptionModel.assigned_user == assigned_user)
        if transaction_id:
            query = query.filter(ExceptionModel.transaction_id == transaction_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(ExceptionModel.description.ilike(search_term))

        total = query.count()
        query = query.order_by(ExceptionModel.created_at.desc())
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total

    def get_by_id(self, exception_id: int) -> Optional[ExceptionModel]:
        return self.db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()

    def create(self, exception_data: dict) -> ExceptionModel:
        exception = ExceptionModel(**exception_data)
        self.db.add(exception)
        self.db.commit()
        self.db.refresh(exception)
        return exception

    def update(self, exception_id: int, update_data: dict, user: str = "system") -> Optional[ExceptionModel]:
        exception = self.get_by_id(exception_id)
        if not exception:
            return None

        for field, value in update_data.items():
            if value is not None:
                setattr(exception, field, value)

        if update_data.get("status") == ExceptionStatus.RESOLVED:
            exception.resolved_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(exception)
        return exception

    def get_summary_stats(self) -> Dict[str, Any]:
        total = self.db.query(func.count(ExceptionModel.id)).scalar() or 0
        
        by_status = self.db.query(
            ExceptionModel.status,
            func.count(ExceptionModel.id)
        ).group_by(ExceptionModel.status).all()
        
        by_severity = self.db.query(
            ExceptionModel.severity,
            func.count(ExceptionModel.id)
        ).group_by(ExceptionModel.severity).all()
        
        by_type = self.db.query(
            ExceptionModel.exception_type,
            func.count(ExceptionModel.id)
        ).group_by(ExceptionModel.exception_type).all()

        return {
            "total": total,
            "by_status": {s.value: c for s, c in by_status},
            "by_severity": {s.value: c for s, c in by_severity},
            "by_type": {t.value: c for t, c in by_type}
        }

    def get_exception_distribution(self) -> List[Dict[str, Any]]:
        results = self.db.query(
            ExceptionModel.exception_type,
            func.count(ExceptionModel.id).label('count')
        ).group_by(ExceptionModel.exception_type).all()

        return [{"type": r.exception_type.value, "count": r.count} for r in results]
