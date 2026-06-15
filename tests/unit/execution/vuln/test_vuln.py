import pytest
from unittest.mock import patch
from execution.vuln.subzy_wrapper import SubzyWrapper
from execution.vuln.ffuf_wrapper import FfufWrapper
from execution.vuln.nuclei_wrapper import NucleiWrapper
from execution.vuln.dalfox_wrapper import DalfoxWrapper

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_subzy_wrapper_success(mock_run):
    mock_run.return_value = (0, "subzy out", "", 1.0)
    res = SubzyWrapper.execute(["sub.example.com"])
    assert res.success

def test_subzy_wrapper_empty():
    res = SubzyWrapper.execute([])
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_ffuf_wrapper_success(mock_run):
    mock_run.return_value = (0, "ffuf out", "", 1.0)
    res = FfufWrapper.execute("http://example.com", "wordlist.txt")
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_nuclei_wrapper_success(mock_run):
    mock_run.return_value = (0, "nuclei out", "", 1.0)
    res = NucleiWrapper.execute(["http://example.com"])
    assert res.success

def test_nuclei_wrapper_empty():
    res = NucleiWrapper.execute([])
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_dalfox_wrapper_success(mock_run):
    mock_run.return_value = (0, "dalfox out", "", 1.0)
    res = DalfoxWrapper.execute(["http://example.com"])
    assert res.success

def test_dalfox_wrapper_empty():
    res = DalfoxWrapper.execute([])
    assert res.success
