import pytest
from datetime import datetime
from pydantic import ValidationError
from schemas.target import TargetState

def test_target_state_valid():
    start = datetime.now()
    target = TargetState(domain="example.com", session_id="123", start_time=start)
    assert target.domain == "example.com"
    assert target.scope == []
    assert target.session_id == "123"
    assert target.start_time == start

def test_target_state_with_scope():
    start = datetime.now()
    target = TargetState(domain="example.com", scope=["*.example.com"], session_id="123", start_time=start)
    assert target.scope == ["*.example.com"]

def test_target_state_missing_required():
    with pytest.raises(ValidationError):
        TargetState(domain="example.com")
