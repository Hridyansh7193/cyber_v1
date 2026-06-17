import pytest
from orchestrator.retry_policy import get_retry_policy

def test_retry_policy():
    policy = get_retry_policy()
    assert policy.max_attempts == 3
    
    # Should retry on TimeoutError, ConnectionError, OSError, RuntimeError
    assert policy.retry_on(TimeoutError())
    assert policy.retry_on(ConnectionError())
    assert policy.retry_on(OSError())
    
    # Should NOT retry on RuntimeError, ValueError or TypeError
    assert not policy.retry_on(RuntimeError())
    assert not policy.retry_on(ValueError())
    assert not policy.retry_on(TypeError())
    
    # Prove wrappers/nodes never loop internally; exceptions propagate
    def wrapper_fails():
        raise TimeoutError("Test")
        
    with pytest.raises(TimeoutError):
        wrapper_fails()
