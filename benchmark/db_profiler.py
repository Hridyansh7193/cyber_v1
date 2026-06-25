import time
import tracemalloc
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from storage.models import Base, ScanSessionModel, FindingModel
from storage.repositories import (
    FindingRepository, URLRepository, APIRepository,
    ParameterRepository, SecretRepository, ReportRepository
)
from schemas.finding import Finding, Severity, Confidence
from schemas.report import Report, ReportFormat

class ProfilerStats:
    def __init__(self):
        self.inserts = 0
        self.selects = 0
        self.commits = 0
        self.rollbacks = 0
        
    def reset(self):
        self.inserts = 0
        self.selects = 0
        self.commits = 0
        self.rollbacks = 0

def create_db_session(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    
    stats = ProfilerStats()
    
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if statement.lower().startswith("insert"):
            stats.inserts += 1
        elif statement.lower().startswith("select"):
            stats.selects += 1
            
    @event.listens_for(engine, "commit")
    def after_commit(conn):
        stats.commits += 1

    @event.listens_for(engine, "rollback")
    def after_rollback(conn):
        stats.rollbacks += 1
        
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal, stats

def profile_db_writes(num_inserts):
    print(f"\n=== Profiling DB Writes: {num_inserts} inserts ===")
    SessionLocal, stats = create_db_session(f"bench_db_{num_inserts}.db")
    session_id = f"bench_session_{num_inserts}"
    
    repo = FindingRepository()
    
    # Pre-create session
    with SessionLocal() as session:
        session.add(ScanSessionModel(session_id=session_id, target_domain="bench.com", status="running", started_at=datetime.now(timezone.utc)))
        session.commit()
    
    # 1. Sequential
    if num_inserts <= 1000: # Sequential takes too long for >1k
        stats.reset()
        tracemalloc.start()
        start_time = time.time()
        
        with SessionLocal() as session:
            for i in range(num_inserts):
                repo.create(
                    db=session,
                    session_id=session_id,
                    title=f"Seq {i}",
                    severity="high",
                    confidence="certain",
                    evidence="E"
                )
                
        seq_time = time.time() - start_time
        seq_current, seq_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"[Sequential] Time: {seq_time:.4f}s | Speed: {num_inserts / seq_time:.2f} inserts/s | Commits: {stats.commits} | Peak Mem: {seq_peak / 1024 / 1024:.2f} MB")
        print(f"             SQL -> Inserts: {stats.inserts}, Selects: {stats.selects}, Commits: {stats.commits}, Rollbacks: {stats.rollbacks}")
    else:
        seq_time = None
        print(f"[Sequential] Skipped for > 1000 to save time")

    # 2. Bulk (With Refresh)
    findings = [
        Finding(title=f"Bulk {i}", severity=Severity.HIGH, confidence=Confidence.CERTAIN, evidence="E")
        for i in range(num_inserts)
    ]
    
    stats.reset()
    tracemalloc.start()
    start_time = time.time()
    
    with SessionLocal() as session:
        repo.create_bulk(db=session, session_id=session_id, findings=findings)
        
    bulk_time = time.time() - start_time
    bulk_current, bulk_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"[Bulk+Refresh] Time: {bulk_time:.4f}s | Speed: {num_inserts / bulk_time:.2f} inserts/s | Commits: {stats.commits} | Peak Mem: {bulk_peak / 1024 / 1024:.2f} MB")
    print(f"               SQL -> Inserts: {stats.inserts}, Selects: {stats.selects}, Commits: {stats.commits}, Rollbacks: {stats.rollbacks}")
    
    if seq_time:
        print(f"Speedup vs Sequential: {seq_time / bulk_time:.2f}x")

def measure_refresh_cost():
    num_inserts = 10000
    print(f"\n=== Refresh Cost Analysis: {num_inserts} inserts ===")
    SessionLocal, stats = create_db_session("bench_refresh.db")
    session_id = "bench_refresh"
    
    with SessionLocal() as session:
        session.add(ScanSessionModel(session_id=session_id, target_domain="bench.com", status="running", started_at=datetime.now(timezone.utc)))
        session.commit()
    
    findings = [
        Finding(title=f"Refresh {i}", severity=Severity.HIGH, confidence=Confidence.CERTAIN, evidence="E")
        for i in range(num_inserts)
    ]
    
    # 1. With Refresh
    repo = FindingRepository()
    stats.reset()
    tracemalloc.start()
    t0 = time.time()
    with SessionLocal() as session:
        repo.create_bulk(db=session, session_id=session_id, findings=findings)
    t_with = time.time() - t0
    _, peak_with = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    stats_with = (stats.inserts, stats.selects, stats.commits)
    
    # 2. Without Refresh (manual)
    stats.reset()
    tracemalloc.start()
    t0 = time.time()
    with SessionLocal() as session:
        models = [
            FindingModel(session_id=session_id, title=f.title, severity=f.severity.value, confidence=f.confidence.value, evidence=f.evidence, status="open")
            for f in findings
        ]
        session.add_all(models)
        session.commit()
    t_without = time.time() - t0
    _, peak_without = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    stats_without = (stats.inserts, stats.selects, stats.commits)
    
    print(f"[With Refresh]    Time: {t_with:.4f}s | Peak Mem: {peak_with / 1024 / 1024:.2f} MB | Selects: {stats_with[1]}")
    print(f"[Without Refresh] Time: {t_without:.4f}s | Peak Mem: {peak_without / 1024 / 1024:.2f} MB | Selects: {stats_without[1]}")
    print(f"Refresh Overhead: Time +{(t_with - t_without):.4f}s | Selects +{stats_with[1] - stats_without[1]}")

def mixed_repository_benchmark():
    print("\n=== Mixed Repository Production Simulation ===")
    counts = {
        "findings": 5000,
        "urls": 5000,
        "apis": 1000,
        "params": 1000,
        "secrets": 500,
        "reports": 500
    }
    SessionLocal, stats = create_db_session("bench_mixed.db")
    session_id = "bench_mixed"
    
    with SessionLocal() as session:
        session.add(ScanSessionModel(session_id=session_id, target_domain="bench.com", status="running", started_at=datetime.now(timezone.utc)))
        session.commit()
    
    tracemalloc.start()
    t0 = time.time()
    stats.reset()
    
    with SessionLocal() as session:
        # 1. Findings
        FindingRepository().create_bulk(session, session_id, [
            Finding(title=f"F{i}", severity=Severity.HIGH, confidence=Confidence.CERTAIN, evidence="E")
            for i in range(counts["findings"])
        ])
        # 2. URLs
        URLRepository().create_bulk(session, [{"session_id": session_id, "url": f"http://{i}"} for i in range(counts["urls"])])
        # 3. APIs
        APIRepository().create_bulk(session, [{"session_id": session_id, "type": "swagger", "url": f"http://{i}"} for i in range(counts["apis"])])
        # 4. Parameters
        ParameterRepository().create_bulk(session, [{"session_id": session_id, "url": "u", "parameter": f"p{i}"} for i in range(counts["params"])])
        # 5. Secrets
        SecretRepository().create_bulk(session, [{"session_id": session_id, "type": "aws", "value": f"v{i}", "source": "trufflehog", "confidence": "high"} for i in range(counts["secrets"])])
        # 6. Reports
        ReportRepository().create_bulk(session, [
            Report(session_id=session_id, report_path=f"/path/{i}", report_format=ReportFormat.JSON)
            for i in range(counts["reports"])
        ])
        
    t_total = time.time() - t0
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    total_entities = sum(counts.values())
    print(f"Total Entities: {total_entities}")
    print(f"Total Time: {t_total:.4f}s")
    print(f"Throughput: {total_entities / t_total:.2f} entities/s")
    print(f"Peak Mem: {peak_mem / 1024 / 1024:.2f} MB")
    print(f"SQL -> Inserts: {stats.inserts}, Selects: {stats.selects}, Commits: {stats.commits}")

if __name__ == "__main__":
    for count in [10000, 25000, 50000, 100000]:
        profile_db_writes(count)
        
    measure_refresh_cost()
    mixed_repository_benchmark()
