from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from app.models.reconciliation_run import ReconciliationRun, RunStatus


class ReconciliationRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[RunStatus] = None
    ) -> tuple[List[ReconciliationRun], int]:
        query = self.db.query(ReconciliationRun)

        if status:
            query = query.filter(ReconciliationRun.status == status)

        total = query.count()
        query = query.order_by(ReconciliationRun.created_at.desc())
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total

    def get_by_id(self, run_id: int) -> Optional[ReconciliationRun]:
        return self.db.query(ReconciliationRun).filter(ReconciliationRun.id == run_id).first()

    def create(self, run_data: dict) -> ReconciliationRun:
        run = ReconciliationRun(**run_data)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update(self, run_id: int, update_data: dict) -> Optional[ReconciliationRun]:
        run = self.get_by_id(run_id)
        if not run:
            return None

        for field, value in update_data.items():
            if value is not None:
                setattr(run, field, value)

        self.db.commit()
        self.db.refresh(run)
        return run
