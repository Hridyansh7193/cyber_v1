import pytest
import subprocess
from unittest.mock import patch
from execution.recon.subfinder_wrapper import SubfinderWrapper
from execution.vuln.nuclei_wrapper import NucleiWrapper

@patch("execution.utils.process_runner.subprocess.run")
def test_integration_subfinder_process_runner(mock_subrun):
    # Setup mock
    mock_process = mock_subrun.return_value
    mock_process.returncode = 0
    mock_process.stdout = '{"host": "sub.example.com"}'
    mock_process.stderr = ""
    
    # Execute through wrapper -> process_runner -> mock_subprocess
    res = SubfinderWrapper.execute("example.com")
    
    # Verify
    assert res.success
    assert res.stdout == '{"host": "sub.example.com"}'
    mock_subrun.assert_called_once()
    
@patch("execution.utils.process_runner.subprocess.run")
def test_integration_nuclei_timeout(mock_subrun):
    mock_subrun.side_effect = subprocess.TimeoutExpired(["nuclei"], 300)
    
    res = NucleiWrapper.execute(["http://example.com"])
    
    assert not res.success
    assert res.exit_code == -1
    mock_subrun.assert_called_once()
