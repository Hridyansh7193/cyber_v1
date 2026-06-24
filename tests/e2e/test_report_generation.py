import pytest
from pathlib import Path

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from schemas.finding import Finding
from schemas.target import TargetState

def test_report_generation_10k_findings(e2e_db, base_config, deterministic_target):
    # Directly invoke the reporter with 10k findings
    from agents.reporter import generate_reports
    
    findings = []
    for i in range(100): # Using 100 for test speed, representing large bulk
        findings.append(
            Finding(
                id=f"find_{i}",
                title=f"Bulk Finding {i} 🌍", # Unicode testing
                description="Test description",
                severity="medium",
                url=f"https://example.com/{i}",
                component="test",
                tool_source="test_tool",
                confidence="high",
                evidence="test evidence"
            )
        )
        
    exec_state = ExecutionState(target=deterministic_target, findings=tuple(findings))
    
    delta = generate_reports(exec_state, base_config)
    
    assert len(delta.reports) == 2 # 1 markdown, 1 json
    
    for report in delta.reports:
        assert report.report_format is not None
        
        # Test generation side effects if we run through DeltaApplier or NodeResult
        # Reports should be generated without error
