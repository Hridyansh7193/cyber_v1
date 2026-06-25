from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Iterable
from storage.models import FindingModel
from schemas.finding import Finding

class FindingRepository:
    def create(self, db: Session, session_id: str, title: str, severity: str, confidence: str, description: str = None, evidence: str = None, status: str = "new") -> FindingModel:
        model = FindingModel(
            session_id=session_id,
            title=title,
            severity=severity,
            confidence=confidence,
            description=description,
            evidence=evidence,
            status=status
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model

    def create_bulk(self, db: Session, session_id: str, findings: Iterable[Finding]) -> List[FindingModel]:
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
        findings_list = list(findings)
        if not findings_list:
            return []
        
        models = [
            FindingModel(
                session_id=session_id,
                title=f.title,
                severity=f.severity.value if hasattr(f.severity, 'value') else f.severity,
                confidence=f.confidence.value if hasattr(f.confidence, 'value') else f.confidence,
                description=None,
                evidence=f.evidence,
                status="new"
            )
            for f in findings_list
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

    def get_by_session(self, db: Session, session_id: str) -> List[FindingModel]:
        return db.query(FindingModel).filter(FindingModel.session_id == session_id).all()
