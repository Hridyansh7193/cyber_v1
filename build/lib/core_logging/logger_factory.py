import logging
import os
from logging.handlers import RotatingFileHandler
from .json_logger import JSONFormatter
from .types import LogLevel

class LoggerFactory:
    @staticmethod
    def get_logger(component_name: str, log_dir: str = "logs", level: LogLevel = LogLevel.INFO) -> logging.Logger:
        logger = logging.getLogger(component_name)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
            
        logger.setLevel(level.value)
        logger.propagate = False
        
        component_dir = os.path.join(log_dir, component_name)
        
        try:
            os.makedirs(component_dir, exist_ok=True)
            log_file = os.path.join(component_dir, f"{component_name}.log")
            
            handler = RotatingFileHandler(
                log_file, maxBytes=50*1024*1024, backupCount=30
            )
            handler.setFormatter(JSONFormatter())
            logger.addHandler(handler)
        except OSError:
            logger.addHandler(logging.NullHandler())
            
        return logger
