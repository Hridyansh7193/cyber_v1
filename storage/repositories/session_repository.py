from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from storage.models import ScanSessionModel

class SessionRepository:
    def create(self, db: Session, session_id: str, target_domain: str) -> ScanSessionModel:
        model = ScanSessionModel(
            session_id=session_id,
            target_domain=target_domain,
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session_id(self, db: Session, session_id: str) -> Optional[ScanSessionModel]:
        return db.query(ScanSessionModel).filter(ScanSessionModel.session_id == session_id).first()

    def update_status(self, db: Session, session_id: str, status: str) -> Optional[ScanSessionModel]:
        model = self.get_by_session_id(db, session_id)
        if model:
            model.status = status
            if status in ["completed", "failed", "cancelled"]:
                model.finished_at = datetime.utcnow()
            db.commit()
            db.refresh(model)
        return model
