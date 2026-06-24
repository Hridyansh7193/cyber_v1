from sqlalchemy.orm import Session
from typing import List
from storage.models import LogModel

class LogRepository:
    def create(self, db: Session, session_id: str, component: str, level: str, message: str) -> LogModel:
        model = LogModel(
            session_id=session_id,
            component=component,
            level=level,
            message=message
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[LogModel]:
        return db.query(LogModel).filter(LogModel.session_id == session_id).all()
