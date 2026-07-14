import pytest
from utils.target_utils import sanitize_workspace_target

def test_sanitize_localhost_port():
    res1 = sanitize_workspace_target("localhost:3000")
    res2 = sanitize_workspace_target("localhost_3000")
    
    # "localhost:3000" contains a colon, so it gets hashed.
    assert res1.startswith("localhost_3000_")
    assert len(res1) > len("localhost_3000_")
    
    # "localhost_3000" is already safe, so no hash appended
    assert res2 == "localhost_3000"
    
    assert res1 != res2

def test_sanitize_http_prefix():
    res = sanitize_workspace_target("http://localhost:3000")
    assert res.startswith("localhost_3000_")
    
    res_https = sanitize_workspace_target("https://example.com:8443/api")
    assert res_https.startswith("example.com_8443_api_")

def test_sanitize_traversal():
    res = sanitize_workspace_target("../../../etc/passwd")
    assert ".." not in res
    assert "/" not in res
    assert "_" in res

def test_sanitize_ipv4_ipv6():
    res_v4 = sanitize_workspace_target("192.168.1.1")
    assert res_v4 == "192.168.1.1" # No invalid chars
    
    res_v6 = sanitize_workspace_target("::1")
    assert "_" in res_v6
    assert ":" not in res_v6

def test_sanitize_windows_reserved():
    res = sanitize_workspace_target("test<>\":/\\|?*name")
    assert "test_________name_" in res

def test_sanitize_long_target():
    long_target = "a" * 100
    res = sanitize_workspace_target(long_target)
    assert len(res) <= 73 # Max length is 64 + 9 (hash) = 73

def test_sanitize_unicode():
    res = sanitize_workspace_target("example.com/測試")
    assert "example.com_測試" in res
