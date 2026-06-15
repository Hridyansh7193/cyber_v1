import pytest
from unittest.mock import patch
from execution.js.linkfinder_wrapper import LinkFinderWrapper
from execution.js.secretfinder_wrapper import SecretFinderWrapper
from execution.js.trufflehog_wrapper import TrufflehogWrapper

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_linkfinder_wrapper_success(mock_run):
    mock_run.return_value = (0, "linkfinder out", "", 1.0)
    res = LinkFinderWrapper.execute(["file1.js"])
    assert res.success

def test_linkfinder_wrapper_empty():
    res = LinkFinderWrapper.execute([])
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_secretfinder_wrapper_success(mock_run):
    mock_run.return_value = (0, "secretfinder out", "", 1.0)
    res = SecretFinderWrapper.execute(["file1.js"])
    assert res.success

def test_secretfinder_wrapper_empty():
    res = SecretFinderWrapper.execute([])
    assert res.success

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_trufflehog_wrapper_success(mock_run):
    mock_run.return_value = (0, "trufflehog out", "", 1.0)
    res = TrufflehogWrapper.execute(["repo1"], ["file1"])
    assert res.success
    assert mock_run.call_count == 2

def test_trufflehog_wrapper_empty():
    res = TrufflehogWrapper.execute([], [])
    assert res.success
