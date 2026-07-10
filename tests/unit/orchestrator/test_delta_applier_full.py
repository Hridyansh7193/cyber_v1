import pytest
from datetime import datetime, timezone
import uuid
from schemas.state import ExecutionState, TargetState, ReconState, JSState, APIState, VulnerabilityState
from agents.deltas import ReconDelta, JSDelta, APIDelta, VulnerabilityDelta, FindingDelta, TaskQueueDelta, ReportDelta
from schemas.finding import Finding, Severity, Confidence
from schemas.task import Task, TaskPriority
from schemas.report import Report, ReportFormat, DiscoveredAssets
from orchestrator.delta_applier import (
    apply_recon_delta, apply_js_delta, apply_api_delta, 
    apply_vulnerability_delta, apply_finding_delta, apply_report_delta, apply_task_queue_delta
)

def test_apply_recon_delta():
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    delta = ReconDelta(subdomains=("sub.example.com",), alive_hosts=("sub.example.com",), urls=("http://sub.example.com",), tech_stack={"sub.example.com": ("nginx",)}, waf_detected={"sub.example.com": False})
    new_state = apply_recon_delta(state, delta)
    assert new_state.recon_state.subdomains == ("sub.example.com",)
    assert new_state.recon_state.tech_stack["sub.example.com"] == ("nginx",)

def test_apply_js_delta():
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    delta = JSDelta(js_files=("app.js",), endpoints=("/api/v1",))
    new_state = apply_js_delta(state, delta)
    assert new_state.js_state.js_files == ("app.js",)

def test_apply_api_delta():
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    delta = APIDelta(swagger_urls=("http://api/docs",), graphql_urls=())
    new_state = apply_api_delta(state, delta)
    assert new_state.api_state.swagger_urls == ("http://api/docs",)

def test_apply_vulnerability_delta():
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    delta = VulnerabilityDelta(findings=[{"id": "1", "title": "XSS"}])
    new_state = apply_vulnerability_delta(state, delta)
    assert len(new_state.findings) == 1
    assert new_state.findings[0].title == "XSS"

def test_apply_finding_delta():
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    delta = FindingDelta(findings=[Finding(id="2", title="IDOR", severity="high", confidence="certain", evidence="", references=())])
    new_state = apply_finding_delta(state, delta)
    assert len(new_state.findings) == 1
    assert new_state.findings[0].title == "IDOR"

def test_apply_report_delta():
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    r1 = Report(report_id=uuid.uuid4(), session_id="1", report_path="test.md", report_format=ReportFormat.MARKDOWN, created_at=datetime.now(timezone.utc))
    delta = ReportDelta(reports=(r1,))
    new_state = apply_report_delta(state, delta)
    assert new_state is not state
    assert len(new_state.reports) == 1
