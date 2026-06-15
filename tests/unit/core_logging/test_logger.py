import pytest
import os
import json
import logging
from core_logging.logger_factory import LoggerFactory
from core_logging.types import LogLevel
from core_logging.json_logger import JSONFormatter

def test_logger_factory_creates_logger(tmpdir):
    log_dir = str(tmpdir.mkdir("logs"))
    logger = LoggerFactory.get_logger("system", log_dir=log_dir)
    assert logger.name == "system"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1

def test_prevent_duplicate_handlers(tmpdir):
    log_dir = str(tmpdir.mkdir("logs"))
    logger1 = LoggerFactory.get_logger("recon", log_dir=log_dir)
    logger2 = LoggerFactory.get_logger("recon", log_dir=log_dir)
    assert len(logger1.handlers) == 1
    assert len(logger2.handlers) == 1
    assert logger1 is logger2

def test_json_formatting_and_file_creation(tmpdir):
    log_dir = str(tmpdir.mkdir("logs"))
    logger = LoggerFactory.get_logger("planner", log_dir=log_dir)
    
    # Need to log something
    logger.info("Test message", extra={"session_id": "123", "event": "test_event", "metadata": {"foo": "bar"}})
    
    # Read the log file
    log_file = os.path.join(log_dir, "planner", "planner.log")
    assert os.path.exists(log_file)
    
    with open(log_file, "r") as f:
        line = f.readline()
        
    data = json.loads(line)
    assert data["message"] == "Test message"
    assert data["level"] == "INFO"
    assert data["session_id"] == "123"
    assert data["event"] == "test_event"
    assert data["component"] == "planner"
    assert data["metadata"] == {"foo": "bar"}

def test_failure_handling_null_handler():
    # Provide an explicitly invalid directory for Windows/Linux
    logger = LoggerFactory.get_logger("invalid_test", log_dir="C:\\invalid|dir\\<>?*")
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.NullHandler)
