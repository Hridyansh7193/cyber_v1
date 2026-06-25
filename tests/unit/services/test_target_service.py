import pytest
from services.target_service import TargetService

def test_validate_domain():
    assert TargetService.validate_domain("example.com") == "example.com"
    assert TargetService.validate_domain("http://example.com") == "example.com"
    assert TargetService.validate_domain("https://example.com/path") == "example.com"
    
    with pytest.raises(ValueError):
        TargetService.validate_domain("")
        
    with pytest.raises(ValueError):
        TargetService.validate_domain("nodot")
        
def test_normalize_target():
    target = TargetService.normalize_target("http://example.com", "session_123")
    assert target.domain == "example.com"
    assert target.session_id == "session_123"
