import time
import tracemalloc
from uuid import uuid4
from pathlib import Path
from datetime import datetime, timezone
from schemas.target import TargetState
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.checkpoint_manager import CheckpointManager
from schemas.finding import Finding

def profile_checkpoints(num_findings):
    print(f"\n--- Profiling Checkpoint Size & Cost: {num_findings} findings ---")
    
    db_path = f"bench_checkpoint_{num_findings}.db"
    if Path(db_path).exists():
        Path(db_path).unlink()
        
    cm = CheckpointManager(db_path=db_path)
    config = {
        "configurable": {
            "thread_id": f"bench_thread_{num_findings}",
            "checkpoint_ns": "",
            "checkpoint_id": str(uuid4())
        }
    }
    
    findings = tuple(Finding(
        title=f"Finding {i}",
        severity="high",
        confidence="certain",
        evidence="payload"
    ) for i in range(num_findings))
    
    exec_state = ExecutionState(
        target=TargetState(domain="bench.com", scope=("bench.com",), session_id="123", start_time=datetime.now(timezone.utc)),
        findings=findings
    )
    
    state = {
        "execution_state": exec_state,
        "orchestration_state": OrchestrationState(execution_state=exec_state, config=None, task_status={}, errors={})
    }
    
    # Measure serialization cost (Put)
    tracemalloc.start()
    start_time = time.time()
    
    # Simulating a state update cycle (Deep Copy Overhead)
    import copy
    
    tracemalloc.start()
    start_time = time.time()
    state_copy = copy.deepcopy(state)
    copy_time = time.time() - start_time
    copy_current, copy_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Measure serialization cost
    tracemalloc.start()
    start_time = time.time()
    serialized = exec_state.model_dump_json()
    serialize_time = time.time() - start_time
    serialize_current, serialize_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Measure File Size (simulated via pickle size)
    size_mb = len(serialized.encode('utf-8')) / 1024 / 1024
    
    # Measure deserialization cost (Get)
    tracemalloc.start()
    start_time = time.time()
    
    saved = ExecutionState.model_validate_json(serialized)
    
    get_time = time.time() - start_time
    get_current, get_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"DeepCopy Time: {copy_time:.4f}s, Peak Mem: {copy_peak / 1024 / 1024:.2f} MB")
    print(f"Serialize Time: {serialize_time:.4f}s, Peak Mem: {serialize_peak / 1024 / 1024:.2f} MB")
    print(f"Deserialize Time: {get_time:.4f}s, Peak Mem: {get_peak / 1024 / 1024:.2f} MB")
    print(f"Serialized Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    for count in [100, 1000, 10000, 50000]:
        profile_checkpoints(count)
