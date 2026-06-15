import pytest
from unittest.mock import patch
from execution.recon.subfinder_wrapper import SubfinderWrapper
from execution.recon.httpx_wrapper import HttpxWrapper
from execution.recon.assetfinder_wrapper import AssetfinderWrapper
from execution.recon.katana_wrapper import KatanaWrapper
from execution.recon.gau_wrapper import GauWrapper

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_subfinder_wrapper_success(mock_run):
    mock_run.return_value = (0, "output", "", 1.0)
    res = SubfinderWrapper.execute("example.com")
    assert res.success
    assert res.stdout == "output"
    assert res.metadata["domain"] == "example.com"

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_httpx_wrapper_success(mock_run):
    mock_run.return_value = (0, "httpx output", "", 1.0)
    res = HttpxWrapper.execute(["sub.example.com"])
    assert res.success
    assert res.stdout == "httpx output"

def test_httpx_wrapper_empty():
    res = HttpxWrapper.execute([])
    assert res.success
    assert res.metadata["input_count"] == 0

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_assetfinder_wrapper_success(mock_run):
    mock_run.return_value = (0, "asset out", "", 1.0)
    res = AssetfinderWrapper.execute("example.com")
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_katana_wrapper_success(mock_run):
    mock_run.return_value = (0, "katana out", "", 1.0)
    res = KatanaWrapper.execute(["http://example.com"])
    assert res.success

def test_katana_wrapper_empty():
    res = KatanaWrapper.execute([])
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_gau_wrapper_success(mock_run):
    mock_run.return_value = (0, "gau out", "", 1.0)
    res = GauWrapper.execute("example.com")
    assert res.success

