from sqlalchemy.orm import Session
from typing import List
from storage.models import JSFileModel

class JSRepository:
    def create(self, db: Session, session_id: str, url: str) -> JSFileModel:
        model = JSFileModel(
            session_id=session_id,
            url=url
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[JSFileModel]:
        return db.query(JSFileModel).filter(JSFileModel.session_id == session_id).all()
