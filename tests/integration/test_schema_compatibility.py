import pytest
import json
from datetime import datetime, timezone
from schemas.state import ExecutionState
from schemas.target import TargetState
from schemas.intelligence import IntelligenceState

def test_phase_12_deserialization():
    # Simulate a Phase 12 ExecutionState JSON which lacks intelligence
    old_json = json.dumps({
        "target": {
            "domain": "example.com",
            "scope": [],
            "session_id": "test_session",
            "start_time": datetime.now(timezone.utc).isoformat()
        },
        "recon_state": {
            "subdomains": ["api.example.com"],
            "urls": []
        },
        "api_state": {
            "swagger_urls": [],
            "graphql_urls": []
        },
        "findings": [],
        "scan_status": "in_progress",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": None
    })
    
    # Verify it deserializes without error
    state = ExecutionState.model_validate_json(old_json)
    
    # Missing intelligence should default to None
    assert getattr(state, "intelligence", None) is None
    
    # Verify model_dump_json is stable
    new_json = state.model_dump_json()
    new_state = ExecutionState.model_validate_json(new_json)
    assert new_state.target.domain == "example.com"
    assert new_state.intelligence is None

def test_intelligence_version():
    intelligence = IntelligenceState()
    # The version field should default to 1 (or as defined)
    assert intelligence.version == 1
    
    # Attempt to mutate version
    with pytest.raises(Exception): # ValidationError / frozen error
        intelligence.version = 2

def test_immutability():
    state = ExecutionState(
        target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc))
    )
    with pytest.raises(Exception):
        state.scan_status = "completed"

