from sqlalchemy.orm import Session
from typing import List
from storage.models import SubdomainModel

class SubdomainRepository:
    def create(self, db: Session, session_id: str, subdomain: str, source: str = None) -> SubdomainModel:
        model = SubdomainModel(
            session_id=session_id,
            subdomain=subdomain,
            source=source
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[SubdomainModel]:
        return db.query(SubdomainModel).filter(SubdomainModel.session_id == session_id).all()
