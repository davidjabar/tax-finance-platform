from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entity import Entity


class EntityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Entity]:
        return self.db.query(Entity).all()

    def get_by_id(self, entity_id: int) -> Optional[Entity]:
        return self.db.query(Entity).filter(Entity.id == entity_id).first()

    def get_by_code(self, code: str) -> Optional[Entity]:
        return self.db.query(Entity).filter(Entity.code == code).first()

    def create(self, entity_data: dict) -> Entity:
        entity = Entity(**entity_data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
