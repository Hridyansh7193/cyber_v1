import pytest
import os
import json
from core_logging.logger_factory import LoggerFactory
from core_logging.types import LogLevel

def test_integration_logging_lifecycle(tmpdir):
    log_dir = str(tmpdir.mkdir("logs"))
    logger = LoggerFactory.get_logger("database", log_dir=log_dir, level=LogLevel.DEBUG)
    
    logger.debug("Database connected", extra={"session_id": "sesh1"})
    logger.error("Query failed", extra={"session_id": "sesh1", "metadata": {"query": "SELECT *", "password": "supersecret"}})
    
    log_file = os.path.join(log_dir, "database", "database.log")
    assert os.path.exists(log_file)
    
    with open(log_file, "r") as f:
        lines = f.readlines()
        
    assert len(lines) == 2
    
    debug_log = json.loads(lines[0])
    assert debug_log["level"] == "DEBUG"
    assert debug_log["message"] == "Database connected"
    
    error_log = json.loads(lines[1])
    assert error_log["level"] == "ERROR"
    assert error_log["message"] == "Query failed"
    assert error_log["metadata"]["query"] == "SELECT *"
    assert error_log["metadata"]["password"] == "supe********cret"
