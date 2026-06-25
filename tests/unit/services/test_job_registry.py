import pytest
from services.job_registry import JobRegistry, JobStatus

def test_job_registry():
    registry = JobRegistry()
    job_id = registry.create_job("example.com")
    
    job = registry.get_job(job_id)
    assert job is not None
    assert job.job_id == job_id
    assert job.target_domain == "example.com"
    assert job.status == JobStatus.PENDING
    
    registry.update_status(job_id, JobStatus.RUNNING)
    assert registry.get_job(job_id).status == JobStatus.RUNNING
    
    registry.update_progress(job_id, "recon", 50.0)
    job = registry.get_job(job_id)
    assert job.current_stage == "recon"
    assert job.progress == 50.0
    
    assert len(registry.get_all_jobs()) == 1
    
    registry.update_status(job_id, JobStatus.COMPLETED)
    assert registry.get_job(job_id).status == JobStatus.COMPLETED
    assert registry.get_job(job_id).completed_at is not None
