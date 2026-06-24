from sqlalchemy.orm import Session
from typing import List
from storage.models import ParameterModel

class ParameterRepository:
    def create(self, db: Session, session_id: str, url: str, parameter: str) -> ParameterModel:
        model = ParameterModel(
            session_id=session_id,
            url=url,
            parameter=parameter
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[ParameterModel]:
        return db.query(ParameterModel).filter(ParameterModel.session_id == session_id).all()
