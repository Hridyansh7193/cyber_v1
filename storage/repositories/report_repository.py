from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Iterable
from storage.models import ReportModel
from schemas.report import Report

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

    def create_bulk(self, db: Session, reports: Iterable[Report]) -> List[ReportModel]:
        """
        API Contract for create_bulk:
        - Deterministic: Identical inputs yield identical database state.
        - Preserves insertion order: Results returned match the input order.
        - Returns ORM instances: Hydrated SQLAlchemy models are returned.
        - Exactly one commit: Performs a single `db.commit()` for the entire batch.
        - Rollback on SQLAlchemyError: Guarantees atomic persistence; no partial writes.
        - No retries: Execution delegates retry logic to higher layers (Orchestrator).
        - Empty iterable: Instantly returns `[]` without triggering database flushes.
        - Backward compatible: Works functionally identical to sequential `create()`.

        Future Compatibility (Unit-of-Work):
        While V1 intentionally performs commits inside this repository method for simplicity, 
        the interface accepts `db: Session` allowing seamless future migration to a Unit-of-Work 
        pattern without requiring upstream caller modifications.
        """
        reports_list = list(reports)
        if not reports_list:
            return []
        
        models = [
            ReportModel(
                session_id=r.session_id,
                report_path=r.report_path,
                report_format=r.report_format.value if hasattr(r.report_format, 'value') else r.report_format
            )
            for r in reports_list
        ]
        db.add_all(models)
        try:
            db.commit()
            for model in models:
                db.refresh(model)
            return models
        except SQLAlchemyError:
            db.rollback()
            raise

    def get_by_session(self, db: Session, session_id: str) -> List[ReportModel]:
        return db.query(ReportModel).filter(ReportModel.session_id == session_id).all()
