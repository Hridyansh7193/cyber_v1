from sqlalchemy.orm import Session
from typing import List
from storage.models import FindingModel

class FindingRepository:
    def create(self, db: Session, session_id: str, title: str, severity: str, confidence: str, description: str = None, evidence: str = None, status: str = "new") -> FindingModel:
        model = FindingModel(
            session_id=session_id,
            title=title,
            severity=severity,
            confidence=confidence,
            description=description,
            evidence=evidence,
            status=status
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[FindingModel]:
        return db.query(FindingModel).filter(FindingModel.session_id == session_id).all()
