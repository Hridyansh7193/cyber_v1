import re
from typing import List, Union

# Regex to match common secret headers and flags
REDACTION_PATTERNS = [
    # Authorization header
    (re.compile(r'(?i)(Authorization:\s*(?:Bearer|Basic)\s+)[^\s"\'\\]+'), r'\1***REDACTED***'),
    # Generic API key header
    (re.compile(r'(?i)(x-api-key:\s*)[^\s"\'\\]+'), r'\1***REDACTED***'),
    # Generic token header
    (re.compile(r'(?i)(token:\s*)[^\s"\'\\]+'), r'\1***REDACTED***'),
    # Nuclei auth flags
    (re.compile(r'(-H\s+["\']?.*?Authorization:\s*(?:Bearer|Basic)\s+)[^\s"\'\\]+'), r'\1***REDACTED***'),
]

def redact_command_string(command: str) -> str:
    """Redact sensitive information from a command string."""
    if not command:
        return command
        
    redacted = command
    for pattern, replacement in REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted

def redact_command_list(command_list: List[str]) -> List[str]:
    """Redact sensitive information from a command list."""
    if not command_list:
        return command_list
        
    redacted_list = []
    # If the previous item was `-H` or `-header`, we might need to redact the current item
    for i, item in enumerate(command_list):
        redacted_item = redact_command_string(item)
        redacted_list.append(redacted_item)
        
    return redacted_list
