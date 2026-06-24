import re
from typing import Any

SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "authorization", "jwt", "cookie"}

def mask_string(value: str) -> str:
    if value.startswith("eyJ") and len(value) > 20:
        return "******** (JWT masked)"
    if re.match(r"(?i)^bearer\s+", value):
        return "Bearer ********"
    
    if len(value) > 8:
        return value[:4] + "********" + value[-4:]
    return "********"

def mask_sensitive_data(data: Any) -> Any:
    if isinstance(data, dict):
        masked_dict = {}
        for k, v in data.items():
            if any(sensitive in str(k).lower() for sensitive in SENSITIVE_KEYS):
                if isinstance(v, str):
                    masked_dict[k] = mask_string(v)
                else:
                    masked_dict[k] = "********"
            else:
                masked_dict[k] = mask_sensitive_data(v)
        return masked_dict
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data
