from sqlalchemy.orm import Session
from typing import List
from storage.models import UrlModel

class URLRepository:
    def create(self, db: Session, session_id: str, url: str, source: str = None) -> UrlModel:
        model = UrlModel(
            session_id=session_id,
            url=url,
            source=source
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[UrlModel]:
        return db.query(UrlModel).filter(UrlModel.session_id == session_id).all()
