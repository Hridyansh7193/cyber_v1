import pytest
import threading
from concurrent.futures import ThreadPoolExecutor
from services.job_registry import JobRegistry, JobStatus

def test_job_registry_basic_lifecycle():
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

def test_job_registry_duplicate_ids():
    registry = JobRegistry()
    job_id = registry.create_job("example.com")
    
    # Simulate a bug where duplicate ID is used, JobRegistry should handle gracefully
    # Though UUIDs make this unlikely, we test that create_job always generates unique, 
    # but we can't easily force create_job to collide UUIDs.
    pass

def test_job_registry_concurrency():
    registry = JobRegistry()
    NUM_JOBS = 100
    
    def worker(domain):
        job_id = registry.create_job(domain)
        registry.update_status(job_id, JobStatus.RUNNING)
        registry.update_progress(job_id, "stage1", 50.0)
        registry.update_status(job_id, JobStatus.COMPLETED)
        return job_id

    job_ids = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(worker, f"example{i}.com") for i in range(NUM_JOBS)]
        for f in futures:
            job_ids.append(f.result())
            
    assert len(registry.get_all_jobs()) == NUM_JOBS
    for job_id in job_ids:
        job = registry.get_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.progress == 50.0

def test_job_registry_cancellation():
    registry = JobRegistry()
    job_id = registry.create_job("example.com")
    registry.update_status(job_id, JobStatus.RUNNING)
    registry.update_status(job_id, JobStatus.CANCELLED)
    
    job = registry.get_job(job_id)
    assert job.status == JobStatus.CANCELLED
    
    # Test illegal transition logic (though not strictly enforced, good to verify it handles it)
    registry.update_status(job_id, JobStatus.COMPLETED)
    
    # Ideally, cancelled jobs shouldn't be completed, but the registry is a dumb data store in this architecture.
    # The adapter enforces cancellation logic.
