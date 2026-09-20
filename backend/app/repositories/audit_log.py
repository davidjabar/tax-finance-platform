from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_record(
        self,
        table_name: str,
        record_id: int,
        limit: int = 50
    ) -> List[AuditLog]:
        return self.db.query(AuditLog).filter(
            AuditLog.table_name == table_name,
            AuditLog.record_id == record_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()

    def get_by_user(self, user: str, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).filter(
            AuditLog.user == user
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()

    def create(self, audit_data: dict) -> AuditLog:
        audit_log = AuditLog(**audit_data)
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log

    def get_recent(self, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
