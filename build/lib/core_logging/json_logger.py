import logging
import json
from datetime import datetime, timezone
from .masking import mask_sensitive_data

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "session_id": getattr(record, "session_id", "unknown"),
            "component": record.name,
            "event": getattr(record, "event", "log_event"),
            "level": record.levelname,
            "message": record.getMessage()
        }
        
        metadata = getattr(record, "metadata", {})
        if metadata:
            log_entry["metadata"] = mask_sensitive_data(metadata)
            
        masked_msg = mask_sensitive_data({"msg": log_entry["message"]})["msg"]
        log_entry["message"] = masked_msg
        
        # We can add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)
