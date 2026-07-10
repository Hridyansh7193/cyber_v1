from services.scope_manager import ScopeManager

def test_no_scope_defined():
    sm = ScopeManager()
    assert sm.is_in_scope("example.com") is True
    assert sm.is_in_scope("192.168.1.1") is True

def test_in_scope_domain():
    sm = ScopeManager(in_scope=["*.example.com", "example.com"])
    assert sm.is_in_scope("example.com") is True
    assert sm.is_in_scope("api.example.com") is True
    assert sm.is_in_scope("hacker.com") is False

def test_in_scope_cidr():
    sm = ScopeManager(in_scope=["192.168.1.0/24"])
    assert sm.is_in_scope("192.168.1.50") is True
    assert sm.is_in_scope("192.168.2.1") is False
    assert sm.is_in_scope("example.com") is False

def test_out_of_scope_overrides():
    sm = ScopeManager(
        in_scope=["*.example.com"],
        out_of_scope=["admin.example.com", "10.0.0.0/8"]
    )
    assert sm.is_in_scope("api.example.com") is True
    assert sm.is_in_scope("admin.example.com") is False
    assert sm.is_in_scope("10.0.0.1") is False

def test_filter_targets():
    sm = ScopeManager(in_scope=["*.test.com", "test.com"], out_of_scope=["bad.test.com"])
    targets = ["test.com", "api.test.com", "bad.test.com", "other.com"]
    filtered = sm.filter_targets(targets)
    assert filtered == ["test.com", "api.test.com"]
