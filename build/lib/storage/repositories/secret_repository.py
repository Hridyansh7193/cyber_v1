from sqlalchemy.orm import Session
from typing import List
from storage.models import SecretModel

class SecretRepository:
    def create(self, db: Session, session_id: str, type: str, value: str, source: str = None, confidence: str = None) -> SecretModel:
        model = SecretModel(
            session_id=session_id,
            type=type,
            value=value,
            source=source,
            confidence=confidence
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[SecretModel]:
        return db.query(SecretModel).filter(SecretModel.session_id == session_id).all()
