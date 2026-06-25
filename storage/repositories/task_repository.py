from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Iterable
from storage.models import TaskHistoryModel

class TaskRepository:
    def create(self, db: Session, session_id: str, task_name: str, status: str, attempts: int = 0, duration: float = None) -> TaskHistoryModel:
        model = TaskHistoryModel(
            session_id=session_id,
            task_name=task_name,
            status=status,
            attempts=attempts,
            duration=duration
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def create_bulk(self, db: Session, entities: Iterable[dict]) -> List[TaskHistoryModel]:
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
        
        models = [TaskHistoryModel(**entity) for entity in entities_list]
        db.add_all(models)
        try:
            db.commit()
            for model in models:
                db.refresh(model)
            return models
        except SQLAlchemyError:
            db.rollback()
            raise

    def get_by_session(self, db: Session, session_id: str) -> List[TaskHistoryModel]:
        return db.query(TaskHistoryModel).filter(TaskHistoryModel.session_id == session_id).all()
