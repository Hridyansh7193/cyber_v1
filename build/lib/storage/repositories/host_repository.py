from sqlalchemy.orm import Session
from typing import List
from storage.models import AliveHostModel

class HostRepository:
    def create(self, db: Session, session_id: str, url: str, status_code: int = None, title: str = None, tech_stack: str = None, response_time: float = None) -> AliveHostModel:
        model = AliveHostModel(
            session_id=session_id,
            url=url,
            status_code=status_code,
            title=title,
            tech_stack=tech_stack,
            response_time=response_time
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[AliveHostModel]:
        return db.query(AliveHostModel).filter(AliveHostModel.session_id == session_id).all()
