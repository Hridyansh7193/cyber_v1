from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Iterable
from datetime import datetime,UTC
from storage.models import ScanSessionModel

class SessionRepository:
    def create(self, db: Session, session_id: str, target_domain: str) -> ScanSessionModel:
        model = ScanSessionModel(
            session_id=session_id,
            target_domain=target_domain,
            status="running",
            started_at=datetime.now(UTC)
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def create_bulk(self, db: Session, entities: Iterable[dict]) -> List[ScanSessionModel]:
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
        entities_list = list(entities)
        if not entities_list:
            return []
        
        now = datetime.now(UTC)
        models = [
            ScanSessionModel(
                session_id=entity["session_id"],
                target_domain=entity["target_domain"],
                status="running",
                started_at=now
            )
            for entity in entities_list
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

    def get_by_session_id(self, db: Session, session_id: str) -> Optional[ScanSessionModel]:
        return db.query(ScanSessionModel).filter(ScanSessionModel.session_id == session_id).first()

    def update_status(self, db: Session, session_id: str, status: str) -> Optional[ScanSessionModel]:
        model = self.get_by_session_id(db, session_id)
        if model:
            model.status = status
            if status in ["completed", "failed", "cancelled"]:
                model.finished_at = datetime.now(UTC)
            db.commit()
            db.refresh(model)
        return model
