import pytest
from execution.utils.redaction import redact_command_string, redact_command_list

def test_redact_command_string():
    # Basic Authorization
    cmd = 'curl -H "Authorization: Bearer secret_token" https://example.com'
    redacted = redact_command_string(cmd)
    assert "secret_token" not in redacted
    assert "Authorization: Bearer ***REDACTED***" in redacted
    
    # x-api-key
    cmd2 = "python script.py -H 'X-API-Key: my_super_secret'"
    redacted2 = redact_command_string(cmd2)
    assert "my_super_secret" not in redacted2
    assert "X-API-Key: ***REDACTED***" in redacted2
    
    # Token
    cmd3 = 'nuclei -H "token: 12345" -u https://example.com'
    redacted3 = redact_command_string(cmd3)
    assert "12345" not in redacted3
    assert "token: ***REDACTED***" in redacted3

def test_redact_command_list():
    cmd_list = ["nuclei", "-H", "Authorization: Basic user:pass", "-u", "https://example.com"]
    redacted_list = redact_command_list(cmd_list)
    assert "user:pass" not in redacted_list[2]
    assert redacted_list[2] == "Authorization: Basic ***REDACTED***"
    
    # Unaffected list
    cmd_list2 = ["ls", "-la"]
    assert redact_command_list(cmd_list2) == ["ls", "-la"]
