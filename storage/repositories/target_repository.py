from sqlalchemy.orm import Session
from typing import Optional, List
from storage.models import TargetModel
from schemas.target import TargetState

class TargetRepository:
    def create(self, db: Session, target: TargetState) -> TargetModel:
        model = TargetModel(
            domain=target.domain,
            scope_type=",".join(target.scope) if target.scope else None,
            program_name=None,
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_domain(self, db: Session, domain: str) -> Optional[TargetModel]:
        return db.query(TargetModel).filter(TargetModel.domain == domain).first()
