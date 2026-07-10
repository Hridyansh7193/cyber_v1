import subprocess
from unittest.mock import patch
from execution.utils.process_runner import ProcessRunner

@patch("execution.utils.process_runner.subprocess.run")
@patch("execution.utils.process_runner.shutil.which")
def test_integration_subfinder_process_runner(mock_which, mock_subrun):
    mock_which.return_value = "/usr/bin/echo"
    # Setup mock
    mock_process = mock_subrun.return_value
    mock_process.returncode = 0
    mock_process.stdout = '{"host": "sub.example.com"}'
    mock_process.stderr = ""
    
    res = ProcessRunner.run(["echo", "hello"], "test")
    
    assert res.success
    assert res.stdout == '{"host": "sub.example.com"}'
    mock_subrun.assert_called_once()
    
@patch("execution.utils.process_runner.subprocess.run")
@patch("execution.utils.process_runner.shutil.which")
def test_integration_nuclei_timeout(mock_which, mock_subrun):
    mock_which.return_value = "/usr/bin/nuclei"
    mock_subrun.side_effect = subprocess.TimeoutExpired(["nuclei"], 300)
    
    res = ProcessRunner.run(["nuclei"], "test")
    
    assert not res.success
    assert res.exit_code == -1
    assert mock_subrun.call_count == 1
