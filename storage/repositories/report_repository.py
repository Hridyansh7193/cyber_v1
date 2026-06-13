from sqlalchemy.orm import Session
from typing import List
from storage.models import ReportModel

class ReportRepository:
    def create(self, db: Session, session_id: str, report_path: str, report_format: str) -> ReportModel:
        model = ReportModel(
            session_id=session_id,
            report_path=report_path,
            report_format=report_format
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def get_by_session(self, db: Session, session_id: str) -> List[ReportModel]:
        return db.query(ReportModel).filter(ReportModel.session_id == session_id).all()
