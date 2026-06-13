from sqlalchemy.orm import Session
from typing import List
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

    def get_by_session(self, db: Session, session_id: str) -> List[TaskHistoryModel]:
        return db.query(TaskHistoryModel).filter(TaskHistoryModel.session_id == session_id).all()
