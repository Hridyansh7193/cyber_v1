import pytest
from pydantic import ValidationError
from schemas.task import Task, TaskPriority, TaskStatus

def test_task_valid_defaults():
    task = Task(name="recon_task")
    assert task.name == "recon_task"
    assert task.priority == TaskPriority.MEDIUM
    assert task.status == TaskStatus.PENDING
    assert task.retry_count == 0
    assert task.dependencies == ()

def test_task_custom_values():
    task = Task(
        name="scan",
        priority=TaskPriority.HIGH,
        status=TaskStatus.IN_PROGRESS,
        retry_count=2,
        dependencies=["recon_task"]
    )
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.retry_count == 2
    assert task.dependencies == ("recon_task",)

def test_task_invalid_retry_count():
    with pytest.raises(ValidationError):
        Task(name="scan", retry_count=-1)

def test_task_invalid_priority():
    with pytest.raises(ValidationError):
        Task(name="scan", priority="super_high")
