from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Iterable
from storage.models import TargetModel
from schemas.target import TargetState

class TargetRepository:
    def create(self, db: Session, target: TargetState) -> TargetModel:
        model = TargetModel(
            domain=target.domain,
            scope_type=",".join(target.scope) if target.scope else None,
            program_name=None,
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def create_bulk(self, db: Session, targets: Iterable[TargetState]) -> List[TargetModel]:
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
        targets_list = list(targets)
        if not targets_list:
            return []
        
        models = [
            TargetModel(
                domain=t.domain,
                scope_type=",".join(t.scope) if t.scope else None,
                program_name=None,
            )
            for t in targets_list
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

    def get_by_domain(self, db: Session, domain: str) -> Optional[TargetModel]:
        return db.query(TargetModel).filter(TargetModel.domain == domain).first()
