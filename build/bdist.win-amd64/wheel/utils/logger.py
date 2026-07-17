import logging
import sys
import os

_loggers = {}
_root_configured = False

def get_logger(name: str) -> logging.Logger:
    global _root_configured
    if not _root_configured:
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            stream=sys.stdout)
        _root_configured = True
        
    if name in _loggers:
        return _loggers[name]
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
        
    _loggers[name] = logger
    return logger

def setup_job_logger(job_id: str, workspace_path: str):
    """Sets up a file handler for the specific job's execution.log"""
    log_dir = os.path.join(workspace_path, "sessions", job_id)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "execution.log")
    
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    # Attach to root logger so all logs go to this file
    logging.getLogger().addHandler(fh)
