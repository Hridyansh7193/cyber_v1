from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Iterable
from storage.models import SecretModel

class SecretRepository:
    def create(self, db: Session, session_id: str, type: str, value: str, source: str = None, confidence: str = None) -> SecretModel:
        model = SecretModel(
            session_id=session_id,
            type=type,
            value=value,
            source=source,
            confidence=confidence
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def create_bulk(self, db: Session, entities: Iterable[dict]) -> List[SecretModel]:
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
        
        models = [SecretModel(**entity) for entity in entities_list]
        db.add_all(models)
        try:
            db.commit()
            for model in models:
                db.refresh(model)
            return models
        except SQLAlchemyError:
            db.rollback()
            raise

    def get_by_session(self, db: Session, session_id: str) -> List[SecretModel]:
        return db.query(SecretModel).filter(SecretModel.session_id == session_id).all()
