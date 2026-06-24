from sqlalchemy.orm import Session
from typing import List
from storage.models import APIEndpointModel

class APIRepository:
    def create(self, db: Session, session_id: str, type: str, url: str) -> APIEndpointModel:
        model = APIEndpointModel(
            session_id=session_id,
            type=type,
            url=url
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[APIEndpointModel]:
        return db.query(APIEndpointModel).filter(APIEndpointModel.session_id == session_id).all()
