import pytest
import urllib.error
from services.target_service import TargetService
from services.target_resolver import TargetResolver

def test_validate_domain():
    assert TargetService.validate_domain("example.com") == "example.com"
    assert TargetService.validate_domain("http://example.com") == "example.com"
    assert TargetService.validate_domain("https://example.com/path") == "example.com"
    assert TargetService.validate_domain("http://localhost:3000") == "localhost:3000"
    assert TargetService.validate_domain("127.0.0.1:8080") == "127.0.0.1:8080"
    
    with pytest.raises(ValueError):
        TargetService.validate_domain("")
        
    with pytest.raises(ValueError):
        TargetService.validate_domain("nodot")
        
def test_normalize_target():
    target = TargetService.normalize_target("http://example.com", "session_123")
    assert target.domain == "example.com"
    assert target.session_id == "session_123"


def test_normalize_local_url_preserves_connection_details():
    target = TargetService.normalize_target("http://localhost:3000", "session_123")

    assert target.domain == "localhost:3000"
    assert target.hostname == "localhost"
    assert target.scheme == "http"
    assert target.port == 3000


def test_explicit_url_is_preserved_when_head_probe_fails(monkeypatch):
    target = TargetService.normalize_target("http://localhost:3000", "session_123")

    def reject_head(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "http://localhost:3000", 405, "Method Not Allowed", {}, None
        )

    monkeypatch.setattr("urllib.request.urlopen", reject_head)

    resolved = TargetResolver().resolve_target(target)

    assert resolved.alive is True
    assert resolved.resolved_url == "http://localhost:3000"
    assert resolved.scheme == "http"
    assert resolved.port == 3000
