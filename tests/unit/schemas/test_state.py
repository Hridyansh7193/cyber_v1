import pytest
from datetime import datetime, UTC
from schemas.state import ReconState, JSState, APIState, VulnerabilityState, ExecutionState
from schemas.target import TargetState
from pydantic import ValidationError

def test_recon_state():
    state = ReconState(subdomains=("a.com",))
    assert state.subdomains == ("a.com",)
    assert state.alive_hosts == ()

def test_js_state():
    state = JSState(endpoints=("/api",))
    assert state.js_files == ()
    assert state.endpoints == ("/api",)

def test_api_state():
    state = APIState(swagger_urls=("/swagger.json",))
    assert state.swagger_urls == ("/swagger.json",)

def test_vulnerability_state():
    state = VulnerabilityState(nuclei_results=({"vuln": "xss"},))
    assert state.nuclei_results == ({"vuln": "xss"},)

def test_execution_state_defaults():
    start = datetime.now(UTC)
    target = TargetState(domain="example.com", session_id="123", start_time=start)
    exec_state = ExecutionState(target=target)
    
    assert exec_state.target.domain == "example.com"
    assert exec_state.task_queue == ()
    assert isinstance(exec_state.recon_state, ReconState)
    assert isinstance(exec_state.js_state, JSState)
    assert isinstance(exec_state.api_state, APIState)
    assert isinstance(exec_state.vuln_state, VulnerabilityState)
    assert exec_state.findings == ()
    assert exec_state.reports == ()
    assert exec_state.logs == ()
    assert exec_state.metadata == {}

def test_execution_state_serialization():
    start = datetime.now(UTC)
    target = TargetState(domain="example.com", session_id="123", start_time=start)
    exec_state = ExecutionState(target=target)
    
    data = exec_state.model_dump()
    assert data["target"]["domain"] == "example.com"
    assert "recon_state" in data
    
    json_data = exec_state.model_dump_json()
    assert "example.com" in json_data

def test_execution_state_deserialization():
    start = datetime.now(UTC)
    data = {
        "target": {
            "domain": "example.com",
            "session_id": "123",
            "start_time": start.isoformat(),
            "scope": []
        },
        "task_queue": [],
        "recon_state": {"subdomains": [], "alive_hosts": [], "urls": [], "parameters": []},
        "js_state": {"js_files": [], "endpoints": [], "secrets": []},
        "api_state": {"swagger_urls": [], "graphql_urls": []},
        "vuln_state": {"nuclei_results": [], "dalfox_results": [], "takeovers": []},
        "findings": [],
        "reports": [],
        "logs": [],
        "metadata": {}
    }
    
    exec_state = ExecutionState.model_validate(data)
    assert exec_state.target.domain == "example.com"
    assert isinstance(exec_state.recon_state, ReconState)
