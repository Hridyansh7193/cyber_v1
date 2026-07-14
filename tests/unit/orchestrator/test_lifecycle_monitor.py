"""
Test lifecycle monitoring for orchestration execution.

Verifies that:
- Node transitions are tracked
- Watchdog detects stalled nodes
- Diagnostic reports are generated correctly
"""

import time
from orchestrator.lifecycle_monitor import get_monitor, LifecycleMonitor


def test_lifecycle_monitor_node_tracking():
    """Test basic node entry/exit tracking."""
    monitor = LifecycleMonitor()
    job_id = "test-job-123"
    
    # Simulate node execution
    transition = monitor.node_enter(job_id, "test_node")
    assert transition.node_name == "test_node"
    assert transition.job_id == job_id
    assert transition.status == "RUNNING"
    
    time.sleep(0.1)
    monitor.node_exit(transition, status="SUCCESS")
    
    assert transition.status == "SUCCESS"
    assert transition.elapsed_seconds is not None
    assert transition.elapsed_seconds >= 0.08  # Allow for timing variance
    
    # Verify transition is recorded
    transitions = monitor.get_transitions(job_id)
    assert len(transitions) == 1
    assert transitions[0] == transition


def test_lifecycle_monitor_multiple_nodes():
    """Test tracking multiple nodes in sequence."""
    monitor = LifecycleMonitor()
    job_id = "test-job-456"
    nodes = ["node_a", "node_b", "node_c"]
    
    for node_name in nodes:
        t = monitor.node_enter(job_id, node_name)
        time.sleep(0.05)
        monitor.node_exit(t, status="SUCCESS")
    
    transitions = monitor.get_transitions(job_id)
    assert len(transitions) == 3
    assert [t.node_name for t in transitions] == nodes
    assert all(t.status == "SUCCESS" for t in transitions)


def test_lifecycle_monitor_error_tracking():
    """Test tracking node failures."""
    monitor = LifecycleMonitor()
    job_id = "test-job-error"
    
    transition = monitor.node_enter(job_id, "failing_node")
    time.sleep(0.05)
    monitor.node_exit(transition, status="FAILED", error="Test error message")
    
    transitions = monitor.get_transitions(job_id)
    assert len(transitions) == 1
    assert transitions[0].status == "FAILED"
    assert transitions[0].error == "Test error message"


def test_lifecycle_monitor_diagnostics():
    """Test diagnostic report generation."""
    monitor = LifecycleMonitor()
    job_id = "test-job-diag"
    
    # Simulate a multi-node execution
    nodes = [
        ("init", 0.05),
        ("recon", 0.1),
        ("scope", 0.03),
    ]
    
    for node_name, sleep_time in nodes:
        t = monitor.node_enter(job_id, node_name)
        time.sleep(sleep_time)
        monitor.node_exit(t, status="SUCCESS")
    
    diagnostics = monitor.dump_diagnostics(job_id)
    
    # Verify diagnostics contain expected information
    assert job_id in diagnostics
    assert "Lifecycle Diagnostics" in diagnostics
    assert "Total nodes executed: 3" in diagnostics
    assert "init" in diagnostics
    assert "recon" in diagnostics
    assert "scope" in diagnostics


def test_lifecycle_monitor_watchdog():
    """Test watchdog detection of stalled nodes."""
    monitor = LifecycleMonitor(warn_node_timeout_sec=0.2)
    monitor.start_watchdog()
    
    job_id = "test-job-watchdog"
    
    try:
        transition = monitor.node_enter(job_id, "stalled_node")
        
        # Keep node running longer than timeout
        time.sleep(0.5)
        
        monitor.node_exit(transition, status="SUCCESS")
    finally:
        monitor.stop_watchdog()
    
    # Verify the node was tracked
    transitions = monitor.get_transitions(job_id)
    assert len(transitions) == 1


def test_lifecycle_monitor_singleton():
    """Test that get_monitor() returns a singleton."""
    m1 = get_monitor()
    m2 = get_monitor()
    
    assert m1 is m2


def test_lifecycle_monitor_scan_lifecycle():
    """Test complete scan lifecycle tracking."""
    monitor = LifecycleMonitor()
    job_id = "test-job-full"
    
    # Start scan
    monitor.scan_start(job_id, "example.com")
    
    # Simulate nodes
    nodes_data = [
        ("init_node", "SUCCESS", None),
        ("planner_node", "SUCCESS", None),
        ("passive_recon_node", "SUCCESS", None),
        ("scope_enforcement_node", "SUCCESS", None),
        ("active_recon_node", "SUCCESS", None),
    ]
    
    for node_name, status, error in nodes_data:
        t = monitor.node_enter(job_id, node_name)
        time.sleep(0.01)
        monitor.node_exit(t, status=status, error=error)
    
    # Complete scan
    monitor.scan_complete(job_id, "COMPLETED", findings_count=42)
    
    # Verify all transitions recorded
    transitions = monitor.get_transitions(job_id)
    assert len(transitions) == 5
    assert all(t.status == "SUCCESS" for t in transitions)


if __name__ == "__main__":
    test_lifecycle_monitor_node_tracking()
    test_lifecycle_monitor_multiple_nodes()
    test_lifecycle_monitor_error_tracking()
    test_lifecycle_monitor_diagnostics()
    test_lifecycle_monitor_watchdog()
    test_lifecycle_monitor_singleton()
    test_lifecycle_monitor_scan_lifecycle()
    print("All lifecycle monitor tests passed!")
